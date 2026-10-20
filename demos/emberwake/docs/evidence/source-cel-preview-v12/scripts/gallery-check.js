async (page) => {
 const receipts=[];const check=(v,n)=>{receipts.push({name:n,passed:!!v})};
 await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
 const meta=()=>page.evaluate(()=>{const v=document.querySelector('video');return {source:v.currentSrc,duration:v.duration,width:v.videoWidth,height:v.videoHeight,loop:v.loop,rate:v.playbackRate,paused:v.paused,time:v.currentTime,error:v.error?.code??null}});
 let a=await meta();check(a.width===640&&a.height===280&&Math.abs(a.duration-.9)<.001,'NE actual decoded640x280/.9second media');check(a.loop&&!a.error,'NE looping withoutdecodererror');
 const samples=await page.evaluate(async()=>{const v=document.querySelector('video');await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=.001});await v.play();const values=[];const start=performance.now();await new Promise(resolve=>{function step(){values.push(v.currentTime);if(performance.now()-start>1250)resolve();else requestAnimationFrame(step)}requestAnimationFrame(step)});return{count:values.length,min:Math.min(...values),max:Math.max(...values),wrapped:values.some((x,i)=>i&&x+0.2<values[i-1])}});
 check(samples.count>=8&&samples.wrapped,'NE actual normalclock progress andloopwrap observed');
 await page.locator('#speed').selectOption('.5');check((await meta()).rate===.5,'real halfspeedcontrol');
 await page.locator('#view').selectOption('northwest');await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&v.currentSrc.includes('northwest')});a=await meta();check(a.width===640&&a.height===280&&Math.abs(a.duration-.9)<.001,'NW actual decodedmedia');check(a.rate===.5&&!a.error,'NW carrieshalfspeed withoutdecodererror');
 await page.locator('#speed').selectOption('1');check((await meta()).rate===1,'normalclock restored');
 check((await page.locator('#poses').getAttribute('href')).includes('northwest-pose-strip'),'actualNWpose link');check((await page.locator('#route').getAttribute('href')).includes('northwest-translation'),'actualNWtranslation link');
 await page.screenshot({path:'/home/astra/artifacts/emberwake-source-cel-game-preview-v12/GALLERY.png'});
 return {passed:receipts.every(r=>r.passed),receipts,samples,final:await meta(),scope:'Browsertransportandnormalclockprogressonly, no continuoushumanvisualgrade or contactacceptance'};
}