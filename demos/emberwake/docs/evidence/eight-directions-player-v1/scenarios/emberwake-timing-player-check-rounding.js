async (page) => {
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.waitForFunction(()=>window.walkReview&&window.walkReview.ready);
 const receipts=[];const check=(name,ok,detail)=>{receipts.push({name,ok,detail});if(!ok)throw new Error(name)};
 check('32 actual PNG images loaded',await page.evaluate(()=>window.walkReview.imageCount===32));
 const hashResult=await page.evaluate(async()=>{const s=await(await fetch('INPUTS.json')).json(),rows=[];for(const views of Object.values(s.variants))for(const entries of Object.values(views))for(const e of entries){const bytes=await(await fetch(e.path)).arrayBuffer(),h=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');rows.push({path:e.path,ok:h===e.sha256})}return rows});
 check('browser-fetched PNG SHA256 matches all32 inputs',hashResult.every(x=>x.ok),hashResult.length);
 const states=[];for(let i=0;i<8;i++){states.push(await page.evaluate(n=>{walkReview.setPhase(n);const rows=[];for(const id of ['a','as','b','bs']){const c=document.getElementById(id),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(const x of p)h=Math.imul(h^x,16777619);rows.push(h>>>0)}return{phase:walkReview.phase,rows}},i))}
 check('all8 candidate poses rendered at both scales',new Set(states.map(s=>s.rows[2])).size===8&&new Set(states.map(s=>s.rows[3])).size===8);
 await page.locator('#step').click();check('step wraps07 to00',await page.evaluate(()=>walkReview.phase===0));
 await page.locator('#view').selectOption('southwest');check('mirrored-view selection works',await page.locator('#view').inputValue()==='southwest');
 await page.locator('#bg').selectOption('#e1ded1');check('background changes painted canvas',await page.evaluate(()=>Array.from(document.getElementById('b').getContext('2d').getImageData(0,0,1,1).data).join(',')==='225,222,209,255'));
 await page.locator('#view').selectOption('southeast');await page.locator('#bg').selectOption('#202732');
 await page.evaluate(()=>walkReview.setPhase(0));await page.screenshot({path:'output/playwright/timing-only-player.png',fullPage:true});
 const observed=await page.evaluate(async()=>{const seen=new Set;walkReview.play();const end=performance.now()+1100;while(performance.now()<end){seen.add(walkReview.phase);await new Promise(r=>requestAnimationFrame(r))}return [...seen]});
 check('live PNG clock presents all8 phases over actual two loops',observed.length===8,observed);
 await page.evaluate(()=>walkReview.seekSeconds(.1));
 check('A/B clocks differ at100ms as authored',await page.evaluate(()=>walkReview.phases.A===1&&walkReview.phases.B===2),await page.evaluate(()=>walkReview.phases));
 const rendered=await page.evaluate(async()=>{let ok=true;for(const[id,path]of[['a','A/southeast/01.png'],['b','B/southeast/02.png']]){const image=new Image();image.src=path;await image.decode();const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.fillStyle='#202732';ctx.fillRect(0,0,256,256);ctx.drawImage(image,0,0,256,256);const a=document.getElementById(id).getContext('2d').getImageData(0,0,256,256).data,b=ctx.getImageData(0,0,256,256).data;for(let i=0;i<a.length;i++)if(Math.abs(a[i]-b[i])>1)ok=false}return ok});
 check('actual canvases show A01/B02 within measured1RGB GPU-CPU alpha rounding',rendered);
 await page.evaluate(()=>walkReview.seekSeconds(.225));check('opposite contact key4 stays at225ms for both',await page.evaluate(()=>walkReview.phases.A===4&&walkReview.phases.B===4));
 await page.evaluate(()=>walkReview.seekSeconds(.45));check('exact.45s loop wraps both to key0',await page.evaluate(()=>walkReview.phases.A===0&&walkReview.phases.B===0));
 const video=page.locator('video');await video.evaluate(v=>v.play());await page.waitForFunction(()=>document.querySelector('video').currentTime>.4);
 check('normal-speed MP4 playback advances',await video.evaluate(v=>v.readyState>=2&&v.duration===3.6&&v.currentTime>.4));
 await video.evaluate(v=>v.pause());await page.evaluate(()=>walkReview.setPhase(0));
 check('no page/console errors',errors.length===0,errors);
 return{passed:receipts.every(r=>r.ok),receipts,canvasStates:states,qualification:'Browser playback/UI/hash evidence; not a human art or motion score.'};
}