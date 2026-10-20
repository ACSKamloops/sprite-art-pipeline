"""Claim-driven red-team controls, not all-family or artistic acceptance.

Failing invariants stay failures until the owner fixes code or narrows the claim.
"""
import numpy as np

from sprite_workbench.core import Store, ValidationError, load_sequence, save_sequence
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.pipeline import execute_plan
from sprite_workbench.raster import crop, paste
from sprite_workbench.scene import render_scene


def test_nullable_ownership_scene_has_editable_exchange(tmp_path):
    store = Store(tmp_path/'store')
    art = np.array([[[255,0,0,255]]],dtype=np.uint8)
    mask = np.array([[[0,0,0,255]]],dtype=np.uint8)
    scene = {'canvas':[1,1], 'nodes':[{'id':'p','raster':store.put_raster(art),
              'mask':store.put_raster(mask),'ownership':None}], 'frames':[{'duration':[1,10]}]}
    sequence = render_scene(store,scene)
    load_sequence(store,sequence)  # It is an admitted valid local scene.
    report = export_sequence(store,sequence,tmp_path/'editable',['editable'])
    assert report['formats']['editable']['status'] == 'written'
    assert import_editable(Store(tmp_path/'fresh'),tmp_path/'editable/editable') == sequence


def test_false_string_cannot_acknowledge_unsupported_export(tmp_path):
    store = Store(tmp_path/'store')
    sequence = save_sequence(store,[np.array([[[1,2,3,128]]],dtype=np.uint8)])
    def plan(flag,path):
        return {'version':1,'steps':[
            {'id':'export','action':'export','sequence':sequence,'directory':path,'formats':['gif'],
             'allow_unsupported_formats':flag},
            {'id':'publish','action':'publish','head':'accepted','artifact':sequence,'expected':None}]}
    control = execute_plan(store,plan(False,'correct-false'),base_dir=tmp_path)
    assert control['status'] == 'failed' and store.get_head('accepted') is None
    observed = execute_plan(store,plan('false','string-false'),base_dir=tmp_path)
    assert observed['status'] == 'failed' and store.get_head('accepted') is None


def test_documented_every_edit_lineage_includes_standalone_paste(tmp_path):
    store = Store(tmp_path/'store')
    original = np.array([[[255,0,0,255],[0,0,255,255]]],dtype=np.uint8)
    source = store.put_raster(original)
    packet = crop(store,source,[0,0,0,0])
    pasted = paste(store,packet,[[[0,255,0,255]]],expected=packet['guard'])
    result = store.get_json(pasted)
    # Standalone raster lineage uses its own typed schema; it has no animation clock.
    assert result['metadata']['parent_raster'] == source
    decision = store.get_json(result['metadata']['paste_decision'])
    assert decision['parent_raster'] == source
    assert decision['guard'] == packet['guard'] and decision['region'] == [0,0,0,0]
    assert decision['node'] == 'composite' and decision['stamp'] is False
    np.testing.assert_array_equal(store.get_raster(decision['patch']),[[[0,255,0,255]]])
    full_mask = store.put_raster(np.full((1,2,4),255,dtype=np.uint8))
    sequence = render_scene(store,{'canvas':[2,1], 'nodes':[{'id':'edited','raster':pasted,
        'mask':full_mask}], 'frames':[{'duration':[1,10]}]})
    export_sequence(store,sequence,tmp_path/'exchange',['editable'])
    fresh = Store(tmp_path/'fresh')
    assert import_editable(fresh,tmp_path/'exchange/editable') == sequence
    np.testing.assert_array_equal(fresh.get_raster(source), original)
    assert fresh.get_json(result['metadata']['paste_decision']) == decision
    replay_packet = crop(fresh,source,decision['region'],node=decision['node'])
    replay = paste(fresh,replay_packet,fresh.get_raster(decision['patch']),
                   expected=decision['guard'],stamp=decision['stamp'])
    assert replay == pasted
    np.testing.assert_array_equal(fresh.get_raster(replay),store.get_raster(pasted))


def test_direct_failed_plan_commits_prior_explicit_publication(tmp_path):
    """Observation control: direct plans are sequential, not whole-plan transactions."""
    store = Store(tmp_path/'store')
    sequence = save_sequence(store,[np.array([[[255,0,0,255]]],dtype=np.uint8)])
    run = execute_plan(store,{'version':1,'steps':[
        {'id':'publish','action':'publish','head':'checkpoint','artifact':sequence,'expected':None},
        {'id':'bad','action':'edit','sequence':sequence,'changes':[
            {'operation':'patch_pixels','frames':[1],'layer':'image','reason':'wrong expected color',
             'pixels':[[0,0,'#0000ffff','#00ff00ff']]}]}]},base_dir=tmp_path)
    assert run['status'] == 'failed'
    assert store.get_head('checkpoint') == sequence


def test_missing_font_after_successful_step_retains_failed_run_receipt(tmp_path):
    """README promises a failed run receipt, including expected local file failures."""
    store = Store(tmp_path/'store')
    sequence = save_sequence(store,[np.array([[[255,0,0,255]]],dtype=np.uint8)])
    run = execute_plan(store,{'version':1,'steps':[
        {'id':'first','action':'candidate','artifact':sequence},
        {'id':'missing','action':'font','path':'missing.ttf','characters':'A'}]},base_dir=tmp_path)
    assert run['status'] == 'failed' and run['failed_step'] == 'missing'
    receipt = store.get_json(run['run'])
    assert receipt['steps'][0]['step'] == 'first'
    assert receipt['status'] == 'failed'
