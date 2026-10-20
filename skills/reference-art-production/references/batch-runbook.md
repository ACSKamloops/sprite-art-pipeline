# Runnable claim, generation and review pipeline

Read this for a collection large enough to benefit from resumable workers. This packages the claim-next pattern used in the art-production run: prepared prompts, inspected references, exclusive jobs, immediate per-job receipts, one publisher, pending comparison sheets, targeted repairs and hash-bound acceptance. It uses a SQLite transaction instead of the original small `fcntl` lock file so claims and histories remain durable and concurrent workers cannot reserve the same job. It runs locally and makes no image API calls itself.

## 1. Prepare the work area and plan

Use a dedicated working collection, keeping source inputs unchanged. The two helpers live in this skill's `scripts/` directory. Discover that directory in the current environment; the paths below are examples.

```bash
ART_SKILL=/absolute/path/to/reference-art-production
ART_WORK=/absolute/path/to/art-work-area
mkdir -p "$ART_WORK"
cd "$ART_WORK"
```

Prepare `generation-plan.json` with the frozen inventory and actual executable prompts. Hash input files using SHA-256. All input paths resolve from this work area; absolute reference paths are supported for a shared local machine. Do not include invented reference hashes.

```json
{
  "schema_version": 1,
  "target_ids": ["explorer", "explorer-catalog-alias"],
  "art_spec": {
    "kind": "pixel-sprite", "transparent": true,
    "canvas": [256, 256], "fit": [224, 224],
    "anchor": "bottom", "baseline": 240,
    "alpha_threshold": 128, "scales": [1, 2],
    "reject_source_boundary_touch": true
  },
  "jobs": [{
    "job_id": "explorer", "name": "Clockwork explorer", "group": "Characters",
    "covers": ["explorer", "explorer-catalog-alias"], "priority": 0,
    "mode": "generate", "transparent_background": true,
    "prompt": "Actual complete subject prompt with ordered image roles and approved style constraints",
    "references": [
      {"role": "identity", "path": "source/explorer.jpg", "sha256": "ACTUAL_SHA256"},
      {"role": "style", "path": "source/approved-style.png", "sha256": "ACTUAL_SHA256"}
    ],
    "notes": ["Static portrait; unseen rear details are authored"]
  }]
}
```

For non-pixel native raster art, use `{"kind":"raster","transparent":false}` as the art specification. For original designs with no images, use `references: []` and a concrete written brief in the prompt. One job may cover catalog aliases only when the required art is interchangeable. Each frozen target must be covered exactly once.

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" init generation-plan.json
```

Initialization is resumable with the identical original plan and will not reset completed work. Do not edit and reinitialize the plan to retry a subject. The database `.art-pipeline/state.sqlite3` is the durable queue; its event history preserves earlier plans, attempts, errors and reviews. Attempt-specific masters and receipts remain in `masters/` and `receipts/`.

## 2. Inspect and approve generation inputs

View each identity/style/pose image using the image-viewing tool. Check missing photos, wrong variants and hidden geometry before spending generation work. Read the approved art brief for original designs without photos. Save actual source-review observations:

```json
{"reviewer":"root-agent","observations":["Full silhouette, goggles and backpack are visible","Second input is style only"]}
```

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" source-review \
  --job explorer --review review/source-explorer.json
```

This records an inspection already performed; it does not perform visual inspection automatically. The coordinator binds it to the exact prompt and input hashes. Jobs with missing/stale source approval are not claimable. For unchanged inputs on a retry, actual earlier observations may be reused without pretending another inspection occurred.

## 3. Claim and execute bounded worker windows

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" next --worker worker-a
```

The JSON result contains `job_id`, worker, a unique token, attempt number, plan hash and complete plan. Only that worker/token can complete, fail or release that claim. `next` skips claimed, generated, failed, rejected and accepted jobs. Lower priority numbers are selected first. It returns JSON `null` when no approved ready job is available; this does **not** mean the collection is complete.

Use the built-in image tool with the claimed prompt and ordered local inputs, retaining the specified transparency. [worker-driver.js](worker-driver.js) is a concrete `functions.exec` orchestration example: adapt `ROOT` and `SKILL`, use the enabled tool's actual names/result format, then paste it into `functions.exec`. It runs a small number of async tool workers and awaits them all. It does not spawn agents, require an API key, auto-retry errors or approve outputs. Use one worker if concurrency is unsupported. Keep source references pre-inspected before starting the window.

Issue progress updates as the worker cell yields. Resume a running cell with the appropriate wait tool; do not start duplicate cells because a long image call has not yet returned. Await all worker promises so successful calls are not discarded when the exec context ends. Save every output before claiming the next subject. Repeat bounded windows rather than regenerating completed jobs after a context change.

A successful generation receipt must contain the actual values:

```json
{
  "executed_prompt": "Exactly the claimed prompt",
  "reference_paths": ["/actual/ordered/input-1.jpg", "/actual/ordered/input-2.png"],
  "generated_source": "/actual/saved/tool-output.png",
  "tool": "image_gen.imagegen"
}
```

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" complete \
  --job explorer --worker worker-a --token TOKEN_FROM_CLAIM --receipt tool-result.json
```

