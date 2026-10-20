"""Independent checkpoint-history counterexamples and small explicit oracles.

No producer fixtures or randomized scalar differential helpers are reused.
The tests exercise public history operations, immutable Store boundaries and
portable closure; private instrumentation only measures replay object retention.
"""
import gc
import weakref

import numpy as np
import pytest

from sprite_workbench import construction as c, construction_core as scalar
from sprite_workbench import construction_engine as engine
from sprite_workbench.construction_services import invoke_construction
from sprite_workbench.core import Store, ValidationError, save_sequence
from sprite_workbench.export import export_sequence, import_editable


def drawing():
    return {'schema': 'sprite-edit-project/v1',
        'canvas': {'width': 3, 'height': 2, 'render_pivot': [-1, 2], 'ground_pivot': [1, 3]},
        'palette': [[0, 0, 0, 0], [255, 0, 0, 255], [255, 0, 0, 255],
                    [19, 37, 61, 0], [255, 0, 0, 128], [0, 0, 255, 128]],
        'layers': [{'id': 'body', 'name': 'Body', 'locked': False},
                   {'id': 'detail', 'name': 'Detail', 'locked': False}],
        'cels': {'shared': {'layer_id': 'body', 'pixels': [1, 0, 4, 0, 0, 0]},
                 'top': {'layer_id': 'detail', 'pixels': [0, 0, 5, 0, 0, 0]}},
        'frames': [{'id': 'a', 'duration_ticks': 3, 'cels': {'body': 'shared', 'detail': 'top'}, 'landmarks': {'hand': [2, 0]}},
                   {'id': 'b', 'duration_ticks': 7, 'cels': {'body': 'shared'}, 'landmarks': {}}],
        'animations': [{'id': 'walk', 'frames': ['a', 'b', 'a'], 'fps': 60,
                        'loop': True, 'events': [{'at_tick': 3, 'name': 'contact'}]}],
        'provenance': {'kind': 'independent mechanical discriminator; not character art'}}


def transaction(p, operations):
    return {'schema': 'sprite-edit-transaction/v1',
            'expected_project_sha256': scalar.project_hash(p),
            'reason': 'Independent checkpoint review', 'operations': operations}


def initial(store, p=None):
    p = drawing() if p is None else p
    return c.create_history(store, c.save_project(store, p)['project'])


def change(store, state, operations):
    p = c.load_project(store, state['project'])
    return c.edit_history(store, state['history'], transaction(p, operations))


def history_chain(store, count=4):
    state = initial(store)
    for i in range(count):
        state = change(store, state, [{'op': 'pivots', 'render_pivot': [i, -i], 'ground_pivot': [2, i + 3]}])
    return state


def test_explicit_alias_hidden_color_and_integer_composite_oracles(tmp_path):
    store = Store(tmp_path); p = drawing()
    pixels = np.asarray(scalar.render_frame(p, 'a'))
    assert pixels[0].tolist() == [[255, 0, 0, 255], [0, 0, 0, 0], [85, 0, 170, 192]]
    state = initial(store, p)
    result = change(store, state, [{'op': 'paint', 'cel_id': 'shared', 'points': [[0, 0, 2], [1, 0, 3]]}])
    assert result['receipt']['diff']['cels'] == {'shared': {'changed_pixels': 2, 'coordinates': [[0, 0], [1, 0]]}}
    assert result['receipt']['diff']['frames'] == {}
    assert result['receipt']['diff']['unchanged_frames'] == ['a', 'b']
    c.clear_history_proofs()
    restored = c.load_project(Store(tmp_path), c.load_history(Store(tmp_path), result['history'])['project'])
    assert restored['cels']['shared']['pixels'][:2] == [2, 3]
    assert restored['palette'][3] == [19, 37, 61, 0]
    assert restored['frames'] == p['frames'] and restored['animations'] == p['animations']
    assert c.move_history(store, result['history'], 'undo')['project'] == state['project']


@pytest.mark.parametrize('mutation', ['kind', 'version_bool', 'version_float', 'project_hash', 'document_extra'])
def test_rehashed_malformed_checkpoint_envelopes_rejected_cold(tmp_path, mutation):
    store = Store(tmp_path); state = history_chain(store)
    history = store.get_json(state['history']); project = store.get_json(history['checkpoints'][1])
    if mutation == 'kind': project['kind'] = 'sequence'
    elif mutation == 'version_bool': project['version'] = True
    elif mutation == 'version_float': project['version'] = 1.0
    elif mutation == 'project_hash': project['project_hash'] = '0' * 64
    else: project['unexpected'] = 'a typed envelope must have exact fields'
    history['checkpoints'][1] = store.put_json(project)
    forged = store.put_json(history)
    c.clear_history_proofs()
    with pytest.raises(ValidationError): c.load_history(store, forged)


def test_replay_verifies_the_redo_tail_while_cursor_is_undone(tmp_path):
    store = Store(tmp_path); state = history_chain(store)
    state = c.move_history(store, state['history'], 'undo')
    history = store.get_json(state['history'])
    assert history['journal']['cursor'] < len(history['journal']['receipts'])
    history['journal']['receipts'][-1]['after_sha256'] = '0' * 64
    forged = store.put_json(history)
    c.clear_history_proofs()
    with pytest.raises(ValidationError, match='exact replay receipt'):
        c.load_history(store, forged)


