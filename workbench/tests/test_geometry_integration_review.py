"""Selected integration admission/replay invariants, not synthetic art acceptance.

Initially failing invariants are deliberately retained as failures for owner fixes.
No renderer/backend substitute is installed to turn an unavailable branch into a pass.
"""
from fractions import Fraction

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.composition import compose_sequences
from sprite_workbench.core import Store, ValidationError, load_sequence, save_sequence
from sprite_workbench.export import import_editable
from sprite_workbench.pipeline import execute_plan
from sprite_workbench.scene import render_scene


def chained_plan(store, directory):
    art = np.array([[[255,0,0,255],[0,255,0,255]],[[0,0,255,255],[9,8,7,0]]],dtype=np.uint8)
    Image.fromarray(art).save(directory/'marker.png')
    mask = np.zeros_like(art); mask[...,3] = 255
    mask_id = store.put_raster(mask)
    blank = np.zeros((2,4,4),dtype=np.uint8); flash = blank.copy(); flash[1,3] = [255,0,255,255]
    fx = save_sequence(store,[blank,flash],[Fraction(3,20),Fraction(1,10)])
    scene = {'canvas':[4,2],'require_source_coverage':True,'nodes':[
        {'id':'root'}, {'id':'part','parent':'root','raster':{'ref':'source.rasters.0'},'mask':mask_id,
         'ownership':{'source':{'ref':'source.rasters.0'},'origin':[0,0]}}]}
    plan = {'version':1,'name':'supplied-chain-mechanics-only','steps':[
        {'id':'source','action':'import','path':'marker.png'},
        {'id':'bake','action':'tracks','scene':scene,'frame_count':3,'fps':10,'direction':'south','pivot':[1,2],
         'tracks':[{'node':'part','property':'position','interpolation':'linear',
                    'keys':[{'time':[0,1],'value':[0,0]},{'time':[1,10],'value':[2,0]}]}]},
        {'id':'patch','action':'edit','sequence':{'ref':'bake.sequence'},'changes':[
            {'operation':'patch_pixels','layer':'image','frames':[2],'reason':'explicit supplied diagnostic color',
             'pixels':[[3,0,'#00ff00ff','#ffff00ff']]}]},
        {'id':'compose','action':'compose','body':{'ref':'patch.sequence'},'front':fx},
        {'id':'export','action':'export','sequence':{'ref':'compose.sequence'},'directory':'output',
         'formats':['png','sheet','manifest','apng','editable','review']} ]}
    left = np.zeros((2,4,4),dtype=np.uint8); left[:,:2] = art
    right = np.zeros_like(left); right[:,2:] = art
    patched = right.copy(); patched[0,3] = [255,255,0,255]
    mid = patched.copy(); mid[1,3] = flash[1,3]
    later = right.copy(); later[1,3] = flash[1,3]
    return plan,[left,patched,mid,later,right]


def run_chain(store,directory):
    plan,goldens = chained_plan(store,directory)
    run = execute_plan(store,plan,base_dir=directory)
    assert run['status'] == 'completed',run
    ident = run['results']['compose']['sequence']
    doc,arrays = load_sequence(store,ident)
    assert [Fraction(*f['duration']) for f in doc['frames']] == [Fraction(1,10)]+[Fraction(1,20)]*4
    assert len(arrays) == 5 and doc['frames'][0]['pivot'] == [1,2]
    assert all(np.array_equal(a[a[...,3]>0],b[b[...,3]>0]) for a,b in zip(arrays,goldens))
    assert all(np.array_equal(a[...,3],b[...,3]) for a,b in zip(arrays,goldens))
    return plan,run,doc,arrays,goldens


def test_selected_import_tracks_patch_compose_exact_RGBA(tmp_path):
    store = Store(tmp_path/'store')
    _,_,_,arrays,goldens = run_chain(store,tmp_path)
    # Empty/ended optional layers must not destroy the body's owned hiddenRGB.
    assert all(np.array_equal(a,b) for a,b in zip(arrays,goldens))


def test_selected_editable_fresh_store_lineage_and_replay(tmp_path):
    store = Store(tmp_path/'store'); plan,run,_,arrays,_ = run_chain(store,tmp_path)
    fresh = Store(tmp_path/'fresh')
    ident = import_editable(fresh,tmp_path/'output/editable')
    assert ident == run['results']['compose']['sequence']
    for key in ['bake','patch']:
        assert fresh.get_json(run['results'][key]['sequence'])['kind'] == 'sequence'
    audit = run['results']['bake']['track_audit']
    assert fresh.get_json(audit)['kind'] == 'track-bake'
    body = fresh.get_json(run['results']['bake']['sequence'])
    assert audit in str(fresh.get_json(body['metadata']['scene_id']))
    raw_id = run['results']['source']['source_bytes']
    replay_dir = tmp_path/'replay'; replay_dir.mkdir()
    (replay_dir/'marker.png').write_bytes(fresh.get_bytes(raw_id))
    rerun = execute_plan(fresh,plan,base_dir=replay_dir)
    assert rerun['status'] == 'completed',rerun
    _,again = load_sequence(fresh,rerun['results']['compose']['sequence'])
    assert all(np.array_equal(a,b) for a,b in zip(arrays,again))


