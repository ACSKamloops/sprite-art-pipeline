"""Independent metadata round-trip/admission regressions; no artistic approval."""
from copy import deepcopy
from fractions import Fraction

import numpy as np
import pytest

from sprite_workbench import construction as c
from sprite_workbench.core import Store, ValidationError, load_sequence, save_sequence


def source_project(loop):
    return {
        'schema': 'sprite-edit-project/v1',
        'canvas': {'width': 3, 'height': 2, 'render_pivot': [1, 0], 'ground_pivot': [1, 2]},
        'palette': [[0, 0, 0, 0], [10, 20, 30, 255], [70, 80, 90, 127]],
        'layers': [{'id': 'art', 'name': 'Supplied art', 'locked': False}],
        'cels': {'a': {'layer_id': 'art', 'pixels': [1, 0, 2, 0, 1, 0]},
                 'b': {'layer_id': 'art', 'pixels': [0, 1, 2, 0, 1, 0]}},
        'frames': [{'id': 'contact', 'duration_ticks': 2, 'cels': {'art': 'a'}, 'landmarks': {'sole': [1, 1]}},
                   {'id': 'passing', 'duration_ticks': 6, 'cels': {'art': 'b'}, 'landmarks': {'sole': [2, 1]}}],
        'animations': [{'id': 'walk', 'frames': ['contact', 'passing', 'contact'],
                        'fps': 120, 'loop': loop,
                        'events': [{'at_tick': 0, 'name': 'start'}, {'at_tick': 2, 'name': 'pass'},
                                   {'at_tick': 9, 'name': 'last_hold'}]}],
    }


def rendered(store, loop=True):
    project = c.save_project(store, source_project(loop))
    seq = c.render_animation(store, project['project'], 'walk')['sequence']
    return seq


@pytest.mark.parametrize('loop', [False, True])
def test_construction_render_import_render_preserves_semantics_and_pixels(tmp_path, loop):
    store = Store(tmp_path / 'store')
    source = rendered(store, loop)
    before, before_pixels = load_sequence(store, source)
    imported = c.from_sequence(store, source, animation_id='reopened')
    project = c.load_project(Store(store.path), imported['project'])
    anim = project['animations'][0]
    assert project['canvas']['render_pivot'] == [1, 0]
    assert project['canvas']['ground_pivot'] == [1, 2]
    assert anim == {'id': 'reopened', 'frames': ['contact', 'passing', 'contact'], 'fps': 120,
                    'loop': loop, 'events': source_project(loop)['animations'][0]['events']}
    assert [f['id'] for f in project['frames']] == ['contact', 'passing']
    assert [f['duration_ticks'] for f in project['frames']] == [2, 6]
    assert [f['landmarks'] for f in project['frames']] == [{'sole': [1, 1]}, {'sole': [2, 1]}]
    after_id = c.render_animation(store, imported['project'], 'reopened')['sequence']
    after, after_pixels = load_sequence(store, after_id)
    assert [f['duration'] for f in after['frames']] == [[1, 60], [1, 20], [1, 60]]
    for key in ['fps', 'duration_ticks', 'frame_ids', 'landmarks', 'events', 'ground_pivot']:
        assert after['metadata'][key] == before['metadata'][key]
    assert [f['pivot'] for f in after['frames']] == [f['pivot'] for f in before['frames']]
    assert after['loop'] == before['loop'] and after['play_count'] == before['play_count']
    assert all(np.array_equal(a, b) for a, b in zip(before_pixels, after_pixels))
    assert c.from_sequence(Store(store.path), source, fps=120)['project']


@pytest.mark.parametrize('override', [
    {'fps': True}, {'fps': 0}, {'fps': None}, {'fps': 10 ** 400},
    {'duration_ticks': [2, 5, 2]}, {'duration_ticks': [2, True, 2]},
    {'duration_ticks': [2, 6]}, {'duration_ticks': None},
    {'ground_pivot': [1]}, {'ground_pivot': [1, 0.5]},
    {'landmarks': [{}, {}]}, {'landmarks': [{}, {'sole': [True, 1]}, {}]},
    {'frame_ids': ['same', 'same', 'same']}, {'frame_ids': ['a', 'b']},
    {'events': [{'at_tick': 10, 'name': 'outside'}]}, {'events': 'bad'},
])
def test_invalid_declared_metadata_rejects_before_new_store_artifacts(tmp_path, override):
    store = Store(tmp_path / 'store'); ident = rendered(store)
    doc = store.get_json(ident); doc['metadata'].update(deepcopy(override)); source = store.put_json(doc)
    inventory = {p.name for p in (store.path / 'blobs').iterdir()}
    with pytest.raises(ValidationError):
        c.from_sequence(store, source)
    assert {p.name for p in (store.path / 'blobs').iterdir()} == inventory


@pytest.mark.parametrize('field', ['fps', 'duration_ticks'])
def test_clock_declarations_cannot_be_silently_ignored(tmp_path, field):
    store = Store(tmp_path / 'store'); ident = rendered(store)
    if field == 'fps':
        doc = store.get_json(ident); del doc['metadata']['fps']; source = store.put_json(doc)
        with pytest.raises(ValidationError): c.from_sequence(store, source)
    else:
        with pytest.raises(ValidationError, match='conflicts'):
            c.from_sequence(store, ident, fps=60)


def test_plain_supplied_sequence_still_uses_exact_auto_clock_and_explicit_defaults(tmp_path):
    store = Store(tmp_path / 'store'); a = np.zeros((2, 3, 4), dtype=np.uint8); a[0, 0] = [7, 11, 13, 255]
    ident = save_sequence(store, [a, a], durations=[Fraction(1, 7), Fraction(2, 9)], pivots=[[1, 1]] * 2)
    imported = c.from_sequence(store, ident); p = c.load_project(store, imported['project'])
    assert p['animations'][0]['fps'] == 63
    assert [f['duration_ticks'] for f in p['frames']] == [9, 14]
    assert p['animations'][0]['events'] == []
    assert p['canvas']['ground_pivot'] == [1, 1]
    assert p['frames'][0]['cels'] == p['frames'][1]['cels']  # Shared scope remains explicit policy.
