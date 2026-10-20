"""Selected source-handler parity; this does not prove private reducer behavior."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

import numpy as np
import pytest

from sprite_workbench.core import ValidationError
from sprite_workbench import parity_palette

ASSET = Path(os.environ.get('PIXELLAB_PALETTE_ORIGINAL',
    '/home/astra/artifacts/pixellab-recovery-web-20261014/assets/2713c302f049-create-9c5cec3372075418.js'))


def oracle(rgba):
    if not ASSET.exists():
        pytest.skip('Retained original asset unavailable; set PIXELLAB_PALETTE_ORIGINAL')
    if not shutil.which('node'):
        pytest.skip('Original JavaScript execution requires Node')
    request = {'width': rgba.shape[1], 'height': rgba.shape[0], 'rgba': rgba.reshape(-1).tolist()}
    result = subprocess.run(['node', str(Path(__file__).with_name('parity_palette_oracle.cjs')), str(ASSET)],
        input=json.dumps(request), capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def fixture(name):
    if name == 'transparent':
        return np.array([[[199,11,29,0],[0,255,0,0]]], np.uint8)
    if name == 'one-rgb-multiple-alpha':
        return np.array([[[31,42,53,1],[31,42,53,127],[31,42,53,255]]], np.uint8)
    if name == 'first-seen-partial':
        return np.array([[[199,11,29,0],[90,2,7,1],[1,18,255,255],[90,2,7,255]]],np.uint8)
    if name == 'one-5bit-bin':
        values = [[r,g,b,255] for r in range(8) for g in range(8) for b in range(8)]
        return np.array(values,np.uint8).reshape(16,32,4)
    size = {'threshold256':256,'threshold257':257,'many4096':4096,'many4096-reversed':4096}[name]
    values = [[(i*71)%256, (i//256*19+i*7)%256, (i//256*53+i*13)%256, [1,127,255][i%3]] for i in range(size)]
    if name.endswith('reversed'):
        values.reverse()
    return np.array(values,np.uint8).reshape(1,size,4)


@pytest.mark.parametrize('name',['transparent','one-rgb-multiple-alpha','first-seen-partial',
    'threshold256','threshold257','one-5bit-bin','many4096','many4096-reversed'])
def test_exact_original_factory_handler_outcomes(name):
    rgba = fixture(name); before = rgba.copy()
    expected = oracle(rgba)
    actual = parity_palette.import_palette_image(rgba)
    assert {k:actual[k] for k in ('colors','warning','error')} == expected
    assert actual['accepted'] is (expected['error'] is None)
    assert np.array_equal(rgba,before)
    assert actual['adapter']['source_rgba_sha256'] == hashlib.sha256(rgba.tobytes()).hexdigest()


def test_original_manifest_slices_match_actual_bundle_bytes():
    if not ASSET.exists():
        pytest.skip('Original source unavailable')
    raw = ASSET.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == parity_palette.SOURCE_SHA256
    manifest = json.loads(Path(parity_palette.__file__).with_name('parity_palette_source.json').read_text())
    for part in manifest['parts']:
        start,end = part['utf8_range']
        assert raw[start:end].decode() == part['text']
        assert hashlib.sha256(raw[start:end]).hexdigest() == part['sha256']


def test_source_first_seen_and_alpha_rule_are_explicit():
    actual = parity_palette.import_palette_image(fixture('first-seen-partial'))
    assert actual['colors'] == ['#5a0207','#0112ff']
    assert actual['palette_rgba'] == [[90,2,7,255],[1,18,255,255]]
    assert actual['adapter']['unique_visible_rgb'] == 2
    assert actual['warning'] is None


def test_exact_threshold_does_not_reduce_256_colors():
    source = fixture('threshold256')
    actual = parity_palette.import_palette_image(source)
    assert len(actual['colors']) == 256
    assert actual['adapter']['branch'] == 'original-first-seen'
    assert actual['colors'][0] == '#000000'
    reduced = parity_palette.import_palette_image(fixture('threshold257'))
    assert reduced['adapter']['unique_visible_rgb'] == 257
    assert reduced['adapter']['branch'] == 'original-32-representatives'
    assert len(reduced['colors']) <= 32
    assert '257' in reduced['warning']


def test_original_single_bin_degeneracy_is_not_repaired():
    outcome = parity_palette.import_palette_image(fixture('one-5bit-bin'))
    assert outcome['accepted'] is False
    assert outcome['colors'] == []
    assert outcome['error'] == 'The image has 1 colour; a palette needs at least 2.'


@pytest.mark.parametrize('value',[np.zeros((1,1,3),np.uint8),np.zeros((1,1,4),np.float64),
                                 np.zeros((513,512,4),np.uint8)])
def test_invalid_or_over_budget_input_rejects(value):
    with pytest.raises(ValidationError):
        parity_palette.import_palette_image(value)


def test_canvas_readback_boundary_is_not_raw_png_codec_parity():
    # Retained real Chromium diagnostic: alpha1 RGB is rounded by canvas. Do not
    # implement guessed PNG premultiplication in this palette-only operation.
    readback = np.array([[[0,0,0,0],[0,0,0,1],[1,18,255,255],[90,2,7,255]]],np.uint8)
    result = parity_palette.import_palette_image(readback)
    assert result['colors'] == ['#000000','#0112ff','#5a0207']
    assert {k:result[k] for k in ('colors','warning','error')} == oracle(readback)
    assert result['colors'] != parity_palette.import_palette_image(fixture('first-seen-partial'))['colors']


def test_receipt_and_execution_share_input_snapshot(monkeypatch):
    source = np.array([[[255,0,0,255],[0,255,0,255]]], np.uint8)
    submitted = source.copy()
    original_run = parity_palette.subprocess.run
    def mutate_after_execution(*args, **kwargs):
        completed = original_run(*args, **kwargs)
        source[:] = [0,0,255,255]
        return completed
    monkeypatch.setattr(parity_palette.subprocess, 'run', mutate_after_execution)
    result = parity_palette.import_palette_image(source)
    assert result['colors'] == ['#ff0000','#00ff00']
    assert result['adapter']['unique_visible_rgb'] == 2
    assert result['adapter']['source_rgba_sha256'] == hashlib.sha256(submitted.tobytes()).hexdigest()
    assert result['adapter']['source_rgba_sha256'] != hashlib.sha256(source.tobytes()).hexdigest()
