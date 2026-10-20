// Shared v1 contract implementation. Pure pixel operations; no DOM or canvas dependency.
export const clone = value => structuredClone(value);
export function canonical(value) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'number') { if (!Number.isFinite(value)) throw Error('Nonfinite JSON number'); return JSON.stringify(value); }
  if (Array.isArray(value)) { for(let i=0;i<value.length;i++)if(!Object.hasOwn(value,i))throw Error('Sparse arrays are not JSON data'); if(value.every(v=>typeof v==='number'&&Number.isFinite(v)))return JSON.stringify(value); return `[${value.map(canonical).join(',')}]`; }
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  throw Error('Not JSON data');
}
export async function sha(value) { const bytes = new TextEncoder().encode(canonical(value)); return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2,'0')).join(''); }
function integer(n, min, max, label) { if (!Number.isSafeInteger(n) || n < min || n > max) throw Error(`${label} must be an integer in ${min}..${max}`); }
function rgba(color) { if (!Array.isArray(color) || color.length !== 4) throw Error('RGBA needs four bytes'); for(const v of color)integer(v,0,255,'RGBA'); }
function point(p, width, height) { if (!Array.isArray(p) || p.length !== 2) throw Error('Coordinate needs [x,y]'); integer(p[0],0,width-1,'x'); integer(p[1],0,height-1,'y'); }
function exactKeys(op, keys, optional=[]) { const allowed = new Set([...keys,...optional]); if (Object.keys(op).some(k=>!allowed.has(k)) || keys.some(k=>!Object.hasOwn(op,k))) throw Error(`Invalid keys for ${op.op}`); }
export function validate(project) {
  if (!project || project.schema !== 'sprite-edit-project/v1') throw Error('Expected sprite-edit-project/v1');
  const c=project.canvas; if (!c) throw Error('Missing canvas'); integer(c.width,1,Number.MAX_SAFE_INTEGER,'Width'); integer(c.height,1,Number.MAX_SAFE_INTEGER,'Height'); if(c.width*c.height>16777216)throw Error('Canvas exceeds 16777216 pixels'); exactKeys(project,['schema','canvas','palette','layers','cels','frames','animations'],['provenance']); exactKeys(c,['width','height','render_pivot','ground_pivot']);
  for (const name of ['render_pivot','ground_pivot']) { if (!Array.isArray(c[name]) || c[name].length!==2 || c[name].some(v=>!Number.isSafeInteger(v))) throw Error(`Invalid ${name}`); }
  if (!Array.isArray(project.palette) || !project.palette.length) throw Error('Invalid palette'); for(const color of project.palette)rgba(color); if (canonical(project.palette[0]) !== '[0,0,0,0]') throw Error('Palette index0 must be transparent');
  if (!Array.isArray(project.layers)) throw Error('Invalid layers'); const layers=new Set();
  for (const l of project.layers) { exactKeys(l,['id','name','locked']); if (typeof l.id!=='string' || !l.id || layers.has(l.id) || typeof l.name!=='string' || !l.name || typeof l.locked!=='boolean') throw Error('Invalid layer'); layers.add(l.id); }
  if (!project.cels || typeof project.cels!=='object' || Array.isArray(project.cels)) throw Error('Missing cels');
  for (const [id,cel] of Object.entries(project.cels)) { exactKeys(cel,['layer_id','pixels']); if (!id || !layers.has(cel.layer_id) || !Array.isArray(cel.pixels) || cel.pixels.length!==c.width*c.height) throw Error(`Invalid cel ${id}`); for(const v of cel.pixels)integer(v,0,project.palette.length-1,'Pixel index'); }
  if (!Array.isArray(project.frames) || !project.frames.length) throw Error('Missing frames'); const frames=new Set();
  for (const f of project.frames) { exactKeys(f,['id','duration_ticks','cels','landmarks']); if (typeof f.id!=='string' || !f.id || frames.has(f.id)) throw Error('Invalid frame ID'); frames.add(f.id); integer(f.duration_ticks,1,Number.MAX_SAFE_INTEGER,'Hold'); if (!f.cels || typeof f.cels!=='object' || Array.isArray(f.cels)) throw Error('Invalid frame cels'); for (const [layer,id] of Object.entries(f.cels)) if (!layers.has(layer) || !project.cels[id] || project.cels[id].layer_id!==layer) throw Error('Frame cel/layer mismatch'); if(!f.landmarks || typeof f.landmarks!=='object' || Array.isArray(f.landmarks))throw Error('Invalid landmarks'); for (const [name,p] of Object.entries(f.landmarks)) if (!name || !Array.isArray(p) || p.length!==2 || p.some(v=>!Number.isSafeInteger(v))) throw Error('Invalid landmark'); }
  if (!Array.isArray(project.animations)) throw Error('Missing animations'); const animations=new Set();
  for (const a of project.animations) { exactKeys(a,['id','frames','fps','loop','events']); if (typeof a.id!=='string' || !a.id || animations.has(a.id)) throw Error('Invalid animation'); animations.add(a.id); if (!Array.isArray(a.frames) || !a.frames.length || Array.from(a.frames).some(f=>!frames.has(f)) || !Number.isFinite(a.fps) || a.fps<=0 || typeof a.loop!=='boolean' || !Array.isArray(a.events)) throw Error('Invalid animation fields'); const ticks=a.frames.reduce((sum,id)=>sum+project.frames.find(f=>f.id===id).duration_ticks,0); for (const e of a.events) { exactKeys(e,['at_tick','name']); integer(e.at_tick,0,ticks-1,'Event tick'); if (typeof e.name!=='string' || !e.name) throw Error('Invalid event name'); } }
  if(project.provenance!==undefined)canonical(project.provenance); return true;
}
export function render(project, frameID, onlyLayer=null) {
 const f=project.frames.find(f=>f.id===frameID); if (!f) throw Error('Unknown frame'); const out=new Uint8ClampedArray(project.canvas.width*project.canvas.height*4);
 for (const layer of project.layers) {
  if (onlyLayer && layer.id!==onlyLayer) continue; const cel=project.cels[f.cels[layer.id]]; if (!cel) continue;
  cel.pixels.forEach((index,i)=>{const src=project.palette[index],j=i*4,sa=src[3]; if(!sa)return; if(sa===255){out.set(src,j);return;} const da=out[j+3],n=sa*255+da*(255-sa); for(let k=0;k<3;k++)out[j+k]=Math.floor((src[k]*sa*255+out[j+k]*da*(255-sa)+Math.floor(n/2))/n);out[j+3]=Math.floor((n+127)/255);});
 }
 return out;
}
export function diff(before, after) {
 const cels={}; const frames={}; const w=before.canvas.width;
 for(const id of new Set([...Object.keys(before.cels),...Object.keys(after.cels)])){const a=before.cels[id]?.pixels||[],b=after.cels[id]?.pixels||[];const coords=[];for(let i=0;i<Math.max(a.length,b.length);i++)if(a[i]!==b[i])coords.push([i%w,Math.floor(i/w)]);if(coords.length)cels[id]={changed_pixels:coords.length,coordinates:coords};}
 for(const f of before.frames){const a=render(before,f.id),b=render(after,f.id),coords=[];for(let i=0;i<a.length;i+=4)if(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2]||a[i+3]!==b[i+3])coords.push([(i/4)%w,Math.floor(i/4/w)]);if(coords.length)frames[f.id]={changed_pixels:coords.length,coordinates:coords,bounds:coords.reduce((b,p)=>[Math.min(b[0],p[0]),Math.min(b[1],p[1]),Math.max(b[2],p[0]+1),Math.max(b[3],p[1]+1)],[w,before.canvas.height,0,0])};}
 return {cels,frames,unchanged_frames:before.frames.filter(f=>!frames[f.id]).map(f=>f.id)};
}
export async function transact(project,tx) {
 validate(project); if(!tx || tx.schema!=='sprite-edit-transaction/v1' || typeof tx.reason!=='string' || !tx.reason || !Array.isArray(tx.operations) || !tx.operations.length)throw Error('Invalid transaction'); exactKeys(tx,['schema','expected_project_sha256','reason','operations']); const beforeHash=await sha(project); if(tx.expected_project_sha256!==beforeHash)throw Error('Stale project hash; no edits applied'); const result=clone(project),w=project.canvas.width,h=project.canvas.height;
 const celTarget=id=>{const cel=result.cels[id];if(!cel)throw Error('Unknown cel');if(result.layers.find(l=>l.id===cel.layer_id).locked)throw Error('Layer is locked');return cel;};
 const makeMask=value=>{if(!Array.isArray(value))throw Error('Mask must be coordinate list');const result=new Set();for(const p of value){point(p,w,h);const i=p[1]*w+p[0];if(result.has(i))throw Error('Duplicate mask point');result.add(i);}return result;};
 const paletteIndex=n=>integer(n,0,result.palette.length-1,'Palette index');
 const shift=(cel,dx,dy,allow)=>{integer(dx,-Number.MAX_SAFE_INTEGER,Number.MAX_SAFE_INTEGER,'dx');integer(dy,-Number.MAX_SAFE_INTEGER,Number.MAX_SAFE_INTEGER,'dy');if(typeof allow!=='boolean')throw Error('allow_clip must be boolean');const pixels=new Array(w*h).fill(0);cel.pixels.forEach((v,i)=>{const x=i%w+dx,y=Math.floor(i/w)+dy;if(x<0||y<0||x>=w||y>=h){if(v&&!allow)throw Error('Translation would clip nontransparent pixels');}else pixels[y*w+x]=v;});cel.pixels=pixels;};
 for(const op of tx.operations){if(!op || typeof op.op!=='string')throw Error('Missing operation');switch(op.op){
 case 'paint': case 'erase': {exactKeys(op,['op','cel_id','points'],['mask']);const c=celTarget(op.cel_id);if(!Array.isArray(op.points))throw Error('No points');const allowed=op.mask===undefined?null:makeMask(op.mask);for(const p of op.points){if(!Array.isArray(p)||p.length!==(op.op==='paint'?3:2))throw Error('Invalid point');point(p.slice(0,2),w,h);if(allowed&&!allowed.has(p[1]*w+p[0]))throw Error('Stroke outside mask');const index=op.op==='erase'?0:p[2];paletteIndex(index);c.pixels[p[1]*w+p[0]]=index;}break;}
 case 'replace_color': {exactKeys(op,['op','cel_id','from_index','to_index','mask']);const c=celTarget(op.cel_id);paletteIndex(op.from_index);paletteIndex(op.to_index);for(const i of makeMask(op.mask)){if(c.pixels[i]===op.from_index)c.pixels[i]=op.to_index;}break;}
 case 'translate': {exactKeys(op,['op','cel_id','dx','dy'],['allow_clip']);shift(celTarget(op.cel_id),op.dx,op.dy,Object.hasOwn(op,'allow_clip')?op.allow_clip:false);break;}
 case 'translate_layer': {exactKeys(op,['op','layer_id','dx','dy'],['allow_clip']);const l=result.layers.find(l=>l.id===op.layer_id);if(!l)throw Error('Unknown layer');if(l.locked)throw Error('Layer is locked');for(const c of Object.values(result.cels))if(c.layer_id===l.id)shift(c,op.dx,op.dy,Object.hasOwn(op,'allow_clip')?op.allow_clip:false);break;}
 case 'palette': {exactKeys(op,['op','index','rgba']);paletteIndex(op.index);if(op.index===0)throw Error('Transparent entry is immutable');if(Object.values(result.cels).some(c=>result.layers.find(l=>l.id===c.layer_id).locked && c.pixels.includes(op.index)))throw Error('Palette index is used by a locked layer');rgba(op.rgba);result.palette[op.index]=clone(op.rgba);break;}
 case 'palette_add': {exactKeys(op,['op','rgba']);rgba(op.rgba);result.palette.push(clone(op.rgba));break;}
 case 'candidate_patch': {exactKeys(op,['op','cel_id','mask','candidate_pixels','expected_cel_sha256']);const c=celTarget(op.cel_id);if(await sha(c)!==op.expected_cel_sha256)throw Error('Stale cel hash');if(!Array.isArray(op.mask)||!Array.isArray(op.candidate_pixels)||op.candidate_pixels.length!==w*h)throw Error('Invalid patch');const mask=makeMask(op.mask);op.candidate_pixels.forEach((v,i)=>{paletteIndex(v);if(!mask.has(i)&&v!==c.pixels[i])throw Error('Candidate changes pixels outside allowed mask');});c.pixels=clone(op.candidate_pixels);break;}
 case 'frame_timing': {exactKeys(op,['op','frame_id','duration_ticks']);const f=result.frames.find(f=>f.id===op.frame_id);if(!f)throw Error('Unknown frame');integer(op.duration_ticks,1,Number.MAX_SAFE_INTEGER,'Hold');f.duration_ticks=op.duration_ticks;break;}
 case 'pivots': {exactKeys(op,['op','render_pivot','ground_pivot']);for(const name of ['render_pivot','ground_pivot']){if(!Array.isArray(op[name])||op[name].length!==2||op[name].some(v=>!Number.isSafeInteger(v)))throw Error('Invalid pivot');result.canvas[name]=clone(op[name]);}break;}
 default:throw Error(`Unsupported operation ${op.op}`);
 }}
 validate(result);return {project:result,receipt:{schema:'sprite-edit-receipt/v1',before_sha256:beforeHash,after_sha256:await sha(result),transaction:clone(tx),diff:diff(project,result)}};
}
