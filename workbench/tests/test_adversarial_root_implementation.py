"""Reviewer-owned bounded regressions for root commit6ae55c6.

These tests specify validation/identity oracles, not vendor engine parity.
Initial failures are retained in docs/adversarial-root-implementation/.
"""
from copy import deepcopy
from fractions import Fraction
from io import BytesIO
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, save_sequence, load_sequence
from sprite_workbench.raster import apply_edits, crop, paste, edit_sequence
from sprite_workbench.acquisition import import_image
from sprite_workbench.effects import render_effect


def image():
    a=np.zeros((5,6,4),np.uint8)
    a[2,2]=[255,0,0,255];a[1,1]=[17,29,39,0];a[3,4]=[0,180,0,127]
    return a


def op(operation, **fields):
    return {'operation':operation,'layer':'image','frames':[1],'reason':'Frozen independent reviewer control',**fields}


@pytest.mark.parametrize('number',['NaN','Infinity','-Infinity','1e999'])
def test_json_reader_rejects_nonfinite_hash_valid_blob(tmp_path,number):
    store=Store(tmp_path);ident=store.put_bytes(('{"clock":'+number+'}').encode())
    with pytest.raises(ValidationError): store.get_json(ident)
    # Text containing the word is legal; failure must be numerical/schema based.
    assert store.get_json(store.put_json({'text':'NaN Infinity'}))['text']=='NaN Infinity'


@pytest.mark.parametrize('mutate',[
    lambda d:d['frames'][0].update(duration=[0,1]),
    lambda d:d['frames'][0].update(duration=[-1,30]),
    lambda d:d['frames'][0].update(duration=[1,0]),
    lambda d:d['frames'][0].update(duration=[3601,1]),
    lambda d:d['frames'][0].update(index=99),
    lambda d:d['frames'][0].update(pivot=['x',0]),
    lambda d:d['frames'][0].update(direction=''),
    lambda d:d.update(loop='false'),
    lambda d:d.update(metadata=[]),
    lambda d:d.update(version=99),
    lambda d:d.update(frames={'frame0':d['frames'][0]}),
    lambda d:d['frames'][0].pop('raster'),
],ids=['zero-clock','negative-clock','zero-denominator','clock-budget','wrong-index','nonnumeric-pivot','blank-direction','nonbool-loop','nonobject-metadata','unknown-version','nonarray-frames','missing-raster'])
def test_forged_sequence_rejected_before_consumption(tmp_path,mutate):
    store=Store(tmp_path);ident=save_sequence(store,[image()],[Fraction(1,30)])
    document=store.get_json(ident);mutate(document);forged=store.put_json(document)
    with pytest.raises(ValidationError): load_sequence(store,forged)
    original,arrays=load_sequence(store,ident)
    assert original['frames'][0]['duration']==[1,30]
    np.testing.assert_array_equal(arrays[0],image())


@pytest.mark.parametrize('fields',[{'kind':'rgba','version':1}, {'kind':'rgba','version':99,'width':1,'height':1},
                                  {'kind':'rgba','version':1,'width':True,'height':1,'blob':'0'*64,'raw_sha256':'0'*64}])
def test_invalid_raster_documents_fail_structured(tmp_path,fields):
    store=Store(tmp_path)
    with pytest.raises(ValidationError):store.get_raster(store.put_json(fields))


def test_corrupted_bytes_and_pathlike_ids_fail_closed(tmp_path):
    store=Store(tmp_path);ident=store.put_raster(image());meta=store.get_json(ident)
    (store.path/'blobs'/meta['blob']).write_bytes(b'changed')
    with pytest.raises(ValidationError,match='integrity'):store.get_raster(ident)
    for ident in ('../state.sqlite','A'*64,'abc',None):
        with pytest.raises(ValidationError):store.get_bytes(ident)
    assert store.get_head('current') is None


def test_import_decodes_captured_bytes_even_if_path_changes(tmp_path,monkeypatch):
    store=Store(tmp_path/'store');path=tmp_path/'changing.png'
    Image.new('RGBA',(2,2),(255,0,0,255)).save(path);captured=path.read_bytes()
    original=Image.open
    def changed_before_open(arg,*args,**kwargs):
        Image.new('RGBA',(2,2),(0,255,0,255)).save(path)
        return original(arg,*args,**kwargs)
    monkeypatch.setattr('sprite_workbench.acquisition.Image.open',changed_before_open)
    result=import_image(store,path);doc,frames=load_sequence(store,result['sequence'])
    assert store.get_bytes(result['source_bytes'])==captured
    assert frames[0][0,0].tolist()==[255,0,0,255] # oracle is the retained encoded source
    assert doc['metadata']['source_name']=='changing.png'


