"""Independent local geometry/export discriminators; synthetic mechanics only."""
import copy
from fractions import Fraction
from io import BytesIO
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, save_sequence, load_sequence
from sprite_workbench.scene import render_scene
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.review import review_sequence


def art(store, pixels):
    array=np.array(pixels,dtype=np.uint8)
    mask=np.zeros_like(array);mask[...,3]=255
    return store.put_raster(array),store.put_raster(mask),array


def single_scene(raster, mask):
    return {'canvas':[1,1],'nodes':[{'id':'part','raster':raster,'mask':mask}],
            'frames':[{'duration':[1,10]}]}


def player_indices(path, samples):
    node=shutil.which('node')
    if node is None:pytest.skip('Node unavailable, player logic not executed')
    script=r'''
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const body=html.match(/<script id="review-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const nodes={};const document={getElementById(id){return nodes[id]??=(id==='review-data'?{textContent:body}:{value:id==='scale'?'1':'0',style:{}})}};
const scope=vm.createContext({document,performance:{now:()=>0},requestAnimationFrame:()=>1,cancelAnimationFrame:()=>{},Image:class{set src(v){this.onload()}}});
vm.runInContext(code,scope,{timeout:1000});
const samples=JSON.parse(process.argv[2]);
console.log(JSON.stringify(samples.map(t=>vm.runInContext(`indexAt(${t})`,scope))));
'''
    result=subprocess.run([node,'-e',script,str(path),json.dumps(samples)],capture_output=True,text=True,timeout=5)
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def test_adversarial_two_partial_layers_match_independent_straight_alpha_golden(tmp_path):
    store=Store(tmp_path/'store')
    back,mask,_=art(store,[[[21,151,241,96]]]);front,_,_=art(store,[[[201,33,18,64]]])
    scene=single_scene(back,mask);scene['nodes'].append({'id':'front','raster':front,'mask':mask,'z':1})
    _,frames=load_sequence(store,render_scene(store,scene))
    # Fractional straight-alpha derivation independently rounded to nearest byte.
    assert frames[0][0,0].tolist()==[106,95,136,136]


def test_adversarial_hidden_rgb_protection_and_unowned_source_binding(tmp_path):
    store=Store(tmp_path/'store')
    source,mask,raw=art(store,[[[81,42,19,0]]]);scene=single_scene(source,mask)
    reference=render_scene(store,scene);assert store.set_head('accepted',reference,None)
    changed=raw.copy();changed[0,0,0]=82
    variant=store.put_raster(changed)
    scene['frames'][0]['nodes']={'part':{'raster':variant}}
    scene['guards']={'reference_sequence':reference,'protected':[{'frame':0,'mask':mask}]}
    with pytest.raises(ValidationError,match='Protected'):render_scene(store,scene)
    assert store.get_head('accepted')==reference
    # Source rectangle equality intentionally includes unowned hiddenRGB.
    raw=np.array([[[1,2,3,255],[41,23,17,0]]],dtype=np.uint8)
    owned=np.zeros_like(raw);owned[0,0,3]=255
    original=store.put_raster(raw);other=raw.copy();other[0,1,2]=18
    bound={'canvas':[2,1],'nodes':[{'id':'p','raster':store.put_raster(other),'mask':store.put_raster(owned),
           'ownership':{'source':original,'origin':[0,0]}}],'frames':[{'duration':[1,10]}]}
    with pytest.raises(ValidationError,match='hiddenRGB'):render_scene(store,bound)


def test_adversarial_huge_integer_scene_rejected_as_validation_not_engine_exception(tmp_path):
    store=Store(tmp_path/'store');raster,mask,_=art(store,[[[1,2,3,255]]]);scene=single_scene(raster,mask)
    scene['nodes'][0]['position']=[10**400,0]
    try:
        with pytest.raises(ValidationError):render_scene(store,scene)
    except OverflowError:
        pytest.xfail('R01 reproduced: bounded point validator converts huge int in math.isfinite and leaks OverflowError')


def test_adversarial_editable_keeps_never_sampled_base_art_for_reverting_override(tmp_path):
    store=Store(tmp_path/'source')
    base,base_mask,_=art(store,[[[17,31,43,255]]]);replacement,replacement_mask,_=art(store,[[[71,83,97,255]]])
    scene=single_scene(base,base_mask)
    scene['frames'][0]['nodes']={'part':{'raster':replacement,'mask':replacement_mask}}
    sequence=render_scene(store,scene)
    export_sequence(store,sequence,tmp_path/'pack',formats=['editable'])
    fresh=Store(tmp_path/'fresh');assert import_editable(fresh,tmp_path/'pack/editable')==sequence
    layered=store.get_json(store.get_json(sequence)['metadata']['scene_id'])
    restored=copy.deepcopy(layered['scene']);restored['frames'][0]['nodes']={}
    base_present=(fresh.path/'blobs'/base).exists()
    try: output=render_scene(fresh,restored)
    except ValidationError as e:
        if not base_present:pytest.xfail('R02 reproduced: overridden original base-node art is absent from editable closure')
        raise
    _,frames=load_sequence(fresh,output)
    assert frames[0][0,0].tolist()==[17,31,43,255]


