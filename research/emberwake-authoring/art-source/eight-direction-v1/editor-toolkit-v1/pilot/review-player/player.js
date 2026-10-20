const $=id=>document.getElementById(id);
const packPath=new URLSearchParams(location.search).get('pack')||'../rigged-character/generated/';
const packURL=new URL(packPath.endsWith('/')?packPath:packPath+'/',location.href);
if(packURL.origin!==location.origin)throw Error('Select a pack on this local server');
const state={manifest:null,binding:null,clock:0,playing:false,speed:1,drawnTick:-1,ready:false,rendered:[],errors:[],token:0,loads:0};
const cache=new Map();
const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
const fail=e=>{state.playing=false;state.errors.push(String(e));$('error').textContent=String(e);};
const rgbaCanvas=image=>{const c=document.createElement('canvas');c.width=image.width;c.height=image.height;const x=c.getContext('2d',{willReadFrequently:true});x.drawImage(image,0,0);return {canvas:c,rgba:x.getImageData(0,0,c.width,c.height)};};
async function loadFrame(row){
 const key=row.png+':'+row.pixel_sha256;
 if(!cache.has(key))cache.set(key,(async()=>{
  const url=new URL(row.png,packURL);if(url.origin!==location.origin||!url.href.startsWith(packURL.href))throw Error('Frame path escapes pack');
  const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`Missing ${row.png}`);
  const image=await createImageBitmap(await r.blob());const decoded=rgbaCanvas(image);image.close();
  if(decoded.canvas.width!==192||decoded.canvas.height!==192)throw Error('Changed frame canvas');
  if(await hash(decoded.rgba.data)!==row.pixel_sha256)throw Error(`Changed rendered pixels: ${row.png}`);
  state.loads++;return decoded;
 })());
 return cache.get(key);
}
function clip(){return state.manifest.clips[state.binding];}
function held(){const n=clip().frames.length;return clip().loop?Math.floor(state.clock)%n:Math.min(n-1,Math.floor(state.clock));}
function guides(ctx){ctx.clearRect(0,0,192,192);ctx.fillStyle='#23313e';ctx.fillRect(0,0,192,192);ctx.strokeStyle='#667f88';ctx.beginPath();ctx.moveTo(0,170.5);ctx.lineTo(192,170.5);ctx.stroke();}
async function draw(){
 const token=++state.token,c=clip(),tick=held(),prior=tick===0?(c.loop?c.frames.length-1:0):tick-1;
 const [a,b]=await Promise.all([loadFrame(c.frames[prior]),loadFrame(c.frames[tick])]);if(token!==state.token)return;
 for(const [id,frame]of [['previous-frame',a],['current-frame',b]]){const ctx=$(id).getContext('2d');guides(ctx);if(id==='current-frame'&&$('onion').checked){ctx.globalAlpha=.3;ctx.drawImage(a.canvas,0,0);ctx.globalAlpha=1;}ctx.drawImage(frame.canvas,0,0);}
 const diff=$('difference').getContext('2d');guides(diff);diff.globalAlpha=.25;diff.drawImage(b.canvas,0,0);diff.globalAlpha=1;
 let changed=0;for(let i=0;i<a.rgba.data.length;i+=4)if(a.rgba.data.slice(i,i+4).some((v,j)=>v!==b.rgba.data[i+j])){changed++;const p=i/4;diff.fillStyle='#fa69d6';diff.fillRect(p%192,Math.floor(p/192),1,1);}
 state.drawnTick=tick;state.rendered.push({binding:state.binding,tick,prior,clock:state.clock,wallTime:performance.now(),changed});if(state.rendered.length>15000)state.rendered.shift();
 $('seek').value=tick;$('status').textContent=`${state.binding} · frame ${tick+1}/${c.frames.length} · ${state.playing?'playing':'paused'} · ${changed} changed pixels\n${c.loop?'Loop':'One-shot'} · ${state.manifest.fps} Hz source · ${state.speed}× speed`;
}
async function select(binding){if(!state.manifest.clips[binding])throw Error('Missing action/view');state.binding=binding;state.clock=0;state.playing=false;state.drawnTick=-1;const c=clip();$('seek').max=c.frames.length-1;await Promise.all(c.frames.map(loadFrame));await draw();}
function advance(ticks){if(!Number.isFinite(ticks)||ticks<0||ticks>10000)throw Error('Invalid time delta');if(!state.playing)return;state.clock+=ticks;const c=clip();if(!c.loop&&state.clock>=c.frames.length){state.clock=c.frames.length;state.playing=false;}draw().catch(fail);}
function scale(){for(const id of ['previous-frame','current-frame','difference']){$(id).style.width=`${192*Number($('scale').value)}px`;$(id).style.height=`${192*Number($('scale').value)}px`;}}
async function choose(){await select(`${$('clip').value}/${$('view').value}`);}
$('clip').onchange=()=>choose().catch(fail);$('view').onchange=()=>choose().catch(fail);
$('play').onclick=()=>{if(!clip().loop&&state.clock>=clip().frames.length)return;state.playing=true;draw().catch(fail);};$('pause').onclick=()=>{state.playing=false;draw().catch(fail);};$('replay').onclick=()=>{state.clock=0;state.playing=true;draw().catch(fail);};
for(const [id,step] of [['previous',-1],['next',1]])$(id).onclick=()=>{state.playing=false;const n=clip().frames.length;state.clock=clip().loop?(held()+step+n)%n:Math.max(0,Math.min(n-1,held()+step));draw().catch(fail);};
$('seek').oninput=()=>{state.playing=false;state.clock=Number($('seek').value);draw().catch(fail);};$('speed').onchange=()=>{state.speed=Number($('speed').value);};$('scale').onchange=scale;$('onion').onchange=()=>draw().catch(fail);
let then=performance.now(),autoWait=0;function loop(now){const dt=(now-then)/1000;then=now;if(state.ready){if(state.playing)advance(dt*state.manifest.fps*state.speed);if($('cycle').checked){const c=clip();if((c.loop&&state.clock>=c.frames.length*2)||(!c.loop&&!state.playing&&state.clock>=c.frames.length)){autoWait+=dt;if(autoWait>.35){autoWait=0;const names=[...$('clip').options].map(x=>x.value);$('clip').value=names[(names.indexOf($('clip').value)+1)%names.length];choose().then(()=>{state.playing=true;}).catch(fail);}}else autoWait=0;}}requestAnimationFrame(loop);}requestAnimationFrame(loop);
window.SpriteReview={state,select,advance,draw,loadFrame,held,canvasRGBA:id=>$(id).getContext('2d').getImageData(0,0,192,192).data};
try{
 const r=await fetch(new URL('manifest.json',packURL),{cache:'no-store'});if(!r.ok)throw Error('Missing local pack manifest');state.manifest=await r.json();if(state.manifest.fps!==60||state.manifest.canvas.join(',')!=='192,192')throw Error('Unsupported source clock/canvas');
 for(const [name,expected]of Object.entries(state.manifest.source_bindings)){const r=await fetch(new URL('../'+name,packURL),{cache:'no-store'});if(!r.ok||await hash(await r.arrayBuffer())!==expected)throw Error('Stale source pack: '+name);}
 for(const [binding,c] of Object.entries(state.manifest.clips)){if(!Array.isArray(c.frames)||c.frames.length!==c.duration_ticks||c.frames.length<2||typeof c.loop!=='boolean')throw Error('Invalid clip '+binding);for(const [i,f]of c.frames.entries())if(f.tick!==i||f.duration_ticks!==1||f.region.slice(2).join(',')!=='192,192')throw Error('Invalid frame hold/order '+binding);}
 const names=[...new Set(Object.keys(state.manifest.clips).map(binding=>binding.split('/')[0]))].sort();for(const name of names){const o=new Option(name,name);$('clip').add(o);}for(const view of state.manifest.views)$('view').add(new Option(view,view));$('clip').value=names.includes('walk')?'walk':names[0];$('view').value=state.manifest.views[0];scale();await choose();state.ready=true;
}catch(e){fail(e);}
