"""Finite actual-preset regression, distinct from private constructor recovery.

The external retained research is required for these comparisons. Its absence
is a visible skip through the original-root fixture, never a claimed pass.
Opaque preview cells establish displayed RGB only, not alpha or clock identity.
"""
import base64
import copy
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, load_sequence
from sprite_workbench.effects import render_effect
from sprite_workbench.source_controls import apply_controls
from test_source_fidelity import original_root, original_method, oracle, sha


FIXTURES = Path(__file__).parent / 'fixtures/effects'
MANIFEST = json.loads((FIXTURES / 'retained-presets-complete.json').read_text())
CASES = MANIFEST['cases']


def retained(case, research):
    recipe_bytes = (research / case['recipe_path']).read_bytes()
    response_bytes = (research / case['response_path']).read_bytes()
    assert sha(recipe_bytes) == case['recipe_sha256']
    assert sha(response_bytes) == case['response_sha256']
    recipe = json.loads(recipe_bytes)
    response = json.loads(response_bytes)
    assert response['id'] == case['request_id']
    returned = json.JSONDecoder().raw_decode(response['result']['content'][0]['text'].split('\n', 1)[1])[0]
    assert recipe == returned
    pages = [base64.b64decode(block['data']) for block in response['result']['content'] if block['type'] == 'image']
    assert [sha(page) for page in pages] == case['preview_page_sha256']
    assert recipe['frames'] == case['frames']
    return recipe, pages


def test_complete_retained_presets_closed_finite_inventory():
    assert len(CASES) == 17
    assert len({row['name'] for row in CASES}) == 17
    assert {row['request_id'] for row in CASES} == set(range(109, 126))
    assert sum(len(row['preview_page_sha256']) for row in CASES) == 18
    assert sum(row['frames'] for row in CASES) == 162
    subject = MANIFEST['public_subject']
    raw = (FIXTURES / subject['file']).read_bytes()
    assert sha(raw) == subject['sha256']
    with Image.open(BytesIO(raw)) as image:
        assert image.size == (subject['width'], subject['height'])


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['name'])
def test_complete_presets_actual_recipe_metadata(original_root, case):
    retained(case, original_root)


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['name'])
def test_complete_presets_original_streams_and_actual_preview(tmp_path, original_root, case):
    recipe, pages = retained(case, original_root)
    before = copy.deepcopy(recipe)
    code, expected_controls = original_method(original_root, 'controls', recipe)
    assert code == 0
    controls = apply_controls(recipe)
    assert controls['normalized_recipe'] == expected_controls['normalized']
    assert controls['recipe'] == expected_controls['applied']
    assert recipe == before
    # The declaration is normalized and controls applied once. A normalized
    # receipt is not a re-entrant input (it can contain e.g. rng:null).
    render_input = controls['renderer_input']
    subject = None
    if case['subject_fixture']:
        subject = np.array(Image.open(FIXTURES / case['subject_fixture']).convert('RGBA'))
    expected = oracle(original_root, render_input, subject=subject)
    store = Store(tmp_path / 'store')
    actual = render_effect(store, render_input, subject=store.put_raster(subject) if subject is not None else None)
    assert actual['executed_modules'] == expected['executed']
    assert store.get_json(actual['recipe'])['normalized'] == expected['recipe']
    from fractions import Fraction
    for stream, ident in actual['streams'].items():
        doc, frames = load_sequence(store, ident)
        assert [frame.tobytes() for frame in frames] == [base64.b64decode(frame) for frame in expected['streams'][stream]]
        assert doc['metadata']['subject_box'] == expected['subjectBox']
        assert all(Fraction(*frame['duration']) == 1 / Fraction(str(expected['recipe']['fps'])) for frame in doc['frames'])
    _, frames = load_sequence(store, actual['streams']['frames'])
    assert len(frames) == case['frames']
    union = np.logical_or.reduce([frame[..., 3] > 0 for frame in frames])
    ys, xs = np.nonzero(union)
    assert len(xs), 'Reject vacuous empty-preview comparisons'
    policy = MANIFEST['preview_policy']
    pad, scale = policy['alpha_union_padding'], policy['scale']
    height, width = frames[0].shape[:2]
    box = (max(0, int(xs.min())-pad), max(0, int(ys.min())-pad), min(width, int(xs.max())+pad+1), min(height, int(ys.max())+pad+1))
    tile_w, tile_h = (box[2]-box[0])*scale, (box[3]-box[1])*scale
    yy, xx = np.indices((tile_h, tile_w))
    checker = (xx // policy['checker_size'] + yy // policy['checker_size']) % 2
    background = np.array(policy['checker_colors'], np.uint8)[checker]
    gutter, label = policy['gutter'], policy['label_height']
    index = 0
    for raw in pages:
        target = np.array(Image.open(BytesIO(raw)).convert('RGB'))
        columns, xrem = divmod(target.shape[1]-gutter, tile_w+gutter)
        rows, yrem = divmod(target.shape[0]-gutter, tile_h+gutter+label)
        assert xrem == yrem == 0
        assert columns > 0 and rows > 0
        for y in range(rows):
            for x in range(columns):
                if index >= len(frames):
                    break
                px, py = x*(tile_w+gutter)+gutter, y*(tile_h+gutter+label)+gutter+label
                cell = target[py:py+tile_h, px:px+tile_w]
                expected_cell = Image.fromarray(np.dstack([background, np.full((tile_h, tile_w), 255, np.uint8)]))
                expected_cell.alpha_composite(Image.fromarray(frames[index]).crop(box).resize((tile_w, tile_h), Image.Resampling.NEAREST))
                np.testing.assert_array_equal(np.array(expected_cell.convert('RGB')), cell)
                index += 1
    assert index == len(frames)
