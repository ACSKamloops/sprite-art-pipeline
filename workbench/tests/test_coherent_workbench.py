"""Complete local workflows with frozen inputs; no artwork quality inference."""
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

from sprite_workbench.core import Store,load_sequence
from sprite_workbench.export import import_editable,export_sequence
from sprite_workbench.jobs import JobManager
from sprite_workbench.library import Library
from sprite_workbench.pipeline import execute_plan,register_pipeline_job
from sprite_workbench.prepare import prepare_request
from sprite_workbench.assets import build_glyph_atlas,render_text
from sprite_workbench.capabilities import CapabilityRegistry

EXAMPLE=Path(__file__).resolve().parents[1]/'examples/supplied-motion'


def copied_example(directory):
    shutil.copytree(EXAMPLE,directory)
    return json.loads((directory/'plan.json').read_text())


def test_f01_f02_f09_f10_actual_plan_cli_and_fresh_editable_replay(tmp_path):
    work=tmp_path/'example';plan=copied_example(work)
    workspace=tmp_path/'store'
    process=subprocess.run([sys.executable,'-m','sprite_workbench','--workspace',str(workspace),'run',str(work/'plan.json')],
                           capture_output=True,text=True,timeout=30)
    assert process.returncode==0,process.stdout+process.stderr
    run=json.loads(process.stdout);assert run['status']=='completed'
    store=Store(workspace)
    edit=run['results']['fine_edit']
    assert store.get_json(edit['revision'])['sequence']==edit['sequence']
    body,frames=load_sequence(store,edit['sequence'])
    assert len(frames)==8 and frames[0][28,28].tolist()==[255,255,0,255]
    assert all(f['pivot']==[32,40] and f['direction']=='diagnostic-south' for f in body['frames'])
    assert [Fraction(*f['duration']) for f in body['frames']]==[Fraction(1,12)]*8
    # Frozen independent retained arc output hashes, not fresh self-goldens.
    expected=next(c for c in json.loads((EXAMPLE.parents[1]/'tests/fixtures/effects/reference-cases.json').read_text())['cases'] if c['family']=='arc')
    from sprite_workbench.core import digest
    for name,sequence in run['results']['effect']['streams'].items():
        _,arrays=load_sequence(store,sequence)
        assert [digest(a.tobytes()) for a in arrays]==expected['expected'][name]
    output=work/'output/composed';report=json.loads((output/'export-report.json').read_text())
    assert all(record['status']=='written' for record in report['formats'].values())
    fresh=Store(tmp_path/'fresh')
    ident=import_editable(fresh,output/'editable')
    original,arrays=load_sequence(store,ident);again,decoded=load_sequence(fresh,ident)
    assert original==again and all(np.array_equal(a,b) for a,b in zip(arrays,decoded))
    for frame,array in zip(json.loads((output/'manifest.json').read_text())['frames'],arrays):
        np.testing.assert_array_equal(np.array(Image.open(output/frame['file']).convert('RGBA')),array)
    source_bytes=run['results']['source']['source_bytes'];assert fresh.get_bytes(source_bytes)==(work/'source.png').read_bytes()
    # Reproduce from declared source files in a clean Store, preserving oracles.
    replay=tmp_path/'replay';replay.mkdir()
    for key,file in [('source','source.png'),('mask','owned-mask.png')]:
        (replay/file).write_bytes(fresh.get_bytes(run['results'][key]['source_bytes']))
    rerun=execute_plan(fresh,plan,base_dir=replay)
    assert rerun['status']=='completed'
    _,rebuilt=load_sequence(fresh,rerun['results']['compose']['sequence'])
    assert all(np.array_equal(a,b) for a,b in zip(arrays,rebuilt))