def test_apng_default_poster_is_not_manufactured_animation_time(tmp_path):
    path=tmp_path/'poster.png';poster=Image.new('RGBA',(2,2),(255,0,0,255))
    green=Image.new('RGBA',(2,2),(0,255,0,255));blue=Image.new('RGBA',(2,2),(0,0,255,255))
    poster.save(path,save_all=True,append_images=[green,blue],default_image=True,duration=[200,300],loop=0)
    with Image.open(path) as source:
        assert source.info['default_image'] is True and source.n_frames==3
    store=Store(tmp_path/'store');result=import_image(store,path);doc,frames=load_sequence(store,result['sequence'])
    assert len(frames)==2 # two timed APNG animation frames; poster is distinct
    assert [f['duration']for f in doc['frames']]==[[1,5],[3,10]]
    assert [a[0,0].tolist()for a in frames]==[[0,255,0,255],[0,0,255,255]]
    # Retained source includes the poster regardless of the metadata key chosen.
    assert store.get_bytes(result['source_bytes'])==path.read_bytes()


def test_invalid_and_truncated_acquisition_returns_structured_error(tmp_path):
    store=Store(tmp_path/'store');path=tmp_path/'not-image.bin';path.write_bytes(b'not an image')
    with pytest.raises(ValidationError):import_image(store,path)
    path=tmp_path/'truncated.png';Image.new('RGBA',(16,16),(255,0,0,255)).save(path)
    path.write_bytes(path.read_bytes()[:45])
    with pytest.raises(ValidationError):import_image(store,path)
    assert store.get_head('import') is None


@pytest.mark.parametrize('change',[
    op('brush',points=[[1,1]]),
    op('outline',mode='outside'),
    op('outline',mode='recolor'),
    op('map_colors',region=[0,0,1,1],colors=[]),
    op('select_mask',name='bad',selector={'kind':'color','colors':None}),
    op('brush',points=[[1,1]],color='#ff0000',pixel_perfect='false'),
    op('brush',points=[[1,1]],color='#ff0000',view=float('nan')),
],ids=['missing-brush-color','missing-outline-color','missing-outline-map','nonobject-map','nonarray-selector-colors','nonbool-pixel-perfect','nonfinite-view'])
def test_invalid_conditional_raster_inputs_fail_structured(change):
    layers={'image':image()[None]};before=layers['image'].copy()
    with pytest.raises(ValidationError):apply_edits(layers,[change])
    np.testing.assert_array_equal(layers['image'],before)


def test_empty_layer_rejected_and_late_guard_failure_does_not_publish(tmp_path):
    with pytest.raises(ValidationError):apply_edits({'image':np.zeros((1,0,3,4),np.uint8)},[op('select_mask',name='a',selector={'kind':'alpha'})])
    store=Store(tmp_path);source=save_sequence(store,[image()]);assert store.set_head('current',source,None)
    valid=op('patch_pixels',pixels=[[2,2,'#ff0000','#00ff00']])
    invalid=op('patch_pixels',pixels=[[2,2,'#ff0000','#0000ff']])
    with pytest.raises(ValidationError):edit_sequence(store,source,[valid,invalid],head='current',expected_head=source)
    assert store.get_head('current')==source
    np.testing.assert_array_equal(load_sequence(store,source)[1][0],image())


@pytest.mark.parametrize('change,protected_xy',[
    (op('patch_pixels',pixels=[[2,2,'#ff0000','#ff0000']]),(2,2)),
    (op('map_colors',region=[0,0,5,4],colors={'#ff0000':'#ff0000'}),(2,2)),
    (op('copy_region',source_layer='image',source_frame=1,region=[2,2,2,2],at=[2,2]),(2,2)),
    (op('flood_fill',seed=[2,2],expected='#ff0000',color='#ff0000',max_pixels=1),(2,2)),
    (op('brush',points=[[0,0]],mode='erase'),(0,0)),
    (op('outline',mode='inside',color='#ff0000'),(2,2)),
    (op('outline',mode='outside',color='#000000'),(2,1)),
],ids=['patch-noop','map-noop','copy-noop','fill-noop','erase-noop','inner-outline','outer-outline'])
def test_trusted_protection_blocks_touched_not_only_changed(change,protected_xy):
    layers={'image':image()[None]};protected=np.zeros((1,5,6),bool)
    x,y=protected_xy;protected[0,y,x]=True
    with pytest.raises(ValidationError,match='protected'):apply_edits(layers,[change],{'image':protected})
    np.testing.assert_array_equal(layers['image'][0],image())


