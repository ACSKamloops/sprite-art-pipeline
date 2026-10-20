"""Adversarial offline conditioning checks, never provider/credential calls."""
from copy import deepcopy
from fractions import Fraction
import importlib.util
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import pytest

from sprite_workbench import calibrated_palette as palette_rule, motion_workflow as workflow
from sprite_workbench.core import Store, ValidationError, digest, load_sequence, save_sequence
from sprite_workbench.motion_services import invoke_motion


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / 'store')


def fixture_sequence(store, *, events=False):
    a = np.full((8, 8, 4), [0, 220, 0, 255], dtype=np.uint8)
    a[2:6, 2:6] = [200, 0, 0, 255]
    a[3:5, 3:5] = [0, 220, 0, 255]  # enclosed same-color hole
    a[4, 2] = [7, 12, 25, 128]
    a[5, 2] = [17, 23, 31, 0]  # intentionally nonzero hidden RGB
    meta = {'frame_ids': ['pose-a', 'pose-b'], 'ground_pivot': [4, 7],
            'landmarks': [{'grip': [2, 3]}, {'grip': [3, 4]}],
            'clock_note': 'authored diagnostic source clock',
            'fps': 24, 'duration_ticks': [1, 2]}
    if events:
        meta['events'] = [{'name': 'impact', 'at_tick': 1}]
    ident = save_sequence(store, [a, a.copy()], [Fraction(1, 24), Fraction(1, 12)],
                          pivots=[[4, 7], [3, 6]], metadata=meta, loop=False)
    doc = store.get_json(ident)
    for f, pts in zip(doc['frames'], [1024, 1536]):
        f['pts'] = pts
    doc['metadata']['native_time_base'] = [1, 12288]
    return store.put_json(doc), a


def test_keep_preserves_every_rgba_pts_hold_and_raw_document(store):
    source, a = fixture_sequence(store, events=True)
    before = store.get_bytes(source)
    result = workflow.condition(store, source, output_size=[8, 8],
                                background={'method': 'keep'}, palette={'method': 'keep'})
    doc, arrays = load_sequence(store, result['sequence'])
    original = store.get_json(source)
    assert store.get_bytes(source) == before
    assert all(np.array_equal(x, a) for x in arrays)
    assert [f['pts'] for f in doc['frames']] == [1024, 1536]
    assert [f['duration'] for f in doc['frames']] == [[1, 24], [1, 12]]
    assert doc['metadata']['events'] == original['metadata']['events']
    assert doc['metadata']['frame_ids'] == original['metadata']['frame_ids']
    assert doc['metadata']['ground_pivot'] == [4, 7]
    assert doc['metadata']['landmarks'] == original['metadata']['landmarks']
    assert result['background_changed_pixels'] == 0


def test_full_34_pose_native_cycle_reaches_editable_export_without_frame_loss(store, tmp_path):
    """The observed complete gait exceeds the former32-pose admission cap."""
    from sprite_workbench.export import export_sequence, import_editable
    arrays = []
    for i in range(34):
        a = np.zeros((8, 8, 4), dtype=np.uint8)
        a[2:6, 2:6] = [i + 1, 70, 120, 255]
        arrays.append(a)
    source = save_sequence(store, arrays, [Fraction(1, 24)] * 34, loop=True)
    original = store.get_json(source)
    for i, frame in enumerate(original['frames']):
        frame['pts'] = (38 + i) * 512
    source = store.put_json(original)
    result = workflow.condition(store, source, output_size=[8, 8],
                                background={'method': 'keep'}, palette={'method': 'keep'})
    doc, rendered = load_sequence(store, result['sequence'])
    assert len(rendered) == 34
    assert all(np.array_equal(a, b) for a, b in zip(arrays, rendered))
    assert [f['pts'] for f in doc['frames']] == [(38 + i) * 512 for i in range(34)]
    assert sum(Fraction(*f['duration']) for f in doc['frames']) == Fraction(17, 12)
    export_sequence(store, result['sequence'], tmp_path / 'complete-cycle', formats=('editable',))
    cold = Store(tmp_path / 'cold-cycle')
    assert import_editable(cold, tmp_path / 'complete-cycle/editable') == result['sequence']
    assert load_sequence(cold, result['sequence'])[0] == doc


