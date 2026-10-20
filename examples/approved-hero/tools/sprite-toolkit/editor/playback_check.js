async (page) => {
 await page.goto('http://127.0.0.1:8140/editor/');await page.waitForFunction(()=>window.SpriteEditor?.ready);
 const report=await page.evaluate(async()=>{
  const checks=[],check=(pass,name)=>{checks.push({name,pass:!!pass});if(!pass)throw Error(name);};
  const p=SpriteEditor.getProject();p.animations[0].loop=false;p.animations[0].events=[{at_tick:0,name:'start'},{at_tick:5,name:'contact'},{at_tick:17,name:'last'}];
  await SpriteEditor.loadProject(p);SpriteEditor.play();SpriteEditor.advanceTicks(8);SpriteEditor.pause();const paused=await SpriteEditor.snapshot();
  SpriteEditor.play();SpriteEditor.pause();const resumed=await SpriteEditor.snapshot();
  check(paused.play_tick===8&&resumed.play_tick===8,'Play resumes paused tick8');check(JSON.stringify(paused.events)===JSON.stringify(resumed.events),'Resume does not duplicate start/contact events');
  SpriteEditor.advanceTicks(9);const last=await SpriteEditor.snapshot();check(last.play_tick===17&&last.frame_id==='frame-3'&&!last.play_completed,'Last frame retains its final native tick');
  SpriteEditor.advanceTicks(1);const done=await SpriteEditor.snapshot();check(done.play_completed&&!done.playing&&done.play_tick===17,'One-shot completes after final hold');
  SpriteEditor.play();SpriteEditor.pause();const restart=await SpriteEditor.snapshot();check(restart.play_tick===0&&!restart.play_completed&&restart.events.length===1,'Play after completion starts a new run');
  SpriteEditor.advanceTicks(8);SpriteEditor.replay();SpriteEditor.pause();const replay=await SpriteEditor.snapshot();check(replay.play_tick===0&&replay.events.length===1,'Explicit Replay starts at0 and clears prior run events');
  SpriteEditor.selectFrame('frame-2');SpriteEditor.play();SpriteEditor.pause();const seek=await SpriteEditor.snapshot();check(seek.play_tick===5&&seek.frame_id==='frame-2','Selected cel seeks to its hold start');
  p.animations[0].loop=true;await SpriteEditor.loadProject(p);SpriteEditor.play();SpriteEditor.pause();SpriteEditor.advanceTicks(59);const loop=await SpriteEditor.snapshot();
  check(loop.play_tick===5&&loop.frame_id==='frame-2','Large tick advance preserves three wraps and remainder');check(loop.events.filter(e=>e.name==='start').length===4&&loop.events.filter(e=>e.name==='contact').length===4&&loop.events.filter(e=>e.name==='last').length===3,'Crossed events are emitted once per occurrence');
  for(const ticks of [-1,1.5,10001]){const before=await SpriteEditor.snapshot();let rejected=false;try{SpriteEditor.advanceTicks(ticks);}catch{rejected=true;}const after=await SpriteEditor.snapshot();check(rejected&&JSON.stringify(before)===JSON.stringify(after),'Invalid advance is atomic: '+ticks);}
  const beforeReload=await SpriteEditor.snapshot();await SpriteEditor.loadProject(p);const loaded=await SpriteEditor.snapshot();check(beforeReload.play_tick===5&&loaded.play_tick===0&&!loaded.events.length,'Project loading resets old clock and event state');
  return {passed:true,checks,paused,resumed,last,done,restart,replay,seek,loop,limits:['Browser editor clock only; actual native Godot controller tested separately','These checks do not approve anatomy or movement quality']};
 });
 const download=page.waitForEvent('download');await page.evaluate(report=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));a.download='editor-playback-check.json';a.click();},report);await(await download).saveAs('evidence/editor-playback-check.json');return{passed:report.passed,checks:report.checks.length};
}
