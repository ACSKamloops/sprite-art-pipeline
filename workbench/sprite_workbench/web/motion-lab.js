'use strict';

// Host workflow only: source PTS, declared local cuts and explicit provider actions.
window.MotionLabUI = class {
  static id(value) { if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) throw new Error('Expected a retained artifact ID.'); return value; }
  static validatedMediaBinding(value) {
    if(!value||typeof value!=='object'||Array.isArray(value))throw new Error('Downloaded media admission must include valid media and both receipt IDs.');
    return {media:this.id(value.media),native_video:this.id(value.native_video),download_receipt:this.id(value.download_receipt)};
  }
  static packetSnapshot(result, packet) {
    const statuses=['prepared','submission-attempted','accepted','submission-ambiguous','submission-failed','queued','running','succeeded','failed','cancelled'];
    const valid=result.packet===packet&&statuses.includes(result.status)&&[0,1].includes(result.submission_attempts)&&
      (result.task_id===null||(typeof result.task_id==='string'&&/^[A-Za-z0-9_-]{1,128}$/.test(result.task_id)));
    if(!valid)return {valid:false,ready:false,attempted:false,status:'unverified status',task:null};
    const attempted=result.submission_attempts===1||result.status!=='prepared'||result.task_id!==null;
    return {valid:true,ready:!attempted,attempted,status:result.status,task:result.task_id};
  }
  static json(value, label) { try { return JSON.parse(value); } catch { throw new Error(`${label} must be valid JSON.`); } }
  static pair(n, d) {
    if (d <= 0n || n <= 0n) throw new Error('A source-derived hold is not positive; use strictly increasing indices.');
    let a=n,b=d; while(b) [a,b]=[b,a%b]; n/=a; d/=a;
    if(n>BigInt(Number.MAX_SAFE_INTEGER)||d>BigInt(Number.MAX_SAFE_INTEGER)) throw new Error('Hold exceeds the browser exact-integer range.');
    return [Number(n),Number(d)];
  }
  constructor(api) {
    this.api=api; this.$=id=>document.getElementById('motion-'+id); this.epoch=0; this.pending=false; this.catalog=null;
    this.mediaBinding=null; this.mediaBindingError=null; this.extraction=null; this.sample=null; this.conditioned=null; this.packet=null; this.packetReady=false; this.submitted=[]; this.packetStates={}; this.playing=false; this.frame=0; this.elapsed=0; this.images=[]; this.previewEpoch=0; this.renderedFrame=null;
    this.formIds=['indices','holds','roles','loop','size','background','seed-x','seed-y','tolerance','palette','normalize','media','first','last','last-same','prompt','duration','resolution'];
    const click=(id,fn)=>this.$(id).addEventListener('click',()=>this.api.action(()=>this.run(fn)));
    click('load',()=>this.loadExample()); click('decode',()=>this.decode()); click('sample',()=>this.makeSample()); click('condition',()=>this.condition()); click('studio',()=>this.openStudio());
    click('source-holds',()=>this.sourceHolds()); click('neutral-roles',()=>{this.$('roles').value=JSON.stringify(this.indices().map(()=>'unlabelled pose'));this.invalidate('sample');});
    click('all-indices',()=>{this.requireExtraction();this.$('indices').value=JSON.stringify(this.extraction.frames.map((_,i)=>i));this.invalidate('sample');});
    click('add-index',()=>{const list=this.indices(true);list.push(Number(this.$('native-index').value));this.$('indices').value=JSON.stringify(list);this.invalidate('sample');});
    click('resume-packet',()=>this.resumePacket()); click('prepare',()=>this.prepare()); click('submit',()=>this.provider('submit')); click('poll',()=>this.provider('poll')); click('download',()=>this.provider('download'));
    this.$('play').addEventListener('click',()=>this.api.action(async()=>this.playing?this.pause():this.play()));
    this.$('restart').addEventListener('click',()=>this.api.action(async()=>{this.pause();this.elapsed=0;this.frame=0;this.showCandidate();this.play();}));
    this.$('native-index').addEventListener('input',()=>this.inspectNative());
    this.$('candidate-index').addEventListener('input',()=>this.renderCandidateFrame(Number(this.$('candidate-index').value)));
    this.$('video-file').addEventListener('change',event=>{const file=event.target.files[0];event.target.value='';if(file)this.api.action(()=>this.run(()=>this.uploadVideo(file)));});
    for(const which of ['first','last']) this.$(which+'-file').addEventListener('change',event=>{const file=event.target.files[0];event.target.value='';if(file)this.api.action(()=>this.run(()=>this.uploadPNG(which,file)));});
    for(const id of this.formIds) this.$(id).addEventListener('input',()=>{
      if(['indices','holds','roles','loop'].includes(id)) this.invalidate('sample');
      else if(['size','background','seed-x','seed-y','tolerance','palette'].includes(id)) this.invalidate('condition');
      else if(['first','last','last-same','prompt','duration','resolution'].includes(id)) this.invalidate('packet');
      else if(id==='media'){this.clearMediaBinding();this.detachNativeSource();this.invalidate('sample');}
      else {this.epoch++;this.persist();this.sync();}
    });
    document.addEventListener('visibilitychange',()=>{if(document.hidden)this.pause();});
    window.addEventListener('pagehide',()=>{this.pause();this.persist();});
    this.restore();this.sync();
  }
  async run(fn) {
    if(this.pending)return;this.pending=true;this.sync();
    try{return await fn();}catch(error){this.$('status').textContent=error.message;throw error;}finally{this.pending=false;this.sync();}
  }
  async enter() {
    if(this.pending)return;
    return this.run(async()=>{
      if(!this.catalog){this.catalog=await this.api.invoke('local.motion.catalog',{});this.$('example').replaceChildren();for(const e of this.catalog.examples||[]){const o=document.createElement('option');o.value=e.id;o.textContent=e.title;this.$('example').append(o);}
        this.$('methods').textContent=this.catalog.methods ? 'Registered methods: '+JSON.stringify(this.catalog.methods) : '';
        this.$('palette-reference').textContent='Palette reference: '+(this.catalog.palette_reference||'unavailable');
        this.$('live-status').textContent=this.catalog.live_provider_enabled?'Server permits explicit paid submission. Preparation does not submit.':'Live provider disabled. Local video workflow and packet preparation remain available.';
        if(this.savedExtraction){const id=this.savedExtraction;this.savedExtraction=null;await this.adoptExtraction({extraction:id,media_url:'/api/motion/media/'+id+'.mp4'},false);}
        if(this.savedCandidate){const id=this.savedCandidate;this.savedCandidate=null;await this.preview(id);}
      }
      this.sync();
    });
  }
  invoke(method,args){return this.api.invoke('local.motion.'+method,args);}
  receipt(value){this.$('receipt').textContent=JSON.stringify(value,null,2);}
  invalidate(scope) {
    this.epoch++;this.savedCandidate=null;this.pause();
    if(scope==='sample'){this.sample=null;this.conditioned=null;this.clearCandidate();}
    if(scope==='condition'){this.conditioned=null;this.clearCandidate();}
    if(scope==='packet'){this.packet=null;this.packetReady=false;this.$('packet-id').textContent='Request changed. Prepare a new packet.';}
    this.persist();this.sync();
  }
  clearCandidate(){this.previewEpoch++;this.images=[];this.renderedFrame=null;this.candidate=null;this.sequence=null;this.clock=null;this.$('candidate-frame').hidden=true;this.$('candidate-label').textContent='Candidate invalidated. Create a new sequence/draft for the current declarations.';this.$('candidate-clock').textContent='No current candidate.';}
  requireExtraction(){if(!this.extraction)throw new Error('Decode or load a native source first.');}
  indices(allowEmpty=false){this.requireExtraction();const a=this.constructor.json(this.$('indices').value,'Indices');if(!Array.isArray(a)||(!allowEmpty&&!a.length)||a.length>512||a.some(i=>!Number.isSafeInteger(i)||i<0||i>=this.extraction.frames.length))throw new Error('Choose 1–512 explicit indices inside this native source.');return a;}
  async loadExample(){this.clearMediaBinding();this.detachNativeSource();this.invalidate('sample');const epoch=this.epoch;const result=await this.invoke('load_example',{id:this.$('example').value});if(epoch!==this.epoch)return;await this.adoptExtraction(result,true);this.receipt(result);}
  clearMediaBinding(){this.mediaBinding=null;this.mediaBindingError=null;}
  detachNativeSource(){this.$('video').pause();this.$('video').removeAttribute('src');this.$('video').load();this.extraction=null;this.extractionId=null;this.savedExtraction=null;this.$('native-frame').hidden=true;this.$('native-info').textContent='Current media has not been decoded. Choose Decode video explicitly.';}
  async decode() {
    if(this.mediaBindingError)throw new Error(this.mediaBindingError);
    const media=this.constructor.id(this.$('media').value.trim()),args={media};
    if(this.mediaBinding){const binding=this.constructor.validatedMediaBinding(this.mediaBinding);if(binding.media!==media)throw new Error('Downloaded receipt binding belongs to another media blob. Choose the source again.');Object.assign(args,{native_video:binding.native_video,download_receipt:binding.download_receipt});}
    this.invalidate('sample');const epoch=this.epoch,result=await this.invoke('decode',args);if(epoch!==this.epoch)return;await this.adoptExtraction(result,true);this.receipt(result);
  }
  async uploadVideo(file){if(!file.size||file.size>64*1024*1024)throw new Error('Video must be at most 64 MiB.');const epoch=this.epoch;const reply=await this.api.request('/api/motion/upload',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:file});if(epoch!==this.epoch)return;const result=reply.result??reply,media=this.constructor.id(result.media);this.clearMediaBinding();this.detachNativeSource();this.invalidate('sample');this.$('media').value=media;this.persist();this.receipt(result);this.$('status').textContent='Video bytes retained. Choose Decode video to admit its frames.';}
  async validateDownloadBinding(result,packet) {
    const binding=this.constructor.validatedMediaBinding(result);
    const [native,receipt]=await Promise.all([this.api.request('/api/artifact/'+binding.native_video),this.api.request('/api/artifact/'+binding.download_receipt)]);
    if(native.kind!=='motion-native-video'||native.version!==1||receipt.kind!=='motion-media-download'||receipt.version!==1||native.video!==binding.media||receipt.video!==binding.media||native.packet!==packet||receipt.packet!==packet)
      throw new Error('Downloaded media receipts do not match the current packet and media; admission rejected.');
    return binding;
  }
  async adoptExtraction(result,reset) {
    const id=this.constructor.id(result.extraction),epoch=this.epoch,doc=await this.api.request('/api/artifact/'+id);if(epoch!==this.epoch)return;
    if(doc.kind!=='motion-extraction'||!Array.isArray(doc.frames)||!doc.frames.length||doc.frames.length>512)throw new Error('Invalid decoded extraction.');
    if(!reset&&this.$('media').value.trim()&&doc.media!==this.$('media').value.trim()){this.detachNativeSource();this.invalidate('sample');this.$('status').textContent='Stored preview belongs to another media. Decode the current media explicitly.';return;}
    if(this.mediaBinding&&this.mediaBinding.media!==doc.media)throw new Error('Decoded extraction disagrees with the downloaded media binding.');
    this.pause();this.extraction=doc;this.extractionId=id;
    if(reset){this.sample=null;this.conditioned=null;this.clearCandidate();for(const k of ['indices','holds','roles'])this.$(k).value='[]';this.$('loop').checked=false;}
    this.$('media').value=doc.media;this.$('video').src='/api/motion/media/'+id+'.mp4';
    this.$('native-index').max=doc.frames.length-1;this.$('native-index').value=0;
    this.$('native-info').textContent=`${doc.frames.length} native frames · ${doc.canvas.join(' × ')} · source duration ${doc.duration.join('/')} s · ${doc.native_clock}`;
    this.inspectNative();this.persist();this.$('status').textContent='Native source decoded. Choose explicit indices, holds and roles; no candidate is assumed.';
  }
  inspectNative(){if(!this.extraction)return;const i=Number(this.$('native-index').value),d=this.extraction,f=d.frames[i];if(!f)return;this.$('native-frame').src='/api/raster/'+this.constructor.id(f.raster)+'.png';this.$('native-frame').hidden=false;this.$('pts').textContent=`Native index ${i} · PTS ${d.pts[i]} × ${d.time_base.join('/')} s (origin ${d.pts_origin}) · native hold ${f.duration.join('/')} s`;}
  sourceHolds(){const indices=this.indices(),d=this.extraction;if(indices.some((v,i)=>i&&v<=indices[i-1]))throw new Error('Source-PTS holds require strictly increasing native indices.');
    if(![...d.pts,...d.time_base,...d.duration,d.pts_origin].every(Number.isSafeInteger))throw new Error('Source PTS exceeds exact browser integer limits.');
    const [bn,bd]=d.time_base.map(BigInt),[dn,dd]=d.duration.map(BigInt),origin=BigInt(d.pts_origin);
    const pairs=indices.map((i,n)=>n+1<indices.length?this.constructor.pair((BigInt(d.pts[indices[n+1]])-BigInt(d.pts[i]))*bn,bd):this.constructor.pair(dn*bd-(BigInt(d.pts[i])-origin)*bn*dd,dd*bd));
    this.$('holds').value=JSON.stringify(pairs);this.invalidate('sample');this.$('status').textContent='Source-PTS-derived pose holds declared. Omitted motion is represented by holding selected poses.';
  }
  async makeSample(){const args={extraction:this.extractionId,indices:this.indices(),holds:this.constructor.json(this.$('holds').value,'Holds'),roles:this.constructor.json(this.$('roles').value,'Roles'),loop:this.$('loop').checked},epoch=this.epoch;
    const result=await this.invoke('sample',args);if(epoch!==this.epoch)return;this.sample=result;this.conditioned=null;await this.preview(this.constructor.id(result.sequence));if(epoch!==this.epoch)return;this.receipt(result);this.persist();}
  async condition(){if(!this.sample)throw new Error('Create a sampled sequence first.');const args={sequence:this.sample.sequence,output_size:this.$('size').value==='native'?this.extraction.canvas:[256,256],background:{method:this.$('background').value},palette:{method:this.$('palette').value}};
    if(args.background.method!=='keep'){args.background.seed=[Number(this.$('seed-x').value),Number(this.$('seed-y').value)];args.background.tolerance=Number(this.$('tolerance').value);}
    if(args.palette.method!=='keep')args.palette.reference_raster=this.constructor.id(this.catalog.palette_reference);
    const epoch=this.epoch,result=await this.invoke('condition',args);if(epoch!==this.epoch)return;this.conditioned=result;await this.preview(this.constructor.id(result.sequence));if(epoch!==this.epoch)return;this.receipt(result);this.persist();}
  async rasterImage(id) {
    this.constructor.id(id);
    const image=new Image();
    await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('A candidate PNG could not be loaded.'));image.src='/api/raster/'+id+'.png';});
    await image.decode();
    return image;
  }
  async preview(id) {
    this.pause();this.clearCandidate();
    const epoch=this.epoch,ticket=this.previewEpoch;
    this.$('candidate-label').textContent='Loading and decoding every candidate frame before playback…';this.sync();
    const d=await this.api.request('/api/artifact/'+id);
    if(epoch!==this.epoch||ticket!==this.previewEpoch)return;
    const clock=window.SpriteStudioUI.clock(d),[width,height]=d.canvas||[];
    if(![width,height].every(v=>Number.isSafeInteger(v)&&v>0)||!Number.isSafeInteger(width*height*d.frames.length)||width*height*d.frames.length>16777216)
      throw new Error('Candidate preview exceeds the 16M total-pixel limit. Select fewer poses or create a 256 × 256 conditioned draft first. No frames were removed.');
    // Repeated raster IDs share one decoded image, but every ordered frame/hold is retained.
    const unique=new Map();
    let images;
    try{images=await Promise.all(d.frames.map(f=>{this.constructor.id(f.raster);if(!unique.has(f.raster))unique.set(f.raster,this.rasterImage(f.raster));return unique.get(f.raster);}));}
    catch(error){if(epoch!==this.epoch||ticket!==this.previewEpoch)return;throw error;}
    if(epoch!==this.epoch||ticket!==this.previewEpoch)return;
    if(images.some(image=>image.naturalWidth!==width||image.naturalHeight!==height))throw new Error('Candidate PNG dimensions disagree with its full canvas.');
    this.images=images;this.sequence=d;this.candidate=id;this.clock=clock;this.frame=0;this.elapsed=0;
    this.$('candidate-index').max=d.frames.length-1;
    this.$('candidate-label').textContent=(this.conditioned?'Conditioned local draft':'Sampled source pixels')+` · ${d.canvas.join(' × ')} · ${d.frames.length} poses · ${id} · all frames decoded · visual acceptance unreviewed`;
    this.showCandidate();this.persist();this.sync();
  }
  showCandidate() {
    if(!this.sequence||!this.images[this.frame])return;
    const f=this.sequence.frames[this.frame],canvas=this.$('candidate-frame'),[width,height]=this.sequence.canvas;
    if(canvas.width!==width)canvas.width=width;if(canvas.height!==height)canvas.height=height;
    const context=canvas.getContext('2d');context.imageSmoothingEnabled=false;context.clearRect(0,0,width,height);context.drawImage(this.images[this.frame],0,0);
    this.renderedFrame=this.frame;canvas.dataset.renderedFrame=String(this.frame);canvas.hidden=false;
    this.$('candidate-index').value=this.frame;
    this.$('candidate-clock').textContent=`Pose ${this.frame+1}/${this.sequence.frames.length} · declared hold ${f.duration.join('/')} s · ${this.sequence.loop?'authored loop':'authored one-shot'} · total ${this.clock.total/1000} s`;
  }
  renderCandidateFrame(index) {
    if(!this.sequence||!Number.isSafeInteger(index)||index<0||index>=this.images.length)return false;
    this.pause();this.frame=index;this.elapsed=this.clock.holds.slice(0,index).reduce((a,b)=>a+b,0);this.showCandidate();return true;
  }
  getPreviewState() {
    return {candidate:this.candidate||null,frame:this.frame,rendered_frame:this.renderedFrame,playing:this.playing,elapsed_ms:this.playing?this.elapsed+performance.now()-this.started:this.elapsed,loaded_frames:this.images.length,
      holds:this.sequence?this.sequence.frames.map(f=>[...f.duration]):[],canvas:this.sequence?[...this.sequence.canvas]:null};
  }
  pause(){if(this.playing)this.elapsed+=performance.now()-this.started;this.playing=false;if(this.handle)cancelAnimationFrame(this.handle);this.handle=null;if(this.$('video'))this.$('video').pause();this.sync();}
  play(){if(this.pending||!this.sequence)return;if(this.elapsed>=this.clock.end)return;this.playing=true;this.started=performance.now();const epoch=this.epoch;const tick=now=>{if(!this.playing||epoch!==this.epoch)return;const p=window.SpriteStudioUI.frameAt(this.clock,this.elapsed+now-this.started);if(this.frame!==p.index){this.frame=p.index;this.showCandidate();}if(p.ended){this.elapsed=this.clock.end;this.playing=false;this.handle=null;this.sync();return;}this.handle=requestAnimationFrame(tick);};this.handle=requestAnimationFrame(tick);this.sync();}
  async openStudio(){if(!this.candidate)throw new Error('Create a current candidate first.');this.pause();const epoch=this.epoch,result=await this.api.invoke('local.studio.from_sequence',{sequence:this.candidate,animation_id:'motion-clip',normalize_hidden_rgb:this.$('normalize').checked});if(epoch!==this.epoch)return;await this.api.openStudio(result);this.receipt(result);}
  async uploadPNG(which,file){if(!/\.png$/i.test(file.name)||file.size>32*1024*1024)throw new Error('Choose a PNG of at most32 MiB.');this.invalidate('packet');const epoch=this.epoch,reply=await this.api.request('/api/upload',{method:'POST',headers:{'Content-Type':'image/png','X-Workbench-Filename':encodeURIComponent(file.name)},body:file});if(epoch!==this.epoch)return;const result=reply.result??reply;this.$(which).value=this.constructor.id(result.source_bytes);this.receipt(result);this.persist();}
  rememberPacket(packet,status) {
    this.submitted=[...this.submitted.filter(id=>id!==packet),packet].slice(-32);this.packetStates[packet]=status.slice(0,80);
  }
  async prepare() {
    const first=this.constructor.id(this.$('first').value.trim()),args={first_png:first,prompt:this.$('prompt').value,duration:Number(this.$('duration').value),resolution:this.$('resolution').value};
    if(!args.prompt.trim())throw new Error('Write a nonblank literal motion prompt.');
    if(this.$('last-same').checked)args.last_png=first;else if(this.$('last').value.trim())args.last_png=this.constructor.id(this.$('last').value.trim());
    this.packetReady=false;
    const epoch=this.epoch,result=await this.invoke('prepare',args);if(epoch!==this.epoch)return;
    this.packet=this.constructor.id(result.packet);
    const state=this.constructor.packetSnapshot(result,this.packet);
    this.packetReady=state.ready&&!this.submitted.includes(this.packet);
    if(state.attempted)this.rememberPacket(this.packet,state.status+(state.task?' · task '+state.task:''));
    this.$('packet-id').textContent=`${state.attempted?'Existing immutable run':'Packet'} · ${state.status}${state.task?' · task '+state.task:''} · ${this.packet}`;
    this.$('status').textContent=state.attempted?'Existing run found. It was not submitted again. Poll or download explicitly.':state.valid?'Request prepared without submission. Submit only if intended.':'Packet retained, but safe status is unavailable. Refresh it with Prepare before submitting.';
    this.receipt(result);this.persist();this.sync();
  }
  async resumePacket(){const packet=this.constructor.id(this.$('packet-history').value);if(!this.submitted.includes(packet))throw new Error('Choose a retained submitted packet.');const epoch=this.epoch,document=await this.api.request('/api/artifact/'+packet);if(epoch!==this.epoch)return;this.packet=packet;this.packetReady=false;this.$('packet-id').textContent='Resumed immutable submitted packet (editable draft above is separate): '+packet;this.receipt(document);this.persist();}
  async provider(method){if(!this.packet)throw new Error('Prepare the current request first.');const packet=this.packet,epoch=this.epoch;if(method==='submit'){if(!this.packetReady)throw new Error('Refresh the current packet with Prepare; only a verified unattempted state may submit.');if(!this.catalog?.live_provider_enabled)throw new Error('Live provider is disabled on this server.');if(this.submitted.includes(packet))throw new Error('Submission was already attempted for this packet. Poll it; no automatic retry.');this.packetReady=false;this.rememberPacket(packet,'submission attempted');this.persist();}
    const result=await this.invoke(method,{packet});if(epoch!==this.epoch)return;let binding=null;if(method==='download'){try{binding=await this.validateDownloadBinding(result,packet);}catch(error){if(epoch!==this.epoch)return;throw error;}if(epoch!==this.epoch)return;}const status=typeof result.state==='string'?result.state:typeof result.state?.status==='string'?result.state.status:typeof result.status==='string'?result.status:null;this.packetStates[packet]=(method+' returned'+(status?': '+status:'')).slice(0,80);this.persist();this.receipt(result);this.$('status').textContent=`Explicit ${method} returned. Inspect the receipt; nothing else is automatically requested.`;if(method==='download'){this.detachNativeSource();this.invalidate('sample');this.mediaBinding=binding;this.mediaBindingError=null;this.$('media').value=binding.media;this.persist();this.$('status').textContent='Returned video retained. Choose Decode video to inspect it.';}this.sync();}
  persist(){const form={};for(const id of this.formIds)form[id]=this.$(id).type==='checkbox'?this.$(id).checked:this.$(id).value;try{localStorage.setItem('sprite-workbench.motion.v1',JSON.stringify({form,mediaBinding:this.mediaBinding,mediaBindingError:this.mediaBindingError,extraction:this.extractionId,sample:this.sample,conditioned:this.conditioned,candidate:this.candidate,packet:this.packet,submitted:this.submitted,packetStates:Object.fromEntries(this.submitted.map(id=>[id,this.packetStates[id]||'status not retained']))}));}catch{this.$('status').textContent='Browser restore unavailable; keep the receipt/artifact IDs.';}}
  restore(){try{const d=JSON.parse(localStorage.getItem('sprite-workbench.motion.v1')||'null');if(!d)return;for(const id of this.formIds)if(Object.hasOwn(d.form||{},id)){if(this.$(id).type==='checkbox')this.$(id).checked=d.form[id]===true;else this.$(id).value=String(d.form[id]);}if(d.mediaBindingError){this.mediaBindingError='Stored download binding is malformed or belongs to another media. Choose the source again or re-download before decoding.';this.$('status').textContent=this.mediaBindingError;}if(d.mediaBinding!=null){try{const binding=this.constructor.validatedMediaBinding(d.mediaBinding);if(binding.media!==this.$('media').value.trim())throw new Error('wrong media');this.mediaBinding=binding;}catch{this.mediaBinding=null;this.mediaBindingError='Stored download binding is malformed or belongs to another media. Choose the source again or re-download before decoding.';this.$('status').textContent=this.mediaBindingError;}}this.savedExtraction=d.extraction?this.constructor.id(d.extraction):null;this.sample=d.sample;this.conditioned=d.conditioned;this.savedCandidate=d.candidate?this.constructor.id(d.candidate):null;this.packet=d.packet?this.constructor.id(d.packet):null;this.submitted=Array.isArray(d.submitted)?[...new Set(d.submitted.filter(v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v)))].slice(-32):[];this.packetStates=Object.fromEntries(this.submitted.map(id=>[id,typeof d.packetStates?.[id]==='string'?d.packetStates[id].slice(0,80):'status not retained']));if(this.packet)this.$('packet-id').textContent=(this.submitted.includes(this.packet)?'Submitted immutable packet (editable draft may differ): ':'Stored packet · Prepare again to refresh safe status: ')+this.packet;}catch{this.savedExtraction=null;this.savedCandidate=null;this.packet=null;this.sample=null;this.conditioned=null;}}
  sync(){const selected=this.$('packet-history').value;this.$('packet-history').replaceChildren(...this.submitted.map(id=>{const o=document.createElement('option');o.value=id;o.title=id;o.textContent=id.slice(0,12)+'…'+id.slice(-8)+' · '+(this.packetStates[id]||'status not retained');return o;}));if(this.submitted.includes(selected))this.$('packet-history').value=selected;
    for(const el of document.querySelectorAll('#view-motion input,#view-motion textarea,#view-motion select,#view-motion button'))el.disabled=this.pending;
    for(const id of ['load'])this.$(id).disabled=this.pending||!this.catalog?.examples?.length;
    for(const id of ['native-index','add-index','all-indices','source-holds','neutral-roles','sample'])this.$(id).disabled=this.pending||!this.extraction;
    this.$('decode').disabled=this.pending||Boolean(this.mediaBindingError);this.$('condition').disabled=this.pending||!this.sample;for(const id of ['play','restart','candidate-index','studio'])this.$(id).disabled=this.pending||!this.candidate;
    this.$('play').textContent=this.playing?'Pause candidate':this.clock&&this.elapsed>=this.clock.end?'Completed · use Restart':'Play candidate';
    this.$('last').disabled=this.pending||this.$('last-same').checked;this.$('last-file').disabled=this.$('last').disabled;
    this.$('submit').disabled=this.pending||!this.packet||!this.packetReady||!this.catalog?.live_provider_enabled||this.submitted.includes(this.packet);
    for(const id of ['packet-history','resume-packet'])this.$(id).disabled=this.pending||!this.submitted.length;
    for(const id of ['poll','download'])this.$(id).disabled=this.pending||!this.packet||!this.submitted.includes(this.packet);
  }
};
