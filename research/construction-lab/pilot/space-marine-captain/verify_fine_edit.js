async (page) => {
  const output=__OUTPUT_DIR__;
  const started=Date.now();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8144/editor/');
  await page.waitForFunction(()=>window.SpriteEditor?.ready);
  await page.locator('#open-project').setInputFiles(__EDITABLE_PROJECT__);
  await page.waitForFunction(()=>SpriteEditor.getProject().frames.length===72,{},{timeout:60000});
  const loaded=await page.evaluate(()=>SpriteEditor.snapshot());
  const load_ms=Date.now()-started;
  const result=await page.evaluate(async()=>{
    const api=SpriteEditor,original=api.getProject(),frame=original.frames[0],layer='head';
    api.selectFrame(frame.id);api.selectLayer(layer);
    const cel=frame.cels[layer],pixels=original.cels[cel].pixels,w=256,rgba=api.renderRGBA(frame.id);
    let position=-1;
    for(let y=1;y<255&&position<0;y++)for(let x=1;x<255;x++){
      const i=y*w+x,index=pixels[i],color=original.palette[index];
      if(!index||color[3]!==255)continue;
      if(![-w-1,-w,-w+1,-1,1,w-1,w,w+1].every(d=>pixels[i+d]>0))continue;
      if(!color.every((v,k)=>rgba[i*4+k]===v))continue;
      position=i;break;
    }
    if(position<0)throw Error('No visible interior head pixel');
    const before=pixels[position],old=original.palette[before];
    let palette_index=-1,distance=Infinity;
    original.palette.forEach((color,index)=>{
      const d=color.slice(0,3).reduce((n,v,k)=>n+(v-old[k])**2,0);
      if(index&&color[3]===255&&d>0&&d<distance){distance=d;palette_index=index;}
    });
    const x=position%256,y=Math.floor(position/256);
    const initial=await api.snapshot();
    const editStart=performance.now();
    const transaction={schema:'sprite-edit-transaction/v1',expected_project_sha256:initial.project_sha256,
      reason:'Reversible one-pixel head highlight precision test; accepted art is not changed',
      operations:[{op:'paint',cel_id:cel,points:[[x,y,palette_index]],mask:[[x,y]]}]};
    const receipt=await api.applyTransaction(transaction),edited=await api.snapshot();
    const edit_ms=performance.now()-editStart;
    const canonical=api.renderRGBA(frame.id),actual=api.canvasRGBA();
    const expected=original.palette[palette_index];
    if(!expected.every((v,k)=>canonical[position*4+k]===v&&actual[position*4+k]===v))throw Error('Actual canvas differs from exact pixel edit');
    if(Object.keys(receipt.diff.cels).length!==1||receipt.diff.cels[cel].changed_pixels!==1)throw Error('Edit escaped its one-pixel mask');
    if(!Object.values(receipt.diff.frames).every(row=>row.changed_pixels===1&&row.coordinates[0][0]===x&&row.coordinates[0][1]===y))throw Error('Composite edit escaped coordinate');
    const affected=original.frames.filter(f=>Object.values(f.cels).includes(cel)).map(f=>f.id);
    if(!Object.keys(receipt.diff.frames).every(id=>affected.includes(id)))throw Error('Unbound frame changed');
    const journal=await api.exportJournal();
    await api.undo();if((await api.snapshot()).project_sha256!==initial.project_sha256)throw Error('Undo not exact');
    await api.redo();if((await api.snapshot()).project_sha256!==edited.project_sha256)throw Error('Redo not exact');
    await api.undo();
    const replay=await api.replayJournal(original,journal);
    if(replay.project_sha256!==edited.project_sha256)throw Error('Journal replay not exact');
    await api.undo();
    if((await api.snapshot()).project_sha256!==initial.project_sha256)throw Error('Final source restoration not exact');
    return{initial_hash:initial.project_sha256,edited_hash:edited.project_sha256,edit_ms,
      choice:{frame:frame.id,layer,cel,x,y,before,palette_index,expected,shared_bindings:affected},
      transaction,receipt,journal,actual_canvas_matches:true,undo_redo_replay_exact:true,
      restored_original:true,scope:'Exact one-pixel masked browser edit on complete72-frame9-layer14405-colour project; demonstrates precise editing, not added art points'};
  });
  await page.screenshot({path:output+'actual-editor.png',fullPage:true});
  const report={...result,load_ms,loaded,errors,passed:errors.length===0};
  const download=page.waitForEvent('download');
  await page.evaluate(r=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(r,null,2)],{type:'application/json'}));a.download='receipt.json';a.click();},report);
  await(await download).saveAs(output+'receipt.json');
  return{passed:report.passed,load_ms,edit_ms:result.edit_ms,restored_original:result.restored_original,changed_coordinate:[result.choice.x,result.choice.y],shared_bindings:result.choice.shared_bindings.length};
}