def test_adversarial_malformed_editable_index_rejected_without_raw_attribute_error(tmp_path):
    pack=tmp_path/'pack';pack.mkdir();(pack/'index.json').write_text('[]');(pack/'artifacts').mkdir()
    try:
        with pytest.raises(ValidationError):import_editable(Store(tmp_path/'fresh'),pack)
    except AttributeError:
        pytest.xfail('R03 reproduced: editable index assumes parsed JSON object and leaks AttributeError')


def test_adversarial_tampered_editable_preserves_existing_store_and_output(tmp_path):
    source=Store(tmp_path/'source');_,_,pixels=art(source,[[[19,41,83,255]]])
    sequence=save_sequence(source,[pixels]);export_sequence(source,sequence,tmp_path/'pack',formats=['editable'])
    index=json.loads((tmp_path/'pack/editable/index.json').read_text())
    blob=tmp_path/'pack/editable/artifacts'/index['artifact_ids'][-1];blob.write_bytes(blob.read_bytes()+b'corrupt')
    target=Store(tmp_path/'target');prior=target.put_json({'kind':'sentinel'});assert target.set_head('accepted',prior,None)
    inventory={p.name for p in (target.path/'blobs').iterdir()}
    with pytest.raises(ValidationError,match='hash mismatch'):import_editable(target,tmp_path/'pack/editable')
    assert target.get_head('accepted')==prior
    assert {p.name for p in (target.path/'blobs').iterdir()}==inventory
    out=tmp_path/'existing';out.mkdir();(out/'sentinel.txt').write_bytes(b'keep me')
    with pytest.raises(ValidationError):export_sequence(source,sequence,out,formats=['png'])
    assert (out/'sentinel.txt').read_bytes()==b'keep me'
    with pytest.raises(UnsupportedCapability):export_sequence(source,sequence,out,formats=['aseprite'])
    assert (out/'sentinel.txt').read_bytes()==b'keep me'


def parse_apng(raw):
    assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    offset=8;holds=[];pixels=[];compressed=None;size=None;plays=None
    while offset<len(raw):
        length=struct.unpack('!I',raw[offset:offset+4])[0];kind=raw[offset+4:offset+8]
        data=raw[offset+8:offset+8+length];crc=struct.unpack('!I',raw[offset+8+length:offset+12+length])[0]
        assert crc==zlib.crc32(kind+data)&0xffffffff
        if kind==b'IHDR':
            w,h,depth,color,compression,filter_,interlace=struct.unpack('!IIBBBBB',data)
            assert (depth,color,compression,filter_,interlace)==(8,6,0,0,0);size=(w,h)
        elif kind==b'acTL':count,plays=struct.unpack('!II',data)
        elif kind==b'fcTL':
            if compressed is not None:pixels.append(zlib.decompress(compressed))
            serial,w,h,x,y,num,den,disposal,blend=struct.unpack('!IIIIIHHBB',data)
            assert (w,h)==size and (x,y,disposal,blend)==(0,0,0,0)
            holds.append(Fraction(num,den));compressed=b''
        elif kind==b'IDAT':compressed+=data
        elif kind==b'fdAT':compressed+=data[4:]
        offset+=length+12
    pixels.append(zlib.decompress(compressed));assert len(pixels)==count
    return holds,pixels,plays


def test_adversarial_apng_independent_chunks_and_gif_explicit_clock_error(tmp_path):
    store=Store(tmp_path/'store')
    a=np.array([[[23,47,89,255],[19,31,43,0]]],dtype=np.uint8)
    holds=[Fraction(1,12),Fraction(1,200),Fraction(3,200)]
    sequence=save_sequence(store,[a,a,a],durations=holds,play_count=2)
    report=export_sequence(store,sequence,tmp_path/'pack',formats=['apng','gif','sheet'])
    actual,payloads,plays=parse_apng((tmp_path/'pack/animation.apng').read_bytes())
    assert actual==holds and plays==2
    assert payloads==[b'\0'+a.tobytes()]*3
    gif=Image.open(tmp_path/'pack/animation.gif');assert gif.n_frames==3 and gif.info['loop']==1
    durations=[]
    for index in range(3):
        gif.seek(index);durations.append(gif.info['duration']);decoded=np.asarray(gif.convert('RGBA'))
        assert decoded[0,0].tolist()==[23,47,89,255] and decoded[0,1,3]==0
    assert durations==[80,10,20]
    assert report['formats']['gif']['frames'][-1]['cumulative_error_seconds']==[1,150]
    for frame in range(3):
        decoded=np.asarray(Image.open(tmp_path/f'pack/frames/frame-{frame:04d}.png'))
        np.testing.assert_array_equal(decoded,a)  # PNG remains hiddenRGB authority.


