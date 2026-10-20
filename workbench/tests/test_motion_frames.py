"""Offline codec/admission checks; no providers, generation or credentials."""
from fractions import Fraction
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.motion_frames import (
    VideoExtractionError, _timing, extract_video, sample_frames,
)


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / 'store')


@pytest.fixture
def encoded():
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('Local FFmpeg tools unavailable')
    frames = np.zeros((3, 8, 8, 4), dtype=np.uint8)
    frames[..., 3] = 255
    frames[0, 1, 2] = [255, 0, 0, 255]
    frames[1, 2, 3] = [0, 255, 0, 128]
    frames[2, 3, 4] = [0, 0, 255, 0]
    run = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-f', 'rawvideo',
        '-pixel_format', 'rgba', '-video_size', '8x8', '-framerate', '7', '-i', 'pipe:0',
        '-c:v', 'ffv1', '-pix_fmt', 'bgra', '-f', 'matroska', 'pipe:1'],
        input=frames.tobytes(), capture_output=True, timeout=10, check=True)
    return run.stdout, frames


def test_lossless_all_frames_alpha_and_source_clock(store, encoded):
    raw, expected = encoded
    result = extract_video(store, raw)
    doc = store.get_json(result['extraction'])
    seq, arrays = load_sequence(store, result['sequence'])
    assert store.get_bytes(result['media']) == raw
    assert result['frame_count'] == 3 and result['canvas'] == [8, 8]
    assert all(np.array_equal(a, b) for a, b in zip(arrays, expected))
    assert doc['opaque'] is False
    assert doc['pts'] == [0, 143, 286]
    assert [f['pts'] for f in doc['frames']] == doc['pts']
    assert doc['time_base'] == [1, 1000]
    assert [f['duration'] for f in seq['frames']] == [[143, 1000], [143, 1000], [71, 500]]
    assert result['duration'] == [107, 250]
    assert seq['loop'] is False and seq['play_count'] == 1
    assert doc['media'] in seq['metadata']['source_ids']
    assert store.get_bytes(doc['probe'])


def test_explicit_sample_repeated_indices_and_roles(store, encoded):
    native = extract_video(store, encoded[0])
    result = sample_frames(store, native['extraction'], indices=[2, 1, 1, 0],
        holds=[[1, 9], [1, 18], [1, 3], [1, 2]], loop=False,
        roles=['recovery', 'strike', 'authored hold', 'anticipation'])
    sample, arrays = load_sequence(store, result['sequence'])
    decision = store.get_json(result['decision'])
    assert [s['native_index'] for s in decision['samples']] == [2, 1, 1, 0]
    assert [s['native_pts'] for s in decision['samples']] == [286, 143, 143, 0]
    assert sample['frames'][1]['raster'] == sample['frames'][2]['raster']
    assert len(sample['frames']) == 4
    assert [s['duration'] for s in sample['frames']] == [[1, 9], [1, 18], [1, 3], [1, 2]]
    assert decision['media_sha256'] == native['media']
    assert native['extraction'] in sample['metadata']['source_ids']
    assert np.array_equal(arrays[0], encoded[1][2])


@pytest.mark.parametrize('change', [
    {'indices': [True]}, {'indices': [-1]}, {'indices': [3]},
    {'holds': [[0, 1]]}, {'holds': [[True, 1]]}, {'holds': [[1, 0]]},
    {'roles': ['']}, {'roles': []}, {'loop': 1},
])
def test_invalid_sample_writes_nothing(store, encoded, change):
    native = extract_video(store, encoded[0])
    before = set((store.path / 'blobs').iterdir())
    args = {'indices': [0], 'holds': [[1, 2]], 'loop': False, 'roles': ['inspection']} | change
    with pytest.raises(ValidationError):
        sample_frames(store, native['extraction'], **args)
    assert set((store.path / 'blobs').iterdir()) == before


def test_failure_retains_original_media_and_bounded_receipt(store):
    with pytest.raises(VideoExtractionError) as caught:
        extract_video(store, b'not a video\x00')
    receipt = store.get_json(caught.value.receipt)
    assert receipt['kind'] == 'motion-extraction-failure'
    assert store.get_bytes(receipt['media']) == b'not a video\x00'
    assert caught.value.to_dict()['extraction_failure'] == caught.value.receipt


@pytest.mark.parametrize('value', ['https://example.invalid/video.mp4', b'', bytearray(b'x')])
def test_no_paths_urls_or_mutable_media(store, value):
    with pytest.raises(ValidationError):
        extract_video(store, value)
    assert not list((store.path / 'blobs').iterdir())


