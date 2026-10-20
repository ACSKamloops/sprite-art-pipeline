'use strict';
// Trusted pinned source only. Canvas/Image are deterministic in-memory host boundaries.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto'),path=require('node:path');
const sha=value=>crypto.createHash('sha256').update(value).digest('hex');
const manifestBytes=fs.readFileSync(path.join(__dirname,'parity_palette_source.json'));
if(sha(manifestBytes)!=='a32ca0ece88e70b9199173f1af0e7ee0c1d1868ea3383df8cc652074565f0d3c')throw Error('Palette source manifest identity mismatch');
const manifest=JSON.parse(manifestBytes);
for(const part of manifest.parts)if(sha(part.text)!==part.sha256)throw Error('Palette original source slice mismatch');
const inputBytes=fs.readFileSync(0);if(inputBytes.length>1500000)throw Error('Palette request exceeds host byte budget');
const input=JSON.parse(inputBytes),rgba=Buffer.from(input.rgba,'base64');
if(!Number.isSafeInteger(input.width)||!Number.isSafeInteger(input.height)||Math.min(input.width,input.height)<1||input.width*input.height>262144||rgba.length!==input.width*input.height*4)throw Error('Palette RGBA dimensions/budget mismatch');
const result={colors:[],warning:null,error:null};
const context=vm.createContext({
  a:{},i:value=>{result.colors=Array.from(value.customColors);},u:()=>{},m:value=>{result.warning=value||null;},_:value=>{result.error=String(value);},
  window:{Image:class {constructor(){this.width=input.width;this.height=input.height;}set src(_value){this.onload();}}},
  document:{createElement:name=>{if(name!=='canvas')throw Error('Unexpected original DOM operation');return{getContext:()=>({drawImage:()=>{},getImageData:()=>({data:new Uint8ClampedArray(rgba)})})};}}
},{codeGeneration:{strings:false,wasm:false}});
const original=manifest.parts.map(p=>'let '+p.text+';').join('\n');
const pending=vm.runInContext(original+'\nS({base64:"data:image/png;base64,canvas-boundary"});',context,{timeout:5000});
Promise.resolve(pending).then(()=>process.stdout.write(JSON.stringify(result)),error=>{process.stderr.write(String(error));process.exitCode=1;});