def test_selected_bad_prior_ref_has_failed_run_receipt(tmp_path):
    store = Store(tmp_path/'store')
    plan = {'version':1,'steps':[{'id':'bad','action':'edit','sequence':{'ref':'not_a_prior_step.sequence'},'changes':[]}]}
    run = execute_plan(store,plan,base_dir=tmp_path)
    assert run['status'] == 'failed' and run['failed_step'] == 'bad'
    assert store.get_json(run['run'])['status'] == 'failed'


def test_selected_unknown_guard_field_is_not_silently_accepted(tmp_path):
    store = Store(tmp_path/'store'); a = np.array([[[255,0,0,255]]],dtype=np.uint8)
    seq = save_sequence(store,[a]); mask = np.array([[[0,0,0,255]]],dtype=np.uint8)
    plan = {'version':1,'steps':[{'id':'edit','action':'edit','sequence':seq,
        'protected':{'image':[store.put_raster(mask)]},
        'changes':[{'operation':'patch_pixels','frames':[1],'layer':'image','reason':'guard admission discriminator',
                    'pixels':[[0,0,'#ff0000ff','#00ff00ff']]}]}]}
    run = execute_plan(store,plan,base_dir=tmp_path)
    assert run['status'] == 'failed'  # Either honor declared protection or reject unsupported input.


def test_selected_finite_body_clock_is_not_discarded(tmp_path):
    store = Store(tmp_path/'store')
    a = np.array([[[255,0,0,255]]],dtype=np.uint8); b = np.array([[[0,0,255,255]]],dtype=np.uint8)
    body = save_sequence(store,[a,b],[Fraction(1,10)]*2,play_count=3)
    result = compose_sequences(store,body,duration=[3,5])
    doc,arrays = load_sequence(store,result['sequence'])
    assert [f['duration'] for f in doc['frames']] == [[1,10]]*6
    assert [x[0,0].tolist() for x in arrays] == [a[0,0].tolist(),b[0,0].tolist()]*3


def test_selected_scene_cannot_return_unloadable_play_count(tmp_path):
    store = Store(tmp_path/'store'); a = np.array([[[1,2,3,255]]],dtype=np.uint8)
    mask = np.array([[[0,0,0,255]]],dtype=np.uint8)
    scene = {'canvas':[1,1],'loop':False,'play_count':65537,
              'nodes':[{'id':'p','raster':store.put_raster(a),'mask':store.put_raster(mask)}],
              'frames':[{'duration':[1,10]}]}
    with pytest.raises(ValidationError):
        render_scene(store,scene)


def test_selected_unsupported_export_and_stale_publish_are_not_passes(tmp_path):
    store = Store(tmp_path/'store'); a = np.array([[[1,2,3,128]]],dtype=np.uint8)
    seq = save_sequence(store,[a])
    plan = {'version':1,'steps':[
        {'id':'export','action':'export','sequence':seq,'directory':'unsupported','formats':['gif']},
        {'id':'publish','action':'publish','head':'approved','artifact':seq,'expected':None}]}
    run = execute_plan(store,plan,base_dir=tmp_path)
    assert run['status'] == 'failed' and run['failed_step'] == 'export'
    assert store.get_head('approved') is None
    receipt = store.get_json(run['run'])
    assert receipt['steps'][0]['partial_result']['formats']['gif']['status'] == 'unsupported'
    assert (tmp_path/'unsupported/frames/frame-0000.png').exists()
    other = save_sequence(store,[np.zeros_like(a)])
    assert store.set_head('approved',other,None)
    run = execute_plan(store,{'version':1,'steps':[{'id':'publish','action':'publish','head':'approved',
                                                'artifact':seq,'expected':None}]})
    assert run['status'] == 'failed' and store.get_head('approved') == other


