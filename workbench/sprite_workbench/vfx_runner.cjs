// Pinned recovered factory adapter. No browser bootstrap, service calls or DOM.
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
function raster(x){if(!x)return null;const data=Buffer.from(x.rgba_base64,'base64');
 if(data.length!==x.width*x.height*4)throw Error('InputRGBA length mismatch');
 return{width:x.width,height:x.height,data:new Uint8ClampedArray(data)};
}
let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',d=>{input+=d;if(input.length>64*1024*1024)throw Error('Input budget exceeded');});
process.stdin.on('end',()=>{
 try{
  const request=JSON.parse(input),images={};for(const [id,image]of Object.entries(request.images||{}))images[id]=raster(image);
  const out=req(manifest.entry)[manifest.export](request.recipe,raster(request.subject),images);
  const streams={};for(const key of ['frames','back','front'])streams[key]=out[key].map(a=>Buffer.from(a.buffer,a.byteOffset,a.byteLength).toString('base64'));
  process.stdout.write(JSON.stringify({status:'candidate',recipe:out.recipe,subjectBox:out.subjectBox,streams,executed,
   adapter:'pinned-website-factories-v1',manifest_sha256:sha(fs.readFileSync(path.join(dir,'manifest.json')))}));
 }catch(error){process.stdout.write(JSON.stringify({status:'validation_error',reason:error.message}));process.exitCode=2;}
});
