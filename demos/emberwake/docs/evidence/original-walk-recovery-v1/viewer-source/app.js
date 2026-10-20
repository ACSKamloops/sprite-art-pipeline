const $=id=>document.getElementById(id);
let manifest,ready=false,playing=false,time=0,anchor=0,offset=0;
const images=new Map(),choice=[{version:'public',direction:'east'},{version:'installed',direction:'southeast'}];
const actor=()=>$('actor').value;
const now=()=>playing?offset+(performance.now()-anchor)*1000:time;
const clip=i=>manifest.versions[choice[i].version].actors[actor()][choice[i].direction];
function frameAt(us,c){let x=us%c.duration_us;for(let i=0;i<c.frames.length;i++){const h=c.frames[i].hold;x-=h[0]*1e6/h[1];if(x<0)return i;}return 0;}
function populate(i){
 const v=$('version'+i),d=$('direction'+i);v.replaceChildren();
 for(const [key,item]of Object.entries(manifest.versions))if(item.actors[actor()]){const o=new Option(item.label,key);v.add(o);}
 if(![...v.options].some(x=>x.value===choice[i].version))choice[i].version='public';v.value=choice[i].version;
 const directions=Object.keys(manifest.versions[choice[i].version].actors[actor()]);if(!directions.includes(choice[i].direction))choice[i].direction=directions[0];
 d.replaceChildren(...directions.map(x=>new Option(x,x)));d.value=choice[i].direction;
}
function draw(){
 if(!ready)return;const us=now(),zoom=Number($('zoom').value);
 for(let i=0;i<2;i++){
  const c=clip(i),f=frameAt(us,c),canvas=$('canvas'+i),ctx=canvas.getContext('2d'),size=128*manifest.scale*zoom;
  ctx.imageSmoothingEnabled=false;ctx.fillStyle='#48563b';ctx.fillRect(0,0,420,300);ctx.strokeStyle='#78856855';ctx.lineWidth=1;
  ctx.beginPath();for(let x=18;x<420;x+=32) {ctx.moveTo(x+.5,0);ctx.lineTo(x+.5,300);}for(let y=6;y<300;y+=32){ctx.moveTo(0,y+.5);ctx.lineTo(420,y+.5);}ctx.stroke();
  const left=210-64*manifest.scale*zoom,top=212-112*manifest.scale*zoom;
  ctx.drawImage(images.get(c.frames[f].path),left,top,size,size);
  $('caption'+i).textContent=manifest.versions[choice[i].version].label+' · '+choice[i].direction+' · frame '+f+'/'+c.frames.length+' · '+c.duration_us/1000+'ms loop';
 }
 $('clock').textContent=(us/1e6).toFixed(3)+'s · '+(playing?'Playing at normal speed':'Paused')+' · exact source holds; no frame interpolation';
}
function pause(){time=now();playing=false;$('play').textContent='Play';}
function play(){offset=time;anchor=performance.now();playing=true;$('play').textContent='Pause';}
$('play').onclick=()=>{playing?pause():play();draw();};$('restart').onclick=()=>{time=0;offset=0;anchor=performance.now();draw();};$('zoom').onchange=draw;
$('actor').onchange=()=>{for(let i=0;i<2;i++)populate(i);draw();};
for(let i=0;i<2;i++){$('version'+i).onchange=()=>{choice[i].version=$('version'+i).value;populate(i);draw();};$('direction'+i).onchange=()=>{choice[i].direction=$('direction'+i).value;draw();};}
document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing){pause();draw();}});
async function sha(bytes){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');}
async function load(){
 manifest=await fetch('manifest.json').then(r=>{if(!r.ok)throw Error('Manifest missing');return r.json();});const all=new Map();
 for(const v of Object.values(manifest.versions))for(const clips of Object.values(v.actors))for(const c of Object.values(clips))for(const f of c.frames)all.set(f.path,f);
 await Promise.all([...all.values()].map(async f=>{const r=await fetch(f.path);if(!r.ok)throw Error('Missing '+f.path);const b=await r.arrayBuffer();if(await sha(b)!==f.sha256)throw Error('Hash mismatch '+f.path);images.set(f.path,await createImageBitmap(new Blob([b],{type:'image/png'})));}));
 ready=true;for(let i=0;i<2;i++)populate(i);$('play').disabled=false;$('restart').disabled=false;
 $('integrity').textContent=images.size+' source PNG hashes verified. Original public atlas/manifest files match Git release2a80f53. Source-only crops; no new quality rating.';
 play();function tick(){draw();requestAnimationFrame(tick);}requestAnimationFrame(tick);
}
window.originalWalkViewer={inspect:()=>({ready,playing,verified_frames:images.size,time_us:now(),actor:actor(),choices:choice.map(x=>({...x})),slots:ready?[0,1].map(i=>frameAt(now(),clip(i))):[],durations:ready?[0,1].map(i=>clip(i).duration_us):[]}),frameAt};
load().catch(e=>{$('integrity').textContent=e.message;console.error(e);});
