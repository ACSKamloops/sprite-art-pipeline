"""Replay actual Studio handoff/render methods; DOM and transport are isolated."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


REPLAY = r'''
const fs=require('fs'), assert=require('assert/strict');
global.window={};
(0,eval)(fs.readFileSync(process.argv[1],'utf8'));
const id=c=>c.repeat(64), frame={duration:[1,8],raster:id('a')};
const sequence={loop:false,play_count:1,canvas:[1,1],metadata:{},frames:[frame,frame]};
const context={project:id('c'),history:id('d'),source_sequence:id('b'),busy:false};
function host(order) {
 const nodes=new Map(); const o=Object.create(window.SpriteStudioUI.prototype);
 Object.assign(o,{epoch:0,frame:0,sourceId:null,sourceDocument:null,sourceImages:[],sourceFrameIds:null,
  selectionReceipts:[],order,
  api:{workspaceContext:()=>context,invoke:async()=>({sequence:id('a')}),request:async()=>sequence},
  $:key=>{if(!nodes.has(key))nodes.set(key,{});return nodes.get(key)},
  pause(){},invalidate(){this.epoch++},animation(){return{frames:this.order}},
  rasterImage:async()=>({naturalWidth:1,naturalHeight:1}),resetPosition(){},buildFrames(){},draw(){},identities(){},persist(){},clearReview(){},receipt(){},
  async hydrate(){this.project={canvas:{width:1,height:1}};await this.render()}});
 return o;
}
(async()=>{
 const adopted=host(['source-frame-1','source-frame-0']);
 await adopted.useWorkspace();
 assert.equal(Boolean(adopted.sourceAligned),false,'Workspace reorder cannot prove raw correspondence');
 assert.equal(adopted.sourceFrameIds,null,'no correspondence invented from current Workspace order');
 const imported=host(['source-frame-0','source-frame-1']);
 await imported.loadResult({...context,source_sequence:id('b'),sequence:id('a')},'fresh import','supplied holds');
 assert.equal(imported.sourceAligned,true,'fresh import establishes positional correspondence');
 assert.deepEqual(imported.sourceFrameIds,['source-frame-0','source-frame-1']);
 imported.order=['source-frame-1','source-frame-0']; await imported.render();
 assert.equal(Boolean(imported.sourceAligned),false,'subsequent reorder invalidates correspondence');
 assert.deepEqual(imported.sourceFrameIds,['source-frame-0','source-frame-1'],'original correspondence retained');
 console.log(JSON.stringify({workspace_adopted_reordered_aligned:Boolean(adopted.sourceAligned),fresh_import_aligned:true,subsequent_reordered_aligned:Boolean(imported.sourceAligned),scope:'actual useWorkspace/loadResult/render methods; mocked DOM and transport; no browser or art approval'}));
})().catch(error=>{console.error(error);process.exitCode=1});
'''


def test_reliable_studio_source_mapping_actual_methods():
    source = Path(os.environ.get('STUDIO_REVIEW_SOURCE', str(
        Path(__file__).resolve().parents[1] / 'sprite_workbench/web/studio.js')))
    if not source.exists():
        pytest.skip('Studio review target unavailable; set STUDIO_REVIEW_SOURCE')
    node = shutil.which('node')
    if not node:
        pytest.skip('Node unavailable; no executable UI method verification claimed')
    result = subprocess.run([node, '-e', REPLAY, str(source)], text=True,
                            capture_output=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(result.stdout)
    assert receipt['workspace_adopted_reordered_aligned'] is False
    assert receipt['fresh_import_aligned'] is True
    assert receipt['subsequent_reordered_aligned'] is False