Completion checks ordered inputs and exact prompt, copies the master into the work area, preserves the receipt and changes the job to `generated`. This is not a visual acceptance. If generation succeeds but bookkeeping fails, keep the receipt and active claim, fix the saving problem, then run `complete` with that same token. Do not generate a second image merely to repair a receipt write. If a crash left an attempt-specific receipt already saved, inspect it and the claim before finishing the same attempt.

For a real failure, save the actual error text in `{"error":"..."}`:

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" fail \
  --job explorer --worker worker-a --token TOKEN_FROM_CLAIM --error tool-error.json --kind transient
```

Use `blocked` for an actual moderation rejection, `transient` for a demonstrably transient service failure, or `other`. Errors and historical masters are retained per attempt. Workers can continue other jobs; failures are not silently erased or retried.

## 4. Publish a stable review snapshot

Only the coordinator/publisher writes the art manifest and derived exports. Workers write through the queue into separate attempt files. Do not let multiple agents edit the same checkout or manifest. If actual agent delegation is requested, follow the environment's worktree/workspace isolation rules and give workers only their assigned areas.

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" sync
python "$ART_SKILL/scripts/art_assets.py" export art-manifest.json
python "$ART_SKILL/scripts/art_assets.py" contact-sheet art-manifest.json \
  --pending-only --page-size 8 --out review/pass-01
```

`sync` includes current successful candidates and keeps existing exports only when the selected master has not changed. It writes `art-manifest.json` plus `source-id-map.json`. It refuses to replace a manifest belonging to another pipeline. It always clears the complete flag because this is an evolving publish step.

Review only the files and IDs in `review/pass-01/pages.json`, not leftover sheet filenames. Use a new pass directory for the next snapshot. Do not regenerate or overwrite that snapshot while inspecting it. Generation workers can finish unrelated jobs meanwhile; sync them into a later snapshot.

Compare each final export to its actual references. Open uncertain subjects separately. Inspect the canonical art and integer enlargement, not only the high-resolution master. Save the exact canonical export hash you inspected, actual reviewer identity and observations:

```json
{
  "export_sha256": "ACTUAL_1X_EXPORT_SHA256",
  "reviewer": "root-agent",
  "observations": ["Silhouette and accessories match", "Fine engraving simplified at this scale"]
}
```

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" review \
  --job explorer --decision accepted --review review/export-explorer.json
```

Use `--decision repair-needed` with concrete defects when it fails. The command records an inspection already performed; it cannot assess art itself. It refuses a stale hash or a manifest for another generation attempt. Independent adversarial review, when requested, uses the same actual files and should report source ambiguity separately from genuine defects.

After recording reviews, run `sync` again to publish current review states and the source-ID map. Unchanged exports keep their acceptance. A changed export or repaired master returns to pending review. A stale database count is not proof of final acceptance: compare the final manifest and actual exported bytes.

## 5. Repairs, retries and interrupted workers

For a rejected image, create `revised-explorer.json` as a **single job object**, retaining its `job_id` and frozen `covers`. Set `mode: edit`, add the latest generated master as an `edit-target` reference with its hash, retain relevant identity/style inputs, and use a targeted prompt naming the defect and invariants. Inspect any newly added completion photographs first. Describe authored changes in `notes`.

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" retry \
  --job explorer --plan revised-explorer.json --reason 'Restore missing backpack; preserve palette and pose'
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" source-review \
  --job explorer --review review/revised-inputs-explorer.json
```

Then claim, edit, complete, sync, export and review the new candidate. Older masters, receipts and review events remain available. A transient failure can be retried with the same plan and an explicit reason, followed by source review. A blocked request requires a genuinely permissible adaptation; the helper rejects identical blocked plans, but a changed hash alone does not establish that the adaptation is appropriate. Do not repeatedly rephrase the same prohibited content. Stop automatic retries when a failure repeats or no meaningful correction remains, preserve the evidence and report what is needed.

Claims do not auto-expire: image calls can legitimately take several minutes. Use `heartbeat` if helpful for monitoring. Release a claim only after its own worker has stopped or no generation is in progress:

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" inspect --job explorer
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" release \
  --job explorer --worker worker-a --token TOKEN_FROM_CLAIM --reason 'Worker stopped before calling generator'
```

For an abandoned worker whose token was lost, stop/confirm termination of that specific worker and inspect any saved success first. Then `recover --job explorer --confirmed-stopped --reason '...'` can return its claim to ready. Do not reclaim based on elapsed time alone or race an in-flight generator. Wrong or obsolete tokens cannot commit another attempt.

## 6. Completion and handoff

```bash
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" status
python "$ART_SKILL/scripts/claim_next.py" --root "$ART_WORK" sync
python "$ART_SKILL/scripts/art_assets.py" verify art-manifest.json --complete
```

The final sync must occur **before** completion verification; syncing afterward clears the complete flag. Finish any requested gallery/engine/animation checks first. Verification fails if frozen targets are missing, sources/exports have changed, or any current canonical asset lacks accepted visual-review evidence. `generated`, an empty claim queue and a successful comparison-sheet render are not completion criteria.

Deliver relative exports, the full source-ID map, handoff instructions and references/credits. Include the queue's receipts/events and original/repaired master locations when another local AI needs to continue the process. The queue is a working artifact; do not expose unrelated local paths or account settings in a public delivery.