def test_corrected_original_base_parts_remain_editable(tmp_path):
    store = Store(tmp_path/'store')
    base = np.array([[[255,0,0,255],[8,7,6,0]]],dtype=np.uint8)
    override = np.array([[[0,0,255,255],[4,5,6,0]]],dtype=np.uint8)
    base_mask = np.array([[[0,0,0,255],[0,0,0,0]]],dtype=np.uint8)
    alternate_mask = base_mask.copy(); alternate_mask[0,1,3] = 255
    ids = {k:store.put_raster(v) for k,v in [('base',base),('override',override),('base_mask',base_mask),('alternate_mask',alternate_mask)]}
    scene = {'canvas':[2,1],'nodes':[{'id':'p','raster':ids['base'],'mask':ids['base_mask'],
              'ownership':{'source':ids['base'],'origin':[0,0]}}],
              'frames':[{'duration':[1,10],'nodes':{'p':{'raster':ids['override'],
                  'mask':ids['alternate_mask'],'ownership':{'source':ids['override'],'origin':[0,0]}}}}]}
    ident = render_scene(store,scene)
    from sprite_workbench.export import export_sequence
    export_sequence(store,ident,tmp_path/'output',['editable'])
    fresh = Store(tmp_path/'fresh'); assert import_editable(fresh,tmp_path/'output/editable') == ident
    assert np.array_equal(fresh.get_raster(ids['base']),base)
    assert np.array_equal(fresh.get_raster(ids['base_mask']),base_mask)
    saved = fresh.get_json(fresh.get_json(ident)['metadata']['scene_id'])['scene']
    saved['frames'][0]['nodes'] = {}
    _,restored = load_sequence(fresh,render_scene(fresh,saved))
    expected = base.copy(); expected[0,1] = [0,0,0,0]
    assert np.array_equal(restored[0],expected)


def test_corrected_prepared_raster_ownership_retains_acquisition(tmp_path):
    store = Store(tmp_path/'store')
    art = np.array([[[255,0,0,255],[0,255,0,255]],[[0,0,255,255],[9,8,7,0]]],dtype=np.uint8)
    Image.fromarray(art).save(tmp_path/'marker.png')
    raw = (tmp_path/'marker.png').read_bytes()
    mask = np.zeros_like(art); mask[...,3] = 255
    mask[0,0,:3] = [12,34,56]; mask[1,1,:3] = [60,70,80]
    plan = {'version':1,'steps':[
        {'id':'source','action':'import','path':'marker.png'},
        {'id':'prepare','action':'prepare','sequence':{'ref':'source.sequence'},'adapter':'local-rgba-v1',
            'options':{'roi':[0,0,2,2],'output_size':[4,4],'mask':store.put_raster(mask)}},
        {'id':'scene','action':'scene','scene':{'canvas':[4,4],'require_source_coverage':True,
            'nodes':[{'id':'p','raster':{'ref':'prepare.raster_ids.0'},'mask':{'ref':'prepare.mask_id'},
                      'ownership':{'source':{'ref':'prepare.raster_ids.0'},'origin':[0,0]}}],
            'frames':[{'duration':[1,5],'pivot':[2,4],'direction':'south'}]}},
        {'id':'export','action':'export','sequence':{'ref':'scene.sequence'},'directory':'output','formats':['editable']} ]}
    run = execute_plan(store,plan,base_dir=tmp_path); assert run['status'] == 'completed',run
    fresh = Store(tmp_path/'fresh'); import_editable(fresh,tmp_path/'output/editable')
    assert fresh.get_bytes(run['results']['source']['source_bytes']) == raw
    audit = fresh.get_json(run['results']['prepare']['audit_id'])
    assert audit['adapter'] == 'local-rgba-v1'
    assert np.array_equal(fresh.get_raster(audit['source_mask']),mask)
    assert audit['source_mask_format'] == {'shape':[2,2,4],'dtype':'uint8','packing':'rgba'}
    assert fresh.get_json(run['results']['prepare']['sequence'])['kind'] == 'sequence'
    _,arrays = load_sequence(fresh,run['results']['scene']['sequence'])
    assert np.array_equal(arrays[0],np.repeat(np.repeat(art,2,axis=0),2,axis=1))
    replay_dir = tmp_path/'replay'; replay_dir.mkdir(); (replay_dir/'marker.png').write_bytes(raw)
    rerun = execute_plan(fresh,plan,base_dir=replay_dir)
    assert rerun['status'] == 'completed',rerun
    assert rerun['results']['scene']['sequence'] == run['results']['scene']['sequence']


def test_corrected_pipeline_revision_sequence_binding(tmp_path):
    store = Store(tmp_path/'store'); a = np.array([[[255,0,0,255]]],dtype=np.uint8)
    seq = save_sequence(store,[a])
    plan = {'version':1,'steps':[{'id':'patch','action':'edit','sequence':seq,'changes':[
        {'operation':'patch_pixels','layer':'image','frames':[1],'reason':'revision-output coherence',
         'pixels':[[0,0,'#ff0000ff','#00ff00ff']]}]}]}
    run = execute_plan(store,plan,base_dir=tmp_path)
    assert run['status'] == 'completed',run
    result = run['results']['patch']
    assert store.get_json(result['revision'])['sequence'] == result['sequence']
