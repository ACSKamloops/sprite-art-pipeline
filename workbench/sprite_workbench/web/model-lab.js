'use strict';

// Preparation and declared-result bookkeeping only. No executor/provider calls.
window.ModelLabUI = class {
  constructor(api) {
    this.api = api; this.catalog = null; this.pending = false; this.loading = null;
    this.tasks = []; this.packet = null; this.packetTask = null;
    this.$ = id => document.getElementById('models-' + id);
    const click = (id, operation) => this.$(id).addEventListener('click', () =>
      this.api.action(() => this.run(operation)));
    const submit = (id, operation) => this.$(id).addEventListener('submit', event => {
      event.preventDefault(); this.api.action(() => this.run(operation));
    });
    click('refresh', () => this.refresh());
    submit('prepare-form', () => this.prepare());
    click('inspect', () => this.inspectPacket());
    click('download', () => this.downloadPacket());
    click('export', () => this.exportPacket());
    click('results-refresh', () => this.loadResults());
    submit('ingest-form', () => this.ingest());
    submit('audit-form', () => this.audit());
    this.$('task').addEventListener('change', () => {
      this.packet = null; this.packetTask = null;
      this.$('packet').textContent = 'Inspect this task to load its handoff packet.';
      this.sync();
    });
    for (const id of ['experiment', 'sequence', 'left', 'right'])
      this.$(id).addEventListener('input', () => this.sync());
    this.$('experiment').addEventListener('input', () => {
      if (this.$('experiment').value.trim() !== this.preparedExperiment) {
        this.tasks = []; this.packet = null; this.packetTask = null; this.$('task').replaceChildren();
        this.$('packet').textContent = 'Prepared task selection cleared after the experiment ID changed.';
        this.$('state').textContent = 'Result lookup'; this.sync();
      }
    });
    this.$('size-requested').addEventListener('change', () => {
      for (const id of ['width', 'height']) this.$(id).disabled = !this.$('size-requested').checked;
    });
    this.sync();
  }
  async enter() { if (!this.catalog) await this.refresh(); }
  async run(operation) {
    if (this.pending) return;
    this.pending = true; this.sync();
    try { return await operation(); }
    finally { this.pending = false; this.sync(); }
  }
  sync() {
    const blocked = this.pending;
    const available = this.catalog?.executors || [];
    const paired = ['codex.imagegen', 'hermes.image_generate'].every(id => available.some(e => e.id === id));
    const task = this.$('task').value;
    this.$('refresh').disabled = blocked;
    this.$('prepare').disabled = blocked || !paired;
    this.$('task').disabled = blocked || !this.tasks.length;
    this.$('inspect').disabled = blocked || !task;
    this.$('download').disabled = blocked || !task;
    this.$('export').disabled = blocked || !task;
    this.$('ingest').disabled = blocked || !task || !this.isID(this.$('sequence').value.trim());
    this.$('results-refresh').disabled = blocked || !this.isID(this.$('experiment').value.trim());
    this.$('audit').disabled = blocked || !this.isID(this.$('left').value.trim()) || !this.isID(this.$('right').value.trim());
  }
  isID(value) { return /^[0-9a-f]{64}$/.test(value); }
  artifact(value, label) {
    const id = value.trim(); if (!this.isID(id)) throw new Error(label + ' must be a 64-character SHA256.');
    return id;
  }
  jsonInput(id, label) {
    try { return JSON.parse(this.$(id).value); }
    catch { throw new Error(label + ' must be valid JSON.'); }
  }
  print(id, value) { this.$(id).textContent = JSON.stringify(value, null, 2); }
  async refresh() {
    if (this.loading) return this.loading;
    this.loading = (async () => {
      const catalog = await this.api.invoke('local.models.catalog', {});
      this.catalog = catalog; this.$('executors').replaceChildren();
      for (const executor of catalog.executors) {
        const card = document.createElement('div'); card.className = 'models-executor';
        const title = document.createElement('h3'); title.textContent = executor.label;
        const id = document.createElement('p'); id.className = 'small mono'; id.textContent = executor.id;
        const status = document.createElement('span'); status.className = 'tag'; status.textContent = executor.status;
        const boundary = document.createElement('p'); boundary.className = 'small'; boundary.textContent = executor.boundary;
        const details = document.createElement('details'), summary = document.createElement('summary'), capabilities = document.createElement('pre');
        summary.textContent = 'Recorded capabilities'; capabilities.textContent = JSON.stringify(executor.capabilities, null, 2);
        details.append(summary, capabilities); card.append(title, id, status, boundary, details); this.$('executors').append(card);
      }
      this.$('boundary').textContent = catalog.boundary;
      this.sync();
    })();
    try { await this.loading; } finally { this.loading = null; }
  }
  brief() {
    const prompt = this.$('prompt').value;
    if (!prompt.trim()) throw new Error('Enter a prompt before preparing tasks.');
    const task = this.$('task-kind').value, inputs = this.jsonInput('inputs', 'Supplied raster inputs');
    if (!Array.isArray(inputs)) throw new Error('Supplied raster inputs must be a JSON array.');
    for (const input of inputs) {
      if (!input || !['subject', 'style', 'edit_target'].includes(input.role) || typeof input.raster !== 'string' || !this.isID(input.raster))
        throw new Error('Each input needs a subject/style/edit_target role and existing raster SHA256.');
    }
    if (task === 'edit' && inputs.filter(input => input.role === 'edit_target').length !== 1)
      throw new Error('An edit brief requires exactly one edit_target raster.');
    let desired = null;
    if (this.$('size-requested').checked) {
      desired = ['width', 'height'].map(id => Number(this.$(id).value));
      if (desired.some(value => !Number.isSafeInteger(value) || value < 1)) throw new Error('Desired size must use positive whole pixels.');
    }
    return {version: 1, task, prompt, inputs,
      requirements: {transparent_background: this.$('transparent').checked, desired_size: desired}, hard_controls: {}};
  }
  async prepare() {
    const brief = this.brief();
    const output = await this.api.invoke('local.models.prepare', {brief, executors: ['codex.imagegen', 'hermes.image_generate']});
    this.$('experiment').value = output.experiment; this.preparedExperiment = output.experiment; this.tasks = output.tasks;
    this.$('task').replaceChildren(); this.packet = null; this.packetTask = null;
    for (const task of output.tasks) {
      const option = document.createElement('option'); option.value = task.task;
      option.textContent = task.executor + ' · ' + task.status + ' · ' + task.task.slice(0, 12);
      this.$('task').append(option);
    }
    this.print('prepared', output); this.$('packet').textContent = 'Choose a task and inspect its handoff packet.';
    this.$('state').textContent = output.execution_status;
    this.$('status').textContent = `${output.tasks.length} tasks prepared. Execution is held; no model calls were made.`;
    this.$('results').textContent = 'Load results for this experiment after attaching existing sequences.';
    this.$('left').value = ''; this.$('right').value = '';
  }
  async inspectPacket() {
    const task = this.artifact(this.$('task').value, 'Prepared task');
    const packet = await this.api.invoke('local.models.packet', {task});
    if (this.$('task').value !== task) return null;
    this.packet = packet; this.packetTask = task; this.print('packet', packet); this.$('packet-details').open = true;
    this.$('status').textContent = 'Handoff packet loaded. Execution remains held.';
    return packet;
  }
  async downloadPacket() {
    const task = this.artifact(this.$('task').value, 'Prepared task');
    const packet = this.packetTask === task ? this.packet : await this.inspectPacket();
    if (!packet) return;
    const blob = new Blob([JSON.stringify(packet, null, 2) + '\n'], {type: 'application/json'});
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = `model-task-${task.slice(0, 12)}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    this.$('status').textContent = 'Task manifest downloaded. Reference PNGs remain in the Store; use export_packet for a complete folder. Execution is held.';
  }
  async loadResults() {
    const experiment = this.artifact(this.$('experiment').value, 'Experiment');
    const output = await this.api.invoke('local.models.results', {experiment});
    this.print('results', output);
    this.$('status').textContent = `${output.results.length} declared results loaded. Their execution identities are supplied evidence.`;
    return output;
  }
  async exportPacket() {
    const task = this.artifact(this.$('task').value, 'Prepared task');
    const directory = this.$('export-directory').value.trim();
    if (!directory) throw new Error('Choose an absent or empty handoff folder inside the workspace.');
    const output = await this.api.invoke('local.models.export_packet', {task, directory});
    this.print('packet', output); this.$('packet-details').open = true;
    this.$('status').textContent = `Complete handoff folder exported to ${output.directory}. Execution is held.`;
  }
  async ingest() {
    const task = this.artifact(this.$('task').value, 'Prepared task');
    const sequence = this.artifact(this.$('sequence').value, 'Existing sequence');
    const execution = this.jsonInput('execution', 'Actual execution identity');
    if (!execution || Array.isArray(execution) || typeof execution !== 'object') throw new Error('Actual execution identity must be a JSON object.');
    if (!['supplied-diagnostic', 'external-generation'].includes(execution.kind)) throw new Error('Choose supplied-diagnostic or external-generation as execution.kind.');
    const output = await this.api.invoke('local.models.ingest', {task, sequence, execution});
    this.print('ingested', output);
    if (output.result) {
      const target = !this.$('left').value ? 'left' : !this.$('right').value ? 'right' : null;
      if (target) this.$(target).value = output.result;
    }
    this.$('status').textContent = 'Existing result attached with declared execution metadata. No generation was requested.';
  }
  async audit() {
    const left = this.artifact(this.$('left').value, 'Left result'), right = this.artifact(this.$('right').value, 'Right result');
    if (left === right) throw new Error('Choose two distinct result artifacts.');
    const scope = this.$('audit-scope').value;
    const output = await this.api.invoke('local.models.audit_pair', {left, right, scope});
    this.print('audit-output', output);
    this.$('status').textContent = 'Technical pair audit returned. It is not an artwork score or model-quality approval.';
  }
};