@pytest.mark.parametrize('count,size', [(65, [8, 8]), (34, [1024, 1024])])
def test_full_cycle_support_keeps_frame_and_aggregate_pixel_limits(store, count, size):
    source = save_sequence(store, [np.zeros((1, 1, 4), dtype=np.uint8)] * count,
                           [Fraction(1, 24)] * count, loop=True)
    before = set((store.path / 'blobs').iterdir())
    with pytest.raises(ValidationError, match='64 frames/16M pixels'):
        workflow.condition(store, source, output_size=size,
                           background={'method': 'keep'}, palette={'method': 'keep'})
    assert set((store.path / 'blobs').iterdir()) == before


def test_resize_transforms_all_declared_geometry_and_keeps_timing(store):
    source, a = fixture_sequence(store)
    result = workflow.condition(store, source, output_size=[4, 16],
                                background={'method': 'keep'}, palette={'method': 'keep'})
    doc, arrays = load_sequence(store, result['sequence'])
    assert doc['canvas'] == [4, 16]
    assert [f['pivot'] for f in doc['frames']] == [[2, 14], [1.5, 12]]
    assert doc['metadata']['ground_pivot'] == [2, 14]
    assert doc['metadata']['landmarks'] == [{'grip': [1, 6]}, {'grip': [1.5, 8]}]
    assert doc['metadata']['frame_ids'] == ['pose-a', 'pose-b']
    assert [f['pts'] for f in doc['frames']] == [1024, 1536]
    assert [f['duration'] for f in doc['frames']] == [[1, 24], [1, 12]]
    assert np.array_equal(arrays[0], np.repeat(a[:, ::2], 2, axis=0))


@pytest.mark.skipif(not shutil.which('godot'), reason='Actual recovered selector needs local Godot')
def test_actual_host_selector_preserves_outside_before_global_palette(store):
    source, a = fixture_sequence(store)
    blue = store.put_raster(np.array([[[0, 0, 255, 255]]], dtype=np.uint8))
    result = workflow.condition(store, source, output_size=[8, 8],
        background={'method': 'recovered-host-selection', 'seed': [0, 0], 'tolerance': 0},
        palette={'method': 'calibrated-fixed', 'reference_raster': blue})
    doc, outputs = load_sequence(store, result['sequence'])
    receipt = store.get_json(result['conditioning'])
    for row, output in zip(receipt['frames'], outputs):
        selected = store.get_json(row['selection'])
        assert selected['kind'] == 'raster-selection'
        assert selected['execution']['source_image_unchanged'] is True
        mask = store.get_raster(row['mask_raster'])[..., 3] > 0
        assert mask[0, 0] and not mask[3, 3]  # enclosed patch is retained
        assert mask.sum() == 48
        assert np.all(output[mask, 3] == 0)
        assert np.array_equal(output[~mask, 3], a[~mask, 3])
        assert np.all(output[..., :3] == [0, 0, 255])
        assert not np.array_equal(output[~mask], a[~mask])  # palette deliberately global
        assert row['outside_mask_rgba_preserved_before_palette'] is True
        assert row['palette_preserves_all_alpha'] is True
    assert np.array_equal(store.get_raster(store.get_json(source)['frames'][0]['raster']), a)
    assert doc['metadata']['parent_sequence'] == source


def test_calibrated_module_exactly_matches_prior_executable_replay():
    path = Path(__file__).parents[1] / 'scripts/replay_pixellab_fixed_palette.py'
    spec = importlib.util.spec_from_file_location('prior_palette_replay', path)
    prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
    rng = np.random.default_rng(14)
    source = rng.integers(0, 256, (17, 31, 4), dtype=np.uint8)
    colors = rng.integers(0, 256, (11, 4), dtype=np.uint8); colors[:, 3] = 255
    assert palette_rule.POLICY == prior.POLICY
    assert np.array_equal(palette_rule.remap_rgba(source, colors), prior.remap_rgba(source, colors))


PROBES = Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014-phase2')


@pytest.mark.skipif(not (PROBES / 'six-color-none/output-00.png').exists(), reason='External retained calibration unavailable')
def test_retained_six_color_nondithered_probe_exact_rgba():
    paths = [PROBES / 'inputs/rgb-cube-gray.png', PROBES / 'inputs/rgba-stripes.png',
             PROBES / 'inputs/six-color-palette.png', PROBES / 'six-color-none/output-00.png',
             PROBES / 'six-color-none/output-01.png']
    hashes = ['02a8c2ed81763a07eb7ac03d74526c24c59bdff4d905431cedec499ea8d042f6',
              'c098f95d8636ffccfbb3efb221ae1796ea5f8d960c730791fa5272a56f3d80f9',
              '6e07995b51ac5aa6fb710172b5965f32519dde776126bfd8db0f16bea15fa6c4',
              '90d0705175c22a5b5c4a42631001606e0b09abc6676e764a4d33ad4ec935b602',
              '8f93758adcee06187a0a7c724f0ec3675873bc4337343cf393834feef6914995']
    assert [digest(p.read_bytes()) for p in paths] == hashes
    arrays = [np.array(Image.open(p).convert('RGBA')) for p in paths]
    colors = arrays[2].reshape(-1, 4)
    assert np.array_equal(palette_rule.remap_rgba(arrays[0], colors), arrays[3])
    assert np.array_equal(palette_rule.remap_rgba(arrays[1], colors), arrays[4])


