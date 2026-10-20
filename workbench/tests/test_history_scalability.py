"""Independent scalar differential, cold replay and mutable-Store adversaries."""
import copy
import json
import random
import subprocess
import sys

import numpy as np
import pytest

from sprite_workbench import construction as c, construction_core as scalar
from sprite_workbench import construction_engine as fast
from sprite_workbench.core import Store, ValidationError, canonical_json, save_sequence


def project(seed=0, size=5, layers=3, frame_count=5):
    rng = random.Random(seed)
    palette = [[0, 0, 0, 0], [11, 22, 33, 0], [1, 2, 3, 255], [1, 2, 3, 255]]
    palette += [[rng.randrange(256) for _ in range(3)]+[alpha] for alpha in [1, 2, 127, 128, 254, 255]]
    return {'schema': 'sprite-edit-project/v1',
        'canvas': {'width': size, 'height': size, 'render_pivot': [2, -1], 'ground_pivot': [2, size]},
        'palette': palette,
        'layers': [{'id': str(i), 'name': 'layer '+str(i), 'locked': False} for i in range(layers)],
        'cels': {str(i): {'layer_id': str(i), 'pixels': [rng.randrange(len(palette)) for _ in range(size*size)]} for i in range(layers)},
        'frames': [{'id': str(i), 'duration_ticks': i+1,
                    'cels': {str(j): str(j) for j in range(layers) if i < 2 or (i+j)%3},
                    'landmarks': {}} for i in range(frame_count)],
        'animations': [{'id': 'test', 'frames': [str(i) for i in range(frame_count)],
                        'fps': 60, 'loop': True, 'events': [{'at_tick': 0, 'name': 'start'}]}]}


def tx(p, ops):
    return {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': scalar.project_hash(p),
            'reason': 'independent integer-compositor oracle', 'operations': ops}


@pytest.mark.parametrize('seed', range(12))
def test_all_operation_receipts_exactly_equal_pinned_scalar(seed):
    p = project(seed)
    operations = [
        [{'op': 'paint', 'cel_id': '0', 'points': [[0, 0, 3], [4, 4, 7]]}],
        [{'op': 'erase', 'cel_id': '1', 'points': [[1, 1], [0, 3]]}],
        [{'op': 'replace_color', 'cel_id': '0', 'from_index': 2, 'to_index': 3, 'mask': [[x, y] for y in range(5) for x in range(5)]}],
        [{'op': 'translate', 'cel_id': '1', 'dx': -1, 'dy': 1, 'allow_clip': True}],
        [{'op': 'translate_layer', 'layer_id': '0', 'dx': 2, 'dy': 0, 'allow_clip': True}],
        [{'op': 'palette', 'index': 2, 'rgba': [255, 22, 17, 128]}],
        [{'op': 'palette_add', 'rgba': [8, 9, 10, 0]}],
        [{'op': 'frame_timing', 'frame_id': '0', 'duration_ticks': 47}],
        [{'op': 'pivots', 'render_pivot': [-4, 7], 'ground_pivot': [2, 9]}],
    ]
    candidate = copy.deepcopy(p['cels']['2']['pixels']); candidate[7] = 2
    operations += [[{'op': 'candidate_patch', 'cel_id': '2', 'mask': [[2, 1]],
                     'candidate_pixels': candidate, 'expected_cel_sha256': scalar.cel_hash(p, '2')}]]
    for ops in operations:
        transaction = tx(p, ops)
        a = scalar.apply_transaction(p, transaction)
        b = fast.apply_transaction(p, transaction)
        assert canonical_json(a) == canonical_json(b)
    bindings = [str(i) for i in range(3)]
    expected = np.asarray(scalar.render_frame(p, '0')).reshape(-1, 4)
    assert np.array_equal(expected, fast.composite(p, bindings))


def test_every_source_destination_alpha_pair_and_chunk_boundary():
    # Exercise all 65,536 alpha pairs, and a pixel in a second compositor chunk.
    p = project(layers=2, frame_count=1)
    p['canvas'].update(width=65537, height=1)
    p['palette'] = [[0, 0, 0, 0]]
    p['palette'] += [[255, 1, 249, alpha] for alpha in range(256)]
    p['palette'] += [[17, 242, 3, alpha] for alpha in range(256)]
    p['cels']['0']['pixels'] = [257+da for da in range(256) for _sa in range(256)]+[384]
    p['cels']['1']['pixels'] = [1+sa for _da in range(256) for sa in range(256)]+[129]
    expected = np.asarray(scalar.render_frame(p, '0')).reshape(-1, 4)
    assert np.array_equal(expected, fast.composite(p, ['0', '1']))