def test_native_clock_rejects_guessing_and_nonmonotonic_pts():
    p = {'streams': [{'width': 8, 'height': 8, 'time_base': '1/24000'}],
         'frames': [{'pts': 7}, {'pts': 7, 'pkt_duration': 1000}]}
    with pytest.raises(ValidationError, match='Exact monotonic'):
        _timing(p)
    p['frames'][1]['pts'] = 1007
    del p['frames'][1]['pkt_duration']
    with pytest.raises(ValidationError, match='Exact monotonic'):
        _timing(p)
    p['frames'][1]['pkt_duration'] = 1000
    _, _, pts, holds, base, _ = _timing(p)
    assert pts == [7, 1007] and base == Fraction(1, 24000)
    assert holds == [Fraction(1, 24)] * 2


def test_frame_and_decode_budget_before_decoder():
    p = {'streams': [{'width': 2048, 'height': 2048, 'time_base': '1/24'}],
         'frames': [{'pts': i, 'pkt_duration': 1} for i in range(33)]}
    with pytest.raises(ValidationError, match='512 MiB'):
        _timing(p)
    p['frames'] *= 16
    with pytest.raises(ValidationError, match='1..512'):
        _timing(p)


PILOT = Path('/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/h3-slash-margin-002/native-video.mp4')


@pytest.mark.skipif(not PILOT.exists(), reason='Retained native pilot is not a packaged fixture')
def test_retained_107_frame_native_pilot_and_strike_indices(store):
    result = extract_video(store, PILOT.read_bytes())
    assert result['media'] == 'aed5ac139188860f2e3e39f58484ebda394c77fa7b8ae99f777cced03c572132'
    assert result['frame_count'] == 107 and result['canvas'] == [768, 768]
    assert result['duration'] == [107, 24]
    doc = store.get_json(result['extraction'])
    assert doc['opaque'] and len(doc['pts']) == 107
    assert all(f['duration'] == [1, 24] for f in doc['frames'])
    # Cross-check every actual decoded RGBA frame against prior retained PNGs,
    # not merely metadata or a contact sheet.
    from PIL import Image
    for i, record in enumerate(doc['frames']):
        png = PILOT.parent / 'media-review' / 'decoded-native' / f'frame-{i:06d}.png'
        if png.exists():
            with Image.open(png) as im:
                assert np.array_equal(store.get_raster(record['raster']), np.array(im.convert('RGBA')))
    chosen = [0, 12, 18, 23, 24, 25, 26, 27, 28, 35, 52, 73, 78, 85, 94, 106]
    sampled = sample_frames(store, result['extraction'], indices=chosen,
        holds=[[1, 24]] * len(chosen), loop=False,
        roles=['authored attack inspection'] * len(chosen))
    decision = store.get_json(sampled['decision'])
    assert [s['native_index'] for s in decision['samples']] == chosen
    assert all(s['raster'] == doc['frames'][s['native_index']]['raster'] for s in decision['samples'])


def test_oversize_frame_count_is_rejected_without_silent_truncation(store):
    if not shutil.which('ffmpeg'):
        pytest.skip('Local FFmpeg unavailable')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-f', 'lavfi',
        '-i', 'color=c=red:size=8x8:rate=24', '-frames:v', '513', '-c:v', 'ffv1',
        '-threads', '1', '-f', 'matroska', 'pipe:1'],
        capture_output=True, check=True, timeout=10).stdout
    with pytest.raises(VideoExtractionError, match='1..512') as error:
        extract_video(store, raw)
    receipt = store.get_json(error.value.receipt)
    assert store.get_bytes(receipt['media']) == raw


def test_two_simultaneous_threaded_decodes(store, encoded):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    barrier = Barrier(2)

    def work():
        barrier.wait(timeout=5)
        result = extract_video(store, encoded[0])
        seq, arrays = load_sequence(store, result['sequence'])
        assert all(np.array_equal(a, b) for a, b in zip(arrays, encoded[1]))
        return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(work) for _ in range(2)]
        results = [future.result(timeout=30) for future in futures]
    assert results[0] == results[1]


def test_missing_prlimit_clean_validation_with_retained_media(store, encoded, monkeypatch):
    original = shutil.which
    monkeypatch.setattr('sprite_workbench.motion_frames.shutil.which',
                        lambda name: None if name == 'prlimit' else original(name))
    with pytest.raises(ValidationError, match='prlimit is unavailable') as error:
        extract_video(store, encoded[0])
    assert isinstance(error.value, VideoExtractionError)
    receipt = store.get_json(error.value.receipt)
    assert store.get_bytes(receipt['media']) == encoded[0]