@pytest.mark.parametrize('palette', [np.array([[1, 2, 3, 128]], dtype=np.uint8),
                                    np.array([[1, 2, 3, 0]], dtype=np.uint8),
                                    np.array([[1, 2, 3, 255]], dtype=np.int64)])
def test_uncalibrated_palette_rejects(palette):
    with pytest.raises(ValidationError):
        palette_rule.remap_rgba(np.zeros((1, 1, 4), dtype=np.uint8), palette)


def test_reference_palette_is_first_seen_opaque_no_clustering():
    a = np.array([[[7, 8, 9, 0], [3, 4, 5, 255], [1, 2, 3, 255], [3, 4, 5, 255]]], dtype=np.uint8)
    assert palette_rule.reference_palette(a).tolist() == [[3, 4, 5, 255], [1, 2, 3, 255]]
    a[0, 1, 3] = 128
    with pytest.raises(ValidationError):
        palette_rule.reference_palette(a)


@pytest.mark.parametrize('change', [
    {'output_size': [2049, 1]}, {'output_size': [True, 1]},
    {'output_size': [513, 8], 'background': {'method': 'recovered-host-selection', 'seed': [0, 0], 'tolerance': 0}},
    {'background': {'method': 'keep', 'seed': [0, 0]}},
    {'background': {'method': 'neural'}},
    {'background': {'method': 'recovered-host-selection', 'seed': [8, 0], 'tolerance': 0}},
    {'background': {'method': 'recovered-host-selection', 'seed': [0, 0], 'tolerance': float('nan')}},
    {'palette': {'method': 'cluster'}}, {'palette': {'method': 'calibrated-fixed'}},
])
def test_invalid_controls_fail_before_selector_and_without_store_writes(store, monkeypatch, change):
    source, _ = fixture_sequence(store)
    before = set((store.path / 'blobs').iterdir())
    monkeypatch.setattr('sprite_workbench.selection.select_raster', lambda *a, **k: pytest.fail('selector invoked before validation'))
    args = {'output_size': [8, 8], 'background': {'method': 'keep'}, 'palette': {'method': 'keep'}} | change
    with pytest.raises(ValidationError):
        workflow.condition(store, source, **args)
    assert set((store.path / 'blobs').iterdir()) == before


def test_explicit_retime_keeps_source_and_pts_then_rejects_events(store):
    source, _ = fixture_sequence(store)
    before = store.get_bytes(source)
    result = workflow.retime(store, source, holds=[[1, 7], [2, 9]], roles=['anticipation', 'strike'], loop=True)
    doc = store.get_json(result['sequence'])
    assert store.get_bytes(source) == before
    assert [f['duration'] for f in doc['frames']] == [[1, 7], [2, 9]]
    assert [f['pts'] for f in doc['frames']] == [1024, 1536]
    assert doc['metadata']['parent_sequence'] == source
    assert doc['metadata']['roles'] == ['anticipation', 'strike']
    assert 'fps' not in doc['metadata'] and 'duration_ticks' not in doc['metadata']
    assert doc['loop'] is True and doc['play_count'] == 0
    event_source, _ = fixture_sequence(store, events=True)
    with pytest.raises(ValidationError, match='event remapping'):
        workflow.retime(store, event_source, holds=[[1, 7], [2, 9]], roles=['a', 'b'], loop=False)


@pytest.mark.parametrize('holds,roles', [(None, ['a', 'b']), ([[1, 2], [1, 2]], None), ('ab', ['a', 'b'])])
def test_direct_retime_malformed_types_are_structured_validation(store, holds, roles):
    source, _ = fixture_sequence(store)
    with pytest.raises(ValidationError):
        workflow.retime(store, source, holds=holds, roles=roles, loop=False)


