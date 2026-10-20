async (page) => {
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8137/editor/');await page.waitForFunction(()=>window.SpriteEditor?.ready);
  const checks=[];const check=(ok,name)=>{checks.push({name,passed:!!ok});if(!ok)throw Error(name);};
  const initial=await page.evaluate(()=>SpriteEditor.getProject());
  const hash0=await page.evaluate(()=>SpriteEditor.projectHash(SpriteEditor.getProject()));
  const clickPixel=async(x,y)=>{const b=await page.locator('#canvas').boundingBox();const size=await page.evaluate(()=>SpriteEditor.getProject().canvas);await page.mouse.click(b.x+(x+.5)*b.width/size.width,b.y+(y+.5)*b.height/size.height);};
  await page.getByRole('button',{name:'Palette 4',exact:true}).click();await clickPixel(6,10);
  await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===1);
  check(await page.evaluate(()=>SpriteEditor.getProject().cels.a.pixels[10*24+6]===4),'Actual mouse pencil changes exact index');
  check(await page.evaluate(()=>JSON.stringify(SpriteEditor.canvasRGBA())===JSON.stringify(SpriteEditor.renderRGBA())),'Actual art canvas pixels equal engine composite');
  await page.getByRole('button',{name:'Eraser E',exact:true}).click();await clickPixel(6,10);await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===2);
  check(await page.evaluate(()=>SpriteEditor.getProject().cels.a.pixels[10*24+6]===0),'Actual mouse eraser removes pixel');
  await page.getByRole('button',{name:'Undo',exact:true}).click();await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===1);
  check(await page.evaluate(()=>SpriteEditor.getProject().cels.a.pixels[10*24+6]===4),'UI undo restores painted pixel');
  await page.getByRole('button',{name:'Redo',exact:true}).click();await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===2);
  check(await page.evaluate(()=>SpriteEditor.getProject().cels.a.pixels[10*24+6]===0),'UI redo restores erased pixel');
  await page.getByRole('button',{name:'Region mask M',exact:true}).click();const b=await page.locator('#canvas').boundingBox();await page.mouse.move(b.x+7.5*12,b.y+10.5*12);await page.mouse.down();await page.mouse.move(b.x+9.5*12,b.y+12.5*12,{steps:3});await page.mouse.up();
  check((await page.evaluate(()=>SpriteEditor.snapshot())).mask.length===9,'Mouse rectangle selects nine exact pixels');
  await page.getByRole('button',{name:'Replace inside mask',exact:true}).click();await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===3);
  const uiJournal=await page.evaluate(()=>SpriteEditor.exportJournal());check(uiJournal.receipts[2].diff.cels.a.changed_pixels===5,'Masked recolor reports exactly five changed pixels');
  check(await page.evaluate(()=>SpriteEditor.getProject().cels.a.pixels[10*24+10]===1),'Masked recolor preserves outside pixel');
  await page.getByRole('button',{name:'Locked reference mark',exact:true}).click();await page.getByRole('button',{name:'Pencil P',exact:true}).click();const beforeLocked=await page.evaluate(()=>SpriteEditor.projectHash(SpriteEditor.getProject()));await clickPixel(3,3);check(await page.evaluate(()=>SpriteEditor.projectHash(SpriteEditor.getProject()))===beforeLocked,'Actual mouse edit rejects locked layer');
  await page.getByRole('button',{name:'Editable pixels',exact:true}).click();
  const save=page.waitForEvent('download');await page.getByRole('button',{name:'Save project',exact:true}).click();const download=await save;await download.saveAs('editor/output/playwright/mouse-edited-project.json');
  const saved=await page.evaluate(()=>SpriteEditor.getProject());await page.locator('#open-project').setInputFiles('editor/output/playwright/mouse-edited-project.json');await page.waitForFunction(async()=> (await SpriteEditor.snapshot()).undo_count===0);
  check(await page.evaluate(()=>SpriteEditor.projectHash(SpriteEditor.getProject()))===beforeLocked,'Actual save/file reopen preserves canonical project');
  await page.evaluate(async ({initial,uiJournal})=>SpriteEditor.replayJournal(initial,uiJournal),{initial,uiJournal});check(await page.evaluate(()=>SpriteEditor.projectHash(SpriteEditor.getProject()))===beforeLocked,'UI edit journal exactly replays saved pixels');
  await page.evaluate(()=>SpriteEditor.undo());const undone=await page.evaluate(()=>SpriteEditor.exportJournal());await page.evaluate(async({initial,undone})=>SpriteEditor.replayJournal(initial,undone),{initial,undone});check((await page.evaluate(()=>SpriteEditor.snapshot())).redo_count===1,'Journal replay preserves redo branch');await page.evaluate(()=>SpriteEditor.redo());
  // Independent Python parity input: unchanged initial project, exact transactions, browser receipts and output bytes.
  await page.evaluate(initial=>SpriteEditor.loadProject(initial),initial);
  const parity=await page.evaluate(async()=>{const steps=[];const operations=[
   {op:'paint',cel_id:'a',points:[[1,1,4],[2,1,2]],mask:[[1,1],[2,1]]},
   {op:'erase',cel_id:'a',points:[[2,1]]},
   {op:'replace_color',cel_id:'a',from_index:1,to_index:4,mask:[[7,10],[8,10]]},
   {op:'translate',cel_id:'a',dx:1,dy:0},
   {op:'translate_layer',layer_id:'paint',dx:0,dy:1},
   {op:'palette',index:2,rgba:[50,180,120,123]},
   {op:'palette_add',rgba:[10,20,30,80]},
   {op:'frame_timing',frame_id:'frame-2',duration_ticks:9},
   {op:'pivots',render_pivot:[11,16],ground_pivot:[12,29]}
  ];for(const op of operations){const tx={schema:'sprite-edit-transaction/v1',expected_project_sha256:await SpriteEditor.projectHash(SpriteEditor.getProject()),reason:`Browser parity ${op.op}`,operations:[op]};const receipt=await SpriteEditor.applyTransaction(tx);steps.push({transaction:tx,receipt,project:SpriteEditor.getProject(),frames:Object.fromEntries(SpriteEditor.getProject().frames.map(f=>[f.id,SpriteEditor.renderRGBA(f.id)]))});}
  const p=SpriteEditor.getProject(),candidate=[...p.cels.a.pixels];candidate[0]=4;const m=await import('./pixels.js');const op={op:'candidate_patch',cel_id:'a',mask:[[0,0]],candidate_pixels:candidate,expected_cel_sha256:await m.sha(p.cels.a)};const tx={schema:'sprite-edit-transaction/v1',expected_project_sha256:await SpriteEditor.projectHash(p),reason:'Candidate patch parity',operations:[op]};const receipt=await SpriteEditor.applyTransaction(tx);steps.push({transaction:tx,receipt,project:SpriteEditor.getProject(),frames:Object.fromEntries(SpriteEditor.getProject().frames.map(f=>[f.id,SpriteEditor.renderRGBA(f.id)]))});return steps;});
  check(parity.length===10,'All ten operation families execute with exact browser receipts');
  const negative=await page.evaluate(async()=>{const out=[];const cases=[{name:'stale',ops:[{op:'erase',cel_id:'a',points:[[0,0]]}],hash:'0'.repeat(64)},{name:'locked',ops:[{op:'paint',cel_id:'reference',points:[[0,0,1]]}]},{name:'locked global palette',ops:[{op:'palette',index:3,rgba:[2,3,4,255]}]},{name:'duplicate mask',ops:[{op:'replace_color',cel_id:'a',from_index:1,to_index:2,mask:[[1,1],[1,1]]}]},{name:'out of bounds',ops:[{op:'paint',cel_id:'a',points:[[-1,0,2]]}]},{name:'unknown keys',ops:[{op:'erase',cel_id:'a',points:[],invented:true}]},{name:'batch rollback',ops:[{op:'paint',cel_id:'a',points:[[0,0,2]]},{op:'erase',cel_id:'reference',points:[[0,0]]}]}];for(const c of cases){const before=await SpriteEditor.projectHash(SpriteEditor.getProject());let error=null;try{await SpriteEditor.applyTransaction({schema:'sprite-edit-transaction/v1',expected_project_sha256:c.hash||before,reason:c.name,operations:c.ops});}catch(e){error=e.message;}out.push({name:c.name,error,unchanged:before===await SpriteEditor.projectHash(SpriteEditor.getProject())});}const p=SpriteEditor.getProject(),bad=[...p.cels.a.pixels];bad[3]=2;const m=await import('./pixels.js');const before=await SpriteEditor.projectHash(p);let error;try{await SpriteEditor.applyTransaction({schema:'sprite-edit-transaction/v1',expected_project_sha256:before,reason:'Outside candidate mask',operations:[{op:'candidate_patch',cel_id:'a',mask:[[0,0]],candidate_pixels:bad,expected_cel_sha256:await m.sha(p.cels.a)}]});}catch(e){error=e.message;}out.push({name:'outside candidate mask',error,unchanged:before===await SpriteEditor.projectHash(SpriteEditor.getProject())});return out;});
  check(negative.every(r=>r.error&&r.unchanged),'All eight rejected transactions preserve project');
  // Native holds tested through real requestAnimationFrame playback plus explicit source-tick boundary read-back.
  await page.evaluate(initial=>SpriteEditor.loadProject(initial),initial);await page.getByRole('button',{name:'Play',exact:true}).click();await page.waitForTimeout(140);const live=await page.evaluate(()=>SpriteEditor.snapshot());check(live.playing&&live.play_tick>0,'Real requestAnimationFrame playback advances native clock');await page.getByRole('button',{name:'Pause',exact:true}).click();
  const boundary=await page.evaluate(()=>{SpriteEditor.replay();SpriteEditor.pause();return SpriteEditor.advanceTicks(5);});check(boundary.frame_id==='frame-2'&&boundary.events.length===1&&boundary.events[0].name==='color-check','Exact five tick hold crosses authored event into frame2');
  await page.getByRole('checkbox',{name:'Neighboring frames',exact:true}).check();await page.getByRole('checkbox',{name:'Changed pixels',exact:true}).check();await page.evaluate(()=>{document.querySelector('.tools').scrollTop=0;document.querySelector('.inspector').scrollTop=0;document.querySelector('#notice').classList.remove('visible');});await page.screenshot({path:'editor/output/playwright/editor-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile document has no horizontal overflow');await page.screenshot({path:'editor/output/playwright/editor-mobile.png',fullPage:true});await page.setViewportSize({width:1280,height:900});
  check(!errors.length,'No uncaught browser errors');
  const report={passed:true,checks,errors,initial_project:initial,initial_sha256:hash0,mouse_saved_project:saved,mouse_journal:uiJournal,parity_steps:parity,negative_cases:negative,live_playback:live,exact_boundary:boundary};
  const saveReport=page.waitForEvent('download');await page.evaluate(report=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='browser-check.json';a.click();},report);await(await saveReport).saveAs('editor/output/playwright/browser-check.json');return {checks:checks.length,passed:true,negative_cases:negative.length,parity_steps:parity.length};
}