def test_warm_proof_has_no_cross_store_authority_and_checks_missing_dependency(tmp_path, monkeypatch):
    original = Store(tmp_path / 'original'); state = history_chain(original)
    destination = Store(tmp_path / 'copied')
    for blob in (original.path / 'blobs').iterdir(): destination.put_bytes(blob.read_bytes())
    calls = []
    apply = engine.apply_transaction
    def counted(*args): calls.append(1); return apply(*args)
    monkeypatch.setattr(engine, 'apply_transaction', counted)
    assert c.load_history(destination, state['history'])['project'] == state['project']
    assert len(calls) == 4
    checkpoint = destination.get_json(state['history'])['checkpoints'][2]
    (destination.path / 'blobs' / checkpoint).unlink()
    with pytest.raises(ValidationError): c.load_history(destination, state['history'])


def test_source_sequence_raster_envelope_and_raw_blob_rehashed_on_warm_use(tmp_path, monkeypatch):
    store = Store(tmp_path); pixels = np.zeros((2, 3, 4), np.uint8); pixels[0, 0] = [4, 7, 9, 255]
    sequence = save_sequence(store, [pixels], pivots=[(-1, 2)])
    project = c.from_sequence(store, sequence); state = c.create_history(store, project['project'])
    raster = store.get_json(sequence)['frames'][0]['raster']; raw = store.get_json(raster)['blob']
    reads = set(); get_bytes = store.get_bytes
    def counted(ident, **kwargs): reads.add(ident); return get_bytes(ident, **kwargs)
    monkeypatch.setattr(store, 'get_bytes', counted)
    c.load_history(store, state['history'])
    assert {sequence, raster, raw, state['project'], state['history']} <= reads
    (store.path / 'blobs' / raster).write_bytes(b'{}')
    with pytest.raises(ValidationError): c.move_history(store, state['history'], 'undo')


def test_cold_replay_releases_old_project_objects_and_cache_keeps_ids(tmp_path, monkeypatch):
    store = Store(tmp_path); state = history_chain(store, count=18)
    c.clear_history_proofs(); refs = []; peak = 0; calls = 0
    class TrackedProject(dict): pass
    project_document = c._project_document
    apply = engine.apply_transaction
    def record(value):
        nonlocal peak
        tracked = TrackedProject(value); refs.append(weakref.ref(tracked))
        peak = max(peak, sum(ref() is not None for ref in refs))
        return tracked
    def tracked_document(*args):
        doc = project_document(*args); doc['document'] = record(doc['document']); return doc
    def tracked_apply(*args):
        nonlocal calls
        calls += 1; result = apply(*args); result['project'] = record(result['project']); return result
    monkeypatch.setattr(c, '_project_document', tracked_document)
    monkeypatch.setattr(engine, 'apply_transaction', tracked_apply)
    assert c.load_history(store, state['history'])['project'] == state['project']
    gc.collect()
    assert calls == 18
    assert peak <= 5, 'Cold replay must not retain one full project object per historical edit'
    assert not any(ref() is not None for ref in refs), 'Proof cache must retain artifact identities, not decoded project objects'


def test_undo_branch_portable_closure_contains_every_retained_checkpoint(tmp_path):
    store = Store(tmp_path / 'source'); state = history_chain(store)
    original = state
    undone = c.move_history(store, state['history'], 'undo')
    branch = change(store, undone, [{'op': 'paint', 'cel_id': 'shared', 'points': [[1, 1, 2]]}])
    history = store.get_json(branch['history'])
    assert original['project'] not in history['checkpoints']
    rendered = invoke_construction(store, 'render', {'project': branch['project'], 'history': branch['history'], 'animation_id': 'walk'})
    export_sequence(store, rendered['sequence'], tmp_path / 'package', ['editable'])
    destination = Store(tmp_path / 'fresh'); imported = import_editable(destination, tmp_path / 'package' / 'editable')
    assert imported == rendered['sequence']
    for checkpoint in history['checkpoints']: assert destination.get_bytes(checkpoint) == store.get_bytes(checkpoint)
    c.clear_history_proofs()
    assert c.load_history(destination, branch['history'])['project'] == branch['project']
    moved = branch
    for expected in reversed(history['checkpoints'][:-1]):
        moved = c.move_history(destination, moved['history'], 'undo'); assert moved['project'] == expected
    for expected in history['checkpoints'][1:]:
        moved = c.move_history(destination, moved['history'], 'redo'); assert moved['project'] == expected
    assert store.get_json(original['history'])['project'] == original['project']


def inconsistent_legacy_source(store):
    p = drawing(); old = scalar.History(p)
    old.apply(transaction(p, [{'op': 'paint', 'cel_id': 'shared', 'points': [[1, 1, 1]]}]))
    first = c.save_project(store, p); current = c.save_project(store, old.project)
    source = save_sequence(store, [np.zeros((2, 3, 4), np.uint8)])
    envelope = store.get_json(current['project']); envelope['source_sequence'] = source
    current['project'] = store.put_json(envelope)
    return store.put_json({'kind': 'construction-history', 'version': 1,
                          'initial_project': first['project'], **current, 'journal': old.journal()})


@pytest.mark.parametrize('method', ['move', 'edit'])
def test_inconsistent_legacy_provenance_remains_readable_but_cannot_emit_warm_only_v2(tmp_path, method):
    store = Store(tmp_path); legacy = inconsistent_legacy_source(store)
    state = c.load_history(store, legacy)
    before = {blob.name for blob in (store.path / 'blobs').iterdir()}
    with pytest.raises(ValidationError, match='migration source sequence mismatch'):
        if method == 'move': c.move_history(store, legacy, 'undo')
        else: change(store, state, [{'op': 'pivots', 'render_pivot': [4, 4], 'ground_pivot': [1, 3]}])
    assert {blob.name for blob in (store.path / 'blobs').iterdir()} == before
    c.clear_history_proofs(); assert c.load_history(store, legacy)['project'] == state['project']
