#!/usr/bin/env python3
"""Exercise an installed Motion package offline, outside its source checkout.

Pass an absent output directory. This admits packaged recorded media, never
submits a provider job, and never approves art. Run with the installed Python.
"""
import argparse
from fractions import Fraction
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import urllib.request

import numpy as np

import sprite_workbench
from sprite_workbench.core import Store, ValidationError, load_sequence, digest
from sprite_workbench import motion_workflow as motion, motion_frames, construction, selection, studio
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.pipeline import execute_plan
from sprite_workbench.readiness import source_fingerprint
from sprite_workbench.channel import serve
from sprite_workbench.web_server import ControlServer


def verify(output):
    output.mkdir(parents=True, exist_ok=False)
    report = {'kind':'installed-motion-proof','version':1,
        'package_version':sprite_workbench.__version__,
        'package':str(Path(sprite_workbench.__file__).resolve().parent),
        'source_fingerprint':source_fingerprint(), 'provider_calls':0,
        'visual_acceptance':'unreviewed','checks':[]}
    def check(name, condition, **detail):
        if not condition:
            raise AssertionError(name)
        report['checks'].append({'id':name,'status':'passed',**detail})
    store=Store(output/'store')
    # Any accidental in-process credential lookup fails the proof.
    motion.credentials=lambda: (_ for _ in ()).throw(AssertionError('unexpected credentials'))
    catalog=motion.catalog(store)
    check('packaged_native_examples',len(catalog['examples'])==3 and not catalog['live_provider_enabled'])
    native=motion.load_example(store,'native-slash-margin')
    extraction=store.get_json(native['extraction'])
    check('actual_native_clock',native['frame_count']==107 and native['duration']==[107,24]
        and all(f['duration']==[1,24] for f in extraction['frames']))
    check('pts_kept_per_frame', [f['pts']for f in extraction['frames']]==extraction['pts'])
    indices=[0,12,18,23,24,25,26,27,28,35,52,73,78,85,94,106]
    ticks=[3,3,3,3,1,1,1,1,3,3,3,3,5,5,5,5]
    request={'extraction':native['extraction'],'indices':indices,
        'holds':[[v,60]for v in ticks],'roles':['authored inspection pose']*16,'loop':False}
    sampled=motion_frames.sample_frames(store,**request)
    source=store.get_json(sampled['sequence'])
    check('explicit_fast_strike_frames',source['frames'][6]['raster']==extraction['frames'][26]['raster']
        and source['frames'][7]['raster']==extraction['frames'][27]['raster'])
    check('authored_clock_separate',sampled['duration']==[4,5] and native['duration']==[107,24])
    plan=execute_plan(store,{'version':1,'steps':[{'id':'poses','action':'motion','method':'sample','request':request}]},base_dir=output)
    check('plan_preserves_canonical_sequence_id',plan['status']=='completed' and plan['results']['poses']['sequence']==sampled['sequence'])
    conditioned=motion.condition(store,sampled['sequence'],output_size=[256,256],
        background={'method':'recovered-host-selection','seed':[0,0],'tolerance':.06},
        palette={'method':'calibrated-fixed','reference_raster':catalog['palette_reference']})
    doc,arrays=load_sequence(store,conditioned['sequence'])
    receipt=store.get_json(conditioned['conditioning'])
    check('actual_recovered_masks',all(row['selection']for row in receipt['frames'])
        and all(store.get_json(row['selection'])['execution']['source_image_unchanged']for row in receipt['frames']))
    check('holds_and_order_preserved', [f['duration']for f in doc['frames']]==[f['duration']for f in source['frames']])
    check('fixed_palette_alpha_recorded',receipt['palette_entries']==77
        and all(row['palette_preserves_all_alpha']for row in receipt['frames']))
    # Export closure must include unsampled native frames, not just chosen poses.
    export_sequence(store,conditioned['sequence'],output/'portable',formats=['editable','apng','godot'])
    cold=Store(output/'cold-store');imported=import_editable(cold,output/'portable/editable')
    check('cold_editable_identity',imported==conditioned['sequence'])
    check('cold_unsampled_native_frame',np.array_equal(cold.get_raster(extraction['frames'][1]['raster']),store.get_raster(extraction['frames'][1]['raster'])))
    check('cold_native_media_and_mask',cold.get_bytes(native['media'])==store.get_bytes(native['media'])
        and np.array_equal(cold.get_raster(receipt['frames'][0]['mask_raster']),store.get_raster(receipt['frames'][0]['mask_raster'])))
    check('cold_native_fixture_request_and_reference',len(extraction['source_bindings'])==3
        and all(cold.get_bytes(ident)==store.get_bytes(ident)for ident in extraction['source_bindings']))
    session=studio.from_sequence(store,conditioned['sequence'],animation_id='diagnostic',normalize_hidden_rgb=True)
    project=construction.load_project(store,session['project'])
    cel=next(iter(project['frames'][0]['cels'].values()))
    picked=selection.create_selection(store,session['project'],cel,[128,128],0)
    edit=selection.apply_selection(store,session['history'],picked['selection'],'erase')
    undone=construction.move_history(store,edit['history'],'undo')
    redone=construction.move_history(store,undone['history'],'redo')
    check('precise_edit_undo_redo',edit['changed_indices']>0 and undone['project']==session['project'] and redone['project']==edit['project'])
    check('edit_receipt_replayed',selection.validate_edit_receipt(store,edit['selection_receipt'])['outside_indices_and_rgba_preserved'])
    # Prepare is offline, and reopening must return the real retained state.
    png=store.put_bytes((motion.EXAMPLES/'native-slash-margin/source.png').read_bytes())
    packet=motion.prepare(store,first_png=png,prompt='Offline proof only',base_dir=output)
    check('offline_prepare_safe_state',packet['status']=='prepared' and packet['submission_attempts']==0 and packet['task_id']is None and not packet['submission_performed'])
    state=output/'motion-runs'/packet['packet']/'state.json'
    state.write_text(json.dumps({'packet':packet['packet'],'status':'submission-ambiguous','submission_attempts':1}))
    reopened=motion.prepare(store,first_png=png,prompt='Offline proof only',base_dir=output)
    check('prepare_does_not_reset_attempted_state',reopened['status']=='submission-ambiguous' and reopened['submission_attempts']==1)
    source_lines=io.StringIO('\n'.join(json.dumps(r)for r in [
        {'id':1,'method':'local.motion.status','params':{'packet':packet['packet']}},
        {'id':2,'method':'local.motion.submit','params':{'packet':packet['packet']}},
        {'id':3,'method':'system.shutdown'}])+'\n')
    sink=io.StringIO();serve(store,base_dir=output,result_ref='proof-result',source=source_lines,sink=sink)
    rows=[json.loads(line)for line in sink.getvalue().splitlines()]
    check('jsonl_status_and_disabled_submit',not rows[0]['provider_forwarding'] and rows[1]['result']['status']=='submission-ambiguous' and rows[2]['status']=='validation_error')
    request_path=output/'catalog-request.json';request_path.write_text('{}\n')
    result=subprocess.run([sys.executable,'-m','sprite_workbench','--workspace',str(store.path),'motion','catalog',str(request_path)],capture_output=True,text=True,timeout=30,cwd=output)
    check('installed_cli_motion',result.returncode==0 and len(json.loads(result.stdout)['examples'])==3)
    with ControlServer(store,base_dir=output,port=0)as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with urllib.request.urlopen(server.url+'/api/bootstrap',timeout=20)as response:bootstrap=json.load(response)
            body=json.dumps({'method':'local.motion.status','params':{'packet':packet['packet']}}).encode()
            req=urllib.request.Request(server.url+'/api/invoke',data=body,headers={'Content-Type':'application/json','X-Workbench-Token':bootstrap['csrf_token'],'Origin':server.url})
            with urllib.request.urlopen(req,timeout=20)as response:result=json.load(response)
            check('http_motion_status',result['result']['status']=='submission-ambiguous')
            with urllib.request.urlopen(server.url+native['media_url'],timeout=20)as response:raw=response.read()
            check('http_native_video_bytes',digest(raw)==native['media'])
        finally:server.shutdown();thread.join(timeout=5)
    report.update(status='passed',sequence=conditioned['sequence'],native=native,authored_duration=[4,5])
    (output/'INSTALLED-PROOF.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    report=verify(parser.parse_args().output.resolve())
    print(json.dumps({'status':report['status'],'checks':len(report['checks']),'package':report['package']}))
