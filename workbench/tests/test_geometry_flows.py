"""F02/F10 supplied-art whole flows; independently placed asymmetric pixel goldens."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, load_sequence, save_sequence
from sprite_workbench.scene import render_scene
from sprite_workbench.export import export_sequence, import_editable
from sprite_workbench.review import review_sequence


def fixture(store, loop=False):
    a = np.zeros((3,4,4),dtype=np.uint8)
    a[0,0] = [255,0,0,255]; a[0,1] = [0,255,0,255]
    a[1,0] = [0,0,255,255]; a[2,3] = [255,255,0,255]
    a[2,2] = [11,22,33,0]  # Owned hiddenRGB: exact PNG/source proof discriminant.
    body = np.zeros_like(a); body[0,0,3] = body[0,1,3] = body[2,2,3] = 255
    arm = np.zeros_like(a); arm[1,0,3] = arm[2,3,3] = 255
    sid = store.put_raster(a)
    scene = {'canvas':[8,6],'loop':loop,'name':'asymmetric-mechanics-only',
             'require_source_coverage':True,
             'nodes':[{'id':'root','position':[1,1]},
                      {'id':'body','parent':'root','raster':sid,'mask':store.put_raster(body),
                       'ownership':{'source':sid,'origin':[0,0]},'z':1},
                      {'id':'arm','parent':'root','raster':sid,'mask':store.put_raster(arm),
                       'ownership':{'source':sid,'origin':[0,0]},'anchor':[.5,1.5],'z':2}],
             'frames':[{'duration':[7,100],'pivot':[1,3],'direction':'south'},
                       {'duration':[13,100],'pivot':[1,3],'direction':'south','nodes':{'arm':{'rotation_degrees':90}}},
                       {'duration':[1,20],'pivot':[2,3],'direction':'south','nodes':{'arm':{'rotation_degrees':90}}}]}
    # Goldens enumerate source destinations; they do not call the scene projector.
    expected = []
    for moving in [(3,4),(5,0),(5,0)]:
        out = np.zeros((6,8,4),dtype=np.uint8)
        out[1,1] = a[0,0]; out[1,2] = a[0,1]; out[2,1] = a[1,0]
        out[moving] = a[2,3]; out[3,3] = a[2,2]
        expected.append(out)
    return scene,expected


def test_F02_owned_scene_editable_guard_and_publication(tmp_path):
    store = Store(tmp_path/'store'); scene,golden = fixture(store)
    ident = render_scene(store,scene); doc,frames = load_sequence(store,ident)
    assert all(np.array_equal(a,b) for a,b in zip(frames,golden))
    assert doc['frames'][1]['raster'] == doc['frames'][2]['raster']  # Held duplicate retained.
    assert len(doc['frames']) == 3 and doc['frames'][2]['duration'] == [1,20]
    layered = store.get_json(doc['metadata']['scene_id'])
    assert len(layered['frame_layers']) == 3
    assert layered['scene'] == scene
    assert store.set_head('approved-mechanics',ident,None)
    previous = store.get_head('approved-mechanics')
    rejected = copy.deepcopy(scene)
    rejected['guards'] = {'reference_sequence':ident,'frozen_frames':[0]}
    rejected['frames'][0]['nodes'] = {'body':{'position':[1,0]}}
    with pytest.raises(ValidationError,match='Frozen frame'):
        render_scene(store,rejected)
    assert store.get_head('approved-mechanics') == previous
    export_sequence(store,ident,tmp_path/'portable',formats=['editable','review','sheet'])
    restored = Store(tmp_path/'restored')
    assert import_editable(restored,tmp_path/'portable/editable') == ident
    assert render_scene(restored,restored.get_json(doc['metadata']['scene_id'])['scene']) == ident
    review = json.loads((tmp_path/'portable/review/review.json').read_text())
    assert [(p['from'],p['to']) for p in review['pairs']] == [(0,1),(1,2),(2,0)]
    assert review['pairs'][1]['rgba_exact'] and review['visual_acceptance'] == 'unreviewed'
    assert review['diagnostic_coverage']['continuous_motion_viewed'] is False


@pytest.mark.parametrize('case',['cycle','unknown-parent','overlap','partial-mask','source-mismatch','missing-pose'])
def test_F02_rejected_scene_admission(tmp_path,case):
    store = Store(tmp_path/'store'); scene,_ = fixture(store)
    if case == 'cycle': scene['nodes'][0]['parent'] = 'arm'
    elif case == 'unknown-parent': scene['nodes'][0]['parent'] = 'missing'
    elif case == 'overlap': scene['nodes'][2]['mask'] = scene['nodes'][1]['mask']
    elif case == 'partial-mask':
        a = np.zeros((3,4,4),dtype=np.uint8); a[0,0,3] = 128
        scene['nodes'][1]['mask'] = store.put_raster(a)
    elif case == 'source-mismatch':
        a = store.get_raster(scene['nodes'][1]['raster']).copy(); a[2,2,0] = 99
        scene['nodes'][1]['raster'] = store.put_raster(a)
    else: scene['infer_missing_anatomy'] = True
    with pytest.raises(ValidationError):render_scene(store,scene)
    assert store.get_head('approved') is None


def test_F02_mirror_parent_visibility_and_oblique(tmp_path):
    store = Store(tmp_path/'store'); scene,golden = fixture(store)
    scene['frames'] = [{'duration':[1,10],'nodes':{'root':{'position':[7,1],'scale':[-1,1]}}}]
    _,arrays = load_sequence(store,render_scene(store,scene))
    expected = np.zeros_like(golden[0]); original = golden[0]
    # x'=7-x for local pixel centers; original world basis x=1+local x.
    expected[:,3:7] = original[:,1:5][:,::-1]
    assert np.array_equal(arrays[0],expected)
    scene['frames'][0]['nodes']['root']['visible'] = False
    _,arrays = load_sequence(store,render_scene(store,scene)); assert not arrays[0].any()
    # A 45-degree nearest-neighbor fixture: single center-owned point stays on its anchor.
    a = np.array([[[77,33,11,255]]],dtype=np.uint8); mask = a.copy(); mask[:,:,:3] = 0
    oblique = {'canvas':[3,3],'nodes':[{'id':'p','raster':store.put_raster(a),'mask':store.put_raster(mask),
               'position':[1,1],'anchor':[.5,.5],'rotation_degrees':45}],
               'frames':[{'duration':[1,10]}]}
    _,arrays = load_sequence(store,render_scene(store,oblique)); expected = np.zeros((3,3,4),dtype=np.uint8); expected[1,1] = a[0,0]
    assert np.array_equal(arrays[0],expected)
    # Nontrivial oblique cell-boundary oracle. Ties select the positive source axis;
    # aliasing duplicates the yellow cell and loses red, rather than inventing colors.
    art = np.array([[[255,0,0,255],[0,255,0,255]],[[0,0,255,255],[255,255,0,255]]],dtype=np.uint8)
    mask = np.zeros_like(art); mask[...,3] = 255
    oblique['canvas'] = [6,6]
    oblique['nodes'] = [{'id':'p','raster':store.put_raster(art),'mask':store.put_raster(mask),
                        'position':[2,2],'anchor':[1,1],'rotation_degrees':45}]
    _,arrays = load_sequence(store,render_scene(store,oblique))
    expected = np.zeros((6,6,4),dtype=np.uint8)
    expected[2,2] = art[1,0]; expected[2,3] = art[0,1]
    expected[3,2] = expected[3,3] = art[1,1]
    assert np.array_equal(arrays[0],expected)


def test_F02_clipping_is_reported_or_rejected(tmp_path):
    store = Store(tmp_path/'store'); scene,_ = fixture(store)
    scene['nodes'][0]['position'] = [100,100]
    ident = render_scene(store,scene)
    layers = store.get_json(store.get_json(ident)['metadata']['scene_id'])['frame_layers']
    assert all(l['owned_source_centers_outside_canvas'] > 0 for f in layers for l in f['layers'])
    scene['clip_policy'] = 'reject'
    with pytest.raises(ValidationError,match='outside canvas'):render_scene(store,scene)


def test_F02_protections_palette_partial_alpha(tmp_path):
    store = Store(tmp_path/'store'); scene,_ = fixture(store); ident = render_scene(store,scene)
    protected = np.zeros((6,8,4),dtype=np.uint8); protected[1,1,3] = 255
    scene['guards'] = {'reference_sequence':ident,'protected':[{'frame':1,'mask':store.put_raster(protected)}]}
    scene['frames'][1]['nodes']['body'] = {'position':[1,0]}
    with pytest.raises(ValidationError,match='Protected frame'):render_scene(store,scene)
    a = np.array([[[255,0,0,128]]],dtype=np.uint8); b = np.array([[[0,0,255,255]]],dtype=np.uint8)
    mask = np.array([[[0,0,0,255]]],dtype=np.uint8)
    stacked = {'canvas':[1,1],'nodes':[{'id':'back','raster':store.put_raster(b),'mask':store.put_raster(mask)},
                {'id':'front','raster':store.put_raster(a),'mask':store.put_raster(mask),'z':1}],
                'frames':[{'duration':[1,10]}]}
    _,frames = load_sequence(store,render_scene(store,stacked)); assert frames[0][0,0].tolist() == [128,0,127,255]
    stacked['guards'] = {'palette_reference':store.put_raster(b)}
    with pytest.raises(ValidationError,match='palette guard'):render_scene(store,stacked)


def test_F10_exact_containers_sheet_and_preview_bounds(tmp_path):
    store = Store(tmp_path/'store'); scene,goldens = fixture(store); ident = render_scene(store,scene)
    report = export_sequence(store,ident,tmp_path/'export')
    manifest = json.loads((tmp_path/'export/manifest.json').read_text())
    sheet = np.asarray(Image.open(tmp_path/'export/sheet.png').convert('RGBA'))
    for a,f in zip(goldens,manifest['frames']):
        assert np.array_equal(np.asarray(Image.open(tmp_path/'export'/f['file'])),a)
        x,y,w,h = f['rectangle']; assert np.array_equal(sheet[y:y+h,x:x+w],a)
    apng = Image.open(tmp_path/'export/animation.apng'); gif = Image.open(tmp_path/'export/animation.gif')
    assert apng.n_frames == gif.n_frames == 3
    assert apng.info['loop'] == 1 and 'loop' not in gif.info
    for i,a in enumerate(goldens):
        apng.seek(i); gif.seek(i)
        assert np.array_equal(np.asarray(apng.convert('RGBA')),a)
        decoded = np.asarray(gif.convert('RGBA'))
        assert np.array_equal(decoded[...,3],a[...,3])
        assert np.array_equal(decoded[a[...,3]>0],a[a[...,3]>0])
        assert round(apng.info['duration']) == gif.info['duration'] == [70,130,50][i]
    assert report['formats']['gif']['duplicates'].startswith('all ordered')
    # APNG exact timing cannot silently accept a field overflow; GIF quantization is explicit.
    a = np.array([[[7,8,9,128]]],dtype=np.uint8)
    strange = save_sequence(store,[a],durations=[Fraction(1,100000)])
    r = export_sequence(store,strange,tmp_path/'bounded',formats=['gif','apng'])
    assert r['formats']['gif']['status'] == r['formats']['apng']['status'] == 'unsupported'
    assert (tmp_path/'bounded/frames/frame-0000.png').exists()
    assert not (tmp_path/'bounded/animation.gif').exists()
    with pytest.raises(ValidationError,match='preserved'):export_sequence(store,ident,tmp_path/'export')


@pytest.mark.parametrize('play_count',[1,0,3])
def test_F10_actual_Godot_import_reload_playback(tmp_path,play_count):
    executable = shutil.which('godot') or shutil.which('godot4')
    if executable is None:
        pytest.skip('Godot unavailable; no engine verification claimed')
    loop = play_count == 0
    store = Store(tmp_path/'store'); scene,_ = fixture(store,loop); scene['play_count'] = play_count
    ident = render_scene(store,scene)
    export_sequence(store,ident,tmp_path/'export',formats=['godot','manifest'])
    project = tmp_path/'export/godot'
    for f in (tmp_path/'export/frames').iterdir():shutil.copyfile(f,project/f.name)
    shutil.copyfile(Path(__file__).parent/'fixtures/geometry_engine.gd',project/'verify.gd')
    import_result = subprocess.run([executable,'--headless','--path',str(project),'--editor','--import'],capture_output=True,text=True,timeout=40)
    assert import_result.returncode == 0, import_result.stdout+import_result.stderr
    run = subprocess.run([executable,'--headless','--path',str(project),'--script','verify.gd','--max-fps','240'],capture_output=True,text=True,timeout=15)
    (project/'engine-stdout.txt').write_text(run.stdout+run.stderr)
    assert run.returncode == 0,run.stdout+run.stderr
    receipt = json.loads((project/'engine-receipt.json').read_text())
    assert receipt['errors'] == [],receipt
    assert receipt['frame_count'] == 3 and receipt['loop'] == loop and receipt['play_count'] == play_count
    assert receipt['rendering_scope'] == 'headless texture readback and real AnimatedSprite2D clock; no GPU visual acceptance'


def test_F10_finite_plays_and_quantized_clock_are_explicit(tmp_path):
    store = Store(tmp_path/'store'); scene,_ = fixture(store); scene['play_count'] = 3
    ident = render_scene(store,scene)
    report = export_sequence(store,ident,tmp_path/'finite',formats=['gif','apng','review'])
    assert Image.open(tmp_path/'finite/animation.apng').info['loop'] == 3
    assert Image.open(tmp_path/'finite/animation.gif').info['loop'] == 2
    review = json.loads((tmp_path/'finite/review/review.json').read_text())
    assert review['play_count'] == 3 and review['play_total'] == [3,4]
    assert report['formats']['apng']['num_plays'] == 3
    # Frame count/duplicates remain authoritative even with GIF clock quantization.
    a = np.array([[[8,9,10,255]]],dtype=np.uint8)
    quantized = save_sequence(store,[a,a,a],durations=[Fraction(1,12)]*3)
    report = export_sequence(store,quantized,tmp_path/'centiseconds',formats=['gif','apng'])
    assert Image.open(tmp_path/'centiseconds/animation.gif').n_frames == 3
    assert report['formats']['gif']['frames'][-1]['cumulative_error_seconds'] == [-1,100]


def test_F10_real_generated_player_clock_logic(tmp_path):
    executable = shutil.which('node')
    if executable is None:pytest.skip('Node unavailable; player VM not verified')
    store = Store(tmp_path/'store'); scene,_ = fixture(store); scene['play_count'] = 3
    ident = render_scene(store,scene); review_sequence(store,ident,tmp_path/'review')
    # Runs our actual generated program with an inert DOM facade. No browser/network or paint claim.
    harness = tmp_path/'player-clock.cjs'
    harness.write_text(r'''
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(process.argv[2],'utf8');
const data=html.match(/<script id="review-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};const document={getElementById(id){return elements[id]??=(id==='review-data'?{textContent:data}:{value:id==='scale'?'2':'0',style:{}})}};
const context=vm.createContext({document,performance:{now:()=>0},requestAnimationFrame:()=>1,cancelAnimationFrame:()=>{},Image:class{set src(value){this.onload()}}});
vm.runInContext(code,context,{timeout:2000});
const checks=[[0,0],[0.069,0],[0.07,1],[0.199,1],[0.2,2],[0.249,2],[0.25,0],[0.32,1],[0.45,2],[0.5,0],[0.7,2],[0.75,2],[1.0,2]];
for(const [time,expected] of checks){const got=vm.runInContext(`indexAt(${time})`,context);if(got!==expected)throw Error(`${time}: ${got} expected ${expected}`)}
document.getElementById('seek').value='0.2';vm.runInContext('seek.oninput()',context);if(vm.runInContext('current',context)!==2)throw Error('Seek lost requested time');
console.log(JSON.stringify({scope:'actual generated player in Node VM with inert DOM; not browser playback',checks}));
''')
    result = subprocess.run([executable,str(harness),str(tmp_path/'review/review.html')],capture_output=True,text=True,timeout=10)
    assert result.returncode == 0,result.stderr
    (tmp_path/'player-clock-receipt.json').write_text(result.stdout)