def test_adversarial_partial_alpha_gif_refusal_keeps_lossless_authorities(tmp_path):
    store=Store(tmp_path/'store');a=np.array([[[81,32,19,127],[61,42,23,0]]],dtype=np.uint8)
    sequence=save_sequence(store,[a],durations=[Fraction(1,100000)])
    report=export_sequence(store,sequence,tmp_path/'pack',formats=['gif','apng'])
    assert report['formats']['gif']['status']==report['formats']['apng']['status']=='unsupported'
    assert not (tmp_path/'pack/animation.gif').exists() and not (tmp_path/'pack/animation.apng').exists()
    np.testing.assert_array_equal(np.asarray(Image.open(tmp_path/'pack/frames/frame-0000.png')),a)
    assert json.loads((tmp_path/'pack/manifest.json').read_text())['frames'][0]['duration']==[1,100000]


def test_adversarial_generated_player_finite_cycle_has_independent_boundary_indices(tmp_path):
    store=Store(tmp_path/'store');a=np.array([[[1,2,3,255]]],dtype=np.uint8);b=a.copy();b[0,0,0]=4
    sequence=save_sequence(store,[a,b],durations=[Fraction(1,10),Fraction(3,20)],play_count=2)
    review_sequence(store,sequence,tmp_path/'review')
    samples=[0,.099,.1,.249,.25,.349,.35,.499,.5,.51]
    assert player_indices(tmp_path/'review/review.html',samples)==[0,0,1,1,0,0,1,1,1,1]
    report=json.loads((tmp_path/'review/review.json').read_text())
    assert report['play_total']==[1,2] and report['visual_acceptance']=='unreviewed'
    assert report['diagnostic_coverage']['continuous_motion_viewed'] is False


def test_adversarial_float_clock_underflow_is_explicitly_unsupported_not_written(tmp_path):
    store=Store(tmp_path/'store');a=np.array([[[1,2,3,255]]],dtype=np.uint8);b=a.copy();b[0,0,0]=4
    sequence=save_sequence(store,[a,b],durations=[Fraction(1,10**400)]*2)
    report=export_sequence(store,sequence,tmp_path/'pack',formats=['godot','review'])
    if report['formats']['godot']['status']=='written':
        text=(tmp_path/'pack/godot/clip.tres').read_text()
        assert '"duration": 0.0' in text
        assert player_indices(tmp_path/'pack/review/review.html',[0])==[1]
        pytest.xfail('R04 reproduced: positive rational clocks underflow to zero Godot weights and player starts on last frame')
    assert report['formats']['godot']['status']==report['formats']['review']['status']=='unsupported'
    assert (tmp_path/'pack/manifest.json').exists()


def test_adversarial_independent_godot_finite_clock_and_pivot_reload(tmp_path):
    executable=shutil.which('godot') or shutil.which('godot4')
    if executable is None:pytest.skip('Godot unavailable; no engine verification claimed')
    store=Store(tmp_path/'store')
    a=np.array([[[19,41,83,255],[23,47,89,0]]],dtype=np.uint8);b=a.copy();b[0,0]=[37,61,97,127]
    sequence=save_sequence(store,[a,b],durations=[Fraction(1,10),Fraction(3,20)],
                           pivots=[[.25,.75],[1.25,1.75]],play_count=2)
    export_sequence(store,sequence,tmp_path/'pack',formats=['godot'])
    project=tmp_path/'pack/godot'
    for index in range(2):shutil.copy2(tmp_path/f'pack/frames/frame-{index:04d}.png',project)
    shutil.copy2(Path(__file__).parent/'fixtures/state_geometry_engine.gd',project/'independent_verify.gd')
    import_result=subprocess.run([executable,'--headless','--path',str(project),'--editor','--import'],capture_output=True,text=True,timeout=40)
    assert import_result.returncode==0,import_result.stdout+import_result.stderr
    result=subprocess.run([executable,'--headless','--path',str(project),'--script','independent_verify.gd','--max-fps','240'],capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stdout+result.stderr
    receipt=json.loads((project/'independent-engine-receipt.json').read_text())
    assert receipt['errors']==[]
    assert len(receipt['completed_times'])==2
    assert receipt['initial_offset']==[-.25,-.75]
