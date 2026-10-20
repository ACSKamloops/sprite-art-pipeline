'use strict';

// Local UI orchestration only. Rendering, recovered selection and project edits
// are backend services; the overlay consumes mask alpha, never its RGB values.
window.SpriteStudioUI = class {
  static clock(sequence) {
    if (!Array.isArray(sequence?.frames) || !sequence.frames.length || sequence.frames.length > 512)
      throw new Error('The preview needs 1–512 stored frames.');
    if (typeof sequence.loop !== 'boolean') throw new Error('The preview has no stored loop policy.');
    const holds = sequence.frames.map(frame => {
      const d = frame.duration;
      if (!Array.isArray(d) || d.length !== 2 || !d.every(Number.isSafeInteger) || d[0] <= 0 || d[1] <= 0)
        throw new Error('A frame has no valid stored rational hold.');
      return d[0] / d[1] * 1000;
    });
    const total = holds.reduce((a, b) => a + b, 0);
    const count = sequence.play_count ?? (sequence.loop ? 0 : 1);
    if (!Number.isFinite(total) || total <= 0 || !Number.isSafeInteger(count) || count < 0 || count > 65536 || (count === 0) !== Boolean(sequence.loop))
      throw new Error('The sequence has an invalid stored playback clock.');
    return {holds, total, count, end: count === 0 ? Infinity : total * count};
  }
  static frameAt(clock, elapsed) {
    if (elapsed >= clock.end) return {index: clock.holds.length - 1, ended: true};
    let t = Math.max(0, elapsed) % clock.total, index = 0;
    while (index < clock.holds.length - 1 && t >= clock.holds[index]) t -= clock.holds[index++];
    return {index, ended: false};
  }
  static artifact(id) {
    if (typeof id !== 'string' || !/^[0-9a-f]{64}$/.test(id)) throw new Error('The local service returned an invalid artifact identity.');
    return id;
  }
  constructor(api) {
    this.api = api; this.$ = id => document.getElementById('studio-' + id);
    this.catalog = null; this.project = null; this.projectId = null; this.history = null;
    this.frame = 0; this.zoom = 1; this.epoch = 0; this.pending = false;
    this.images = []; this.sourceImages = []; this.elapsed = 0; this.playing = false;
    this.selectionReceipts = [];
    this.storageKey = 'sprite-workbench.studio.v1'; this.needsRefresh = false;
    this.bind(); this.restore(); this.sync();
  }
  bind() {
    const click = (id, label, fn) => this.$(id).addEventListener('click', () => this.api.action(() => this.run(label, fn)));
    click('load', 'Loading supplied demo…', () => this.loadExample());
    click('use-workspace', 'Opening current Workspace project…', () => this.useWorkspace());
    this.$('use-upload').addEventListener('click', () => { const context = this.api.workspaceContext?.(); if (context?.last_upload) this.$('import-sequence').value = context.last_upload; });
    this.$('import-form').addEventListener('submit', event => { event.preventDefault(); this.api.action(() => this.run('Importing the explicitly selected sequence…', () => this.importSequence())); });
    this.$('upload-file').addEventListener('change', event => { const file = event.target.files[0]; if (file) this.api.action(() => this.run('Retaining uploaded PNG / APNG frames…', () => this.upload(file))); event.target.value = ''; });
    click('refresh', 'Reloading current project…', () => this.hydrate());
    click('select', 'Running the recovered host selector…', () => this.createSelection());
    click('erase', 'Erasing the bound selection…', () => this.applySelection('erase'));
    click('paint', 'Painting the bound selection…', () => this.applySelection('paint'));
    click('undo', 'Restoring previous history state…', () => this.historyStep('undo'));
    click('redo', 'Restoring next history state…', () => this.historyStep('redo'));
    click('verify', 'Checking the current project mechanically…', () => this.verify());
    click('export', 'Building the complete local package…', () => this.exportPackage());
    click('open-editor', 'Opening the fine editor…', async () => {
      this.editorLinked = true; this.persist(); await this.api.openEditor({project: this.projectId, history: this.history});
    });
    this.$('play').addEventListener('click', () => this.api.action(async () => this.playing ? this.pause() : this.play()));
    this.$('prev').addEventListener('click', () => this.seek(this.frame - 1));
    this.$('next').addEventListener('click', () => this.seek(this.frame + 1));
    this.$('frame').addEventListener('input', () => this.seek(Number(this.$('frame').value)));
    this.$('copy').addEventListener('change', () => { this.pause(); this.invalidate('Preview copy changed; select on the working copy.'); this.resetPosition(); this.draw(); this.sync(); });
    for (const [id, scale] of [['zoom1', 1], ['zoom2', 2]]) this.$(id).addEventListener('click', () => { this.zoom = scale; this.draw(); });
    for (const id of ['seed-x', 'seed-y', 'tolerance']) this.$(id).addEventListener('input', () => { this.invalidate('Seed or tolerance changed. Create a new selection.'); this.sync(); });
    this.$('show-mask').addEventListener('change', () => this.drawOverlay());
    this.$('palette-index').addEventListener('input', () => { this.updatePalette(); this.sync(); });
    this.$('layer').addEventListener('change', () => { this.pause(); this.invalidate('Layer changed. Create a new selection.'); this.persist(); this.frameInfo(); this.sync(); });
    this.$('animation').addEventListener('change', () => this.api.action(() => this.run('Rendering selected animation…', async () => {
      this.animationId = this.$('animation').value; this.frame = 0; this.pendingFrameId = null; this.invalidate(); this.clearReview(); this.persist(); await this.render();
    })));
    this.$('canvas').addEventListener('pointerdown', event => {
      if (event.button !== 0 || !this.project || this.pending || this.playing || this.$('copy').value !== 'working') return;
      const canvas = this.$('canvas'), rect = canvas.getBoundingClientRect();
      const x = Math.floor((event.clientX - rect.left) * canvas.width / rect.width), y = Math.floor((event.clientY - rect.top) * canvas.height / rect.height);
      if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) return;
      this.$('seed-x').value = x; this.$('seed-y').value = y; this.invalidate(`Seed set to (${x}, ${y}). Create a selection.`); this.sync();
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden) this.pause(); });
    window.addEventListener('pagehide', () => { this.pause(); this.persist(); });
  }
  async run(label, fn) {
    if (this.pending) return;
    this.pause(); this.pending = true; this.$('status').textContent = label; this.$('status').classList.remove('error'); this.sync();
    try { return await fn(); }
    catch (error) { this.$('status').textContent = error.message; this.$('status').classList.add('error'); throw error; }
    finally { this.pending = false; this.sync(); }
  }
  async enter() {
    if (this.pending) return;
    if (this.catalog && this.project && !this.needsRefresh) { this.sync(); return; }
    return this.run('Opening local Studio…', async () => {
      if (!this.catalog) {
        const catalog = await this.api.invoke('local.studio.catalog', {});
        if (!Array.isArray(catalog.examples)) throw new Error('The Studio catalog has no example list.');
        this.catalog = catalog; const menu = this.$('demo'); menu.replaceChildren();
        for (const entry of catalog.examples) { const option = document.createElement('option'); option.value = entry.id; option.textContent = `${entry.title} · ${entry.frames} frames`; menu.append(option); }
      }
      if (this.projectId && this.history) await this.hydrate();
      else this.$('status').textContent = 'Choose a supplied hero demo. Loading it makes an editable local copy.';
    });
  }
  async loadExample() {
    const entry = this.catalog?.examples.find(e => e.id === this.$('demo').value);
    if (!entry) throw new Error('Choose a supplied demo.');
    const result = await this.api.invoke('local.studio.load_example', {id: entry.id});
    await this.loadResult(result, entry.title, entry.clock_note);
  }
  async loadResult(result, title, clockNote) {
    this.selectionReceipts = []; this.adopt(result); this.sourceId = result.source_sequence ? this.constructor.artifact(result.source_sequence) : null;
    this.normalizedId = result.sequence ? this.constructor.artifact(result.sequence) : null;
    this.title = title; this.clockNote = result.clock_note || clockNote;
    this.normalization = result.normalization || null; this.sourceFrameIds = null; this.captureImportedMapping = true;
    this.sourceDocument = null; this.sourceImages = []; this.frame = 0; this.pendingFrameId = null; this.editorLinked = false;
    this.$('copy').value = 'working'; this.persist(); await this.hydrate(); this.receipt(result);
    this.$('status').textContent = 'Supplied frames loaded. The retained source and editable copy are separate artifacts.';
  }
  async upload(file) {
    if (!/\.(png|apng)$/i.test(file.name) || file.size > 32 * 1024 * 1024) throw new Error('Choose a PNG or APNG of at most 32 MiB.');
    const reply = await this.api.request('/api/upload', {method: 'POST', headers: {'Content-Type': 'image/png', 'X-Workbench-Filename': encodeURIComponent(file.name)}, body: file});
    const result = reply.result ?? reply; this.$('import-sequence').value = this.constructor.artifact(result.sequence);
    this.receipt(result); this.$('status').textContent = 'Upload retained. Review the normalization choice, then choose Import sequence.';
  }
  async importSequence() {
    const sequence = this.constructor.artifact(this.$('import-sequence').value.trim());
    const result = await this.api.invoke('local.studio.from_sequence', {sequence, normalize_hidden_rgb: this.$('normalize').checked});
    await this.loadResult(result, 'Supplied sequence', 'Preview uses the supplied sequence’s stored rational holds.');
  }
  async useWorkspace() {
    const context = this.api.workspaceContext?.();
    if (!context?.project || !context.history || context.busy) throw new Error('Open a project in Workspace and finish its current edit first.');
    this.constructor.artifact(context.project); this.constructor.artifact(context.history);
    const same = context.project === this.projectId && context.history === this.history;
    let source = same ? this.sourceId : context.source_sequence, normalization = same ? this.normalization : null;
    let sourceDocument;
    if (!same && source) {
      const imported = await this.api.request('/api/artifact/' + this.constructor.artifact(source));
      if (imported.metadata?.studio_normalization) {
        const id = this.constructor.artifact(imported.metadata.studio_normalization), record = await this.api.request('/api/artifact/' + id);
        if (record.kind !== 'studio-normalization') throw new Error('The Workspace normalization reference is not a normalization receipt.');
        source = this.constructor.artifact(record.source_sequence); normalization = {policy: record.policy, changed_hidden_rgb_pixels: record.changed_hidden_rgb_pixels, receipt: id};
        sourceDocument = await this.api.request('/api/artifact/' + source);
      } else sourceDocument = imported;
    }
    const current = this.api.workspaceContext?.();
    if (current?.project !== context.project || current?.history !== context.history || current.busy) throw new Error('Workspace changed while opening its project. Try again after its edit completes.');
    if (!same) {
      this.captureImportedMapping = false;
      this.selectionReceipts = []; this.sourceId = source || null; this.normalization = normalization; this.sourceDocument = null; this.sourceImages = []; this.sourceFrameIds = null;
      this.normalizedId = context.source_sequence || null; this.title = 'Workspace project'; this.clockNote = sourceDocument?.metadata?.clock_note || 'Current project holds are used; original timing provenance is retained with the source.';
    }
    this.pendingFrameId = context.frame_id; this.layerId = context.layer_id; this.$('layer').value = context.layer_id || '';
    this.editorLinked = true; this.adopt(context); this.$('copy').value = 'working'; await this.hydrate();
    this.$('status').textContent = 'Current Workspace project and history opened in Studio. No reimport or normalization was performed.';
  }
  adopt(result) {
    const project = this.constructor.artifact(result.project), history = this.constructor.artifact(result.history);
    this.invalidate(); this.projectId = project; this.history = history;
    if (result.animation_id) this.animationId = result.animation_id;
    this.project = null; this.images = []; this.sequence = null; this.journal = null;
    this.needsRefresh = true; this.clearReview(); this.persist();
    this.$('surface').hidden = true; this.$('empty').hidden = false; this.$('empty').textContent = 'Loading the current project preview…';
  }
  async hydrate() {
    if (!this.projectId || !this.history) throw new Error('Load a project first.');
    const requestedProject = this.projectId, requestedHistory = this.history;
    const [reply, history] = await Promise.all([this.api.request('/api/project/' + this.constructor.artifact(this.projectId)), this.api.request('/api/artifact/' + this.constructor.artifact(this.history))]);
    if (requestedProject !== this.projectId || requestedHistory !== this.history) return;
    if (history.project !== this.projectId) throw new Error('The stored history does not refer to this project.');
    const p = reply.document;
    if (!p?.frames?.length || !p.animations?.length || !p.layers?.length || !p.palette?.length || p.canvas.width * p.canvas.height > 1048576)
      throw new Error('This project is outside the Studio preview limits. Open it through Workspace.');
    this.project = p; this.projectHash = reply.project_hash; this.journal = history.journal;
    if (!p.animations.some(a => a.id === this.animationId)) this.animationId = p.animations[0].id;
    const oldLayer = this.$('layer').value || this.layerId;
    this.$('animation').replaceChildren(...p.animations.map(a => this.option(a.id, a.id)));
    this.$('animation').value = this.animationId;
    this.$('layer').replaceChildren(...p.layers.map(l => this.option(l.id, l.name + (l.locked ? ' · locked' : ''))));
    this.$('layer').value = p.layers.some(l => l.id === oldLayer) ? oldLayer : [...p.layers].reverse().find(l => !l.locked)?.id || p.layers[0].id;
    this.$('seed-x').max = p.canvas.width - 1; this.$('seed-y').max = p.canvas.height - 1;
    this.$('seed-x').value = Math.min(Number(this.$('seed-x').value) || 0, p.canvas.width - 1);
    this.$('seed-y').value = Math.min(Number(this.$('seed-y').value) || 0, p.canvas.height - 1);
    this.$('palette-index').max = p.palette.length - 1;
    this.$('palette-index').value = Math.min(Number(this.$('palette-index').value) || 0, p.palette.length - 1);
    this.renderPalette(); await this.render();
    if (requestedProject !== this.projectId || requestedHistory !== this.history) return;
    this.needsRefresh = false;
    this.$('status').textContent = 'Current project and history loaded. Preview uses stored holds.';
  }
  option(value, label) { const option = document.createElement('option'); option.value = value; option.textContent = label; return option; }
  animation() { return this.project?.animations.find(a => a.id === this.animationId); }
  frameDocument() { return this.project?.frames.find(f => f.id === this.animation()?.frames[this.frame]); }
  celId() { return this.frameDocument()?.cels[this.$('layer').value]; }
  async rasterImage(id) {
    this.constructor.artifact(id);
    return new Promise((resolve, reject) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = () => reject(new Error('A retained preview raster could not be loaded.')); image.src = '/api/raster/' + id + '.png'; });
  }
  async render() {
    this.pause(); this.invalidate(); const epoch = this.epoch;
    this.images = []; this.sequence = null; this.$('surface').hidden = true; this.$('empty').hidden = false; this.$('empty').textContent = 'Rendering the current animation…';
    const result = await this.api.invoke('local.construction.render', {project: this.projectId, history: this.history, animation_id: this.animationId});
    const sequence = await this.api.request('/api/artifact/' + this.constructor.artifact(result.sequence));
    this.constructor.clock(sequence);
    if (this.project.canvas.width * this.project.canvas.height * sequence.frames.length > 16777216) throw new Error('This animation exceeds the Studio preview memory limit. Open it in Workspace.');
    const images = await Promise.all(sequence.frames.map(f => this.rasterImage(f.raster)));
    let source = this.sourceDocument, sourceImages = this.sourceImages;
    if (this.sourceId && !source) {
      source = await this.api.request('/api/artifact/' + this.constructor.artifact(this.sourceId));
      this.constructor.clock(source);
      const allowed = source.canvas?.[0] === this.project.canvas.width && source.canvas?.[1] === this.project.canvas.height && this.project.canvas.width * this.project.canvas.height * source.frames.length <= 16777216;
      sourceImages = allowed ? await Promise.all(source.frames.map(f => this.rasterImage(f.raster))) : [];
    }
    if (epoch !== this.epoch) return;
    if (sequence.frames.length !== this.animation().frames.length) throw new Error('Rendered frames do not align with this animation.');
    const {width, height} = this.project.canvas;
    if (images.some(image => image.naturalWidth !== width || image.naturalHeight !== height)) throw new Error('Preview rasters do not preserve the full project canvas.');
    this.sequence = sequence; this.sequenceId = result.sequence; this.images = images;
    this.sourceDocument = source; this.sourceImages = sourceImages || [];
    // Only a fresh import proves positional correspondence. Adopting a Workspace
    // project may follow reorder edits, so equal lengths cannot establish it.
    if (this.captureImportedMapping && source?.frames.length === this.animation().frames.length) this.sourceFrameIds = [...this.animation().frames];
    this.captureImportedMapping = false;
    this.sourceAligned = this.sourceImages.length === source?.frames.length && source?.frames.length === this.animation().frames.length && this.sourceFrameIds?.every((id, i) => id === this.animation().frames[i]) && !this.sourceImages.some(image => image.naturalWidth !== width || image.naturalHeight !== height);
    if (!this.sourceAligned) this.$('copy').value = 'working';
    if (this.pendingFrameId) { const index = this.animation().frames.indexOf(this.pendingFrameId); if (index >= 0) this.frame = index; this.pendingFrameId = null; }
    this.frame = Math.min(this.frame, images.length - 1); this.resetPosition(); this.buildFrames(); this.draw(); this.identities(); this.persist();
  }
  identities() {
    this.$('project-title').textContent = this.title || 'Current project';
    this.$('dimensions').textContent = `${this.project.canvas.width} × ${this.project.canvas.height} px · ${this.images.length} frames · ${this.project.palette.length} palette entries`;
    this.$('clock-note').textContent = this.clockNote || 'Source clock unavailable. Preview uses this project’s stored inspection holds.';
    for (const [name, value] of [['source-id', this.sourceId], ['normalized-id', this.normalizedId], ['sequence-id', this.sequenceId], ['project-id', this.projectId], ['history-id', this.history]]) this.$(name).textContent = value || '—';
    const n = this.normalization;
    this.$('normalization').textContent = n ? `${n.policy}. Hidden-RGB pixels changed: ${n.changed_hidden_rgb_pixels}. Retained source unchanged.` : 'No source normalization receipt recorded for this project.';
  }
  activeSequence() { return this.$('copy').value === 'source' && this.sourceAligned ? this.sourceDocument : this.sequence; }
  clock() { return this.activeSequence() ? this.constructor.clock(this.activeSequence()) : null; }
  resetPosition() { const clock = this.clock(); this.elapsed = clock ? clock.holds.slice(0, this.frame).reduce((a, b) => a + b, 0) : 0; }
  buildFrames() {
    const strip = this.$('frames'); strip.replaceChildren();
    this.sequence.frames.forEach((frame, index) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = String(index + 1).padStart(2, '0'); b.setAttribute('aria-label', `Frame ${index + 1}, ${frame.duration[0]}/${frame.duration[1]} seconds`); b.addEventListener('click', () => this.seek(index)); strip.append(b); });
    this.$('frame').max = this.images.length - 1;
  }
  seek(index) {
    if (this.pending || !this.images.length) return;
    this.pause(); this.frame = Math.max(0, Math.min(index, this.images.length - 1)); this.invalidate('Frame changed. Create a new selection.'); this.resetPosition(); this.draw(); this.persist(); this.sync();
  }
  draw() {
    if (!this.project || !this.images.length) return;
    const {width, height} = this.project.canvas, source = this.$('copy').value === 'source';
    const image = (source ? this.sourceImages : this.images)[this.frame]; if (!image) return;
    for (const id of ['canvas', 'overlay']) { const c = this.$(id); if (c.width !== width || c.height !== height) { c.width = width; c.height = height; } c.style.width = width * this.zoom + 'px'; c.style.height = height * this.zoom + 'px'; }
    const canvas = this.$('canvas'), context = canvas.getContext('2d'); context.imageSmoothingEnabled = false; context.clearRect(0, 0, width, height); context.drawImage(image, 0, 0);
    this.$('surface').hidden = false; this.$('empty').hidden = true;
    this.$('frame').value = this.frame; this.$('frame-label').textContent = `${this.frame + 1} / ${this.images.length}`;
    const sequence = this.activeSequence(), hold = sequence.frames[this.frame].duration;
    this.$('hold').textContent = `${source ? 'Retained source' : 'Working copy'} · hold ${hold[0]}/${hold[1]} s · ${sequence.loop ? 'loop' : (sequence.play_count || 1) === 1 ? 'play once' : `${sequence.play_count} plays`} · full canvas`;
    this.$('frames').querySelectorAll('button').forEach((button, index) => button.setAttribute('aria-pressed', String(index === this.frame)));
    this.$('zoom1').setAttribute('aria-pressed', String(this.zoom === 1)); this.$('zoom2').setAttribute('aria-pressed', String(this.zoom === 2));
    canvas.setAttribute('aria-label', `${source ? 'Retained source' : 'Working copy'}, frame ${this.frame + 1}, full ${width} by ${height} pixel canvas`);
    this.frameInfo(); this.drawOverlay();
  }
  frameInfo() {
    const cel = this.celId(), layer = this.project?.layers.find(l => l.id === this.$('layer').value);
    const linked = cel ? this.project.frames.filter(f => Object.values(f.cels).includes(cel)).length : 0;
    this.$('cel').textContent = cel || 'No cel on this layer in the current frame.';
    this.$('linked').textContent = linked > 1 ? `Linked · ${linked} frames` : cel ? 'One frame' : 'No cel';
    this.$('link-note').textContent = layer?.locked ? 'Layer locked. Choose an unlocked layer to apply edits.' : linked > 1 ? `This cel is shared by ${linked} frames. Selection edits update all of them; no cel is detached.` : 'Edits change this project cel and create an undoable revision.';
  }
  pause() {
    if (this.playing) { this.elapsed += performance.now() - this.started; this.persist(); }
    this.playing = false; if (this.handle) cancelAnimationFrame(this.handle); this.handle = null;
    this.sync();
  }
  play() {
    if (this.pending || !this.images.length) return;
    const clock = this.clock(); if (!clock) return;
    if (this.elapsed >= clock.end) { this.elapsed = 0; this.frame = 0; }
    this.invalidate('Playback changed the frame. Create a new selection when paused.');
    this.playing = true; this.started = performance.now(); const epoch = this.epoch; this.sync();
    const tick = now => {
      if (!this.playing || epoch !== this.epoch) return;
      const position = this.constructor.frameAt(clock, this.elapsed + now - this.started);
      if (this.frame !== position.index) { this.frame = position.index; this.draw(); }
      if (position.ended) { this.elapsed = clock.end; this.playing = false; this.handle = null; this.persist(); this.sync(); return; }
      this.handle = requestAnimationFrame(tick);
    };
    this.draw(); this.handle = requestAnimationFrame(tick);
  }
  invalidate(message = 'Project changed. Create a new selection.') {
    this.epoch++; this.selection = null; this.maskImage = null;
    this.$('selection-info').textContent = message; this.drawOverlay();
  }
  drawOverlay() {
    const canvas = this.$('overlay'), context = canvas.getContext('2d'); context.clearRect(0, 0, canvas.width, canvas.height);
    if (!this.maskImage || !this.$('show-mask').checked || this.$('copy').value !== 'working') return;
    const scratch = document.createElement('canvas'); scratch.width = canvas.width; scratch.height = canvas.height;
    const raw = scratch.getContext('2d', {willReadFrequently: true}); raw.drawImage(this.maskImage, 0, 0);
    const pixels = raw.getImageData(0, 0, canvas.width, canvas.height), data = pixels.data;
    for (let i = 0; i < data.length; i += 4) { const selected = data[i + 3] > 0; data[i] = 200; data[i + 1] = 84; data[i + 2] = 49; data[i + 3] = selected ? 110 : 0; }
    context.putImageData(pixels, 0, 0);
  }
  async createSelection() {
    if (!this.project || !this.celId() || this.$('copy').value !== 'working') throw new Error('Select an existing working-copy project cel.');
    const seed = [Number(this.$('seed-x').value), Number(this.$('seed-y').value)], tolerance = Number(this.$('tolerance').value);
    if (!seed.every(Number.isSafeInteger) || seed[0] < 0 || seed[1] < 0 || seed[0] >= this.project.canvas.width || seed[1] >= this.project.canvas.height || !Number.isFinite(tolerance) || tolerance < 0 || tolerance > 1)
      throw new Error('Enter a seed inside the canvas and a finite tolerance from 0 to 1.');
    this.invalidate(); const epoch = this.epoch, project = this.projectId, cel = this.celId();
    const result = await this.api.invoke('local.selection.create', {project, cel_id: cel, seed, tolerance});
    if (result.source_project !== project || result.cel_id !== cel || result.source_project_hash !== this.projectHash) throw new Error('The selection response does not match the requested project cel.');
    this.constructor.artifact(result.selection); const mask = await this.rasterImage(result.mask_raster);
    if (epoch !== this.epoch || project !== this.projectId || cel !== this.celId()) return;
    if (mask.naturalWidth !== this.project.canvas.width || mask.naturalHeight !== this.project.canvas.height) throw new Error('Selection mask does not match the project canvas.');
    this.selection = {...result, boundProject: project, boundCel: cel, boundFrame: this.frame}; this.maskImage = mask;
    const links = result.shared_frames, count = Array.isArray(links) ? links.length : Number.isInteger(links) ? links : this.project.frames.filter(f => Object.values(f.cels).includes(cel)).length;
    this.$('linked').textContent = count > 1 ? `Linked · ${count} frames` : 'One frame';
    this.$('selection-info').textContent = `${result.selected_pixels} selected pixels · cel ${cel} · ${count} linked frame${count === 1 ? '' : 's'}. Applying updates every shared frame.`;
    this.$('status').textContent = 'Selection is bound to this project revision and cel. Inspect the overlay before applying.';
    this.receipt(result); this.drawOverlay();
  }
  async applySelection(action) {
    const selected = this.selection;
    if (!selected || selected.boundProject !== this.projectId || selected.boundCel !== this.celId() || selected.boundFrame !== this.frame) throw new Error('The selection is stale. Create a new selection.');
    const params = {history: this.history, selection: selected.selection, action};
    if (action === 'paint') { const index = Number(this.$('palette-index').value); if (!Number.isSafeInteger(index) || index < 0 || index >= this.project.palette.length) throw new Error('Choose an existing project palette index.'); params.palette_index = index; }
    this.invalidate(); const currentHistory = this.history; const result = await this.api.invoke('local.selection.apply', params);
    if (this.history !== currentHistory) { this.receipt(result); throw new Error('Another editor revision arrived. The selection result is retained in Last local receipt; reload the current project.'); }
    const receiptId = this.constructor.artifact(result.selection_receipt);
    if (!this.selectionReceipts.includes(receiptId)) this.selectionReceipts.push(receiptId);
    this.adopt(result); await this.hydrate(); this.receipt(result); this.$('status').textContent = `Selection ${action === 'erase' ? 'erased' : 'painted'} in an undoable revision. Linked frames share the same edited cel.`;
  }
  async historyStep(direction) {
    this.invalidate(); const currentHistory = this.history; const result = await this.api.invoke('local.construction.' + direction, {history: currentHistory});
    if (this.history !== currentHistory) { this.receipt(result); throw new Error('Another revision arrived while changing history. Reload the current project.'); }
    this.adopt(result); await this.hydrate(); this.receipt(result); this.$('status').textContent = `${direction === 'undo' ? 'Undo' : 'Redo'} restored an exact history state.`;
  }
  renderPalette() {
    const holder = this.$('palette'); holder.replaceChildren();
    this.project.palette.slice(0, 128).forEach((rgba, index) => {
      const b = document.createElement('button'); b.type = 'button'; b.title = `Index ${index}: RGBA ${rgba.join(', ')}`; b.setAttribute('aria-label', b.title);
      b.style.backgroundColor = `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${rgba[3] / 255})`; b.dataset.transparent = String(rgba[3] === 0);
      b.addEventListener('click', () => { this.$('palette-index').value = index; this.updatePalette(); this.sync(); }); holder.append(b);
    });
    this.updatePalette();
  }
  updatePalette() {
    const index = Number(this.$('palette-index').value), color = this.project?.palette[index];
    this.$('palette-value').textContent = color ? `#${index} · RGBA ${color.join(', ')}${this.project.palette.length > 128 ? ' · first 128 swatches shown' : ''}` : 'Choose an existing palette index.';
    this.$('palette').querySelectorAll('button').forEach((b, i) => b.setAttribute('aria-pressed', String(i === index)));
  }
  clearReview() {
    this.$('mechanical').textContent = 'Mechanical: not checked'; this.$('visual').textContent = 'Visual: unreviewed'; this.$('checks').replaceChildren();
    this.$('download').hidden = true; this.$('download').removeAttribute('href'); this.$('export-status').textContent = 'Export the current revision and its retained evidence.';
  }
  requestContext() { return {project: this.projectId, history: this.history, animation_id: this.animationId, selection_receipts: [...this.selectionReceipts]}; }
  async verify() {
    const context = this.requestContext(); const result = await this.api.invoke('local.studio.verify', context);
    if (JSON.stringify(context) !== JSON.stringify(this.requestContext())) { this.receipt(result); throw new Error('The project changed during verification. Run checks on its current revision.'); }
    this.$('mechanical').textContent = result.mechanical_ready === true && result.status === 'passed' ? 'Mechanical: passed' : 'Mechanical: failed';
    this.$('visual').textContent = 'Visual: ' + (result.visual_acceptance || 'unreviewed');
    this.$('checks').replaceChildren(...(result.checks || []).map(check => { const p = document.createElement('p'); p.className = 'small'; p.textContent = `${check.status} · ${check.id}: ${typeof check.detail === 'string' ? check.detail : JSON.stringify(check.detail)}`; return p; }));
    this.receipt(result); this.$('status').textContent = 'Mechanical review recorded. Visual acceptance is a separate review.';
  }
  async exportPackage() {
    const context = this.requestContext(); const result = await this.api.invoke('local.studio.export', context);
    if (JSON.stringify(context) !== JSON.stringify(this.requestContext())) { this.receipt(result); throw new Error('The project changed during export. Its earlier package is retained in Last local receipt.'); }
    if (typeof result.download_url !== 'string' || !/^\/api\/studio\/download\/[0-9a-f]{64}\.zip$/.test(result.download_url)) throw new Error('The export has no valid local package download.');
    this.$('download').href = result.download_url; this.$('download').hidden = false;
    this.$('export-status').textContent = 'Complete package retained locally. Download the ZIP to keep its editable artifacts and evidence.';
    this.$('status').textContent = 'Complete local package ready to download.'; this.receipt(result);
  }
  receipt(result) { const value = JSON.stringify(result, null, 2); this.$('receipt').textContent = value.length > 80000 ? value.slice(0, 80000) + '\n… display limited' : value; }
  workspaceRevision(result, previousHistory) {
    if (!this.editorLinked || this.history !== previousHistory) return;
    this.pendingFrameId = result.frame_id; this.layerId = result.layer_id;
    if (result.layer_id) this.$('layer').value = result.layer_id;
    this.adopt(result); this.$('status').textContent = 'Fine-editor revision saved. Return to Studio to refresh its preview.';
  }
  persist() {
    if (!this.projectId || !this.history) return;
    const saved = {project: this.projectId, history: this.history, animation_id: this.animationId, frame: this.frame,
      frame_id: this.pendingFrameId || this.frameDocument()?.id, layer_id: this.$('layer').value || this.layerId,
      source_sequence: this.sourceId, normalized_sequence: this.normalizedId, source_frame_ids: this.sourceFrameIds, source_mapping_policy: 'fresh-import-only-v1',
      title: this.title, clock_note: this.clockNote, normalization: this.normalization, editor_linked: Boolean(this.editorLinked), selection_receipts: this.selectionReceipts};
    try { localStorage.setItem(this.storageKey, JSON.stringify(saved)); this.$('session').textContent = 'Project & history saved for reload.'; }
    catch { this.$('session').textContent = 'Browser restore unavailable; keep the project/history IDs.'; }
  }
  restore() {
    try {
      const saved = JSON.parse(localStorage.getItem(this.storageKey) || 'null'); if (!saved) return;
      this.projectId = this.constructor.artifact(saved.project); this.history = this.constructor.artifact(saved.history);
      this.animationId = saved.animation_id; this.frame = Number.isSafeInteger(saved.frame) && saved.frame >= 0 ? saved.frame : 0;
      this.pendingFrameId = saved.frame_id; this.layerId = saved.layer_id; this.sourceId = saved.source_sequence; this.normalizedId = saved.normalized_sequence;
      this.sourceFrameIds = saved.source_mapping_policy === 'fresh-import-only-v1' && Array.isArray(saved.source_frame_ids) && saved.source_frame_ids.length <= 512 ? saved.source_frame_ids : null;
      this.selectionReceipts = Array.isArray(saved.selection_receipts) ? saved.selection_receipts.filter(id => typeof id === 'string' && /^[0-9a-f]{64}$/.test(id)) : [];
      this.title = saved.title; this.clockNote = saved.clock_note; this.normalization = saved.normalization; this.editorLinked = Boolean(saved.editor_linked); this.needsRefresh = true;
    } catch { this.projectId = null; this.history = null; }
  }
  sync() {
    const workspace = this.api.workspaceContext?.();
    this.$('use-workspace').disabled = this.pending || !workspace?.project || !workspace.history || workspace.busy;
    this.$('use-upload').disabled = this.pending || !workspace?.last_upload;
    for (const id of ['upload-file', 'import-sequence', 'normalize', 'import']) this.$(id).disabled = this.pending;
    const ready = Boolean(this.project && this.images.length), editable = ready && this.$('copy').value === 'working' && !this.playing;
    const locked = this.project?.layers.find(l => l.id === this.$('layer').value)?.locked;
    for (const id of ['animation', 'layer', 'frame', 'prev', 'next', 'play', 'copy']) this.$(id).disabled = this.pending || !ready;
    this.$('copy').querySelector('option[value="source"]').disabled = !this.sourceAligned;
    for (const id of ['seed-x', 'seed-y', 'tolerance', 'palette-index', 'select']) this.$(id).disabled = this.pending || !editable || !this.celId();
    const index = Number(this.$('palette-index').value), validIndex = Number.isSafeInteger(index) && index >= 0 && index < (this.project?.palette.length || 0);
    this.$('erase').disabled = this.pending || !editable || !this.selection || locked;
    this.$('paint').disabled = this.$('erase').disabled || !validIndex;
    this.$('undo').disabled = this.pending || !this.journal || this.journal.cursor <= 0;
    this.$('redo').disabled = this.pending || !this.journal || this.journal.cursor >= this.journal.receipts.length;
    for (const id of ['verify', 'export', 'open-editor']) this.$(id).disabled = this.pending || !this.projectId || !this.history || !this.project;
    this.$('refresh').disabled = this.pending || !this.projectId;
    this.$('demo').disabled = this.pending || !this.catalog?.examples.length; this.$('load').disabled = this.$('demo').disabled;
    this.$('play').textContent = this.playing ? 'Pause' : this.sequence && this.elapsed >= this.clock()?.end ? 'Replay' : 'Play';
    this.$('status').classList.toggle('busy', this.pending);
    this.$('frames').querySelectorAll('button').forEach(b => b.disabled = this.pending);
    this.$('palette').querySelectorAll('button').forEach(b => b.disabled = this.pending || !editable);
  }
};
