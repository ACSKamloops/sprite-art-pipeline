// Execute the exact original enhancer function, with synthetic lexical/HTTP host.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const input=JSON.parse(fs.readFileSync(0,'utf8')),calls=[],events=[],messages=[];
const context=vm.createContext({c:{access_token:'OFFLINE-NOT-A-CREDENTIAL'},s:x=>messages.push(x),
 i:x=>events.push(['loading',x]),l:async url=>{calls.push({converted_url:url});return 'data:image/png;base64,AA==';},
 n:{J:x=>typeof x==='string'?x:null},e:{onSuccess:(...args)=>events.push(['success',...args])},
 fetch:async(url,options)=>{calls.push({url,body:JSON.parse(options.body)});return{ok:true,json:async()=>({enhanced_prompt:'enhanced action',caption:{view:'side'}})};}});
const original=new vm.Script('('+input.source+')').runInContext(context),cases=[];
(async()=>{
 let value=await original('data:image/png;base64,AA==','  walk  ',undefined,{});
 assert.equal(value,'enhanced action');assert.equal(calls[0].body.prompt,'  walk  ');assert.equal(calls[0].body.engine,'v3');
 assert.equal(Object.hasOwn(calls[0].body,'image_base64_end'),false);assert.deepEqual(events.map(x=>x[0]),['loading','success','loading']);cases.push('literal_prompt_default_engine_callback_finally');
 calls.length=0;events.length=0;
 await original('https://example.invalid/first.png','slash','https://example.invalid/last.png',
  {engine:'pixminimax',frameCount:16,subjectDescription:'hero',initialPose:'ready',view:'side',direction:'east',improveFields:[]});
 assert.equal(calls.filter(x=>x.converted_url).length,2);const request=calls.at(-1).body;
 assert.equal(request.frame_count,16);assert.equal(request.subject_description,'hero');assert.equal(request.initial_pose,'ready');assert.equal(request.image_base64_end,'data:image/png;base64,AA==');assert.equal(request.improve_fields.length,0);cases.push('first_last_and_caption_field_mapping');
 calls.length=0;await original('data:fake','walk',null,{engine:'',frameCount:12.5,direction:'Auto'});
 assert.equal(calls[0].body.engine,'');assert.equal(calls[0].body.frame_count,12.5);assert.equal(calls[0].body.direction,'Auto');cases.push('helper_does_not_supply_enum_integer_validation');
 calls.length=0;context.c=null;assert.equal(await original('data:fake','walk'),null);assert.equal(calls.length,0);cases.push('missing_auth_is_local_rejection_with_synthetic_context');
 context.c={access_token:'OFFLINE-NOT-A-CREDENTIAL'};assert.equal(await original('data:fake',' \n\t'),null);assert.equal(calls.length,0);cases.push('blank_prompt_is_local_rejection');
 process.stdout.write(JSON.stringify({passed:true,cases,authority:'controlled replay of original function with synthetic lexical host; no React/HTTP/backend execution',source_sha256:crypto.createHash('sha256').update(input.source).digest('hex')}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