def test_f04_f05_f11_jobs_actual_pipeline_candidate_library_reload_export(tmp_path):
    work=tmp_path/'example';plan=copied_example(work);store=Store(tmp_path/'store')
    with JobManager(store,workers=2) as jobs:
        register_pipeline_job(jobs,base_dir=work,result_ref='compose.sequence')
        job=jobs.wait(jobs.submit('local.pipeline',{'plan':plan},head='candidate'),timeout=30)
        assert job['status']=='completed' and job['result_status']=='candidate'
        assert store.get_head('candidate')==job['artifact']
        run=store.get_json(job['outputs'][0]['metadata']['run'])
        assert run['status']=='completed'
        candidate=Library(store).create_candidate(job['artifact'],source_id='diagnostic-motion',technical_status='verified')
        entity=Library(store).promote([candidate],name='mechanical-control',directions={'diagnostic-south':candidate})
        revision=Library(store).get(entity)['revision_id']
        revision=Library(store).set_state(entity,'supplied',expected=revision)
        Library(store).set_animation(entity,'supplied','turn',{'diagnostic-south':candidate},expected=revision)
        reloaded=Library(Store(store.path)).get(entity)
        assert reloaded['document']['states']['supplied']['animations']['turn']['directions']['diagnostic-south']['artifact_id']==job['artifact']
        assert reloaded['document']['candidates'][0]['visual_status']=='unreviewed'
        bad_plan={'version':1,'steps':[{'id':'unsafe','action':'publish','head':'other','artifact':job['artifact']}]}
        failed=jobs.wait(jobs.submit('local.pipeline',{'plan':bad_plan},head='other'))
        assert failed['status']=='validation_error' and store.get_head('other') is None
    exported=export_sequence(store,job['artifact'],tmp_path/'library-export',['editable','manifest'])
    assert exported['formats']['editable']['status']=='written'


def test_preparation_editable_retains_original_mask_values_and_channel_packing(tmp_path):
    from sprite_workbench.core import save_sequence
    store=Store(tmp_path/'store');image=np.zeros((2,3,4),np.uint8)
    mask=image.copy();mask[0,0]=[91,92,93,1];mask[1,2]=[11,22,33,127]
    preparation=prepare_request('local-rgba-v1',[image],{'mask':mask,'roi':[0,0,2,1],'store':store})
    sequence=save_sequence(store,preparation['arrays'],metadata={'preparation':preparation['audit_id']})
    export_sequence(store,sequence,tmp_path/'export',['editable'])
    fresh=Store(tmp_path/'fresh');import_editable(fresh,tmp_path/'export/editable')
    audit=fresh.get_json(preparation['audit_id'])
    np.testing.assert_array_equal(fresh.get_raster(audit['source_mask']),mask)
    assert audit['source_mask_format']=={'dtype':'uint8','packing':'rgba','shape':[2,3,4]}
    assert fresh.get_raster(audit['mask'])[0,0,3]==255


def test_explicit_font_bytes_metrics_coverage_survive_pipeline_export(tmp_path):
    font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    assert font.is_file(),'Declared local font fixture unavailable; test cannot claim a pass'
    store=Store(tmp_path/'store')
    plan={'version':1,'steps':[
        {'id':'font','action':'font','path':str(font),'characters':'AB ','size':12,'columns':3},
        {'id':'text','action':'text','atlas':{'ref':'font.atlas'},'text':'AB','canvas':[32,24],'baseline':[0,16]},
        {'id':'export','action':'export','sequence':{'ref':'text.sequence'},'directory':'output','formats':['editable']} ]}
    run=execute_plan(store,plan,base_dir=tmp_path);assert run['status']=='completed'
    fresh=Store(tmp_path/'fresh');import_editable(fresh,tmp_path/'output/editable')
    atlas=fresh.get_json(run['results']['font']['atlas'])
    assert fresh.get_bytes(atlas['font_source']['bytes'])==font.read_bytes()
    assert atlas['font_source']['rasterization']['coverage']==['A','B',' ']
    for char in 'AB ':fresh.get_raster(atlas['glyphs'][char]['raster'])


def test_bundled_contracts_are_exact_frozen_repository_snapshots():
    registry=CapabilityRegistry()
    source=EXAMPLE.parents[1]/'contracts'
    for file in source.glob('*.json'):
        assert file.read_bytes()==(registry.contract_dir/file.name).read_bytes()
    assert registry.snapshot['implemented_vendor_handlers']==0