def edited(store, count=3):
    p = project(); state = c.create_history(store, c.save_project(store, p)['project'])
    for i in range(count):
        result = c.edit_history(store, state['history'], tx(p, [{'op': 'paint', 'cel_id': '0', 'points': [[i, 0, 2]]}]))
        p = c.load_project(store, result['project']); state = result
    return state


def test_cold_replay_proven_without_trusting_warm_proofs(tmp_path, monkeypatch):
    store = Store(tmp_path); state = edited(store)
    c.clear_history_proofs()
    original = fast.apply_transaction; calls = []
    def counted(*args):
        calls.append(1); return original(*args)
    monkeypatch.setattr(fast, 'apply_transaction', counted)
    assert c.load_history(Store(tmp_path), state['history'])['project'] == state['project']
    assert len(calls) == 3
    calls.clear()
    c.load_history(store, state['history'])
    assert calls == []
    completed = subprocess.run([sys.executable, '-c',
        'import sys,json;from sprite_workbench.construction import load_history;from sprite_workbench.core import Store;'
        'print(json.dumps(load_history(Store(sys.argv[1]),sys.argv[2])))', str(tmp_path), state['history']],
        check=True, capture_output=True, text=True)
    assert json.loads(completed.stdout)['project_hash'] == state['project_hash']


@pytest.mark.parametrize('target', ['initial', 'intermediate', 'current'])
def test_warm_proof_still_rehashes_every_checkpoint(tmp_path, target):
    store = Store(tmp_path); state = edited(store)
    doc = store.get_json(state['history'])
    key = doc['checkpoints'][{'initial': 0, 'intermediate': 1, 'current': -1}[target]]
    path = store.path/'blobs'/key; path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(ValidationError, match='integrity|JSON document'):
        c.load_history(store, state['history'])


def test_cached_source_raster_closure_integrity(tmp_path):
    store = Store(tmp_path); array = np.zeros((2, 2, 4), np.uint8); array[0, 0] = [17, 27, 33, 255]
    source = save_sequence(store, [array], pivots=[(0, 0)])
    imported = c.from_sequence(store, source)
    state = c.create_history(store, imported['project'])
    sequence = store.get_json(source); raster = store.get_json(sequence['frames'][0]['raster'])
    (store.path/'blobs'/raster['blob']).write_bytes(b'corrupt')
    with pytest.raises(ValidationError, match='integrity|JSON document'):
        c.load_history(store, state['history'])


@pytest.mark.parametrize('target', ['checkpoint_order', 'checkpoint_substitute', 'receipt_bool', 'source_change', 'trailing_key'])
def test_validly_hashed_forgeries_replay_rejects(tmp_path, target):
    store = Store(tmp_path); state = edited(store)
    doc = store.get_json(state['history'])
    if target == 'checkpoint_order':
        doc['checkpoints'][1:3] = reversed(doc['checkpoints'][1:3])
    elif target == 'checkpoint_substitute':
        raw = c.load_project(store, doc['checkpoints'][1]); raw['palette'][1] = [29, 29, 29, 0]
        doc['checkpoints'][1] = c.save_project(store, raw)['project']
    elif target == 'receipt_bool':
        receipt = doc['journal']['receipts'][0]
        receipt['diff']['cels']['0']['changed_pixels'] = True
    elif target == 'source_change':
        raw = store.get_json(doc['checkpoints'][1]); raw['source_sequence'] = save_sequence(store, [np.zeros((2, 2, 4), np.uint8)])
        doc['checkpoints'][1] = store.put_json(raw)
    else:
        doc['checkpoints'].append(doc['project'])
    ident = store.put_json(doc)
    with pytest.raises(ValidationError):
        c.load_history(store, ident)


