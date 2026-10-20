"""Diagnostic recipes exercise retained controls, not generated character art."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.effects import render_effect
from sprite_workbench.source_controls import apply_controls, describe_controls, render_controlled_effect


def recipe():
    records = json.loads((Path(__file__).parent / 'fixtures/effects/reference-cases.json').read_text())
    return deepcopy(records['cases'][0]['recipe'])


def slider(path, *, mode='set', value=2, minimum=1, maximum=3, scale=1, offset=0):
    return {'id': 'adjust', 'label': 'Adjust', 'type': 'slider', 'value': value,
            'min': minimum, 'max': maximum, 'step': .25,
            'binds': [{'path': path, 'mode': mode, 'scale': scale, 'offset': offset}]}


def test_original_set_mapping_values_hashes_and_no_mutation():
    r = recipe()
    r['controls'] = [slider('layers.ring.radius', scale=2, offset=1)]
    before = deepcopy(r)
    result = apply_controls(r, {'adjust': 3})
    assert r == before
    assert result['recipe']['layers'][0]['radius'] == 7
    assert result['controls'][0]['value'] == 3
    assert result['renderer_input']['layers'][0]['radius'] == 10
    assert all(len(v) == 64 for v in result['hashes'].values())
    assert describe_controls(r)['controls'][0]['value'] == 2


@pytest.mark.parametrize(('base', 'mode', 'expected'), [
    ({'from': 2, 'to': 6}, 'mul', {'from': 4, 'to': 12}),
    ({'keys': [[0, 2], [1, 6]]}, 'add', {'keys': [[0, 4], [1, 8]]}),
    ({'expr': 'u', 'scale': 3, 'offset': 1}, 'mul', {'scale': 6, 'offset': 2}),
    ({'wave': {'mid': 5, 'amp': 2, 'cycles': 1, 'phase': 0}}, 'mul', {'wave': {'mid': 10, 'amp': 4}}),
])
def test_original_animated_forms(base, mode, expected):
    r = recipe(); r['layers'][0]['radius'] = base
    r['controls'] = [slider('layers.ring.radius', mode=mode)]
    result = apply_controls(r)['recipe']['layers'][0]['radius']
    for key, value in expected.items():
        if isinstance(value, dict):
            assert all(result[key][k] == v for k, v in value.items())
        else:
            assert result[key] == value


def test_original_pair_rounding_and_nested_key_binding():
    r = recipe()
    r['layers'] = [{'id': 'p', 'type': 'particles', 'count': 2, 'size': [1, 3]}]
    r['controls'] = [slider('layers.p.size', mode='mul', value=1.5, minimum=1, maximum=2)]
    assert apply_controls(r)['recipe']['layers'][0]['size'] == [2, 5]
    r = recipe(); r['layers'][0]['radius'] = {'keys': [[0, 2], [1, 6]]}
    r['controls'] = [slider('layers.ring.radius.keys.1.1')]
    assert apply_controls(r)['recipe']['layers'][0]['radius']['keys'][1] == [1, 2]


@pytest.mark.parametrize('mutation', ['range', 'missing', 'overlap', 'index', 'animated_set', 'unknown_id'])
def test_rejections_leave_caller_recipe_unchanged(mutation):
    r = recipe(); r['controls'] = [slider('layers.ring.radius')]; values = None
    if mutation == 'range': values = {'adjust': 99}
    elif mutation == 'missing': r['controls'][0]['binds'][0]['path'] = 'layers.missing.radius'
    elif mutation == 'index': r['controls'][0]['binds'][0]['path'] = 'layers.ring.life.2'
    elif mutation == 'overlap':
        r['controls'].append({**deepcopy(r['controls'][0]), 'id': 'other'})
    elif mutation == 'animated_set': r['layers'][0]['radius'] = {'from': 2, 'to': 6}
    elif mutation == 'unknown_id': values = {'absent': 1}
    before = deepcopy(r)
    with pytest.raises(ValidationError): apply_controls(r, values)
    assert r == before


def test_renderer_applies_mul_once_and_receipt_persists(tmp_path):
    r = recipe(); r['controls'] = [slider('layers.ring.radius', mode='mul')]
    store = Store(tmp_path)
    actual = render_controlled_effect(store, r, {'adjust': 3})
    direct = deepcopy(r); direct['controls'][0]['value'] = 3
    expected = render_effect(store, direct)
    _, actual_frames = load_sequence(store, actual['sequence'])
    _, expected_frames = load_sequence(store, expected['sequence'])
    assert all(np.array_equal(a, b) for a, b in zip(actual_frames, expected_frames))
    assert actual['controlled_recipe']['layers'][0]['radius'] == 30
    assert store.get_json(actual['control_receipt'])['kind'] == 'source-controls'