def test_registered_api_rejects_bad_controls_and_provider_execution_disabled(store, monkeypatch, tmp_path):
    source, _ = fixture_sequence(store)
    monkeypatch.setattr(workflow, 'credentials', lambda: pytest.fail('credential access'))
    with pytest.raises(ValidationError):
        invoke_motion(store, 'condition', {'sequence': source, 'output_size': [8, 8],
                      'background': {'method': 'keep'}, 'palette': {'method': 'calibrated-fixed'}})
    with pytest.raises(ValidationError, match='disabled'):
        invoke_motion(store, 'submit', {'packet': 'a' * 64}, base_dir=tmp_path)


@pytest.mark.skipif(not shutil.which('godot'), reason='Actual recovered selector needs local Godot')
def test_complete_conditioning_and_retime_evidence_survives_cold_export(store, tmp_path):
    from sprite_workbench.export import export_sequence, import_editable
    source, _ = fixture_sequence(store)
    reference = store.put_raster(np.array([[[0, 0, 255, 255], [255, 255, 255, 255]]], dtype=np.uint8))
    conditioned = workflow.condition(store, source, output_size=[8, 8],
        background={'method': 'recovered-host-selection', 'seed': [0, 0], 'tolerance': 0},
        palette={'method': 'calibrated-fixed', 'reference_raster': reference})
    retimed = workflow.retime(store, conditioned['sequence'], holds=[[1, 7], [2, 9]],
                              roles=['anticipation', 'strike'], loop=False)
    receipt = store.get_json(conditioned['conditioning'])
    required = {source, reference, conditioned['sequence'], conditioned['conditioning'], retimed['decision']}
    for frame in receipt['frames']:
        required.update(frame[k] for k in ('source_raster', 'resized_raster', 'selection', 'mask_raster', 'output_raster'))
    target = tmp_path / 'export'
    export_sequence(store, retimed['sequence'], target, formats=('editable',))
    cold = Store(tmp_path / 'cold')
    assert import_editable(cold, target / 'editable') == retimed['sequence']
    missing = sorted(ident for ident in required if not (cold.path / 'blobs' / ident).exists())
    assert not missing, 'Portable closure omitted conditioning evidence: ' + repr(missing)
    assert load_sequence(cold, retimed['sequence'])[0] == load_sequence(store, retimed['sequence'])[0]


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='Local tiny codec fixture needs FFmpeg')
def test_tiny_video_sample_condition_retime_cold_closure_keeps_unsampled_native_frame(store, tmp_path):
    import subprocess
    from sprite_workbench.motion_frames import sample_frames
    from sprite_workbench.export import export_sequence, import_editable
    frames = np.empty((3, 8, 8, 4), dtype=np.uint8)
    frames[0] = [100, 10, 20, 255]
    frames[1] = [10, 120, 20, 128]
    frames[2] = [20, 10, 140, 0]
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-f', 'rawvideo',
        '-pixel_format', 'rgba', '-video_size', '8x8', '-framerate', '7', '-i', 'pipe:0',
        '-c:v', 'ffv1', '-pix_fmt', 'bgra', '-f', 'matroska', 'pipe:1'],
        input=frames.tobytes(), capture_output=True, check=True, timeout=10).stdout
    media = store.put_bytes(raw)
    decoded = workflow.decode(store, media)
    native = store.get_json(decoded['extraction'])
    sampled = sample_frames(store, decoded['extraction'], indices=[2, 0],
        holds=[[1, 7], [2, 7]], loop=False, roles=['recovery', 'anticipation'])
    conditioned = workflow.condition(store, sampled['sequence'], output_size=[8, 8],
        background={'method': 'keep'}, palette={'method': 'keep'})
    retimed = workflow.retime(store, conditioned['sequence'], holds=[[1, 9], [2, 9]],
        roles=['authored recovery', 'authored anticipation'], loop=False)
    target = tmp_path / 'video-export'
    export_sequence(store, retimed['sequence'], target, formats=('editable',))
    cold = Store(tmp_path / 'video-cold')
    assert import_editable(cold, target / 'editable') == retimed['sequence']
    assert cold.get_bytes(media) == raw
    assert cold.get_bytes(native['probe']) == store.get_bytes(native['probe'])
    assert cold.get_json(sampled['decision']) == store.get_json(sampled['decision'])
    assert cold.get_json(decoded['extraction'])['pts'] == [0, 143, 286]
    # Middle frame was never sampled; complete native evidence must retain it.
    assert np.array_equal(cold.get_raster(native['frames'][1]['raster']), frames[1])