def test_current_selection_snapshot_copy_and_outline_have_independent_oracles():
    a=np.zeros((1,5,6,4),np.uint8);a[0,2,2]=[255,0,0,255]
    changes=[op('patch_pixels',pixels=[[2,2,'#ff0000','#00ff00']]),
             op('select_mask',name='live',selector={'kind':'color','color':'#00ff00'}),
             op('patch_pixels',mask='live',pixels=[[2,2,'#00ff00','#0000ff'],[3,2,'#999999','#ffffff']]),
             op('copy_region',source_layer='image',source_frame=1,region=[2,2,2,2],at=[4,2]),
             op('outline',mode='outside',color='#ffffff')]
    edited,audit=apply_edits({'image':a},changes)
    assert edited['image'][0,2,2].tolist()==[0,0,255,255]
    assert edited['image'][0,2,4].tolist()==[255,0,0,255] # pre-list copy
    assert edited['image'][0,2,3].tolist()==[255,255,255,255] # one-ring original silhouette
    assert edited['image'][0,2,5].tolist()==[0,0,0,0] # copied island did not enter outline geometry
    assert audit['operations'][2]['matched']==1 # masked expected mismatch was excluded
    assert a[0,2,2].tolist()==[255,0,0,255]


def test_mask_exclusion_cannot_hide_invalid_patch_coordinate_or_color():
    mask=op('select_mask',name='empty',selector={'kind':'alpha','min':255,'max':255})
    a=np.zeros((1,5,6,4),np.uint8)
    for pixel in ([99,0,'#00000000','#ff0000'],[0,0,'bad','#ff0000']):
        with pytest.raises(ValidationError):apply_edits({'image':a},[mask,op('patch_pixels',mask='empty',pixels=[pixel])])


def test_crop_source_node_guard_stamp_and_bounds(tmp_path):
    store=Store(tmp_path);source=store.put_raster(image());packet=crop(store,source,[1,1,2,2],node='owned-body')
    rows=np.array(packet['rgba'],np.uint8);rows[1,1]=[93,94,95,0]
    stamped=paste(store,packet,rows,expected=packet['guard'],stamp=True)
    overwritten=paste(store,packet,rows,expected=packet['guard'],stamp=False)
    assert store.get_raster(stamped)[2,2].tolist()==[255,0,0,255]
    assert store.get_raster(overwritten)[2,2].tolist()==[93,94,95,0]
    forged=deepcopy(packet);forged['node']='other-body'
    with pytest.raises(ValidationError,match='guard'):paste(store,forged,rows,expected=packet['guard'])
    for rows in (np.zeros((1,1,4),np.uint8),np.full((2,2,4),256,np.int64),np.zeros((2,2,4),float)):
        with pytest.raises(ValidationError):paste(store,packet,rows,expected=packet['guard'])
    np.testing.assert_array_equal(store.get_raster(source),image())


def test_brush_interpolation_budget_rejects_before_raster_paint():
    a=np.zeros((1,2,256,4),np.uint8)
    points=[[0 if i%2==0 else 255,0]for i in range(1000)]
    with pytest.raises(ValidationError,match='interpolation budget'):
        apply_edits({'image':a},[op('brush',points=points,color='#ff0000',size=64)])
    assert not a.any()


@pytest.mark.parametrize('recipe',[[], {'canvas':[]}, {'canvas':{'w':16,'h':16},'layers':1}])
def test_effect_outer_shape_validation_is_structured(tmp_path,recipe):
    with pytest.raises(ValidationError):render_effect(Store(tmp_path),recipe)


def test_pinned_factory_tampering_rejected_in_isolated_resource_copy(tmp_path,monkeypatch):
    import sprite_workbench.effects as effects
    source=Path(effects.__file__).parent;target=tmp_path/'isolated'
    target.mkdir();shutil.copy2(source/'vfx_runner.cjs',target/'vfx_runner.cjs')
    shutil.copytree(source/'vendor',target/'vendor')
    manifest=json.loads((target/'vendor/vfx/manifest.json').read_text())
    entry=next(m for m in manifest['modules']if m['id']==manifest['entry'])
    factory=target/'vendor/vfx'/entry['file'];factory.write_bytes(factory.read_bytes()+b'\n')
    monkeypatch.setattr(effects,'__file__',str(target/'effects.py'))
    with pytest.raises(ValidationError,match='Factory integrity failed'):
        effects.render_effect(Store(tmp_path/'store'),{'canvas':{'w':16,'h':16},'frames':1,'layers':[]})
