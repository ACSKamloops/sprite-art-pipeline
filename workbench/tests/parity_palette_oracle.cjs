'use strict';
// Independent oracle: register the full retained webpack asset, locate its factory,
// then obtain original lexical definitions by unique literals, not production offsets.
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const input=JSON.parse(fs.readFileSync(0,'utf8')),bytes=fs.readFileSync(process.argv[2]);
if(sha(bytes)!=='819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d')throw Error('Original asset mismatch');
const registered=vm.createContext({self:{}});vm.runInContext(bytes.toString('utf8'),registered,{timeout:1000});
const factory=registered.self.webpackChunk_N_E.flatMap(chunk=>Object.entries(chunk[1])).find(([id])=>id==='97981')[1].toString();
if(sha(factory)!=='e9c6cb49052afbda45b9f16559a109f802dba299eab6fd3b166da3154188e0ee')throw Error('Original factory mismatch');
function part(start,end){const at=factory.indexOf(start);if(at<0||factory.indexOf(start,at+1)>=0)throw Error('Ambiguous source anchor');const stop=factory.indexOf(end,at);if(stop<0)throw Error('Missing source end');return factory.slice(at,stop);}
const definitions=[part('tR=e=>{let t=e/255;',',tT='),part('tT=(e,t)=>Math.hypot(', ',tM='),part('tO=(e,t,a)=>"#"+',',tL='),part('S=async e=>{let t=Array.isArray(e)?e[0]:e,r=t.base64',',I=async()=>')];
const outcome={colors:[],warning:null,error:null};
const sandbox={a:{},i:state=>{outcome.colors=[...state.customColors]},u:()=>{},m:value=>{outcome.warning=value||null},_:value=>{outcome.error=String(value)},document:{createElement:()=>({getContext:()=>({drawImage(){},getImageData(){return{data:Uint8ClampedArray.from(input.rgba)}}})})},window:{Image:class{constructor(){this.width=input.width;this.height=input.height}set src(value){this.onload()}}}};
const context=vm.createContext(sandbox);const promise=vm.runInContext(definitions.map(s=>'let '+s+';').join('\n')+'\nS([{base64:"canvas-fixture"}]);',context,{timeout:5000});
Promise.resolve(promise).then(()=>process.stdout.write(JSON.stringify(outcome)));
