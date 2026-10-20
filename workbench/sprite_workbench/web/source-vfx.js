'use strict';

// Host controls only. All recipe math, binding and effect pixels execute the
// unchanged source factories on the local backend.
window.PixelLabSourceUI = class {
  constructor(api) {
    this.api = api; this.catalog = null; this.values = {}; this.epoch = 0;
    this.pending = false; this.job = null; this.result = null; this.sequence = null;
    this.frames = []; this.frame = 0; this.playing = false; this.handle = null;
    this.loading = null; this.recent = [];
    this.$ = id => document.getElementById('source-' + id);
    const act = fn => this.api.action(fn);
    this.$('refresh').addEventListener('click', () => act(() => this.refresh()));
    this.$('load-preset').addEventListener('click', () => act(() => this.loadPreset()));
    this.$('validate').addEventListener('click', () => act(() => this.readControls()));
    this.$('render').addEventListener('click', () => act(() => this.render()));
    this.$('recipe').addEventListener('input', () => {
      this.values = {}; this.observedId = null; this.beginSelection();
      this.$('controls').replaceChildren(); this.$('controls-count').textContent = 'Read controls after recipe edits';
      this.$('status').textContent = 'Recipe changed. Read its original controls before rendering.';
    });
    this.$('file').addEventListener('change', event => act(async () => {
      const file = event.target.files[0]; if (!file) return;
      const selection = this.beginSelection();
      if (file.size > 2 * 1024 * 1024) throw new Error('Recipe JSON exceeds the local 2 MiB limit.');
      const text = await file.text();
      if (this.selectionEpoch !== selection) return;
      const raw = JSON.parse(text);
      this.observedId = null;
      this.$('recipe').value = JSON.stringify(raw, null, 2); this.values = {};
      this.$('preset-note').textContent = 'Loaded recipe file. Its origin is caller-supplied; this does not certify it as a PixelLab preset.';
      await this.readControls(); event.target.value = '';
    }));
    this.$('play').addEventListener('click', () => this.playing ? this.pause() : this.play());
    this.$('frame').addEventListener('input', () => { this.pause(); this.draw(Number(this.$('frame').value)); });
    this.$('open-editor').addEventListener('click', () => act(() => this.api.openEditor(this.result.sequence)));
    this.$('save-recipe').addEventListener('click', () => act(async () => {
      const snapshot = await this.api.invoke('local.pixellab.vfx.controls', {recipe: this.readRecipe(), values: {...this.values}});
      const blob = new Blob([JSON.stringify(snapshot.declared_recipe, null, 2) + '\n'], {type: 'application/json'});
      const url = URL.createObjectURL(blob), a = document.createElement('a');
      a.href = url; a.download = 'pixellab-declared-recipe.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    }));
    this.$('recent').addEventListener('change', () => act(async () => {
      const selection = this.beginSelection(), inputEpoch = this.epoch;
      const current = () => this.selectionEpoch === selection && this.epoch === inputEpoch;
      const entry = this.recent.find(r => r.id === this.$('recent').value);
      if (!entry) return;
      const receipt = await this.api.request('/api/artifact/' + entry.result.control_receipt);
      if (!current()) return;
      const effect = await this.api.request('/api/artifact/' + entry.result.recipe);
      if (!current()) return;
      if (receipt.kind !== 'source-controls' || !receipt.declared_recipe) throw new Error('Retained render has no raw declared recipe.');
      if (effect.kind !== 'effect-recipe') throw new Error('Retained render has no effect input record.');
      this.observedId = entry.result.observed_id || null;
      this.$('recipe').value = JSON.stringify(receipt.declared_recipe, null, 2); this.values = {}; this.epoch++;
      this.$('subject').value = effect.subject || '';
      this.$('images').value = JSON.stringify(effect.images || {}, null, 2);
      this.$('preset-note').textContent = 'Restored the raw declared recipe from control receipt ' + entry.result.control_receipt;
      const restoredEpoch = this.epoch;
      await this.readControls();
      if (this.selectionEpoch === selection && this.epoch === restoredEpoch) await this.showResult(entry.result);
    }));
    for (const field of ['subject', 'images']) this.$(field).addEventListener('input', () => this.changed());
  }
  beginSelection() {
    this.selectionEpoch = (this.selectionEpoch || 0) + 1;
    this.previewEpoch = (this.previewEpoch || 0) + 1;
    this.epoch++; this.$('render').disabled = true;
    return this.selectionEpoch;
  }
  async enter() {
    if (!this.catalog) await this.refresh();
    await this.refreshRecent();
  }
  async refresh() {
    if (this.loading) return this.loading;
    this.loading = (async () => {
      const catalog = await this.api.request('/api/pixellab/source'); this.catalog = catalog;
      this.$('identity').textContent = `${Object.keys(catalog.source.families).length} original layer families · ${catalog.observed_counts.defaults} observed defaults · ${catalog.observed_counts.controls} declared controls · unchanged pinned browser functions · manifest ${catalog.source.manifest_sha256}`;
      this.$('preset').replaceChildren();
      for (const [label, entries, prefix] of [
        ['Retained get_preset snapshots', catalog.presets, 'preset:'],
        ['Observed prepared defaults · retained fitted instances', catalog.observed_defaults || [], 'observed:'],
        ['Observed subject examples · own R9 image', catalog.observed_subject_examples || [], 'observed:']]) {
        const group = document.createElement('optgroup'); group.label = label;
        for (const entry of entries) {
          const option = document.createElement('option'); option.value = prefix + entry.id; option.textContent = entry.label + (entry.provenance.needs_subject ? ' · needs subject setup' : '');
          group.append(option);
        }
        this.$('preset').append(group);
      }
      const available = catalog.presets.length + (catalog.observed_defaults || []).length;
      this.$('preset').disabled = !available; this.$('load-preset').disabled = !available;
      this.$('validate').disabled = false; this.$('save-recipe').disabled = false;
      if (!this.$('recipe').value && catalog.presets.length) await this.loadPreset();
    })();
    try { await this.loading; } finally { this.loading = null; }
  }
  readRecipe() {
    let recipe; try { recipe = JSON.parse(this.$('recipe').value); } catch { throw new Error('Recipe JSON is invalid.'); }
    if (!recipe || Array.isArray(recipe) || typeof recipe !== 'object') throw new Error('A recipe must be a JSON object.');
    return recipe;
  }
  async loadPreset() {
    const selected = this.$('preset').value, observed = selected.startsWith('observed:');
    const id = selected.slice(selected.indexOf(':') + 1);
    const preset = (observed ? [...this.catalog.observed_defaults, ...(this.catalog.observed_subject_examples || [])] : this.catalog.presets).find(p => p.id === id);
    if (!preset) throw new Error('Choose a retained recipe.');
    this.beginSelection(); this.observedId = observed ? id : null;
    this.$('recipe').value = JSON.stringify(preset.recipe, null, 2); this.values = {};
    if (observed) {
      this.$('subject').value = ''; this.$('images').value = '{}';
      this.$('preset-note').textContent = `${preset.provenance.needs_subject ? 'Needs subject setup: this retained default has no configured subject and is transparent. Supplying a raster alone does not configure a subject. Choose its R9 subject example in the library to replay the captured setup. ' : ''}${preset.subject_png ? 'Uses the packaged retained R9 subject PNG. ' : ''}${this.catalog.observed_boundary} Response ${preset.provenance.response_sha256}`;
    } else this.$('preset-note').textContent = `Original get_preset response ${preset.provenance.request_id} · ${preset.provenance.response_sha256}`;
    await this.readControls();
  }
  async readControls() {
    const epoch = this.epoch, recipe = this.readRecipe(); this.$('render').disabled = true;
    const output = await this.api.invoke('local.pixellab.vfx.controls', {recipe, values: {...this.values}});
    if (this.epoch !== epoch) return;
    this.$('validation').textContent = JSON.stringify(output, null, 2);
    this.$('controls').replaceChildren(); this.$('controls-count').textContent = `${output.controls.length} declared`;
    this.values = Object.fromEntries(output.controls.map(c => [c.id, c.value]));
    for (const control of output.controls) {
      const label = document.createElement('label'); label.className = 'source-control';
      const title = document.createElement('span'); title.textContent = control.label || control.id; label.append(title);
      let input;
      if (control.type === 'slider') {
        input = document.createElement('input'); input.type = 'range';
        input.min = control.min; input.max = control.max; input.step = control.step; input.value = control.value;
        const value = document.createElement('output'); value.textContent = String(control.value);
        input.addEventListener('input', () => {
          this.values[control.id] = Number(input.value); value.textContent = input.value; this.changed();
        }); label.append(input, value);
      } else if (control.type === 'toggle') {
        input = document.createElement('input'); input.type = 'checkbox'; input.checked = control.value;
        input.addEventListener('change', () => { this.values[control.id] = input.checked; this.changed(); });
        label.append(input);
      } else if (control.type === 'ramp' || control.type === 'select') {
        input = document.createElement('select');
        const options = control.options.map((option, index) => {
          const value = control.type === 'select' ? option.value : option;
          return {key: control.type === 'ramp' && typeof value === 'string' ? value : 'option:' + index, value,
            label: control.type === 'select' ? option.label : (typeof option === 'string' ? option : JSON.stringify(option))};
        });
        if (control.type === 'ramp' && !options.some(entry => JSON.stringify(entry.value) === JSON.stringify(control.value))) {
          options.push({key: 'current-ramp', value: control.value, label: 'Current custom ramp'});
        }
        for (const entry of options) {
          const option = document.createElement('option'); option.value = entry.key; option.textContent = entry.label; input.append(option);
        }
        input.value = options.find(entry => JSON.stringify(entry.value) === JSON.stringify(control.value))?.key || '';
        input.addEventListener('change', () => {
          this.values[control.id] = options.find(entry => entry.key === input.value).value; this.changed();
        });
        label.append(input);
      } else {
        const note = document.createElement('span'); note.textContent = `Unexposed control type: ${control.type}. Use Methods with its recorded schema.`; label.append(note);
      }
      if (input) { input.dataset.controlId = control.id; input.setAttribute('aria-label', control.label || control.id); }
      if (control.help) label.title = control.help;
      this.$('controls').append(label);
    }
    this.$('render').disabled = this.pending;
    this.$('status').textContent = 'Original control declarations read. Render executes the original mapping and renderer once.';
  }
  changed() {
    this.epoch++;
    this.$('status').textContent = 'Settings changed. The previous output is retained; render to update it.';
  }
  async render() {
    if (this.pending) return;
    const recipe = this.readRecipe(), values = {...this.values};
    const observedId = this.observedId, params = observedId ? {id: observedId, values} : {recipe, values};
    const subject = this.$('subject').value.trim(); if (subject) params.subject = subject;
    let images; try { images = JSON.parse(this.$('images').value); } catch { throw new Error('Named image IDs must be JSON.'); }
    if (!images || Array.isArray(images) || typeof images !== 'object') throw new Error('Named image IDs must be an object.');
    if (Object.keys(images).length) params.images = images;
    const epoch = this.epoch; this.pending = true; this.$('render').disabled = true; this.$('job-state').textContent = 'Submitting';
    try {
      const job = await this.api.invoke('local.jobs.submit', {handler: observedId ? this.catalog.observed_render_job : this.catalog.render_job, request: params});
      this.job = typeof job === 'string' ? job : (job.job_id || job.id);
      if (!this.job) throw new Error('Source job submission returned no job ID. Inspect Jobs.');
      this.$('status').textContent = `Original source job ${this.job}`;
      const start = Date.now();
      while (Date.now() - start < 180000) {
        const current = await this.api.invoke('local.jobs.get', {job_id: this.job});
        this.$('job-state').textContent = current.status;
        if (current.status === 'completed') {
          const result = current.outputs.at(-1)?.metadata?.source_result;
          if (!result) throw new Error('Completed source job has no retained source result. Inspect Jobs.');
          await this.showResult(result); await this.refreshRecent();
          if (epoch !== this.epoch) this.$('status').textContent += ' Current settings changed after this job was submitted.';
          return;
        }
        if (['validation_error', 'technical_failure', 'unsupported', 'cancelled', 'interrupted', 'stale'].includes(current.status)) {
          throw new Error(`Source job ${current.status}: ${JSON.stringify(current.error)}`);
        }
        await new Promise(resolve => setTimeout(resolve, 350));
      }
      throw new Error('Automatic source-job polling stopped after 3 minutes. Inspect Jobs; the job has not been cancelled.');
    } finally { this.pending = false; this.$('render').disabled = false; }
  }
  async refreshRecent() {
    const jobs = await this.api.request('/api/jobs');
    this.recent = jobs.filter(j => ['local.pixellab.vfx.render', 'local.pixellab.vfx.render_observed'].includes(j.handler) && j.status === 'completed')
      .map(j => ({id: j.id, result: j.outputs.at(-1)?.metadata?.source_result})).filter(r => r.result);
    const select = this.$('recent'), old = select.value; select.replaceChildren();
    const empty = document.createElement('option'); empty.value = ''; empty.textContent = 'Select a retained render'; select.append(empty);
    for (const entry of this.recent) {
      const option = document.createElement('option'); option.value = entry.id;
      option.textContent = `${entry.id.slice(0, 10)} · ${entry.result.sequence.slice(0, 12)}`; select.append(option);
    }
    if (this.recent.some(r => r.id === old)) select.value = old;
  }
  async showResult(result) {
    this.pause(); const epoch = (this.previewEpoch || 0) + 1; this.previewEpoch = epoch;
    const sequence = await this.api.request('/api/artifact/' + result.sequence);
    const images = await Promise.all(sequence.frames.map(frame => new Promise((resolve, reject) => {
      const image = new Image(); image.onload = async () => {
        try { if (image.decode) await image.decode(); resolve(image); } catch (error) { reject(error); }
      }; image.onerror = () => reject(new Error('A retained source frame failed to load.'));
      image.src = '/api/raster/' + frame.raster + '.png';
    })));
    if (this.previewEpoch !== epoch) return;
    this.result = result; this.sequence = sequence; this.frames = images;
    this.$('canvas').width = sequence.canvas[0]; this.$('canvas').height = sequence.canvas[1];
    this.$('canvas').hidden = false; this.$('empty').hidden = true;
    this.$('frame').disabled = false; this.$('frame').max = images.length - 1; this.$('play').disabled = false;
    this.$('open-editor').disabled = false; this.$('result').textContent = JSON.stringify(result, null, 2);
    this.$('status').textContent = `${images.length} frames decoded · ${sequence.canvas.join(' × ')} · sequence ${result.sequence}`;
    this.$('job-state').textContent = 'Retained result'; this.draw(0);
  }
  draw(index) {
    if (!this.frames.length) return;
    this.frame = index; const canvas = this.$('canvas'), ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.drawImage(this.frames[index], 0, 0);
    this.$('frame').value = index; this.$('frame-label').textContent = `${index + 1} / ${this.frames.length}`;
  }
  pause() {
    if (this.handle) cancelAnimationFrame(this.handle); this.handle = null; this.playing = false;
    this.$('play').textContent = 'Play';
  }
  play() {
    if (!this.frames.length) return;
    this.pause(); this.playing = true; this.$('play').textContent = 'Pause';
    const durations = this.sequence.frames.map(f => f.duration[0] / f.duration[1]);
    const total = durations.reduce((a, b) => a + b, 0), start = performance.now();
    const tick = now => {
      if (!this.playing) return;
      const elapsed = (now - start) / 1000;
      if (!this.sequence.loop && elapsed >= total) { this.draw(this.frames.length - 1); this.pause(); return; }
      let t = elapsed % total, index = 0;
      while (index < durations.length - 1 && t >= durations[index]) t -= durations[index++];
      this.draw(index); this.handle = requestAnimationFrame(tick);
    }; this.handle = requestAnimationFrame(tick);
  }
};
