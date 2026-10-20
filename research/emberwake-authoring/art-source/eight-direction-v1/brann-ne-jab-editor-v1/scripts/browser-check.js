async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('**/*', route => {
    if (route.request().url().startsWith('http://127.0.0.1:8937/')) return route.continue();
    return route.abort();
  });
  await page.goto('http://127.0.0.1:8937/toolkit/editor/?project=../../run/source-project.json');
  await page.waitForFunction(() => window.SpriteEditor?.ready);
  const checks = [];
  const check = (value,name) => { checks.push({name,passed:!!value}); if (!value) throw Error(name); };
  const input = await page.evaluate(async () => ({
    source:await (await fetch('../../run/source-project.json')).json(),
    final:await (await fetch('../../run/preferred-project.json')).json(),
    transaction:await (await fetch('../../run/candidate-transaction.json')).json(),
    journal:await (await fetch('../../run/journal.json')).json()
  }));
  const sourceHash = await page.evaluate(() => SpriteEditor.projectHash(SpriteEditor.getProject()));
  check(sourceHash === input.transaction.expected_project_sha256, 'Actual editor loaded exact frozen source project');
  check(await page.locator('#frames button').count() === 8 && await page.locator('#layers button').count() === 1, 'Actual editor shows eight frames and one flat layer');
  await page.getByText('Programmatic edit',{exact:true}).click();
  await page.getByRole('textbox',{name:'JSON transaction',exact:true}).fill(JSON.stringify(input.transaction));
  await page.getByRole('button',{name:'Apply transaction',exact:true}).click();
  await page.waitForFunction(async () => (await SpriteEditor.snapshot()).undo_count === 1);
  const finalHash = await page.evaluate(() => SpriteEditor.projectHash(SpriteEditor.getProject()));
  check(finalHash === input.journal.receipts[0].after_sha256, 'UI applied one exact guarded candidate transaction');
  const browserJournal = await page.evaluate(() => SpriteEditor.exportJournal());
  check(await page.evaluate(({a,b}) => SpriteEditor.canonical(a) === SpriteEditor.canonical(b),{a:browserJournal,b:input.journal}), 'Actual editor journal and receipt match Python exactly');
  await page.getByRole('button',{name:'Undo',exact:true}).click();
  await page.waitForFunction(async () => (await SpriteEditor.snapshot()).undo_count === 0);
  check(await page.evaluate(() => SpriteEditor.projectHash(SpriteEditor.getProject())) === sourceHash, 'Actual UI Undo restores complete source project');
  await page.getByRole('button',{name:'Redo',exact:true}).click();
  await page.waitForFunction(async () => (await SpriteEditor.snapshot()).undo_count === 1);
  check(await page.evaluate(() => SpriteEditor.projectHash(SpriteEditor.getProject())) === finalHash, 'Actual UI Redo restores complete preferred project');
  const saveProject = page.waitForEvent('download');
  await page.getByRole('button',{name:'Save project',exact:true}).click();
  await (await saveProject).saveAs('output/playwright/browser-saved-project.json');
  const saveJournal = page.waitForEvent('download');
  await page.getByRole('button',{name:'Save journal',exact:true}).click();
  await (await saveJournal).saveAs('output/playwright/browser-saved-journal.json');
  await page.locator('#open-project').setInputFiles('output/playwright/browser-saved-project.json');
  await page.waitForFunction(async () => (await SpriteEditor.snapshot()).undo_count === 0);
  check(await page.evaluate(() => SpriteEditor.projectHash(SpriteEditor.getProject())) === finalHash, 'Actual saved project file reopen is exact');
  await page.locator('#open-project').setInputFiles('run/source-project.json');
  await page.waitForFunction(async hash => (await SpriteEditor.projectHash(SpriteEditor.getProject())) === hash, sourceHash);
  await page.locator('#open-journal').setInputFiles('output/playwright/browser-saved-journal.json');
  await page.waitForFunction(async hash => (await SpriteEditor.projectHash(SpriteEditor.getProject())) === hash, finalHash);
  check((await page.evaluate(() => SpriteEditor.snapshot())).undo_count === 1, 'Actual journal file reopen replays against exact original source');

  const negative = await page.evaluate(async () => {
    const output = [];
    for (const name of ['stale-project','stale-cel','outside-mask']) {
      const fixture=await (await fetch('../../run/negative/'+name+'.json')).json();
      await SpriteEditor.loadProject(fixture.input_project);
      const before=await SpriteEditor.snapshot();
      let error=null;
      try { await SpriteEditor.applyTransaction(fixture.transaction); } catch (e) { error=e.message; }
      const after=await SpriteEditor.snapshot();
      output.push({name,error,before,after,unchanged:JSON.stringify(before)===JSON.stringify(after)});
    }
    return output;
  });
  check(negative.every(row => row.error && row.unchanged && row.before.undo_count===0), 'Actual editor rejects meaningful stale-project, stale-cel and outside-mask fixtures atomically');
  await page.evaluate(async ({source,journal}) => SpriteEditor.replayJournal(source,journal),input);
  const pixels=await page.evaluate(async () => {
    const rows=[];
    for (const frame of SpriteEditor.getProject().frames) {
      const bytes=new Uint8Array(SpriteEditor.renderRGBA(frame.id));
      const digest=await crypto.subtle.digest('SHA-256',bytes);
      rows.push({frame:frame.id,rgba_sha256:[...new Uint8Array(digest)].map(v=>v.toString(16).padStart(2,'0')).join('')});
    }
    return rows;
  });
  const boundaries=await page.evaluate(() => {
    SpriteEditor.replay(); SpriteEditor.pause();
    const rows=[];
    for (const hold of [12,14,11,11,13,7,7,7]) {
      rows.push({before:SpriteEditor.advanceTicks(hold-1),after:SpriteEditor.advanceTicks(1)});
    }
    return rows;
  });
  check(boundaries.map(row=>row.before.frame_id).join(',') === input.final.frames.map(f=>f.id).join(','), 'Actual editor holds every source pose for its exact native tick count');
  const ended=await page.evaluate(()=>SpriteEditor.snapshot());
  check(ended.play_completed && !ended.playing && ended.frame_id==='source-22' && ended.play_tick===81 && ended.events.length===0, 'One-shot ends after 82 ticks on source22 with no invented events');
  // Capture inside the browser so a .410s clip cannot finish during a CLI
  // transport round trip before the live clock observation reaches it.
  const live=await page.evaluate(async()=>{
    document.querySelector('#replay').click();
    for(let i=0;i<20;i++) {
      await new Promise(resolve=>requestAnimationFrame(resolve));
      const state=await SpriteEditor.snapshot();
      if(state.play_tick>0) return state;
    }
    return SpriteEditor.snapshot();
  });
  check(live.playing && live.play_tick > 0, 'Real requestAnimationFrame playback advances this actual clip');
  await page.waitForFunction(() => document.querySelector('#play-state').textContent === 'Completed');
  const done=await page.evaluate(()=>SpriteEditor.snapshot());
  check(done.play_completed && !done.playing && done.events.length===0, 'Real playback stops the nonlooping action without invented events');
  await page.evaluate(()=>SpriteEditor.selectFrame('source-11'));
  await page.getByRole('checkbox',{name:'Changed pixels',exact:true}).check();
  await page.screenshot({path:'output/playwright/editor-source11.png',fullPage:true});
  check(errors.length===0, 'No uncaught editor errors');
  const report={passed:true,checks,source_project_sha256:sourceHash,preferred_project_sha256:finalHash,browser_journal:browserJournal,negative_cases:negative,canonical_rgba: pixels,boundaries,live,done,errors,limits:['Partial alpha exists: canonical editor RGBA is authoritative; Canvas2D displayed readback is not claimed exact','Mechanics only; no new motion or art acceptance','All browser requests restricted to own local server port8937']};
  const saveReport=page.waitForEvent('download');
  await page.evaluate(report=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='browser-proof.json';a.click();},report);
  await (await saveReport).saveAs('output/playwright/BROWSER-PROOF.json');
  return {passed:true,checks:checks.length,negative_cases:negative.length,finalHash};
}
