"""Original Godot shape code, direct-source oracle and real guarded history."""
import copy
import json
from pathlib import Path
import subprocess

import pytest

from sprite_workbench import construction,parity_commands as pc
from sprite_workbench.core import Store,ValidationError,UnsupportedCapability


def project():
    return {'schema':'sprite-edit-project/v1','canvas':{'width':16,'height':12,
        'render_pivot':[8,6],'ground_pivot':[8,12]},
        'palette':[[0,0,0,0],[240,20,40,255],[20,200,60,128],[240,20,40,255],[11,22,33,0]],
        'layers':[{'id':'paint','name':'Paint','locked':False}],
        'cels':{'a':{'layer_id':'paint','pixels':[i%5 for i in range(16*12)]}},
        'frames':[{'id':'f0','duration_ticks':1,'cels':{'paint':'a'},'landmarks':{}},
                  {'id':'f1','duration_ticks':2,'cels':{'paint':'a'},'landmarks':{}}],
        'animations':[{'id':'clip','frames':['f0','f1'],'fps':12,'loop':True,'events':[]}]}


def test_actual_godot_wrapper_matches_all_direct_literal_source_oracles():
    path=Path(__file__).parents[1]/'docs/parity-commands-20261014/FOOTPRINT-ORACLE.json'
    oracle=json.loads(path.read_bytes())
    actual=pc.evaluate([case['command']for case in oracle['cases']])
    assert [r['points']for r in actual['results']]==[c['points']for c in oracle['cases']]
    assert actual['source_provenance']==oracle['source_provenance']
    rows=actual['results']
    assert rows[0]['points']==[[0,0]]*4  # Original duplicates are preserved.
    assert rows[1]['unique_pixels']==5  # Original thin7-high ellipse is not repaired.
    assert rows[5]['points']==rows[6]['points']  # Radius0 source ignores thickness.
    assert rows[4]['unique_pixels']==37  # Filled ellipse thickness expands nominal5x5.


def test_source_geometry_paint_preserves_outside_indices_alpha_aliases_and_real_undo(tmp_path):
    store=Store(tmp_path/'store');p=project();saved=construction.save_project(store,p)
    history=construction.create_history(store,saved['project'])
    command={'method':'ellipse-filled','pos':[3,2],'size':[5,4],'thickness':1}
    result=pc.paint_primitive(store,history['history'],'a',command,2)
    after=construction.load_project(store,result['project']);source=store.get_json(result['footprint'])
    points={tuple(p)for p in source['results'][0]['points']};expected=copy.deepcopy(p)
    for x,y in points:expected['cels']['a']['pixels'][y*16+x]=2
    assert after==expected and result['shared_frames']==['f0','f1']
    assert after['palette'][2][3]==128 and after['palette'][4]==[11,22,33,0]
    assert after['frames']==p['frames'] and after['palette']==p['palette']
    undo=construction.move_history(store,result['history'],'undo');redo=construction.move_history(store,undo['history'],'redo')
    assert undo['project']==saved['project'] and redo['project']==result['project']
    assert construction.load_project(Store(store.path),redo['project'])==expected


def test_outside_source_points_do_not_clip_or_publish_history(tmp_path):
    store=Store(tmp_path/'store');saved=construction.save_project(store,project());h=construction.create_history(store,saved['project'])
    before=set((store.path/'blobs').iterdir())
    with pytest.raises(ValidationError,match='outside canvas'):
        pc.paint_primitive(store,h['history'],'a',{'method':'ellipse-outline','pos':[-1,0],'size':[8,5]},1)
    assert set((store.path/'blobs').iterdir())==before


def test_locked_layer_refuses_before_original_host_execution(tmp_path,monkeypatch):
    store=Store(tmp_path/'store');p=project();p['layers'][0]['locked']=True
    saved=construction.save_project(store,p);h=construction.create_history(store,saved['project'])
    monkeypatch.setattr(pc,'evaluate',lambda *a:pytest.fail('Locked layer reached source execution'))
    with pytest.raises(ValidationError,match='locked'):
        pc.paint_primitive(store,h['history'],'a',{},1)


@pytest.mark.parametrize('commands', [None,[],[{'method':[]}],[{'method':'line'}],
    [{'method':'ellipse-outline','pos':[0,0],'size':[0,3]}],
    [{'method':'ellipse-outline','pos':[True,0],'size':[3,3]}],
    [{'method':'ellipse-outline','pos':[0,0],'size':[3,3],'seed':1}],
    [{'method':'ellipse-filled','pos':[0,0],'size':[3,3]}],
    [{'method':'rounded-rect-filled','pos':[0,0],'size':[3,3],'radius':float('nan')}],
    [{'method':'ellipse-outline','pos':[0,0],'size':[128,128]}]*3])
def test_local_contract_and_work_limits_reject_before_engine(commands,monkeypatch):
    monkeypatch.setattr(pc.subprocess,'run',lambda *a,**k:pytest.fail('Rejected request reached Godot'))
    with pytest.raises(ValidationError):pc.evaluate(commands)


def test_source_hash_drift_and_missing_host_never_use_authored_fallback(tmp_path,monkeypatch):
    command=[{'method':'ellipse-outline','pos':[0,0],'size':[3,3]}]
    bad=tmp_path/'DrawingAlgos.gd';bad.write_bytes(pc.SOURCE.read_bytes()+b'\n')
    monkeypatch.setattr(pc,'SOURCE',bad)
    with pytest.raises(ValidationError,match='source changed'):pc.evaluate(command)
    monkeypatch.undo();monkeypatch.setattr(pc.shutil,'which',lambda _:None)
    with pytest.raises(UnsupportedCapability,match='no Python geometry fallback'):pc.evaluate(command)


def test_timeout_is_explicit_no_local_math_fallback(monkeypatch):
    def timeout(*a,**k):raise subprocess.TimeoutExpired(a[0],30)
    monkeypatch.setattr(pc.subprocess,'run',timeout)
    with pytest.raises(UnsupportedCapability,match='execution unavailable'):
        pc.evaluate([{'method':'ellipse-outline','pos':[0,0],'size':[3,3]}])
