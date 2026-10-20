async (page) => {
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 const receipts=[];const check=(name,ok,detail)=>{receipts.push({name,ok,detail});if(!ok)throw Error(name)};
 check('actual Godot gallery loaded',(await page.title()).includes('v10 walk review'));
 const hashes=await page.evaluate(async()=>{const entries=await(await fetch('MEDIA-RECEIPT.json')).json(),rows=[];for(const entry of entries){const bytes=await(await fetch(entry.clip+'.mp4')).arrayBuffer(),digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');rows.push({clip:entry.clip,ok:digest===entry.mp4_sha256})}return rows});
 check('all6 fetched MP4 hashes match actual native encodes',hashes.length===6&&hashes.every(x=>x.ok),hashes);
 const clips=[];
 for(const actor of ['rowan','lyra','brann'])for(const view of ['southeast','northeast']){
  await page.locator('#actor').selectOption(actor);await page.locator('#view').selectOption(view);
  const key=actor+'-'+view;
  await page.waitForFunction(k=>{const v=document.querySelector('video');return v.currentSrc.endsWith(k+'.mp4')&&v.readyState>=2},key);
  const meta=await page.locator('video').evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,loop:v.loop}));
  check(key+' actual640x280 native video and two-cycle duration',meta.width===640&&meta.height===280&&Math.abs(meta.duration-.9)<.001&&meta.loop,meta);
  await page.locator('video').evaluate(async v=>{v.currentTime=0;await v.play()});await page.waitForFunction(()=>document.querySelector('video').currentTime>.15);
  const pixels=await page.locator('video').evaluate(v=>{const c=document.createElement('canvas');c.width=96;c.height=104;const x=c.getContext('2d');x.drawImage(v,112,132,96,104,0,0,96,104);const d=x.getImageData(0,0,96,104).data;let warm=0;for(let i=0;i<d.length;i+=4)if(d[i]>d[i+1]+20&&d[i]>d[i+2]+20)warm++;v.pause();return{warm_pixels:warm,time:v.currentTime,ready:v.readyState}});
  check(key+' advances and presents colored character pixels',pixels.time>.15&&pixels.ready>=2&&pixels.warm_pixels>40,pixels);clips.push({clip:key,...pixels});
 }
 await page.locator('#speed').selectOption('.5');check('half-speed control reaches media clock',await page.locator('video').evaluate(v=>v.playbackRate===.5));
 await page.locator('video').evaluate(async v=>{v.currentTime=.82;await v.play()});await page.waitForFunction(()=>document.querySelector('video').currentTime<.25);check('actual media loops across route reset',await page.locator('video').evaluate(v=>!v.ended&&v.currentTime<.25));
 await page.locator('#speed').selectOption('1');await page.locator('#actor').selectOption('rowan');await page.locator('#view').selectOption('southeast');await page.waitForFunction(()=>document.querySelector('video').readyState>=2&&document.querySelector('video').currentSrc.endsWith('rowan-southeast.mp4'));
 await page.locator('video').evaluate(async v=>{v.currentTime=.1;await v.play()});await page.waitForFunction(()=>document.querySelector('video').currentTime>.15);await page.locator('video').evaluate(v=>v.pause());
 await page.screenshot({path:'output/playwright/godot-walk-gallery-v10.png',fullPage:true});
 check('no page or console errors',errors.length===0,errors);
 return{passed:receipts.every(x=>x.ok),receipts,clips,qualification:'Browser selection/decode/playback and actual source-media checks, not human temporal art approval or physical contact.'};
}
