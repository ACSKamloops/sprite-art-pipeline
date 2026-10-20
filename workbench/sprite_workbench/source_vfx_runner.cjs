// Local IPC adapter; all recipe methods below execute unchanged pinned factories.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const dir=path.join(__dirname,'vendor','vfx');
const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
const bindings=new Map(manifest.modules.map(x=>[x.id,x]));
const cache=new Map(),executed=[];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const sandbox={TextEncoder,TextDecoder,Uint8Array,Uint8ClampedArray,Uint16Array,Uint32Array,
 Int8Array,Int16Array,Int32Array,Float32Array,Float64Array,ArrayBuffer,DataView,Blob,Buffer};
sandbox.self={};sandbox.globalThis=sandbox;
const context=vm.createContext(sandbox);
function req(id){
 if(cache.has(id))return cache.get(id).exports;
 const binding=bindings.get(id);if(!binding)throw Error('Unprovided factory '+id);
 const code=fs.readFileSync(path.join(dir,binding.file));if(sha(code)!==binding.sha256)throw Error('Factory integrity failed '+id);
 const fn=new vm.Script('('+code.toString('utf8')+')',{filename:binding.file}).runInContext(context,{timeout:10000});
 const mod={exports:{}};cache.set(id,mod);executed.push(id);fn(mod,mod.exports,req);return mod.exports;
}
req.d=(target,defs)=>{for(const [key,get]of Object.entries(defs))if(!Object.hasOwn(target,key))Object.defineProperty(target,key,{enumerable:true,get});};
req.r=target=>{Object.defineProperty(target,'__esModule',{value:true});Object.defineProperty(target,Symbol.toStringTag,{value:'Module'});};
req.o=(o,k)=>Object.hasOwn(o,k);req.g=sandbox;
let input='';process.stdin.setEncoding('utf8');
process.stdin.on('data',d=>{input+=d;if(input.length>2*1024*1024)throw Error('Local source VFX JSON budget exceeded');});
process.stdin.on('end',()=>{try{
 const request=JSON.parse(input),api=req(47381);let value;
 if(request.action==='describe'){
  const schema=table=>Object.fromEntries(Object.entries(table).map(([key,[type,def,bounds]])=>
   [key,{type,required:typeof def==='symbol',default:typeof def==='symbol'?null:def,bounds}]));
  value={common:schema(api.CW),families:Object.fromEntries(Object.entries(api.Nk).map(([k,v])=>[k,schema(v)])),
   ramps:api.E5,presets:[],preset_status:'No original concrete recipe presets extracted; supply a recovered recipe.'};
 }else if(request.action==='validate')value={recipe:api.W$(request.recipe)};
 else if(request.action==='apply_controls'){
  const before=JSON.stringify(request.recipe),recipe=JSON.parse(before),values=request.values==null?{}:request.values;
  if(typeof values!=='object'||Array.isArray(values))throw Error('Local wrapper requires control values object');
  const ids=new Set((recipe.controls||[]).map(c=>c.id));
  for(const id of Object.keys(values))if(!ids.has(id))throw Error('Unknown control ID '+id);
  for(const control of recipe.controls||[])if(Object.hasOwn(values,control.id))control.value=values[control.id];
  const declared=api.W$(recipe);
  value={declared_recipe:recipe,normalized_recipe:declared,recipe:api.uY(declared),controls:declared.controls,
   caller_input_unchanged:before===JSON.stringify(request.recipe)};
 }
 else throw Error('Unsupported source VFX action');
 process.stdout.write(JSON.stringify({...value,executed_modules:executed,manifest_sha256:sha(fs.readFileSync(path.join(dir,'manifest.json')))}));
 }catch(error){process.stdout.write(JSON.stringify({status:'validation_error',reason:error.message}));process.exitCode=2;}});
