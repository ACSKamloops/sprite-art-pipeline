'use strict';
// Offline real-Image/canvas oracle. Arguments: original asset, PNG directory, output directory.
// Uses retained full factory, never production slice offsets/manifest to recover definitions.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),cp=require('child_process');
const {chromium}=require(process.env.PIXELLAB_PLAYWRIGHT_CORE||'/home/astra/projects/openclaw-qgis-plugin/node_modules/openclaw/node_modules/playwright-core');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const [asset,directory,output]=process.argv.slice(2);if(!output)throw Error('asset, PNG directory and external output directory required');
 fs.mkdirSync(output,{recursive:true});
 const bytes=fs.readFileSync(asset);if(sha(bytes)!=='819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d')throw Error('Original asset mismatch');
 const registered=vm.createContext({self:{}});vm.runInContext(bytes.toString('utf8'),registered,{timeout:1000});
 const factory=registered.self.webpackChunk_N_E.flatMap(c=>Object.entries(c[1])).find(([id])=>id==='97981')[1].toString();
 if(sha(factory)!=='e9c6cb49052afbda45b9f16559a109f802dba299eab6fd3b166da3154188e0ee')throw Error('Factory mismatch');
 function part(start,end){const at=factory.indexOf(start);if(at<0||factory.indexOf(start,at+1)>=0)throw Error('Ambiguous source');const stop=factory.indexOf(end,at);if(stop<0)throw Error('Missing end');return factory.slice(at,stop)}
 const code=[part('tR=e=>{let t=e/255;',',tT='),part('tT=(e,t)=>Math.hypot(', ',tM='),part('tO=(e,t,a)=>"#"+',',tL='),part('S=async e=>{let t=Array.isArray(e)?e[0]:e,r=t.base64',',I=async()=>')].map(s=>'let '+s+';').join('\n');
 const browser=await chromium.launch({executablePath:process.env.PIXELLAB_CHROMIUM||'/home/astra/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage();let networkRequests=0;await page.route('**/*',route=>{networkRequests++;return route.abort()});await page.setContent('<!doctype html><title>Offline palette oracle</title>');
 const records=[];
 try{for(const file of fs.readdirSync(directory).filter(s=>s.endsWith('.png')).sort()){
  const png=fs.readFileSync(path.join(directory,file)),uri='data:image/png;base64,'+png.toString('base64');
  const observed=await page.evaluate(async({code,uri})=>{
   const outcome={colors:[],warning:null,error:null};
   const a={},i=value=>{outcome.colors=[...value.customColors]},u=()=>{},m=value=>{outcome.warning=value||null},_=value=>{outcome.error=String(value)};
   await eval('(async()=>{'+code+';await S({base64:uri});})()');
   const image=new Image();image.src=uri;await image.decode();const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const context=canvas.getContext('2d');context.drawImage(image,0,0);return{outcome,width:image.width,height:image.height,rgba:Array.from(context.getImageData(0,0,image.width,image.height).data)};
  },{code,uri});
  const rgba=Buffer.from(observed.rgba);fs.writeFileSync(path.join(output,file+'.canvas.rgba'),rgba);
  const run=cp.spawnSync(process.execPath,[path.resolve(__dirname,'../sprite_workbench/parity_palette_runner.cjs')],{input:JSON.stringify({width:observed.width,height:observed.height,rgba:rgba.toString('base64')}),encoding:'utf8'});if(run.status!==0)throw Error(run.stderr);const production=JSON.parse(run.stdout);
  const exact=JSON.stringify(production)===JSON.stringify(observed.outcome);if(!exact)throw Error('Real canvas mismatch '+file);
  records.push({file,png_sha256:sha(png),width:observed.width,height:observed.height,canvas_rgba_sha256:sha(rgba),canvas_rgba_file:file+'.canvas.rgba',outcome:observed.outcome,adapter_exact:exact});
 }
 const report={version:1,source_sha256:sha(bytes),factory_sha256:sha(factory),browser:browser.version(),network_requests:networkRequests,fixtures:records,boundary:'Real browser PNG canvas -> unchanged source handler; adapter receives canvas readback bytes, not assumed codec-equivalent raw RGBA.'};
 if(networkRequests)throw Error('Unexpected network');fs.writeFileSync(path.join(output,'browser-oracle.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({fixtures:records.length,all_exact:true,network_requests:networkRequests,browser:report.browser}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
