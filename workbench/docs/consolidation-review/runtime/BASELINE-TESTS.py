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
    # README says every edit retains parent/change list/source pixels. This entrypoint doesn't.
    assert result.get('parent') == source or result.get('metadata',{}).get('parent') == source


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
