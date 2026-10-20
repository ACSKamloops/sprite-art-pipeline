"""Selected local orchestration/track/finite-clock and resource boundary oracles."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store,ValidationError,load_sequence,save_sequence
from sprite_workbench.pipeline import execute_plan
from sprite_workbench.tracks import bake_tracks
from sprite_workbench.composition import compose_sequences
from sprite_workbench.raster import apply_edits
from sprite_workbench.effects import render_effect


def pixel(rgba):return np.array([[rgba]],np.uint8)


def test_failed_reference_after_success_retains_failed_run_and_parent(tmp_path):
    store=Store(tmp_path)
    plan={'version':1,'steps':[
        {'id':'pose','action':'pose','joints':[{'label':'NECK','x':.5,'y':.5,'z':.5}]},
        {'id':'missing','action':'edit','sequence':{'ref':'future.sequence'},'changes':[]} ]}
    result=execute_plan(store,plan)
    assert result['status']=='failed' and result['failed_step']=='missing'
    receipt=store.get_json(result['run'])
    assert receipt['steps'][0]['step']=='pose' and len(receipt['steps'])==1
    assert store.get_json(receipt['plan'])['plan']==plan
    assert result['error']['status']=='validation_error'
    assert store.get_head('current') is None


def test_plan_executes_exact_frozen_input_not_mutated_caller(tmp_path,monkeypatch):
    from sprite_workbench import acquisition
    store=Store(tmp_path);source=save_sequence(store,[pixel([255,0,0,255])])
    plan={'version':1,'steps':[{'id':'input','action':'import','path':'placeholder.png'},
        {'id':'pose','action':'pose','direction_degrees':0,'joints':[{'label':'point','x':.75,'y':.5,'z':.5}]}]}
    original=deepcopy(plan)
    def mutate_caller(*args,**kwargs):
        plan['steps'][1]['direction_degrees']=90
        return {'sequence':source}
    monkeypatch.setattr(acquisition,'import_image',mutate_caller)
    result=execute_plan(store,plan)
    assert result['status']=='completed'
    assert result['results']['pose']['pose'][0]['x']==pytest.approx(.75)
    run=store.get_json(result['run']);assert store.get_json(run['plan'])['plan']==original
    assert plan['steps'][1]['direction_degrees']==90 # the controlled mutation occurred


@pytest.mark.parametrize('invalid',[
    {'version':True,'steps':[{'id':'p','action':'pose','joints':[{'label':'a'}]}]},
    {'version':1,'steps':[{'id':None,'action':'pose','joints':[{'label':'a'}]}]},
])
def test_pipeline_preflight_rejects_mistyped_identity_fields(tmp_path,invalid):
    with pytest.raises(ValidationError):execute_plan(Store(tmp_path),invalid)


def test_mistyped_reference_after_success_is_structured_failed_step(tmp_path):
    plan={'version':1,'steps':[{'id':'p','action':'pose','joints':[{'label':'a'}]},
          {'id':'bad','action':'publish','head':'current','artifact':{'ref':17}}]}
    result=execute_plan(Store(tmp_path),plan)
    assert result['status']=='failed' and result['failed_step']=='bad'
    assert result['error']['status']=='validation_error'


def test_pipeline_import_prepare_edit_publish_preserves_clocks_pivots_and_stale_guard(tmp_path):
    store=Store(tmp_path/'store');path=tmp_path/'input.png'
    source=np.zeros((2,3,4),np.uint8);source[0,0]=[255,0,0,255];source[1,1]=[29,31,37,0]
    Image.fromarray(source).save(path)
    plan={'version':1,'name':'Frozen local preparation control','steps':[
        {'id':'input','action':'import','path':path.name},
        {'id':'prep','action':'prepare','sequence':{'ref':'input.sequence'},'adapter':'godot-raw-v1',
         'options':{'roi':[-1,0,4,2],'pad_size':[6,4]}},
        {'id':'edit','action':'edit','sequence':{'ref':'prep.sequence'},'changes':[
            {'operation':'patch_pixels','frames':[1],'reason':'Observed redpixel','pixels':[[2,1,'#ff0000','#00ff00']]}]},
        {'id':'commit','action':'publish','head':'accepted','artifact':{'ref':'edit.revision'},'expected':None} ]}
    result=execute_plan(store,plan,base_dir=tmp_path)
    assert result['status']=='completed' and result['results']['commit']['published'] is True
    sequence=result['results']['edit']['sequence'];doc,arrays=load_sequence(Store(tmp_path/'store'),sequence)
    assert doc['frames'][0]['duration']==[1,12] and doc['frames'][0]['pivot']==[2,1]
    assert arrays[0][1,2].tolist()==[0,255,0,255]
    assert arrays[0][2,3].tolist()==[0,0,0,0]
    assert doc['metadata']['parent_sequence']==result['results']['prep']['sequence']
    stale=execute_plan(store,plan,base_dir=tmp_path)
    assert stale['status']=='failed' and stale['failed_step']=='commit'
    assert store.get_head('accepted')==result['results']['edit']['revision']
    run=store.get_json(stale['run']);assert len(run['steps'])==3


def test_cli_pipeline_failure_emits_json_receipt_and_exit2(tmp_path,capsys):
    from sprite_workbench.cli import main
    path=tmp_path/'plan.json'
    path.write_text(json.dumps({'version':1,'steps':[{'id':'bad','action':'import','path':'absent.png'}]}))
    exitcode=main(['--workspace',str(tmp_path/'store'),'run',str(path)])
    value=json.loads(capsys.readouterr().out)
    assert exitcode==2 and value['status']=='failed' and value['failed_step']=='bad'
    assert Store(tmp_path/'store').get_json(value['run'])['status']=='failed'


def test_finite_body_and_effect_replay_are_honored_through_composition(tmp_path):
    store=Store(tmp_path)
    red=pixel([255,0,0,255]);green=pixel([0,255,0,255])
    body=save_sequence(store,[red,green],[Fraction(1,10)]*2,play_count=2)
    result=compose_sequences(store,body,duration=Fraction(2,5))
    doc,frames=load_sequence(store,result['sequence'])
    assert [a[0,0].tolist()for a in frames]==[[255,0,0,255],[0,255,0,255],[255,0,0,255],[0,255,0,255]]
    assert [f['duration']for f in doc['frames']]==[[1,10]]*4
    # Finite overlay replays twice then disappears; body holds its last frame.
    body=save_sequence(store,[pixel([0,0,255,255])],[Fraction(1,2)])
    effect=save_sequence(store,[red,green],[Fraction(1,10)]*2,play_count=2)
    result=compose_sequences(store,body,front=effect)
    _,frames=load_sequence(store,result['sequence'])
    assert [a[0,0].tolist()for a in frames]==[[255,0,0,255],[0,255,0,255],[255,0,0,255],[0,255,0,255],[0,0,255,255]]


def test_import_finite_gif_and_apng_counts_are_total_plays(tmp_path):
    from sprite_workbench.acquisition import import_image
    store=Store(tmp_path/'store');red=Image.new('RGBA',(2,2),(255,0,0,255));green=Image.new('RGBA',(2,2),(0,255,0,255))
    gif=tmp_path/'two-repeat.gif';red.save(gif,save_all=True,append_images=[green],duration=[50,70],loop=2)
    apng=tmp_path/'two-play.png';red.save(apng,save_all=True,append_images=[green],duration=[50,70],loop=2)
    g,_=load_sequence(store,import_image(store,gif)['sequence']);a,_=load_sequence(store,import_image(store,apng)['sequence'])
    assert g['play_count']==3 and a['play_count']==2
    assert g['loop'] is False and a['loop'] is False
    assert [f['duration']for f in g['frames']]==[[1,20],[7,100]]


def test_track_oracles_linear_smoothstep_unwrapped_rotation_and_hold():
    scene={'canvas':[4,4],'nodes':[{'id':'part'}]}
    tracks=[{'node':'part','property':'position','keys':[{'time':[0,1],'value':[0,0]},{'time':[1,1],'value':[4,8]}]},
            {'node':'part','property':'rotation_degrees','keys':[{'time':[0,1],'value':350},{'time':[1,1],'value':10}]},
            {'node':'part','property':'visible','interpolation':'hold','keys':[{'time':[0,1],'value':False},{'time':[1,2],'value':True}]}]
    frames,audit=bake_tracks(scene,tracks,frame_count=5,fps=4)
    assert [f['nodes']['part']['position']for f in frames['frames']]==[[0,0],[1,2],[2,4],[3,6],[4,8]]
    assert [f['nodes']['part']['rotation_degrees']for f in frames['frames']]==[350,265,180,95,10]
    assert [f['nodes']['part']['visible']for f in frames['frames']]==[False,False,True,True,True]
    assert all(f['duration']==[1,4]for f in frames['frames'])
    smooth=deepcopy(tracks[:1]);smooth[0]['interpolation']='smoothstep'
    result,_=bake_tracks(scene,smooth,frame_count=5,fps=4)
    assert result['frames'][1]['nodes']['part']['position']==[.625,1.25]
    assert 'frames' not in scene and audit['sampling']=='zero-basedframe-start'


def test_baked_frame_values_and_audit_do_not_alias_other_frames_or_caller():
    scene={'canvas':[4,4],'nodes':[{'id':'part'}]}
    tracks=[{'node':'part','property':'position','interpolation':'hold','keys':[{'time':[0,1],'value':[1,2]}]}]
    baked,audit=bake_tracks(scene,tracks,frame_count=2,fps=2)
    baked['frames'][0]['nodes']['part']['position'][0]=99
    tracks[0]['keys'][0]['value'][0]=88
    assert baked['frames'][1]['nodes']['part']['position']==[1,2]
    assert audit['tracks'][0]['keys'][0]['value']==[1,2]


@pytest.mark.parametrize('track',[
    {'node':'part','property':'position','keys':[{'time':[0,1],'value':[0,0]},{'time':[0,1],'value':[1,1]}]},
    {'node':'part','property':'position','interpolation':'invented','keys':[{'time':[0,1],'value':[0,0]}]},
    {'node':'part','property':'visible','interpolation':'linear','keys':[{'time':[0,1],'value':True}]},
])
def test_invalid_track_clock_or_mode_is_structured(track):
    with pytest.raises(ValidationError):bake_tracks({'nodes':[{'id':'part'}]},[track],frame_count=2,fps=2)


def test_aggregate_layer_and_brush_work_caps_with_small_instrumented_budget(monkeypatch):
    import sprite_workbench.raster as raster
    source=np.zeros((1,2,3,4),np.uint8)
    monkeypatch.setattr(raster,'MAX_SEQUENCE_BYTES',40)
    with pytest.raises(ValidationError,match='Aggregate layer byte budget'):
        apply_edits({'image':source,'other':source.copy()},[{'operation':'select_mask','layer':'image','frames':[1],'reason':'Budget control','name':'a','selector':{'kind':'alpha'}}])
    monkeypatch.setattr(raster,'MAX_SEQUENCE_BYTES',512*1024*1024)
    points=[[0 if i%2==0 else 255,0]for i in range(40)]
    source=np.zeros((1,2,256,4),np.uint8)
    with pytest.raises(ValidationError,match='stamp work budget'):
        apply_edits({'image':source},[{'operation':'brush','frames':[1],'reason':'Bounded footprint control','points':points,'shape':'square','size':64,'color':'#ff0000'}])
    assert not source.any()


def test_recomputed_manifest_is_rejected_before_renderer_execution(tmp_path,monkeypatch):
    import sprite_workbench.effects as effects
    root=tmp_path/'isolated';(root/'vendor/vfx').mkdir(parents=True)
    original=Path(effects.__file__).parent/'vendor/vfx/manifest.json'
    (root/'vendor/vfx/manifest.json').write_bytes(original.read_bytes()+b'\n')
    monkeypatch.setattr(effects,'__file__',str(root/'effects.py'))
    def no_process(*args,**kwargs):raise AssertionError('Modified manifest must fail before starting Node')
    monkeypatch.setattr(effects.subprocess,'run',no_process)
    with pytest.raises(ValidationError,match='manifest identity changed'):
        render_effect(Store(tmp_path/'store'),{'canvas':{'w':16,'h':16},'frames':1,'layers':[]})
