'use strict';

// A control surface for registered services. Explicit enabled Motion operations
// can call a provider; readiness remains server-owned, with no silent fallback.
const $ = id => document.getElementById(id);
const state = {token: null, bootstrap: null, catalog: {}, catalogTab: 'flows',
  capabilities: [], method: null, allMethods: false, response: null, jobs: [],
  selectedJob: null, project: null, projectId: null, projectHash: null,
  history: null, historyJournal: null, sequence: null, frame: 0, palette: 1, tool: 'pencil',
  busy: false, loading: false, stroke: null, playing: false, playEpoch: 0, playHandle: null,
  sequencePreview: null, previewEpoch: 0, view: 'readiness', loadEpoch: 0, lastUpload: null,
  verificationJob: null, verificationTimer: null, verificationStarted: 0, verificationSubmitting: false};
const TITLES = {motion: 'MOTION LAB', parity: 'PARITY LAB', studio: 'STUDIO', readiness: 'READINESS', flows: 'FLOWS & GRAMMAR', source: 'PIXELLAB SOURCE', models: 'MODEL LAB', workspace: 'WORKSPACE', jobs: 'JOBS', methods: 'METHODS'};
let sourceUI = null;
let modelLabUI = null;
let studioUI = null;
let motionUI = null;
let parityUI = null;
const MAX_CANVAS_PIXELS = 1048576;
const TERMINAL_JOBS = new Set(['completed', 'stale', 'cancelled', 'interrupted', 'validation_error', 'unsupported', 'technical_failure']);

