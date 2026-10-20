async(page)=>{
 await page.setViewportSize({width:1584,height:1000});
 await page.goto('http://127.0.0.1:8144/pilot/review-player/final.html');
 await page.waitForFunction(()=>window.ReelReview&&document.querySelector('#reel').readyState>=2,null,{timeout:90000});
 // Native controls overlay hid feet in early captures. Hide only for evidence,
 // keep user controls on the final viewer, and capture the encoded 2x dimensions.
 await page.evaluate(()=>reel.controls=false);
 const first=await page.evaluate(()=>({width:reel.videoWidth,height:reel.videoHeight,duration:reel.duration,receipt:ReelReview.receipt}));
 if(!await page.evaluate(()=>ReelReview.source_verified&&ReelReview.video_verified))throw Error('Reel source/video unverified');
 if(first.width!==1536||first.height!==432||Math.abs(first.duration-first.receipt.seconds)>.04)throw Error('Wrong media dimensions/clock');
 const samples=[];
 for(const group of ['walk','run','slash','thrust','shoot','knockdown_sword','recover_blaster']){
  const row=first.receipt.groups.find(x=>x.group===group);
  if(!row)throw Error('Missing review action');
  await page.evaluate(async(start)=>{reel.pause();reel.currentTime=start;await new Promise(resolve=>reel.addEventListener('seeked',resolve,{once:true}));await reel.play();},row.video_start_tick/60);
  const span=(row.video_end_tick-row.video_start_tick+1)/60;
  for(let i=0;i<4;i++){
   const target=row.video_start_tick/60+span*(i/4);
   await page.waitForFunction(target=>reel.currentTime>=target,target);
   const state=await page.evaluate(()=>({time:reel.currentTime,wall:performance.now(),paused:reel.paused}));
   if(state.paused||state.time>(row.video_end_tick+1)/60)throw Error('Timed capture left requested action');
   const path='__OUTPUT_DIRECTORY__/'+group+'-'+i+'.png';
   await page.locator('#reel').screenshot({path});samples.push({group,sample:i,path,...state});
  }
  await page.evaluate(()=>reel.pause());
 }
 const paused=await page.evaluate(()=>reel.currentTime);await page.waitForTimeout(120);
 if(await page.evaluate(()=>reel.currentTime)!==paused)throw Error('Media pause did not freeze');
 await page.evaluate(()=>reel.controls=true);
 await page.screenshot({path:'__OUTPUT_DIRECTORY__/final-viewer.png',fullPage:true});
 return {passed:true,manifest_sha256:first.receipt.bake_manifest_sha256,video_sha256:first.receipt.video_sha256,
         groups:7,actual_timed_captures:samples,dimensions:[first.width,first.height],duration:first.duration,pause_freezes:true,
         scope:'Actual Chromium MP4 playback with chronological timed screenshots of seven action groups in four directions; screenshots viewed separately. No claim of continuous video ingestion by the AI.'};
}
