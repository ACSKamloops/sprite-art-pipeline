async(page)=>{
 await page.reload();await page.waitForFunction(()=>window.SpriteReview?.state.ready);
 const checks=[];const check=(name,passed)=>{checks.push({name,passed});if(!passed)throw Error(name);};
 const initial=await page.evaluate(()=>({binding:SpriteReview.state.binding,n:SpriteReview.state.manifest.clips[SpriteReview.state.binding].frames.length,errors:SpriteReview.state.errors}));
 check('pack loaded without source/pixel failures',initial.errors.length===0);
 await page.locator('#play').click();await page.waitForFunction(()=>SpriteReview.state.clock>=6);
 await page.locator('#pause').click();const pause=await page.evaluate(()=>({clock:SpriteReview.state.clock,rgba:[...SpriteReview.canvasRGBA('current-frame')]}));
 await page.waitForTimeout(120);const after=await page.evaluate(()=>({clock:SpriteReview.state.clock,rgba:[...SpriteReview.canvasRGBA('current-frame')]}));
 check('actual pause freezes clock and visible pixels',pause.clock===after.clock&&pause.rgba.every((v,i)=>v===after.rgba[i]));
 await page.locator('#next').click();await page.waitForTimeout(20);check('actual step shows next held frame',await page.evaluate((clock)=>SpriteReview.held()===Math.floor(clock)+1,pause.clock));
 await page.locator('#replay').click();await page.waitForFunction(()=>SpriteReview.state.clock>0&&SpriteReview.state.clock<6);await page.locator('#pause').click();
 check('actual Replay resets clock and resumes',await page.evaluate(()=>SpriteReview.state.clock<6));
 const apiChecks=await page.evaluate(async()=>{
  const api=SpriteReview;let invalidTime=false,invalidClip=false,badPixels=false;
  const c=api.state.clock;try{api.advance(NaN);}catch(_){invalidTime=api.state.clock===c;}
  const b=api.state.binding;try{await api.select('unknown/right');}catch(_){invalidClip=api.state.binding===b;}
  const row=api.state.manifest.clips[b].frames[0];try{await api.loadFrame({...row,pixel_sha256:'0'.repeat(64)});}catch(_){badPixels=true;}
  await api.select('walk/right');api.state.playing=true;api.advance(65);api.state.playing=false;await api.draw();const loop=api.held()===5;
  await api.select('knockdown/right');const n=api.state.manifest.clips[api.state.binding].frames.length;api.state.playing=true;api.advance(n+100);await api.draw();const oneShot=!api.state.playing&&api.held()===n-1&&api.state.clock===n;
  return {invalidTime,invalidClip,badPixels,loop,oneShot};
 });
 for(const [name,passed]of Object.entries(apiChecks))check(name,passed);
 const terminal=await page.evaluate(()=>SpriteReview.state.clock);await page.locator('#play').click();check('Play preserves completed one-shot; Replay is explicit',await page.evaluate((n)=>SpriteReview.state.clock===n&&!SpriteReview.state.playing,terminal));
 await page.locator('#scale').selectOption('1');check('native scale is192CSSpixels',await page.locator('#current-frame').evaluate(e=>e.getBoundingClientRect().width===194));
 await page.locator('#scale').selectOption('2');await page.locator('#onion').check();await page.waitForTimeout(20);await page.locator('#onion').uncheck();
 const report={scope:'Actual local Chromium PNG source validation, controls, frame holds, pixels and timing; visual judgments recorded separately',passed:checks.every(x=>x.passed),checks,actual_input_controls:true};
 await page.screenshot({path:'__OUTPUT_DIRECTORY__/player-proof.png',fullPage:true});return report;
}