def test_keep_mode_can_exceed_selector_width_without_invoking_selector(store, monkeypatch):
    source, a = fixture_sequence(store)
    before = store.get_bytes(source)
    monkeypatch.setattr('sprite_workbench.selection.select_raster',
                        lambda *a, **k: pytest.fail('keep mode invoked selector'))
    result = workflow.condition(store, source, output_size=[513, 8],
        background={'method': 'keep'}, palette={'method': 'keep'})
    doc, arrays = load_sequence(store, result['sequence'])
    assert doc['canvas'] == [513, 8]
    expected = a[:, (np.arange(513) * 8 // 513)]
    assert all(np.array_equal(frame, expected) for frame in arrays)
    assert [f['duration'] for f in doc['frames']] == [[1, 24], [1, 12]]
    assert [f['pts'] for f in doc['frames']] == [1024, 1536]
    assert store.get_bytes(source) == before
    assert result['background_changed_pixels'] == 0


def test_provider_packet_binding_survives_sampling_and_studio_cold_export(store, tmp_path):
    """Locally supplied receipt fixture; no authentic provider attestation claimed."""
    import subprocess
    from io import BytesIO
    from sprite_workbench import motion_provider, studio
    from sprite_workbench.motion_frames import sample_frames
    from sprite_workbench.export import export_sequence, import_editable
    frame = np.full((8, 8, 4), [90, 120, 160, 255], dtype=np.uint8)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-f', 'rawvideo',
        '-pixel_format', 'rgba', '-video_size', '8x8', '-framerate', '7', '-i', 'pipe:0',
        '-c:v', 'ffv1', '-pix_fmt', 'bgra', '-f', 'matroska', 'pipe:1'],
        input=frame.tobytes()*3, capture_output=True, check=True, timeout=10).stdout
    media=store.put_bytes(raw);buf=BytesIO();Image.fromarray(frame).resize((256,256)).save(buf,format='PNG')
    packet=motion_provider.prepare_packet(store,buf.getvalue(),'offline fixture binding')
    probe=store.put_json({'format':{'duration':'3/7'},'origin':'offline receipt fixture'})
    completion=store.put_json({'status':'succeeded','origin':'offline receipt fixture'})
    native=store.put_json({'kind':'motion-native-video','version':1,'packet':packet['packet'],
                          'video':media,'probe':probe,'supplied_completion':completion})
    download=store.put_json({'kind':'motion-media-download','version':1,
                            'packet':packet['packet'],'video':media})
    decoded=workflow.decode(store,media,native_video=native,download_receipt=download)
    extraction=store.get_json(decoded['extraction'])
    assert extraction['source_bindings']==[native,download]
    assert decoded['extraction']in decoded['media_url']
    sampled=sample_frames(store,decoded['extraction'],indices=[2,0],holds=[[1,9],[2,9]],
                          loop=False,roles=['last','first'])
    conditioned=workflow.condition(store,sampled['sequence'],output_size=[8,8],
                                  background={'method':'keep'},palette={'method':'keep'})
    session=studio.from_sequence(store,conditioned['sequence'],animation_id='bound-test')
    export_sequence(store,session['sequence'],tmp_path/'bound',formats=['editable'])
    cold=Store(tmp_path/'bound-cold');assert import_editable(cold,tmp_path/'bound/editable')==session['sequence']
    # The sampled derivative has no direct native-sequence-wrapper link: these
    # must remain reachable through the extraction itself, including raw PNG/wire.
    for ident in (native,download,probe,completion,packet['packet'],packet['request_sha256']):
        assert cold.get_bytes(ident)==store.get_bytes(ident)
    for reference in store.get_json(packet['packet'])['inputs']:
        assert cold.get_bytes(reference['png'])==buf.getvalue()
    middle=extraction['frames'][1]['raster']
    assert np.array_equal(cold.get_raster(middle),frame)


def test_packaged_fixture_binding_stays_on_extraction(store, tmp_path):
    from sprite_workbench.motion_frames import sample_frames
    from sprite_workbench.export import export_sequence, import_editable
    decoded=workflow.load_example(store,'native-walk')
    extraction=store.get_json(decoded['extraction'])
    assert len(extraction['source_bindings'])==3
    assert decoded['extraction']in decoded['media_url']
    sampled=sample_frames(store,decoded['extraction'],indices=[0],holds=[[1,24]],loop=False,roles=['supplied'])
    export_sequence(store,sampled['sequence'],tmp_path/'fixture-bound',formats=['editable'])
    cold=Store(tmp_path/'fixture-cold');import_editable(cold,tmp_path/'fixture-bound/editable')
    for ident in extraction['source_bindings']:
        assert cold.get_bytes(ident)==store.get_bytes(ident)
