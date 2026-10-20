'use strict';

// Local host forms only. Every palette, pixel and footprint method runs on the
// source-pinned backend. This file implements no quantizer or source geometry.
window.ParityLabUI = class {
  constructor(api) {
    this.api=api; this.catalog=null; this.pending=false; this.epoch=0; this.target=null;
    this.$=id=>document.getElementById('parity-'+id);
    const click=(id,fn)=>this.$(id).addEventListener('click',()=>this.api.action(()=>this.run(fn)));
    click('input-preview-run',()=>this.previewInput()); click('refresh',()=>this.refresh()); click('palette-run',()=>this.palette());
    click('pixels-run',()=>this.pixels()); click('footprint-run',()=>this.footprint());
    click('workspace-refresh',()=>this.readWorkspace()); click('paint-run',()=>this.paint());
    this.$('upload').addEventListener('change',event=>{const file=event.target.files[0];if(file)this.api.action(()=>this.run(()=>this.upload(file)));});
    document.querySelectorAll('#view-parity input:not([type=file]), #view-parity select').forEach(field=>field.addEventListener('input',()=>{
      if(field.id!=='parity-paint-confirm')this.changed();
      this.sync();
    }));
    this.$('operation').addEventListener('change',()=>this.sync());
    this.$('shape').addEventListener('change',()=>this.sync());
    this.sync();
  }
  static id(value,label='Artifact') {
    if(typeof value!=='string'||!/^[0-9a-f]{64}$/.test(value.trim()))throw new Error(label+' must be a SHA256 artifact ID.');
    return value.trim();
  }
  id(field,label=field){return this.constructor.id(this.$(field).value,label);}
  integer(field,min,max){const raw=this.$(field).value,n=Number(raw);if(!raw.trim()||!Number.isSafeInteger(n)||n<min||n>max)throw new Error(field+' must be an integer in '+min+'..'+max+'.');return n;}
  pair(x,y,min,max){return[this.integer(x,min,max),this.integer(y,min,max)];}
  async enter(){if(!this.catalog)await this.run(()=>this.refresh());}
  pause(){}
  async run(fn){if(this.pending)return;this.pending=true;this.sync();try{return await fn();}finally{this.pending=false;this.sync();}}
  status(text){this.$('status').textContent=text;}
  changed(){this.epoch++;this.$('paint-confirm').checked=false;this.clearResult();this.status('Inputs changed. Run the desired operation again.');}
  clearResult(){this.$('input-preview').hidden=true;this.$('input-preview').removeAttribute('src');this.$('output').hidden=true;this.$('output').removeAttribute('src');this.$('output-id').textContent='';this.$('receipt-id').textContent='';this.$('swatches').replaceChildren();this.$('result-json').textContent='No current result.';this.$('result-label').textContent='Run an operation explicitly.';this.$('footprint-canvas').hidden=true;this.$('footprint-info').textContent='Preview shows coordinates only; original ordered points remain in the receipt.';}
  sync(){
    document.querySelectorAll('#view-parity button, #view-parity input[type=file]').forEach(e=>{e.disabled=this.pending;});
    const operation=this.$('operation').value;
    document.querySelectorAll('[data-parity-fields]').forEach(e=>{e.hidden=e.dataset.parityFields!==operation;});
    const notes={serialize:'Source serialization zeros hidden RGB at alpha 0. Output is a separate artifact; raw uploaded bytes stay retained.',transparency:'Tests for alpha exactly 0. Partial alpha alone does not mean this source method reports transparency.',reference_palette:'Original 64 × 64 reference-palette image: unique visible RGBA, x-major order, at most 4096 entries. This is not the private quantizer.',mask:'Output mask uses opaque black/white RGB. This differs from manual selection masks that encode selection in alpha.',decode:'Decode received bytes using the original client. Raw RGBA requires exact dimensions; valid PNG carries its own dimensions.',place:'Preserve-mask alpha > 0 copies source; alpha 0 protects destination. This is not the black/white request-mask convention.'};
    this.$('operation-note').textContent=notes[operation]||'';
    for(const id of ['extent-w','extent-h'])this.$(id).disabled=!this.$('use-extent').checked;
    const shape=this.$('shape').value;
    this.$('radius-label').hidden=!shape.startsWith('rounded-');
    this.$('thickness-label').hidden=!['ellipse-filled','rounded-rect-outline'].includes(shape);
    this.$('paint-run').disabled=this.pending||!this.target||!this.$('paint-confirm').checked;
  }
  async refresh(){const catalog=await this.api.invoke('local.parity.catalog',{});this.catalog=catalog;this.$('catalog').textContent=JSON.stringify(catalog,null,2);this.status('Source method catalog loaded. Operations run only when requested.');}
  async upload(file){
    if(!/\.png$/i.test(file.name)||file.size>32*1024*1024)throw new Error('Choose a PNG of at most 32 MiB.');
    this.changed();const epoch=this.epoch,target=this.$('upload-target').value;
    const response=await this.api.request('/api/upload',{method:'POST',headers:{'Content-Type':'image/png','X-Workbench-Filename':encodeURIComponent(file.name)},body:file});
    const result=response.result??response,sequence=this.constructor.id(result.sequence,'Uploaded sequence');
    const artifact=await this.api.request('/api/artifact/'+sequence);
    const raster=this.constructor.id(artifact.frames?.[0]?.raster,'First uploaded frame raster'),media=this.constructor.id(result.source_bytes,'Original PNG bytes');
    if(epoch!==this.epoch)return;
    this.$(target).value=raster;this.$('media').value=media;
    this.$('upload-info').textContent=`${file.name} · first-frame raster ${raster} · source bytes ${media} · sequence ${sequence}`;
    this.status('PNG retained. Only the selected raster field and decode-byte field were set; run an operation explicitly.');
  }
  previewInput(){const id=this.id('raster','Main raster');this.$('input-preview').src='/api/raster/'+id+'.png';this.$('input-preview').hidden=false;this.status('Previewing supplied raster '+id+'; no operation executed.');}
  show(result,label){
    this.$('footprint-canvas').hidden=true;
    this.$('result-label').textContent=label;this.$('result-json').textContent=JSON.stringify(result,null,2);
    let receiptLabel='';
    if(typeof result.receipt==='string')receiptLabel='Receipt: '+this.constructor.id(result.receipt);
    else if(result.receipt&&typeof result.receipt==='object'&&!Array.isArray(result.receipt))receiptLabel='Inline edit receipt (full result JSON)';
    else if(result.receipt!=null)throw new Error('Invalid returned receipt.');
    if(result.footprint)receiptLabel+=(receiptLabel?' · ':'')+'Footprint: '+this.constructor.id(result.footprint);
    this.$('receipt-id').textContent=receiptLabel;
    this.$('output').hidden=true;this.$('output').removeAttribute('src');this.$('output-id').textContent='';this.$('swatches').replaceChildren();
    if(result.output_raster){const id=this.constructor.id(result.output_raster);this.$('output').src='/api/raster/'+id+'.png';this.$('output').hidden=false;this.$('output-id').textContent='Output raster: '+id;}
  }
  async palette(){const epoch=this.epoch,raster=this.id('raster','Main raster');const result=await this.api.invoke('local.parity.palette',{raster});if(epoch!==this.epoch)return;this.show(result,'Shipped palette-image extraction');
    for(const color of result.colors||[]){if(!/^#[0-9a-f]{6}$/i.test(color))throw new Error('Invalid color in source result.');const swatch=document.createElement('span');swatch.className='parity-swatch';swatch.style.backgroundColor=color;swatch.title=color;swatch.setAttribute('aria-label',color);this.$('swatches').append(swatch);}
    this.status(result.accepted===false?'Original method rejected this input: '+result.error:(result.warning||'Original palette method completed. No image pixels were changed.'));
  }
  pixelRequest(){const operation=this.$('operation').value;let request;
    if(['serialize','transparency','reference_palette'].includes(operation))request={raster:this.id('raster')};
    else if(operation==='mask')request={mask:this.id('mask'),art:this.id('art'),fill_background:this.$('fill-background').checked,inpaint_empty_image:this.$('inpaint-empty').checked};
    else if(operation==='decode')request={media:this.id('media'),width:this.integer('width',1,512),height:this.integer('height',1,512)};
    else if(operation==='place'){request={source:this.id('source'),destination:this.id('destination'),origin:this.pair('origin-x','origin-y',-512,512)};if(this.$('use-extent').checked)request.extent=this.pair('extent-w','extent-h',1,512);if(this.$('preserve').value.trim())request.preserve_mask=this.id('preserve');}
    else throw new Error('Select a supported source pixel operation.');
    return{operation,request};
  }
  async pixels(){const args=this.pixelRequest(),epoch=this.epoch,result=await this.api.invoke('local.parity.pixels',args);if(epoch!==this.epoch)return;this.show(result,'Original pixel method: '+args.operation);this.status('Original pixel method completed. Inspect its receipt and mask/alpha convention.');}
  command(){const method=this.$('shape').value;if(!['ellipse-outline','ellipse-filled','rounded-rect-outline','rounded-rect-filled'].includes(method))throw new Error('Unsupported source footprint.');const cmd={method,pos:this.pair('x','y',-4096,4096),size:this.pair('shape-w','shape-h',1,128)};if(method.startsWith('rounded-'))cmd.radius=this.integer('radius',0,128);if(['ellipse-filled','rounded-rect-outline'].includes(method))cmd.thickness=this.integer('thickness',1,16);return cmd;}
  async footprint(){const command=this.command(),epoch=this.epoch,result=await this.api.invoke('local.parity.footprints',{commands:[command]});if(epoch!==this.epoch)return;this.show(result,'Original ordered footprint points');this.drawFootprint(result);this.status('Source footprint evaluated; no Workspace pixels were painted.');}
  drawFootprint(result){
    const rows=result.results||[],points=rows.flatMap(r=>r.points||[]);if(!points.length){this.$('footprint-info').textContent='The source returned no points.';return;}
    if(points.length>150000||points.some(p=>!Array.isArray(p)||p.length!==2||!p.every(Number.isSafeInteger)))throw new Error('Invalid or over-budget source points.');
    let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;for(const[x,y]of points){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
    const canvas=this.$('footprint-canvas'),ctx=canvas.getContext('2d'),scale=Math.min(8,(canvas.width-20)/(x1-x0+1),(canvas.height-20)/(y1-y0+1));ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle='#187d70';for(const[x,y]of points)ctx.fillRect(10+(x-x0)*scale,10+(y-y0)*scale,Math.max(1,scale),Math.max(1,scale));canvas.hidden=false;
    this.$('footprint-info').textContent=`${points.length} ordered points (duplicates retained in receipt), bounds [${x0},${y0}]..[${x1},${y1}]. Preview fits these bounds for inspection only; paint uses original coordinates.`;
  }
  async workspace(){const context=await this.api.workspaceContext?.();if(!context||context.busy)throw new Error('Open a ready editable Workspace cel first.');this.constructor.id(context.history,'Workspace history');if(typeof context.cel_id!=='string'||!context.cel_id||!Number.isSafeInteger(context.palette_index)||context.palette_index<0)throw new Error('Workspace needs an active cel and existing palette index.');return context;}
  async readWorkspace(){this.target=null;this.$('paint-confirm').checked=false;const context=await this.workspace();this.target={history:context.history,cel_id:context.cel_id,palette_index:context.palette_index,project:context.project};this.$('workspace').textContent=JSON.stringify(this.target,null,2);this.status('Workspace target captured. Confirm the displayed target before painting.');}
  async paint(){
    if(!this.target||!this.$('paint-confirm').checked)throw new Error('Read and explicitly confirm a Workspace target.');
    const current=await this.workspace();for(const key of ['history','cel_id','palette_index','project'])if(current[key]!==this.target[key]){this.target=null;this.$('paint-confirm').checked=false;throw new Error('Workspace changed. Read and confirm the current target again.');}
    const epoch=this.epoch,args={history:current.history,cel_id:current.cel_id,palette_index:current.palette_index,command:this.command()};
    const result=await this.api.invoke('local.parity.paint',args);this.target=null;this.$('paint-confirm').checked=false;
    if(epoch!==this.epoch){this.status('Paint completed for the captured target; inputs changed while it ran. Open the returned history from Methods.');this.$('result-json').textContent=JSON.stringify(result,null,2);return;}
    this.show(result,'Explicit recovered-footprint paint');this.status('Paint committed through guarded history. Shared-cel frame IDs, if any, are in the result.');await this.api.openEditor({project:this.constructor.id(result.project,'Result project'),history:this.constructor.id(result.history,'Result history')});
  }
};
