"""Synthetic offline checks; these never process or approve real pilot artwork."""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
from PIL import Image
import pytest


SCRIPT = Path(__file__).parents[1] / 'scripts/extract_h3_sprite_cycle.py'
spec = importlib.util.spec_from_file_location('extract_h3_sprite_cycle', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_local_key_all_borders_threshold_four_connectivity_and_rgb_preservation():
    source = np.full((7, 7, 4), 255, np.uint8)
    source[0, 0] = [0, 0, 0, 255]
    source[1, 1] = [0, 0, 0, 111]  # Only diagonally connected: retained.
    source[0, 6] = [12, 12, 12, 200]
    source[6, 0] = [13, 0, 0, 255]  # One channel exceeds tolerance: retained.
    source[6, 6] = [0, 0, 0, 255]
    source[3, 0] = [2, 4, 8, 30]
    source[3, 1] = [3, 5, 9, 255]
    original = source.copy()
    output, stats = module.border_black_key(source)
    assert np.array_equal(source, original)
    assert np.array_equal(output[..., :3], original[..., :3])
    assert output[1, 1, 3] == 111
    assert output[6, 0, 3] == 255
    for y, x in [(0, 0), (0, 6), (6, 6), (3, 0), (3, 1)]:
        assert output[y, x, 3] == 0
    assert stats['alpha_values_changed'] == 5


def test_enclosed_black_island_is_not_keyed():
    source = np.zeros((9, 9, 4), np.uint8)
    source[..., 3] = 255
    source[2:7, 2:7, :3] = 100
    source[4, 4, :3] = 0
    output, _ = module.border_black_key(source)
    assert output[4, 4, 3] == 255
    assert np.all(output[2:7, 2:7, 3] == 255)
    assert output[0, 0, 3] == 0


def synthetic_native(tmp_path, *, count=17, rate=8):
    source = tmp_path / 'original'
    source.mkdir()
    records = []
    for index in range(count):
        pixels = np.zeros((16, 16, 4), np.uint8)
        pixels[..., 3] = 255
        pixels[2:14, 2:14, :3] = [50+index, 80, 120]
        pixels[6:10, 6:10, :3] = 0
        raw = module.png_bytes(pixels)
        name = f'frame-{index:06d}.png'
        (source/name).write_bytes(raw)
        records.append({'index': index, 'file': name, 'sha256': module.sha(raw),
            'pts_ticks': index, 'time_base': f'1/{rate}', 'pts_seconds_exact': str(Fraction(index, rate))})
    manifest = source / 'MANIFEST.json'
    manifest.write_text(json.dumps({'version': 1, 'native_dimensions': [16, 16],
        'native_video_sha256': 'a'*64, 'presentation_end_seconds_exact': str(Fraction(count, rate)),
        'native_frames': records}))
    return manifest


def test_export_same_interval_exact_holds_native_bindings_and_fixed_canvas(tmp_path):
    manifest = synthetic_native(tmp_path)
    before = {p.name: p.read_bytes() for p in manifest.parent.iterdir()}
    output = tmp_path / 'derivative'
    result = module.extract(manifest, output, start=0, end=16)
    assert {p.name: p.read_bytes() for p in manifest.parent.iterdir()} == before
    assert (output/'SOURCE-MANIFEST.json').read_bytes() == manifest.read_bytes()
    assert result['candidate']['source_pts_span_seconds_exact'] == '2'
    assert result['candidate']['native_interval'] == [0, 16]
    assert result['source_presentation_end_seconds_exact'] == '17/8'
    assert result['embedded_native_indices'] == list(range(16))
    for clip in result['clips']:
        count = clip['sample_count']
        assert [frame['native_index'] for frame in clip['frames']] == list(range(0, 16, 16//count))
        assert sum((Fraction(*frame['duration_seconds']) for frame in clip['frames']), Fraction()) == 2
        atlas = np.array(Image.open(output/clip['sprite_atlas']).convert('RGBA'))
        for frame in clip['frames']:
            source = np.array(Image.open(output/frame['source']['embedded_source']).convert('RGBA'))
            keyed = np.array(Image.open(output/frame['source']['embedded_keyed_native']).convert('RGBA'))
            assert np.array_equal(source[..., :3], keyed[..., :3])
            native_bytes = (output/frame['source']['embedded_source']).read_bytes()
            assert module.sha(native_bytes) == frame['source']['sha256']
            sprite = np.array(Image.open(output/frame['sprite_png']).convert('RGBA'))
            assert sprite.shape == (256, 256, 4)
            assert np.array_equal(sprite, module.nearest(keyed))
            assert module.sha(sprite.tobytes()) == frame['sprite_rgba_sha256']
            x, y, w, h = frame['atlas_rect']
            assert np.array_equal(atlas[y:y+h, x:x+w], sprite)
    for record in result['files']:
        raw = (output/record['file']).read_bytes()
        assert module.sha(raw) == record['sha256']
        assert len(raw) == record['bytes']
    assert result['assertions']['per_frame_reanchor'] is False
    assert result['transform']['quantization'] is False
    player = (output/'index.html').read_text()
    assert 'window.spriteReviewState=' in player
    assert 'Step forward' in player and 'Step backward' in player
    assert 'fetch(' not in player


@pytest.mark.parametrize('problem', ['hash', 'pts', 'dimensions'])
def test_bad_native_evidence_is_rejected_before_output_creation(tmp_path, problem):
    manifest = synthetic_native(tmp_path)
    data = json.loads(manifest.read_text())
    if problem == 'hash':
        data['native_frames'][5]['sha256'] = 'f'*64
    elif problem == 'pts':
        data['native_frames'][5]['pts_seconds_exact'] = '100'
    else:
        data['native_dimensions'] = [17, 16]
    manifest.write_text(json.dumps(data))
    output = tmp_path / 'derivative'
    with pytest.raises(ValueError):
        module.extract(manifest, output, start=0, end=16)
    assert not output.exists()
    assert not list(tmp_path.glob('derivative.building-*'))


def test_existing_output_is_never_overwritten(tmp_path):
    manifest = synthetic_native(tmp_path)
    output = tmp_path / 'existing'
    output.mkdir()
    marker = output/'keep'
    marker.write_bytes(b'preserved')
    with pytest.raises(ValueError, match='must not exist'):
        module.extract(manifest, output, start=0, end=16)
    assert marker.read_bytes() == b'preserved'


def test_once_includes_first_and_last_with_irregular_native_pts_and_final_hold(tmp_path):
    manifest = synthetic_native(tmp_path)
    source = json.loads(manifest.read_text())
    for record in source['native_frames']:
        record['pts_ticks'] = record['index']**2
        record['time_base'] = '1/128'
        record['pts_seconds_exact'] = str(Fraction(record['pts_ticks'], 128))
    manifest.write_text(json.dumps(source))
    result = module.extract(manifest, tmp_path/'once', start=0, end=17, mode='once')
    assert result['mode'] == 'once'
    assert result['candidate']['exclusive_end_record_included'] is False
    assert result['candidate']['exclusive_end_boundary']['pts_seconds_exact'] == '17/8'
    for clip in result['clips']:
        assert clip['loop'] is False and clip['mode'] == 'once'
        indices = [frame['native_index'] for frame in clip['frames']]
        assert indices[0] == 0 and indices[-1] == 16
        assert indices == [i*16//(clip['sample_count']-1) for i in range(clip['sample_count'])]
        pts = [Fraction(source['native_frames'][i]['pts_seconds_exact']) for i in indices]
        expected = [b-a for a, b in zip(pts, pts[1:]+[Fraction(17, 8)])]
        assert [Fraction(*frame['duration_seconds']) for frame in clip['frames']] == expected
        assert all(hold > 0 for hold in expected)
        assert sum(expected) == Fraction(17, 8)
        assert Fraction(*clip['frames'][-1]['duration_seconds']) == Fraction(1, 8)
        assert Fraction(*clip['duration_seconds']) == Fraction(17, 8)


def test_once_subinterval_uses_existing_exclusive_end_pts(tmp_path):
    manifest = synthetic_native(tmp_path)
    result = module.extract(manifest, tmp_path/'once', start=0, end=16, mode='once')
    assert result['candidate']['exclusive_end_record_included'] is True
    for clip in result['clips']:
        assert clip['frames'][-1]['native_index'] == 15
        assert sum(Fraction(*frame['duration_seconds']) for frame in clip['frames']) == 2


@pytest.mark.parametrize('problem', ['missing_end', 'end_before_last', 'custom_duration', 'loop_missing_frame'])
def test_once_rejects_unknown_end_or_retiming_without_output(tmp_path, problem):
    manifest = synthetic_native(tmp_path)
    data = json.loads(manifest.read_text())
    options = {'start': 0, 'end': 17, 'mode': 'once'}
    if problem == 'missing_end':
        del data['presentation_end_seconds_exact']
    elif problem == 'end_before_last':
        data['presentation_end_seconds_exact'] = '2'
    elif problem == 'custom_duration':
        options['duration'] = 2
    else:
        options['mode'] = 'loop'
    manifest.write_text(json.dumps(data))
    output = tmp_path/'invalid'
    with pytest.raises(ValueError):
        module.extract(manifest, output, **options)
    assert not output.exists()


@pytest.mark.parametrize('mode', ['once', 'loop'])
def test_actual_player_once_completion_replay_and_loop_regression(mode):
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node is required for the isolated player host check')
    clips = []
    for count in (8, 16):
        holds = ([[1, count]]*(count-1) + [[count+1, count]]) if mode == 'once' else [[2, count]]*count
        clips.append({'sample_count': count, 'loop': mode == 'loop', 'mode': mode, 'duration_seconds': [2, 1],
            'frames': [{'native_index': i, 'source': {'pts_seconds_exact': str(i)},
                'duration_seconds': holds[i], 'source_png': f's-{count}-{i}', 'sprite_png': f'k-{count}-{i}'} for i in range(count)]})
    script = re.search(r'<script>(.*?)</script>', module.player_html({'clips': clips}), re.S).group(1)
    parsed = subprocess.run([node, '--check'], input=script, text=True, capture_output=True)
    assert parsed.returncode == 0, parsed.stderr
    host = r'''
const vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map(),queue=new Map();let serial=0;
function el(id){if(!elements.has(id))elements.set(id,{value:id==='speed'?'1':'0',getContext:()=>({clearRect(){},drawImage(){}})});return elements.get(id);}
class Image{set src(value){this.path=value;queueMicrotask(()=>this.onload());}}
const context=vm.createContext({window:{},document:{getElementById:el},Image,
 requestAnimationFrame(fn){queue.set(++serial,fn);return serial;},cancelAnimationFrame(id){queue.delete(id);}});
vm.runInContext(SOURCE,context);
const state=()=>context.window.spriteReviewState();
function advance(now){const pending=[...queue.values()];queue.clear();for(const fn of pending)fn(now);}
(async()=>{await new Promise(setImmediate);assert.equal(state().loaded,true);assert.equal(state().mode,MODE);
const copy=state();copy.holds[0][0]=999;copy.duration_seconds[0]=999;assert.notEqual(state().holds[0][0],999);assert.equal(state().duration_seconds[0],2);
el('play').onclick();advance(0);
if(MODE==='once'){
 advance(875);assert.equal(state().frame,7);assert.equal(state().completed,false);
 advance(1999);assert.equal(state().completed,false);advance(2000);
 assert.equal(state().time,2);assert.equal(state().frame,7);assert.equal(state().completed,true);assert.equal(state().playing,false);assert.equal(queue.size,0);
 el('play').onclick();advance(3000);assert.equal(state().time,2);assert.equal(state().playing,false);
 el('variant').value='1';el('variant').onchange();assert.equal(state().frame,15);assert.equal(state().completed,true);
 el('next').onclick();assert.equal(state().frame,15);assert.equal(state().playing,false);
 el('variant').value='0';el('variant').onchange();assert.equal(state().completed,true);
 el('replay').onclick();assert.equal(state().time,0);assert.equal(state().completed,false);assert.equal(state().playing,true);
 advance(4000);advance(4125);assert.equal(state().frame,1);
 el('variant').value='1';el('variant').onchange();assert.equal(state().frame,2);
 el('play').onclick();const frozen=state().time;advance(9000);assert.equal(state().time,frozen);assert.equal(state().playing,false);
}else{
 advance(2125);assert.equal(state().time,.125);assert.equal(state().playing,true);assert.equal(state().completed,false);
 el('play').onclick();advance(3000);assert.equal(state().time,.125);
 el('prev').onclick();assert.equal(state().frame,7);el('next').onclick();assert.equal(state().frame,0);
 el('variant').value='1';el('variant').onchange();assert.equal(state().variant,16);assert.equal(state().frame,0);
 el('replay').onclick();assert.equal(state().time,0);assert.equal(state().playing,true);
}})().catch(error=>{console.error(error);process.exitCode=1;});
'''.replace('SOURCE', json.dumps(script)).replace('MODE', json.dumps(mode))
    executed = subprocess.run([node], input=host, text=True, capture_output=True)
    assert executed.returncode == 0, executed.stderr


def curated_indices():
    return {'8': [0, 12, 26, 27, 50, 75, 90, 106],
            '16': [0, 7, 14, 21, 26, 27, 35, 42, 49, 56, 63, 70, 77, 84, 98, 106]}


def test_manual_once_indices_retain_fast_frames_and_exact_native_holds(tmp_path):
    manifest = synthetic_native(tmp_path, count=107, rate=24)
    indices = curated_indices()
    selection = tmp_path/'manual-indices.json'
    selection.write_text(json.dumps(indices, indent=2)+'\n')
    output = tmp_path/'curated'
    result = module.extract(manifest, output, start=0, end=107, mode='once', indices_file=selection)
    assert result['sampling']['manual_curation'] is True
    assert result['sampling']['policy'] == 'explicit-manual-indices-v1'
    assert result['sampling']['profiles'] == indices
    assert (output/'INDICES.json').read_bytes() == selection.read_bytes()
    assert result['sampling']['indices_file_sha256'] == module.sha(selection.read_bytes())
    for clip in result['clips']:
        chosen = indices[str(clip['sample_count'])]
        assert [frame['native_index'] for frame in clip['frames']] == chosen
        holds = [Fraction(*frame['duration_seconds']) for frame in clip['frames']]
        assert holds == [Fraction(b-a, 24) for a, b in zip(chosen, chosen[1:]+[107])]
        assert sum(holds) == Fraction(107, 24)
        assert Fraction(*clip['duration_seconds']) == Fraction(107, 24)
    sixteen = result['clips'][1]['frames']
    for native_index in (26, 27):
        record = next(frame for frame in sixteen if frame['native_index'] == native_index)
        native = np.array(Image.open(manifest.parent/f'frame-{native_index:06d}.png').convert('RGBA'))
        exported = np.array(Image.open(output/record['source_png']).convert('RGBA'))
        assert np.array_equal(exported, module.nearest(native))
    assert Fraction(*next(frame for frame in sixteen if frame['native_index'] == 26)['duration_seconds']) == Fraction(1, 24)
    uniform, raw = module.selection_profiles(0, 107, 'once')
    assert raw is None
    assert uniform[16] == module.sample_indices(0, 107, 16, 'once')
    assert 26 not in uniform[16] and 27 not in uniform[16]


@pytest.mark.parametrize('problem,reason', [
    ('out_of_order', 'strictly increasing'), ('duplicate', 'strictly increasing'),
    ('below_start', 'inside the candidate'), ('past_end', 'inside the candidate'),
    ('count8', 'exactly 8 native'), ('count16', 'exactly 16 native'),
    ('start_endpoint', 'include candidate start'), ('end_endpoint', 'include candidate start'),
    ('missing8', 'exactly the 8 and 16'), ('missing16', 'exactly the 8 and 16'),
    ('extra_profile', 'exactly the 8 and 16'), ('float', 'whole native indices'),
    ('boolean', 'whole native indices'), ('loop', 'only supported in once'),
])
def test_invalid_manual_indices_are_rejected_before_native_reads_or_output(tmp_path, problem, reason):
    indices = curated_indices()
    mode = 'once'
    if problem == 'out_of_order': indices['16'][3], indices['16'][4] = indices['16'][4], indices['16'][3]
    elif problem == 'duplicate': indices['16'][4] = indices['16'][3]
    elif problem == 'below_start': indices['16'][1] = -1
    elif problem == 'past_end': indices['16'][-2] = 107
    elif problem == 'count8': indices['8'].pop()
    elif problem == 'count16': indices['16'].append(106)
    elif problem == 'start_endpoint': indices['8'][0] = 1
    elif problem == 'end_endpoint': indices['16'][-1] = 105
    elif problem == 'missing8': del indices['8']
    elif problem == 'missing16': del indices['16']
    elif problem == 'extra_profile': indices['32'] = []
    elif problem == 'float': indices['16'][1] = 7.5
    elif problem == 'boolean': indices['8'][1] = True
    else: mode = 'loop'
    path = tmp_path/'bad-indices.json'
    path.write_text(json.dumps(indices))
    output = tmp_path/'must-not-exist'
    # Missing manifest proves these errors occur before reading native inputs.
    with pytest.raises(ValueError, match=reason):
        module.extract(tmp_path/'absent-source.json', output, start=0, end=107, mode=mode, indices_file=path)
    assert not output.exists()
    assert not list(tmp_path.glob('must-not-exist.building-*'))
