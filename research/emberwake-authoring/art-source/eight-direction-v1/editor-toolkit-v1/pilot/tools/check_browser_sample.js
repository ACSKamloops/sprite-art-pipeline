async (page) => {
  // Replace __SAMPLE_DIRECTORY__ with a JSON-escaped absolute path before execution.
  await page.reload();
  await page.waitForFunction(()=>window.SpriteEditor?.ready);
  await page.locator('#open-project').setInputFiles(__SAMPLE_DIRECTORY__ + "/project.json");
  // Wait on a synchronous state predicate, then explicitly await/hash the
  // loaded bytes. An async polling predicate raced a slow 60-frame file load
  // under the browser CLI and admitted the small calibration document.
  await page.waitForFunction(() => window.SpriteEditor?.getProject().provenance?.source_bindings && window.SpriteEditor.getProject().layers.some(x=>x.id==='torso'));
  const loadedHash=await page.evaluate(async()=>await SpriteEditor.projectHash(SpriteEditor.getProject()));
  if(loadedHash!==__EXPECTED_PROJECT_SHA__)throw Error('Loaded editor document differs from expected project');
  const result = await page.evaluate(async () => {
    const api = window.SpriteEditor;
    const initial = api.getProject();
    const initialHash = await api.projectHash(initial);
    const frame = initial.frames[0];
    api.selectFrame(frame.id);
    api.selectLayer('torso');
    const cel = frame.cels.torso;
    const layerIndex = initial.layers.findIndex(x => x.id === 'torso');
    const above = initial.layers.slice(layerIndex + 1).map(x => frame.cels[x.id]).filter(Boolean).map(id => initial.cels[id].pixels);
    const index = initial.cels[cel].pixels.findIndex((v, i) => v !== 0 && !above.some(p => initial.palette[p[i]][3]));
    const old = initial.cels[cel].pixels[index];
    const target = initial.palette.findIndex((v, i) => i > 0 && i !== old && v[3] === 255);
    const x = index % 192, y = Math.floor(index / 192);
    const transaction = {schema: 'sprite-edit-transaction/v1', expected_project_sha256: initialHash,
      reason: 'Local browser fine-edit proof; candidate only',
      operations: [{op: 'paint', cel_id: cel, points: [[x, y, target]], mask: [[x, y]]}]};
    const before = api.renderRGBA(frame.id);
    await api.applyTransaction(transaction);
    const after = api.renderRGBA(frame.id);
    const changed = [];
    for (let i = 0; i < before.length; i += 4) if (before.slice(i, i + 4).some((v, j) => v !== after[i + j])) changed.push(i / 4);
    if (changed.length !== 1 || changed[0] !== index) throw Error('Visible pixel edit escaped its exact mask');
    let staleRejected = false;
    try { await api.applyTransaction(transaction); } catch (_) { staleRejected = true; }
    if (!staleRejected) throw Error('Stale browser edit accepted');
    const editedHash = await api.projectHash(api.getProject());
    await api.undo();
    if (await api.projectHash(api.getProject()) !== initialHash) throw Error('Undo changed source');
    await api.redo();
    if (await api.projectHash(api.getProject()) !== editedHash) throw Error('Redo changed candidate');
    const canvas = api.canvasRGBA();
    if (canvas.some((v, i) => v !== after[i])) throw Error('Actual canvas differs from edited RGBA');
    return {scope: 'Actual Chromium file load and twelve-layer sample editing, not full action playback',
      passed: true, layers: initial.layers.length, frames: initial.frames.length,
      project_sha256: initialHash, edited_sha256: editedHash,
      changed_coordinate: [x, y], outside_mask_changes: 0, stale_edit_rejected: true,
      undo_exact: true, redo_exact: true, canvas_rgba_exact: true, art_approved: false};
  });
  await page.screenshot({path: __SAMPLE_DIRECTORY__ + "/browser-editor.png", fullPage: true});
  return result;
}