function node(tag, text, className) {
  const n = document.createElement(tag);
  if (text !== undefined && text !== null) n.textContent = String(text);
  if (className) n.className = className;
  return n;
}
function json(value) { return JSON.stringify(value, null, 2); }
function boundedJSON(value) {
  const text = json(value);
  return text.length > 250000 ? text.slice(0, 250000) + '\n… Display limited to 250,000 characters. Copy JSON retains the complete response.' : text;
}
function text(value, fallback = '—') {
  if (value === null || value === undefined || value === '') return fallback;
  return typeof value === 'object' ? json(value) : String(value);
}
function array(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') return Object.entries(value).map(([id, row]) => typeof row === 'object' ? {id, ...row} : {id, detail: row});
  return [];
}
function statusTag(status) {
  const value = text(status, 'unrecorded');
  return node('span', value.replaceAll('_', ' '), 'tag ' + value.replace(/[^a-zA-Z0-9_-]/g, ''));
}
function showError(error) {
  $('global-error').textContent = error instanceof Error ? error.message : text(error);
  $('global-error').hidden = false;
  $('footer-status').textContent = 'Action failed. See the message above.';
}
function clearError() { $('global-error').hidden = true; }
function describeError(payload) {
  const err = payload?.error ?? payload;
  if (typeof err === 'string') return err;
  return text(err?.message ?? err?.detail ?? err?.reason ?? err, 'The local request failed.');
}
async function request(path, options = {}) {
  const headers = {...options.headers};
  if (options.method && options.method !== 'GET') {
    if (!state.token) throw new Error('The local session is not connected. Refresh this page.');
    headers['X-Workbench-Token'] = state.token;
  }
  const response = await fetch(path, {...options, headers, credentials: 'same-origin', cache: 'no-store'});
  let result;
  try { result = await response.json(); }
  catch { throw new Error(`The server returned a non-JSON response (${response.status}).`); }
  if (!response.ok || result?.status === 'error' || result?.error) throw new Error(describeError(result));
  return result;
}
async function post(path, payload) {
  return request(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
}
async function invoke(method, params) {
  const reply = await post('/api/invoke', {method, params});
  if (reply.status && reply.status !== 'completed') throw new Error(describeError(reply));
  return reply.result ?? reply;
}
async function action(fn, button) {
  clearError();
  const wasDisabled = button?.disabled;
  if (button) button.disabled = true;
  try { return await fn(); }
  catch (err) { showError(err); return undefined; }
  finally {
    if (button) button.disabled = wasDisabled;
    // A refresh inside the action may have changed these controls' real state.
    if (state.selectedJob) {
      const current = state.jobs.find(job => (job.id ?? job.job_id) === state.selectedJob);
      if (current) {
        $('cancel-job').disabled = TERMINAL_JOBS.has(current.status);
        $('retry-job').disabled = !TERMINAL_JOBS.has(current.status);
      }
    }
    if (state.method) $('invoke-method').disabled = !(state.method.domain === 'local' && state.method.handler_implemented);
    syncHistoryControls();
    syncVerificationButton();
  }
}
function route() {
  const view = location.hash.slice(1);
  state.view = Object.hasOwn(TITLES, view) ? view : 'readiness';
  Object.keys(TITLES).forEach(id => {
    $('view-' + id).hidden = id !== state.view;
    const link = document.querySelector(`[data-view="${id}"]`);
    link.classList.toggle('active', id === state.view);
    if (id === state.view) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
  });
  $('breadcrumb-current').textContent = TITLES[state.view];
  document.title = TITLES[state.view].toLowerCase().replaceAll(/\b\w/g, ch => ch.toUpperCase()) + ' · Sprite workbench';
  if (state.view !== 'workspace') stopPlayback();
  if (state.view !== 'motion') motionUI?.pause();
  if (state.view === 'motion' && state.token) action(() => motionUI.enter());
  if (state.view === 'parity' && state.token) action(() => parityUI.enter());
  if (state.view !== 'studio') studioUI?.pause();
  if (state.view === 'studio' && state.token) action(() => studioUI.enter());
  if (state.view === 'jobs' && state.token) action(refreshJobs);
  if (state.view !== 'source') sourceUI?.pause();
  if (state.view === 'source' && state.token) action(() => sourceUI.enter());
  if (state.view === 'models' && state.token) action(() => modelLabUI.enter());
}

function renderReadiness(data) {
  state.bootstrap.readiness = data;
  const ready = data.comparison_ready === true;
  const setupReady = data.setup_ready === true;
  const checks = array(data.checks), blockers = array(data.blockers);
  $('nav-gate').textContent = ready ? 'READY' : 'HELD';
  const summary = $('gate-summary'); summary.classList.toggle('blocked', !ready); summary.replaceChildren();
  summary.append(node('span', ready ? '✓' : '◷', 'gate-symbol'));
  const copy = node('div'); copy.append(node('h2', ready ? 'Prerequisites verified' : setupReady ? 'Local setup ready. Analysis gate remains held.' : 'Prerequisites remain open'));
  copy.append(node('p', ready ? 'Only the explicitly verified workflows are available for comparisons.' : `${blockers.length} recorded blocker${blockers.length === 1 ? '' : 's'} · ${setupReady ? 'Setup verification passed' : 'Local setup requires verification'}. Supplied-art editing is available separately.`)); summary.append(copy);
  $('check-count').textContent = `${checks.length} recorded checks`;
  const list = $('checks-list'); list.replaceChildren();
  checks.forEach(check => {
    const row = node('div', null, 'check-row');
    const passed = ['ready', 'passed', 'verified', 'complete', 'completed'].includes(check.status);
    row.append(node('span', passed ? '✓' : '○', 'row-symbol'));
    const content = node('div'); content.append(node('h3', check.label ?? check.title ?? check.id));
    if (check.detail ?? check.reason) content.append(node('p', text(check.detail ?? check.reason)));
    row.append(content, statusTag(check.status)); list.append(row);
  });
  if (!checks.length) list.append(node('p', 'No readiness checks were supplied by the server.', 'small space-top'));
  const remaining = $('blockers-list'); remaining.replaceChildren();
  blockers.forEach((blocker, index) => {
    const row = node('div', null, 'blocker'); row.append(node('span', String(index + 1).padStart(2, '0'), 'blocker-index'));
    const content = node('div'); content.append(node('h3', blocker.title ?? blocker.label ?? blocker.id ?? 'Unresolved prerequisite'));
    content.append(node('p', text(blocker.reason ?? blocker.detail ?? blocker.description, 'No additional detail recorded.')));
    row.append(content); remaining.append(row);
  });
  if (!blockers.length) remaining.append(node('p', ready ? 'No blockers in this record.' : 'The server has not supplied blocker details. This does not close the gate.', 'small'));
  $('comparison-status').textContent = ready ? 'Verified prerequisites met' : 'Held — unresolved prerequisites';
  // There is no implemented original-art comparison action behind this control.
  $('start-comparison').disabled = true;
  $('start-comparison').textContent = ready ? 'No comparison method configured' : 'Comparisons held by readiness gate';
  if (data.verification) $('verification-output').textContent = boundedJSON(data.verification);
  if (data.verification?.job_id && ['queued', 'running'].includes(data.verification.status)) watchVerification(data.verification.job_id);
  else if (state.verificationJob && !state.verificationSubmitting) stopVerificationWatch();
  syncVerificationButton();
}
async function refreshReadiness() { renderReadiness(await request('/api/readiness')); }
function syncVerificationButton() {
  $('verify-setup').disabled = state.verificationSubmitting || Boolean(state.verificationJob);
}
function stopVerificationWatch() {
  if (state.verificationTimer) clearTimeout(state.verificationTimer);
  state.verificationTimer = null; state.verificationJob = null; syncVerificationButton();
}
function watchVerification(jobId) {
  if (state.verificationJob === jobId) return;
  stopVerificationWatch(); state.verificationJob = jobId; state.verificationStarted = Date.now(); syncVerificationButton();
  const poll = async () => {
    if (state.verificationJob !== jobId) return;
    if (Date.now() - state.verificationStarted > 600000) {
      stopVerificationWatch(); $('footer-status').textContent = 'Automatic setup refresh paused after 10 minutes. Refresh Readiness or inspect Jobs.'; return;
    }
    if (document.hidden) { state.verificationTimer = setTimeout(poll, 2000); return; }
    try {
      const job = await invoke('local.jobs.get', {job_id: jobId});
      if (state.verificationJob !== jobId) return;
      $('verification-output').textContent = boundedJSON({job_id: jobId, status: job.status, progress: job.progress, error: job.error, outputs: job.outputs});
      if (TERMINAL_JOBS.has(job.status)) {
        stopVerificationWatch(); await refreshReadiness();
        $('footer-status').textContent = `Setup verification ${job.status}. Comparison prerequisites remain a separate gate.`;
        return;
      }
      state.verificationTimer = setTimeout(poll, 2000);
    } catch (err) {
      stopVerificationWatch(); $('verification-output').textContent = 'Automatic refresh stopped: ' + err.message;
      $('footer-status').textContent = 'Setup status refresh stopped. Refresh Readiness or inspect Jobs.';
    }
  };
  state.verificationTimer = setTimeout(poll, 2000);
}
async function verifySetup() {
  if (state.verificationSubmitting || state.verificationJob) return;
  state.verificationSubmitting = true; syncVerificationButton();
  $('verification-output').textContent = 'Submitting setup verification…';
  try {
    const reply = await post('/api/verify', {});
    const result = reply.result ?? reply;
    $('verification-output').textContent = boundedJSON(result);
    if (result.job_id) watchVerification(result.job_id);
    $('footer-status').textContent = result.job_id ? `Setup verification queued: ${result.job_id}. Status will refresh automatically.` : 'Setup verification response received.';
    await refreshReadiness();
  } finally { state.verificationSubmitting = false; syncVerificationButton(); }
}
async function refreshCatalog() {
  state.catalog = await request('/api/catalog'); renderCatalog();
}
function catalogRows() {
  const c = state.catalog;
  if (state.catalogTab === 'commands') return array(c.commands ?? c.grammar?.commands ?? c.command_records);
  if (state.catalogTab === 'grammar') {
    const g = c.grammar ?? {};
    return [
      {id: 'grammar-boundary', title: 'Grammar overview and unresolved syntax', status: g.status ?? 'unrecorded',
        summary: g.complete === true ? 'See the exact recorded scope of completeness.' : 'The complete hosted grammar is unavailable. Inventory closure does not close missing syntax.', ...g},
      ...array(g.documented_primitives).map(row => ({id: 'primitive:' + row.name, title: 'Primitive · ' + row.name, ...row})),
      ...array(g.retained_grammar_claims).map(row => ({status: 'retained_claim', ...row})),
      ...array(g.declared_conditionals).map(row => ({title: row.scope ?? row.id, status: 'declared_conditional', summary: row.condition, ...row}))
    ];
  }
  if (state.catalogTab === 'transport') return array(c.transport_flows);
  if (state.catalogTab === 'comparisons') return array(c.comparisons);
  if (state.catalogTab === 'interfaces') return array(c.interfaces);
  if (state.catalogTab === 'requirements') return array(c.requirements ?? c.obligations);
  return array(c.flows ?? c.workflows);
}
function rowTitle(row) { return text(row.title ?? row.label ?? row.name ?? row.command ?? row.id ?? row.flow_id, 'Untitled record'); }
function rowDetail(row) { return text(row.summary ?? row.detail ?? row.finding ?? row.reason ?? row.statement ?? row.behavior_verbatim ?? row.broad_gap ?? row.gap ?? row.state_semantics ?? row.scope ?? row.description, 'Select this record for its retained fields.'); }
function renderCatalog() {
  const q = $('catalog-search').value.toLowerCase();
  const all = catalogRows(), rows = all.filter(row => json(row).toLowerCase().includes(q));
  document.querySelectorAll('[data-catalog]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.catalog === state.catalogTab)));
  const grammar = state.catalog.grammar;
  $('catalog-summary').textContent = `${rows.length} of ${all.length} ${state.catalogTab} shown. ` + (state.catalogTab === 'commands' ? text(grammar?.summary ?? grammar?.boundary, 'A command inventory does not establish complete nested grammar or runtime behaviour.') : 'Status describes the recorded scope; inspect evidence and unresolved branches individually.');
  const drift = state.catalog.current_public_drift;
  $('catalog-drift').hidden = !drift;
  if (drift) {
    $('catalog-drift').replaceChildren(node('span', `Current public snapshot: ${text(drift.current_operations)} operations; frozen snapshot: ${text(drift.previous_operations)}. Added: ${array(drift.added).map(v => typeof v === 'string' ? v : text(v.id)).join(', ') || 'none'}. ${array(drift.changed).length} changed definitions. `));
    const inspect = node('button', 'Inspect snapshot changes', 'record-button'); inspect.type = 'button';
    inspect.addEventListener('click', () => { $('record-title').textContent = 'Current public schema drift'; $('record-detail').textContent = boundedJSON(drift); }); $('catalog-drift').append(inspect);
  }
  const body = $('catalog-rows'); body.replaceChildren();
  rows.forEach(row => {
    const tr = node('tr'), title = node('td'), button = node('button', null, 'record-button');
    button.append(node('strong', rowTitle(row)));
    if (row.id ?? row.flow_id) button.append(node('span', row.id ?? row.flow_id));
    button.type = 'button'; button.addEventListener('click', () => {
      body.querySelectorAll('tr').forEach(r => r.classList.remove('selected-row')); tr.classList.add('selected-row');
      $('record-title').textContent = rowTitle(row); $('record-detail').textContent = boundedJSON(row);
    });
    title.append(button); const status = node('td'); status.append(statusTag(row.status ?? row.disposition ?? row.coverage));
    tr.append(title, status, node('td', rowDetail(row))); body.append(tr);
  });
  if (!rows.length) { const tr = node('tr'), td = node('td', 'No matching records.'); td.colSpan = 3; tr.append(td); body.append(tr); }
}

function renderMethods() {
  const q = $('method-search').value.toLowerCase(), list = $('method-list'); list.replaceChildren();
  $('methods-local').setAttribute('aria-pressed', String(!state.allMethods));
  $('methods-all').setAttribute('aria-pressed', String(state.allMethods));
  state.capabilities.filter(cap => (state.allMethods || cap.domain === 'local') && text(cap.id).toLowerCase().includes(q)).forEach(cap => {
    const button = node('button', cap.id); button.type = 'button';
    if (cap.id === state.method?.id) button.classList.add('selected');
    button.append(node('small', cap.domain === 'local' && cap.handler_implemented ? text(cap.local_classification).replaceAll('-', ' ') : `${text(cap.domain)} · captured contract · unavailable`));
    button.addEventListener('click', () => selectMethod(cap)); list.append(button);
  });
  if (!list.children.length) list.append(node('p', 'No matching methods.', 'small'));
}
function schemaExample(schema, depth = 0) {
  if (!schema || depth > 8) return {};
  if (schema.default !== undefined) return schema.default;
  if (schema.example !== undefined) return schema.example;
  if (schema.const !== undefined) return schema.const;
  if (schema.enum?.length) return schema.enum[0];
  if (schema.type === 'object' || schema.properties) return Object.fromEntries((schema.required ?? []).map(key => [key, schemaExample(schema.properties?.[key], depth + 1)]));
  if (schema.type === 'array') return [];
  if (schema.type === 'integer' || schema.type === 'number') return schema.minimum ?? 0;
  if (schema.type === 'boolean') return false;
  return schema.pattern === '^[0-9a-f]{64}$' ? 'ARTIFACT_ID' : '';
}
function selectMethod(cap) {
  state.method = cap; renderMethods();
  $('method-domain').textContent = cap.domain === 'local' ? 'REGISTERED LOCAL METHOD' : 'CAPTURED VENDOR CONTRACT';
  $('method-name').textContent = cap.id;
  const schema = cap.request_schema ?? cap.exact_input_schema;
  $('method-schema').textContent = schema ? boundedJSON(schema) : 'No request schema recorded. Inspect the method policy before invoking.';
  $('method-request').value = json(schemaExample(schema));
  $('method-policy').textContent = text(cap.unsupported_reason ?? cap.evidence?.policy, 'An explicit registered local service. It does not forward to a vendor.');
  $('invoke-method').disabled = !(cap.domain === 'local' && cap.handler_implemented);
}
async function invokeSelected() {
  if (!state.method || state.method.domain !== 'local' || !state.method.handler_implemented) throw new Error('Only registered local methods can be invoked.');
  let params; try { params = JSON.parse($('method-request').value); } catch { throw new Error('Request JSON is invalid. Correct it before invoking.'); }
  if (!params || Array.isArray(params) || typeof params !== 'object') throw new Error('Method parameters must be a JSON object.');
  $('method-response').textContent = 'Invoking local method…';
  try {
    const result = await invoke(state.method.id, params);
    state.response = result; $('method-response').textContent = boundedJSON(result); $('copy-response').disabled = false;
    $('footer-status').textContent = `${state.method.id} completed.`;
  } catch (err) {
    state.response = {error: err.message}; $('method-response').textContent = json(state.response); $('copy-response').disabled = false; throw err;
  }
}

async function refreshJobs() {
  const result = await request('/api/jobs'); state.jobs = array(result.jobs ?? result);
  const list = $('jobs-list'); list.replaceChildren();
  state.jobs.forEach(job => {
    const row = node('div', null, 'job-row'), details = node('div'), button = node('button', text(job.id ?? job.job_id), 'record-button');
    button.type = 'button'; button.addEventListener('click', () => selectJob(job));
    details.append(button, node('p', text(job.handler ?? job.name ?? job.created_at, 'Local job')));
    row.append(details, statusTag(job.status)); list.append(row);
  });
  if (!state.jobs.length) list.append(node('p', 'No jobs in this workspace.', 'small space-top'));
  if (state.selectedJob) {
    const current = state.jobs.find(job => (job.id ?? job.job_id) === state.selectedJob);
    if (current) selectJob(current);
  }
}
function selectJob(job) {
  state.selectedJob = job.id ?? job.job_id;
  $('job-title').textContent = state.selectedJob; $('job-detail').textContent = boundedJSON(job);
  $('cancel-job').disabled = TERMINAL_JOBS.has(job.status);
  $('retry-job').disabled = !TERMINAL_JOBS.has(job.status);
}
async function submitJob() {
  const id = $('job-plan').value.trim(); if (!/^[0-9a-f]{64}$/.test(id)) throw new Error('Enter a valid plan artifact ID.');
  const artifact = await request('/api/artifact/' + id);
  if (artifact.kind !== 'pipeline-plan' || !artifact.plan || typeof artifact.plan !== 'object') throw new Error('This artifact is not a stored pipeline-plan declaration.');
  const job = await invoke('local.jobs.submit', {handler: 'local.pipeline', request: {plan: artifact.plan}});
  state.selectedJob = typeof job === 'string' ? job : job.id ?? job.job_id;
  $('footer-status').textContent = `Plan job submitted: ${text(state.selectedJob)}.`; await refreshJobs();
}
function suppliedImagePlan(path = 'uploads/REPLACE_WITH_UPLOADED_FILE_SHA256.png') {
  return {version: 1, name: 'Supplied image import, editable construction and render', steps: [
    {id: 'source', action: 'import', path},
    {id: 'editable', action: 'construction', method: 'from_sequence', request: {sequence: {ref: 'source.sequence'}, animation_id: 'supplied'}},
    {id: 'rendered', action: 'construction', method: 'render', request: {project: {ref: 'editable.project'}, animation_id: 'supplied'}}
  ]};
}
async function savePlan() {
  let plan; try { plan = JSON.parse($('plan-json').value); } catch { throw new Error('Plan JSON is invalid. Correct it before saving.'); }
  if (!plan || Array.isArray(plan) || typeof plan !== 'object') throw new Error('A declared plan must be a JSON object.');
  const reply = await post('/api/plan', {plan}), result = reply.result ?? reply;
  if (!/^[0-9a-f]{64}$/.test(result.plan)) throw new Error('The server did not return a stored plan identity.');
  $('job-plan').value = result.plan; $('footer-status').textContent = 'Plan saved without execution. Review it, then submit when ready.';
}

async function openArtifact(id, suppliedHistory = null) {
  if (!/^[0-9a-f]{64}$/.test(id)) throw new Error('Enter a 64-character lowercase artifact ID.');
  if (state.busy || state.stroke) throw new Error('Finish the current pixel edit before opening another project.');
  const epoch = ++state.loadEpoch; state.loading = true; stopPlayback(); $('edit-status').textContent = 'Loading…';
  try {
    const artifact = await request('/api/artifact/' + id);
    let projectId = id, history = suppliedHistory, project;
    if (artifact.kind === 'construction-history') {
      history = id; projectId = artifact.project;
    } else if (artifact.kind !== 'construction-project') {
      const made = await invoke('local.construction.from_sequence', {sequence: id}); projectId = made.project;
    }
    project = await request('/api/project/' + projectId);
    if (!history) history = (await invoke('local.construction.history', {project: projectId})).history;
    const historyDocument = artifact.kind === 'construction-history' && history === id ? artifact : await request('/api/artifact/' + history);
    if (epoch !== state.loadEpoch) return;
    state.project = project.document; state.projectId = projectId; state.projectHash = project.project_hash;
    state.history = history; state.historyJournal = historyDocument.journal; state.sequence = null; state.frame = 0;
    state.palette = state.project.palette.length > 1 ? 1 : 0;
    $('artifact-id').value = projectId; $('current-sequence').textContent = '—'; $('server-preview-wrap').hidden = true;
    populateProject(); $('footer-status').textContent = 'Project loaded. Edits will create new immutable revisions.';
  } finally { if (epoch === state.loadEpoch) { state.loading = false; updateFrame(); } }
}
async function applyRevision(result) {
  const previousHistory = state.history;
  const [project, history] = await Promise.all([request('/api/project/' + result.project), request('/api/artifact/' + result.history)]);
  state.project = project.document; state.projectId = result.project; state.projectHash = project.project_hash;
  state.history = result.history; state.historyJournal = history.journal; state.sequence = null;
  $('artifact-id').value = result.project; $('current-sequence').textContent = '—'; $('server-preview-wrap').hidden = true;
  populateProject(true);
  studioUI?.workspaceRevision({project: state.projectId, project_hash: state.projectHash, history: state.history,
    animation_id: currentAnimation()?.id, frame_id: currentFrame()?.id, layer_id: $('layer-select').value}, previousHistory);
}
function syncHistoryControls() {
  const journal = state.historyJournal;
  $('undo-edit').disabled = !journal || journal.cursor <= 0 || state.busy || state.loading;
  $('redo-edit').disabled = !journal || journal.cursor >= journal.receipts.length || state.busy || state.loading;
}
function populateProject(keepSelection = false) {
  const p = state.project;
  const previousLayer = $('layer-select').value, previousAnimation = $('animation-select').value;
  state.frame = Math.min(state.frame, p.frames.length - 1);
  $('canvas-empty').hidden = true; $('sprite-canvas').hidden = false;
  $('project-name').textContent = `${p.canvas.width} × ${p.canvas.height} project`;
  $('project-hash').textContent = 'Guard · ' + state.projectHash.slice(0, 16) + '…';
  $('current-project').textContent = state.projectId; $('current-history').textContent = state.history;
  $('canvas-dimensions').textContent = `${p.canvas.width} × ${p.canvas.height} px`;
  const layers = $('layer-select'); layers.replaceChildren(); p.layers.forEach(layer => {
    const option = node('option', layer.name + (layer.locked ? ' · locked' : '')); option.value = layer.id; layers.append(option);
  });
  layers.disabled = false;
  if (keepSelection && p.layers.some(layer => layer.id === previousLayer)) layers.value = previousLayer;
  else layers.value = [...p.layers].reverse().find(layer => !layer.locked)?.id ?? p.layers[0]?.id ?? '';
  const anims = $('animation-select'); anims.replaceChildren(); p.animations.forEach(anim => {
    const option = node('option', anim.id); option.value = anim.id; anims.append(option);
  });
  if (keepSelection && p.animations.some(anim => anim.id === previousAnimation)) anims.value = previousAnimation;
  anims.disabled = !p.animations.length;
  for (const id of ['undo-edit', 'redo-edit', 'add-color', 'save-timing', 'frame-ticks']) $(id).disabled = false;
  const canvasAllowed = p.canvas.width * p.canvas.height <= MAX_CANVAS_PIXELS;
  $('play-animation').disabled = !p.animations.length || !canvasAllowed;
  $('render-animation').disabled = !p.animations.length;
  renderPalette(); renderFrames(); updateFrame();
  syncHistoryControls();
  if (!canvasAllowed) {
    $('sprite-canvas').hidden = true; $('canvas-empty').hidden = false;
    $('canvas-empty').replaceChildren(node('h3', 'Project exceeds interactive canvas limit'), node('p', 'This browser editor supports up to 1,048,576 canvas pixels. Use Methods or external editor exchange for this project.'));
  }
}
function currentFrame() { return state.project?.frames[state.frame]; }
function currentAnimation() { return state.project?.animations.find(a => a.id === $('animation-select').value); }
function currentCelId() { return currentFrame()?.cels[$('layer-select').value]; }
function renderFrames() {
  const strip = $('frame-strip'); strip.replaceChildren();
  state.project.frames.forEach((frame, index) => {
    const button = node('button', String(index + 1).padStart(2, '0'), 'frame-button'); button.type = 'button';
    button.setAttribute('aria-label', `Frame ${index + 1}, ${frame.duration_ticks} ticks`);
    button.setAttribute('aria-pressed', String(index === state.frame)); button.append(node('small', `${frame.duration_ticks} ticks`));
    button.addEventListener('click', () => { stopPlayback(); state.frame = index; updateFrame(); }); strip.append(button);
  });
}
function updateFrame() {
  if (!state.project) return;
  const frame = currentFrame(), layer = state.project.layers.find(l => l.id === $('layer-select').value), cel = currentCelId();
  $('frame-ticks').value = frame.duration_ticks;
  const anim = currentAnimation(); $('frame-time').textContent = anim ? `${frame.duration_ticks} / ${anim.fps} seconds · ${anim.loop ? 'loop' : 'play once'}` : 'No animation selected.';
  $('cel-info').textContent = layer?.locked ? 'This layer is locked.' : cel ? `Cel ${cel} · ${state.project.frames.filter(f => f.cels[layer.id] === cel).length} frame reference(s)` : 'No cel on this layer in this frame. Use an existing cel or edit the project structure externally.';
  $('frame-strip').querySelectorAll('button').forEach((button, index) => button.setAttribute('aria-pressed', String(index === state.frame)));
  $('edit-status').textContent = state.busy ? 'Committing…' : `Frame ${state.frame + 1} / ${state.project.frames.length}`;
  syncHistoryControls();
  drawCanvas();
}
function renderPalette() {
  const palette = $('palette'); palette.replaceChildren(); const colors = state.project.palette;
  state.palette = Math.min(state.palette, colors.length - 1); $('palette-count').textContent = `${colors.length} entries`;
  colors.slice(0, 256).forEach((rgba, index) => {
    const button = node('button'); button.type = 'button'; button.title = `Index ${index}: ${rgba.join(', ')}`;
    button.setAttribute('aria-label', button.title); button.setAttribute('aria-pressed', String(index === state.palette));
    button.dataset.transparent = String(rgba[3] === 0); button.style.backgroundColor = `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${rgba[3] / 255})`;
    button.addEventListener('click', () => selectPalette(index)); palette.append(button);
  });
  let input = $('palette-index');
  if (!input) {
    const label = node('label', 'Palette index ', 'inline-label space-top'); input = node('input'); input.id = 'palette-index'; input.type = 'number'; input.min = '0'; input.step = '1'; input.style.width = '90px';
    input.addEventListener('change', () => { const index = Number(input.value); if (Number.isInteger(index) && index >= 0 && index < state.project.palette.length) selectPalette(index); else { input.value = state.palette; showError(new Error('Palette index is outside this project.')); } }); label.append(input); palette.after(label);
  }
  input.max = String(colors.length - 1); selectPalette(state.palette);
  if (colors.length > 256) $('palette-count').textContent += ' · first 256 shown';
}
function selectPalette(index) {
  state.palette = index; $('palette-value').textContent = `#${index} · RGBA ${state.project.palette[index].join(', ')}`;
  $('palette').querySelectorAll('button').forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
  $('palette-index').value = index;
}
function drawCanvas() {
  const p = state.project; if (!p || p.canvas.width * p.canvas.height > MAX_CANVAS_PIXELS) return;
  const {width: w, height: h} = p.canvas, canvas = $('sprite-canvas');
  if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  const zoom = Number($('canvas-zoom').value); canvas.style.width = `${w * zoom}px`; canvas.style.height = `${h * zoom}px`;
  const ctx = canvas.getContext('2d'), image = ctx.createImageData(w, h), out = image.data, frame = currentFrame();
  for (const layer of p.layers) {
    const celId = frame.cels[layer.id], cel = p.cels[celId]; if (!cel) continue;
    const pending = state.stroke?.celId === celId ? state.stroke.points : null;
    for (let i = 0; i < cel.pixels.length; i++) {
      const src = p.palette[pending?.get(i) ?? cel.pixels[i]], sa = src[3]; if (!sa) continue;
      const offset = i * 4; if (sa === 255) { out.set(src, offset); continue; }
      const da = out[offset + 3], n = sa * 255 + da * (255 - sa);
      for (let c = 0; c < 3; c++) out[offset + c] = Math.floor((src[c] * sa * 255 + out[offset + c] * da * (255 - sa) + Math.floor(n / 2)) / n);
      out[offset + 3] = Math.floor((n + 127) / 255);
    }
  }
  ctx.putImageData(image, 0, 0);
}
async function edit(operations, reason) {
  if (!state.project || state.busy || state.loading) throw new Error('Wait for the current project operation to finish.');
  stopPlayback(); state.busy = true; $('edit-status').textContent = 'Committing guarded edit…';
  try {
    const result = await invoke('local.construction.edit', {history: state.history, transaction: {schema: 'sprite-edit-transaction/v1', expected_project_sha256: state.projectHash, reason, operations}});
    await applyRevision(result); $('footer-status').textContent = 'Edit committed. Previous artifacts remain unchanged.';
  } finally { state.busy = false; updateFrame(); }
}
function canvasPoint(event) {
  const canvas = $('sprite-canvas'), rect = canvas.getBoundingClientRect();
  return [Math.floor((event.clientX - rect.left) * canvas.width / rect.width), Math.floor((event.clientY - rect.top) * canvas.height / rect.height)];
}
function strokeTo(point) {
  const stroke = state.stroke; if (!stroke) return;
  const [x1, y1] = point, [x0, y0] = stroke.last ?? point, steps = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
  for (let i = 0; i <= steps; i++) {
    const t = steps ? i / steps : 0, x = Math.round(x0 + (x1 - x0) * t), y = Math.round(y0 + (y1 - y0) * t);
    if (x >= 0 && x < state.project.canvas.width && y >= 0 && y < state.project.canvas.height) stroke.points.set(y * state.project.canvas.width + x, stroke.index);
  }
  stroke.last = point; drawCanvas();
}
function setTool(tool) {
  state.tool = tool; $('tool-pencil').setAttribute('aria-pressed', String(tool === 'pencil')); $('tool-erase').setAttribute('aria-pressed', String(tool === 'erase'));
}
function stopPlayback() {
  state.playing = false; state.playEpoch++; if (state.playHandle) cancelAnimationFrame(state.playHandle); state.playHandle = null;
  $('play-animation').textContent = '▶ Play';
}
function playAnimation() {
  if (state.playing) { stopPlayback(); return; }
  const animation = currentAnimation(); if (!animation?.frames.length) throw new Error('Select an animation with frames.');
  const frames = animation.frames.map(id => state.project.frames.findIndex(frame => frame.id === id));
  const durations = frames.map(index => state.project.frames[index].duration_ticks / animation.fps * 1000);
  const total = durations.reduce((a, b) => a + b, 0); if (!Number.isFinite(total) || total <= 0) throw new Error('Animation clock is not playable.');
  state.playing = true; const epoch = ++state.playEpoch, start = performance.now(); $('play-animation').textContent = 'Ⅱ Pause';
  const tick = now => {
    if (!state.playing || epoch !== state.playEpoch) return;
    const elapsed = now - start; let t = animation.loop ? elapsed % total : Math.min(elapsed, total - 0.00001), index = 0;
    while (index < durations.length - 1 && t >= durations[index]) { t -= durations[index]; index++; }
    if (state.frame !== frames[index]) { state.frame = frames[index]; updateFrame(); }
    if (!animation.loop && elapsed >= total) { stopPlayback(); return; }
    state.playHandle = requestAnimationFrame(tick);
  };
  state.playHandle = requestAnimationFrame(tick);
}
async function renderAnimation() {
  const animation = currentAnimation(); if (!animation) throw new Error('Select an animation.');
  const result = await invoke('local.construction.render', {project: state.projectId, history: state.history, animation_id: animation.id});
  state.sequence = result.sequence; $('current-sequence').textContent = result.sequence;
  const sequence = await request('/api/artifact/' + result.sequence);
  state.sequencePreview = sequence; $('server-preview-wrap').hidden = false; $('server-preview-wrap').open = true;
  $('server-preview-info').textContent = `${sequence.frames.length} rendered frames · ${result.sequence}`;
  const epoch = ++state.previewEpoch, start = performance.now();
  const durations = sequence.frames.map(frame => frame.duration[0] / frame.duration[1] * 1000), total = durations.reduce((a, b) => a + b, 0);
  let shown = -1;
  const tick = now => {
    if (epoch !== state.previewEpoch || state.sequence !== result.sequence || state.view !== 'workspace') return;
    const elapsed = now - start, repeats = sequence.play_count === 0 || sequence.loop === true;
    let t = repeats ? elapsed % total : Math.min(elapsed, total - 0.00001), index = 0;
    while (index < durations.length - 1 && t >= durations[index]) { t -= durations[index]; index++; }
    if (shown !== index) { $('server-preview').src = `/api/raster/${sequence.frames[index].raster}.png`; shown = index; }
    if (repeats || elapsed < total) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick); $('footer-status').textContent = 'Authoritative animation rendered to immutable store.';
}
async function uploadFile(file) {
  if (!file) return;
  if (state.busy || state.stroke) throw new Error('Finish the current pixel edit before importing another project.');
  const jsonFile = file.name.toLowerCase().endsWith('.json'), limit = (jsonFile ? 16 : 32) * 1024 * 1024;
  if (file.size > limit) throw new Error(`File exceeds the ${jsonFile ? 16 : 32} MiB upload limit.`);
  $('footer-status').textContent = 'Importing local file…';
  const result = await request('/api/upload', {method: 'POST', headers: {'Content-Type': jsonFile ? 'application/json' : 'image/png', 'X-Workbench-Filename': encodeURIComponent(file.name)}, body: file});
  const data = result.result ?? result; const id = data.project ?? data.sequence;
  if (!id) throw new Error('Upload did not return a project or sequence artifact.');
  if (data.sequence && data.source_bytes) { state.lastUpload = data; $('plan-from-upload').disabled = false; }
  await openArtifact(id, data.history ?? null); location.hash = 'workspace';
}

function bindEvents() {
  window.addEventListener('hashchange', route);
  $('refresh-readiness').addEventListener('click', event => action(refreshReadiness, event.currentTarget));
  $('verify-setup').addEventListener('click', event => action(verifySetup, event.currentTarget));
  $('refresh-catalog').addEventListener('click', event => action(refreshCatalog, event.currentTarget));
  $('catalog-search').addEventListener('input', renderCatalog);
  document.querySelectorAll('[data-catalog]').forEach(button => button.addEventListener('click', () => { state.catalogTab = button.dataset.catalog; renderCatalog(); }));
  $('method-search').addEventListener('input', renderMethods);
  $('methods-local').addEventListener('click', () => { state.allMethods = false; renderMethods(); });
  $('methods-all').addEventListener('click', () => { state.allMethods = true; renderMethods(); });
  $('invoke-method').addEventListener('click', event => action(invokeSelected, event.currentTarget));
  $('copy-response').addEventListener('click', event => action(async () => { await navigator.clipboard.writeText(json(state.response)); $('footer-status').textContent = 'Response JSON copied.'; }, event.currentTarget));
  $('refresh-jobs').addEventListener('click', event => action(refreshJobs, event.currentTarget));
  $('submit-job-form').addEventListener('submit', event => { event.preventDefault(); action(submitJob, event.submitter); });
  $('save-plan-form').addEventListener('submit', event => { event.preventDefault(); action(savePlan, event.submitter); });
  $('plan-json').value = json(suppliedImagePlan());
  $('plan-from-upload').addEventListener('click', () => {
    if (!state.lastUpload?.source_bytes) return;
    $('plan-json').value = json(suppliedImagePlan(`uploads/${state.lastUpload.source_bytes}.png`));
    $('footer-status').textContent = 'Example plan now references the last image uploaded in this session. Save it before submitting.';
  });
  $('plan-file').addEventListener('change', event => {
    const file = event.target.files[0]; event.target.value = '';
    action(async () => {
      if (!file) return; if (file.size > 4 * 1024 * 1024) throw new Error('Plan JSON file exceeds 4 MiB.');
      const contents = await file.text(); let plan;
      try { plan = JSON.parse(contents); } catch { throw new Error('The selected plan file is not valid JSON.'); }
      if (plan?.kind === 'pipeline-plan') plan = plan.plan;
      $('plan-json').value = json(plan); $('footer-status').textContent = 'Plan file loaded for review. It has not been saved or executed.';
    });
  });
  $('cancel-job').addEventListener('click', event => action(async () => { await invoke('local.jobs.cancel', {job_id: state.selectedJob}); await refreshJobs(); }, event.currentTarget));
  $('retry-job').addEventListener('click', event => action(async () => { await invoke('local.jobs.retry', {job_id: state.selectedJob}); await refreshJobs(); }, event.currentTarget));
  $('load-project-form').addEventListener('submit', event => { event.preventDefault(); action(() => openArtifact($('artifact-id').value.trim()), event.submitter); });
  $('upload-file').addEventListener('change', event => { const file = event.target.files[0]; action(() => uploadFile(file)); event.target.value = ''; });
  $('layer-select').addEventListener('change', updateFrame);
  $('animation-select').addEventListener('change', () => { stopPlayback(); updateFrame(); });
  $('canvas-zoom').addEventListener('change', drawCanvas);
  $('tool-pencil').addEventListener('click', () => setTool('pencil'));
  $('tool-erase').addEventListener('click', () => setTool('erase'));
  for (const direction of ['undo', 'redo']) $(direction + '-edit').addEventListener('click', event => action(async () => {
    if (state.busy || state.loading || !state.history) return; stopPlayback(); state.busy = true;
    try { await applyRevision(await invoke('local.construction.' + direction, {history: state.history})); $('footer-status').textContent = `${direction === 'undo' ? 'Undo' : 'Redo'} restored an exact history state.`; }
    finally { state.busy = false; updateFrame(); }
  }, event.currentTarget));
  $('add-color-form').addEventListener('submit', event => {
    event.preventDefault(); const hex = $('new-color').value, alpha = Number($('new-alpha').value);
    if (!Number.isInteger(alpha) || alpha < 0 || alpha > 255) { showError(new Error('Alpha must be an integer from 0 to 255.')); return; }
    const rgba = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)); rgba.push(alpha);
    action(async () => { await edit([{op: 'palette_add', rgba}], 'Add explicitly selected palette RGBA color in local web editor'); selectPalette(state.project.palette.length - 1); }, event.submitter);
  });
  $('save-timing').addEventListener('click', event => action(async () => {
    const ticks = Number($('frame-ticks').value); if (!Number.isSafeInteger(ticks) || ticks < 1) throw new Error('Frame ticks must be a positive safe integer.');
    await edit([{op: 'frame_timing', frame_id: currentFrame().id, duration_ticks: ticks}], 'Set exact frame duration in local web editor');
  }, event.currentTarget));
  $('play-animation').addEventListener('click', () => action(playAnimation));
  $('render-animation').addEventListener('click', event => action(renderAnimation, event.currentTarget));
  const canvas = $('sprite-canvas');
  canvas.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !state.project || state.busy || state.loading || state.playing) return;
    const layer = state.project.layers.find(l => l.id === $('layer-select').value), celId = currentCelId();
    if (!celId || layer?.locked) { showError(new Error(layer?.locked ? 'The selected layer is locked.' : 'This frame has no cel on the selected layer.')); return; }
    clearError(); canvas.setPointerCapture(event.pointerId); state.stroke = {celId, tool: state.tool, index: state.tool === 'erase' ? 0 : state.palette, points: new Map(), last: null}; strokeTo(canvasPoint(event));
  });
  canvas.addEventListener('pointermove', event => {
    const point = canvasPoint(event); $('pixel-position').textContent = `x ${point[0]} · y ${point[1]}`; if (state.stroke) strokeTo(point);
  });
  canvas.addEventListener('pointerup', event => {
    const stroke = state.stroke; if (!stroke) return;
    strokeTo(canvasPoint(event)); state.stroke = null;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    const points = [...stroke.points].map(([i, index]) => stroke.tool === 'erase' ? [i % state.project.canvas.width, Math.floor(i / state.project.canvas.width)] : [i % state.project.canvas.width, Math.floor(i / state.project.canvas.width), index]);
    if (points.length) action(() => edit([{op: stroke.tool === 'erase' ? 'erase' : 'paint', cel_id: stroke.celId, points}], 'Explicit pixel stroke in local web editor')).then(drawCanvas);
    else drawCanvas();
  });
  canvas.addEventListener('pointercancel', () => { state.stroke = null; drawCanvas(); });
  window.addEventListener('keydown', event => {
    if (state.view !== 'workspace' || !state.project || ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName) || event.target.isContentEditable) return;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') { event.preventDefault(); $(event.shiftKey ? 'redo-edit' : 'undo-edit').click(); }
    else if (!event.ctrlKey && !event.metaKey && event.key.toLowerCase() === 'b') setTool('pencil');
    else if (!event.ctrlKey && !event.metaKey && event.key.toLowerCase() === 'e') setTool('erase');
    else if (event.code === 'Space') { event.preventDefault(); if (!$('play-animation').disabled) action(playAnimation); }
  });
  setInterval(() => { if (state.view === 'jobs' && state.token && !document.hidden) action(refreshJobs); }, 5000);
}
async function start() {
  studioUI = new window.SpriteStudioUI({request, invoke, action,
    workspaceContext: () => ({project: state.projectId, history: state.history, animation_id: currentAnimation()?.id,
      frame_id: currentFrame()?.id, layer_id: $('layer-select').value, source_sequence: state.project?.provenance?.workbench_source_sequence,
      last_upload: state.lastUpload?.sequence, busy: state.busy || state.loading}),
    openEditor: async ({project, history}) => { await openArtifact(history || project, history); location.hash = 'workspace'; }});
  motionUI = new window.MotionLabUI({request, invoke, action, openStudio: async result => {
    await studioUI.loadResult(result, 'Motion Lab candidate', 'Explicit local pose selection and rational holds; no inferred sprite FPS.'); location.hash = 'studio';
  }});
  parityUI = new window.ParityLabUI({request, invoke, action,
    workspaceContext: () => ({project: state.projectId, history: state.history,
      cel_id: currentFrame()?.cels?.[$('layer-select').value], palette_index: state.palette,
      busy: state.busy || state.loading}),
    openEditor: async ({project, history}) => { await openArtifact(history || project, history); location.hash = 'workspace'; }});
  modelLabUI = new window.ModelLabUI({request, invoke, action});
  sourceUI = new window.PixelLabSourceUI({request, invoke, action,
    openEditor: async sequence => { await openArtifact(sequence); location.hash = 'workspace'; }});
  bindEvents(); route();
  try {
    const bootstrap = await request('/api/bootstrap'); state.bootstrap = bootstrap; state.token = bootstrap.csrf_token;
    const capabilities = bootstrap.capabilities;
    state.capabilities = Array.isArray(capabilities) ? capabilities : array(
      capabilities && Object.hasOwn(capabilities, 'entries') ? capabilities.entries :
      capabilities && Object.hasOwn(capabilities, 'capabilities') ? capabilities.capabilities : capabilities);
    const workspace = bootstrap.workspace ?? {};
    $('store-path').textContent = text(workspace.store ?? workspace.store_path ?? workspace.path ?? (typeof workspace === 'string' ? workspace : null));
    $('analysis-path').textContent = text(workspace.analysis ?? workspace.analysis_path, 'See Flows & grammar for the retained catalog.');
    $('connection').replaceChildren(node('span', null, 'status-dot'), node('span', 'Local connection'));
    renderReadiness(bootstrap.readiness ?? {status: 'blocked', blockers: [{title: 'Readiness record unavailable', reason: 'The server supplied no readiness record.'}]});
    renderMethods(); await refreshCatalog();
    if (state.view === 'jobs') await refreshJobs();
    if (state.view === 'source') await sourceUI.enter();
    if (state.view === 'models') await modelLabUI.enter();
    if (state.view === 'studio') await studioUI.enter();
    if (state.view === 'motion') await motionUI.enter();
    if (state.view === 'parity') await parityUI.enter();
    $('footer-status').textContent = 'Connected to local workbench. Provider actions require explicit submission.';
  } catch (err) { $('connection').classList.add('failed'); $('connection').replaceChildren(node('span', null, 'status-dot'), node('span', 'Connection failed')); showError(err); }
}
start();
