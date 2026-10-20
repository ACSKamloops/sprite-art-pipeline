// @exec: {"yield_time_ms": 1000, "max_output_tokens": 1200}
// Paste into functions.exec after adapting these paths and reading batch-runbook.md.
// All job inputs must already have been inspected and source-reviewed by the agent.
// This drives tool calls, not subagents, and never auto-approves generated artwork.
const ROOT = "/absolute/path/to/art-work-area";
const SKILL = "/absolute/path/to/reference-art-production";
const WORKERS = 2; // Choose supported concurrency; 1 is sufficient.
const JOBS_PER_WORKER = 3; // Bounded windows; resume by running another window.

function quote(value) {
  return "'" + String(value).replaceAll("'", "'\"'\"'") + "'";
}
async function command(args) {
  let result = await tools.exec_command({
    cmd: ["python", `${SKILL}/scripts/claim_next.py`, "--root", ROOT, ...args].map(quote).join(" "),
    workdir: ROOT,
    yield_time_ms: 1000,
    max_output_tokens: 10000,
  });
  let output = result.output;
  while (result.session_id) {
    result = await tools.write_stdin({session_id: result.session_id, chars: "", yield_time_ms: 1000, max_output_tokens: 10000});
    output += result.output;
  }
  if (result.exit_code !== 0) throw new Error(output);
  return JSON.parse(output);
}
async function writeJson(path, value) {
  const body = JSON.stringify(value, null, 2).split("\n").map(line => "+" + line).join("\n");
  const result = await tools.apply_patch(`*** Begin Patch\n*** Add File: ${path}\n${body}\n*** End Patch`);
  if (result?.isError) throw new Error("Receipt write failed");
}
async function worker(index) {
  const workerName = `art-worker-${index}`;
  let generated = 0;
  for (let count = 0; count < JOBS_PER_WORKER; count++) {
    const job = await command(["next", "--worker", workerName]);
    if (!job) return {worker: workerName, generated, idle: true};
    const plan = job.plan;
    const references = (plan.references || []).map(ref =>
      ref.path.startsWith("/") ? ref.path : `${ROOT}/${ref.path}`);
    const receiptPath = `${ROOT}/.art-pipeline/tool-result-${job.token}.json`;
    let receipt;
    try {
      const args = {prompt: plan.prompt, transparent_background: plan.transparent_background ?? false};
      if (references.length) args.referenced_image_paths = references;
      const result = await tools.image_gen__imagegen(args);
      // Use the actual saved output returned by the enabled tool. Adapt if its result format differs.
      const outputPath = result.output_hint?.match(/as (\/.*?\.png) by default/)?.[1];
      if (!outputPath) throw new Error("Tool returned no recognizable saved image path; inspect its result");
      receipt = {executed_prompt: plan.prompt, reference_paths: references,
        generated_source: outputPath, tool: "image_gen.imagegen", output_hint: result.output_hint};
    } catch (error) {
      const errorPath = `${ROOT}/.art-pipeline/tool-error-${job.token}.json`;
      const message = String(error);
      await writeJson(errorPath, {error: message});
      const kind = /moderation|rejected by the safety system/i.test(message) ? "blocked" : "other";
      await command(["fail", "--job", job.job_id, "--worker", workerName, "--token", job.token,
        "--error", errorPath, "--kind", kind]);
      notify({job_id: job.job_id, failed: true});
      continue; // Another job, not an automatic retry of this failure.
    }
    await writeJson(receiptPath, receipt);
    // If saving/committing fails, stop this worker. Keep its claim and successful tool receipt
    // for recovery; do not generate the same image again merely to fix bookkeeping.
    await command(["complete", "--job", job.job_id, "--worker", workerName, "--token", job.token,
      "--receipt", receiptPath]);
    generated++;
    notify({job_id: job.job_id, generated: true, review: "pending"});
  }
  return {worker: workerName, generated, window_finished: true};
}
const results = await Promise.allSettled(Array.from({length: WORKERS}, (_, index) => worker(index)));
for (const result of results) {
  text(result.status === "fulfilled" ? result.value : {worker_error: String(result.reason)});
}