def test_legacy_load_read_only_exact_and_mutation_migrates(tmp_path, monkeypatch):
    store = Store(tmp_path); p = project(); initial = c.save_project(store, p)
    history = scalar.History(p)
    for i in range(2):
        history.apply(tx(history.project, [{'op': 'paint', 'cel_id': '0', 'points': [[i, 0, 2]]}]))
    saved = c.save_project(store, history.project)
    doc = {'kind': 'construction-history', 'version': 1, 'initial_project': initial['project'],
           **saved, 'journal': history.journal()}
    old = store.put_json(doc); before = set((store.path/'blobs').iterdir())
    assert c.load_history(store, old)['project'] == saved['project']
    assert set((store.path/'blobs').iterdir()) == before
    moved = c.move_history(store, old, 'undo')
    assert store.get_json(moved['history'])['version'] == 2
    c.clear_history_proofs()
    redone = c.move_history(Store(tmp_path), moved['history'], 'redo')
    assert redone['project'] == saved['project']
    monkeypatch.setattr(c, 'MAX_RENDER_WORK', 1500)
    with pytest.raises(ValidationError, match='journal replay work'):
        c.load_history(store, old)


def test_v2_peak_and_byte_and_cold_work_caps(tmp_path, monkeypatch):
    store = Store(tmp_path); state = edited(store)
    for name, value, message in [('MAX_HISTORY_CEL_VALUES', 200, 'snapshot index'),
                                 ('MAX_HISTORY_CHECKPOINT_BYTES', 100, 'checkpoint byte'),
                                 ('MAX_HISTORY_REPLAY_WORK', 10, 'replay work')]:
        with monkeypatch.context() as scoped:
            scoped.setattr(c, name, value)
            with pytest.raises(ValidationError, match=message):
                c.load_history(store, state['history'])


def test_legacy_migration_rejects_changed_typed_source_before_writing(tmp_path):
    store = Store(tmp_path); p = project(); initial = c.save_project(store, p)
    history = scalar.History(p)
    history.apply(tx(p, [{'op': 'pivots', 'render_pivot': [1, 2], 'ground_pivot': [2, 3]}]))
    source = save_sequence(store, [np.zeros((2, 2, 4), np.uint8)])
    current = c._save_project(store, history.project, source_sequence=source)
    old = store.put_json({'kind': 'construction-history', 'version': 1,
        'initial_project': initial['project'], **current, 'journal': history.journal()})
    # Preserve the old v1 read contract; refuse a v2 migration that would fail
    # its stricter unchanged-source chain when subsequently loaded cold.
    assert c.load_history(store, old)['project'] == current['project']
    before = set((store.path/'blobs').iterdir())
    with pytest.raises(ValidationError, match='migration source'):
        c.move_history(store, old, 'undo')
    assert set((store.path/'blobs').iterdir()) == before


def test_undo_branch_does_not_retain_abandoned_checkpoint(tmp_path):
    store = Store(tmp_path); state = edited(store)
    undone = c.move_history(store, state['history'], 'undo')
    p = c.load_project(store, undone['project'])
    branch = c.edit_history(store, undone['history'], tx(p, [{'op': 'pivots', 'render_pivot': [9, 9], 'ground_pivot': [9, 12]}]))
    doc = store.get_json(branch['history'])
    assert state['project'] not in doc['checkpoints']
    c.clear_history_proofs()
    assert c.load_history(store, branch['history'])['project'] == branch['project']
    with pytest.raises(ValidationError, match='Nothing to redo'):
        c.move_history(store, branch['history'], 'redo')


def test_repeated_identical_checkpoints_use_unique_byte_budget_cold_and_warm(tmp_path, monkeypatch):
    store = Store(tmp_path); p = project()
    state = c.create_history(store, c.save_project(store, p)['project'])
    initial_project_id = state['project']
    bytes_one_project = len(store.get_bytes(initial_project_id))
    monkeypatch.setattr(c, 'MAX_HISTORY_CHECKPOINT_BYTES', bytes_one_project+1)
    for _ in range(3):
        state = c.edit_history(store, state['history'], tx(p, [{'op': 'pivots',
            'render_pivot': p['canvas']['render_pivot'], 'ground_pivot': p['canvas']['ground_pivot']}]))
        assert state['project'] == initial_project_id
    c.clear_history_proofs()
    assert c.load_history(store, state['history'])['project'] == initial_project_id
