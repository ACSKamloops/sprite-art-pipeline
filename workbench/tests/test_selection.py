"""Actual recovered Godot selection plus guarded local history, supplied markers only."""
import base64
import copy
from io import BytesIO
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image
import pytest

from sprite_workbench import construction, construction_core as toolkit, selection
from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, canonical_json, digest
from sprite_workbench.selection_services import invoke_selection


def project():
    return {'schema': 'sprite-edit-project/v1',
        'canvas': {'width': 4, 'height': 3, 'render_pivot': [2, 1], 'ground_pivot': [2, 3]},
        'palette': [[0, 0, 0, 0], [255, 0, 0, 255], [0, 0, 255, 255],
                    [0, 255, 0, 128], [255, 0, 0, 255], [11, 22, 33, 0]],
        'layers': [{'id': 'back', 'name': 'Back', 'locked': False}, {'id': 'front', 'name': 'Front', 'locked': False}],
        'cels': {'a': {'layer_id': 'back', 'pixels': [0, 1, 0, 0, 0, 1, 4, 0, 0, 0, 5, 3]},
                 'b': {'layer_id': 'front', 'pixels': [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0]}},
        'frames': [{'id': 'f0', 'duration_ticks': 1, 'cels': {'back': 'a', 'front': 'b'}, 'landmarks': {}},
                   {'id': 'f1', 'duration_ticks': 1, 'cels': {'back': 'a'}, 'landmarks': {}}],
        'animations': [{'id': 'clip', 'frames': ['f0', 'f1'], 'fps': 12, 'loop': True, 'events': []}]}


@pytest.fixture
def prepared(tmp_path):
    store = Store(tmp_path / 'store')
    saved = construction.save_project(store, project())
    history = construction.create_history(store, saved['project'])
    selected = invoke_selection(store, 'create', {'project': saved['project'], 'cel_id': 'a', 'seed': [1, 1], 'tolerance': 0})
    return store, saved, history, selected


def test_actual_original_selector_targets_cel_not_composite_and_preserves_aliases(prepared):
    store, saved, _, selected = prepared
    doc, mask = selection.load_selection(store, selected['selection'])
    assert doc['selected_pixels'] == 3
    assert np.argwhere(mask[..., 3]).tolist() == [[0, 1], [1, 1], [1, 2]]
    assert np.all(mask[..., :3] == 255)  # Includes unselected transparent white.
    assert selected['shared_frames'] == ['f0', 'f1']
    assert doc['source_cel_rgba_sha256'] == digest(np.array(toolkit.render_cel(project(), 'a')).tobytes())
    assert construction.load_project(store, saved['project']) == project()
    assert doc['source_provenance']['files']['similar_colors.gd.fragment'] == '5c69c15d8218ee0ec1a6f752eeb032d42cde9c337beaf424faa624f51f9a1e9f'


def test_masked_erase_paint_undo_redo_preserve_indices_alpha_aliasing(prepared):
    store, saved, history, selected = prepared
    erased = invoke_selection(store, 'apply', {'history': history['history'], 'selection': selected['selection'], 'action': 'erase'})
    result = construction.load_project(store, erased['project'])
    expected = project()
    for i in [1, 5, 6]:
        expected['cels']['a']['pixels'][i] = 0
    assert result == expected and erased['changed_indices'] == 3
    assert result['cels']['a']['pixels'][10:] == [5, 3]  # Hidden RGB + partial alpha outside.
    assert store.get_json(erased['selection_receipt'])['outside_indices_and_rgba_preserved']
    undone = construction.move_history(store, erased['history'], 'undo')
    assert undone['project'] == saved['project']
    assert construction.load_project(store, undone['project']) == project()  # Restores1/4 aliases.
    redone = construction.move_history(store, undone['history'], 'redo')
    assert redone['project'] == erased['project']
    painted = invoke_selection(store, 'apply', {'history': undone['history'], 'selection': selected['selection'],
        'action': 'paint', 'palette_index': 3})
    output = construction.load_project(store, painted['project'])
    assert [output['cels']['a']['pixels'][i] for i in [1, 5, 6]] == [3, 3, 3]
    assert output['palette'][3][3] == 128  # No forced opaque conversion.
    assert output['cels']['b'] == project()['cels']['b'] and output['frames'] == project()['frames']
    assert selection.load_selection(Store(store.path), selected['selection'])[0]['shared_frames'] == ['f0', 'f1']


def test_stale_project_and_alias_only_change_fail_before_edit_or_new_blobs(prepared, monkeypatch):
    store, _, history, selected = prepared
    p = project()
    # Same RGBA, different index alias. The project guard must still fail.
    p['cels']['a']['pixels'][1] = 4
    saved = construction.save_project(store, p)
    changed = construction.create_history(store, saved['project'])
    monkeypatch.setattr(construction, 'edit_history', lambda *_: pytest.fail('Stale edit reached mutation'))
    count = len(list((store.path / 'blobs').iterdir()))
    with pytest.raises(ValidationError, match='Stale selection'):
        selection.apply_selection(store, changed['history'], selected['selection'], 'erase')
    assert len(list((store.path / 'blobs').iterdir())) == count


def test_unrelated_cel_change_also_requires_reselection(prepared):
    store, _, history, selected = prepared
    p = project()
    tx = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': construction.project_hash(p),
          'reason': 'supplied marker', 'operations': [{'op': 'erase', 'cel_id': 'b', 'points': [[1, 1]]}]}
    changed = construction.edit_history(store, history['history'], tx)
    with pytest.raises(ValidationError, match='Stale selection'):
        selection.apply_selection(store, changed['history'], selected['selection'], 'erase')


def test_empty_mask_rejected_before_mutation(prepared, monkeypatch):
    store, _, history, selected = prepared
    doc = store.get_json(selected['selection'])
    mask = np.full((3, 4, 4), 255, dtype=np.uint8)
    mask[..., 3] = 0
    doc.update(mask_raster=store.put_raster(mask), mask_rgba_sha256=digest(mask.tobytes()), selected_pixels=0)
    ident = store.put_json(doc)
    monkeypatch.setattr(construction, 'edit_history', lambda *_: pytest.fail('Empty edit reached mutation'))
    count = len(list((store.path / 'blobs').iterdir()))
    with pytest.raises(ValidationError, match='empty selection'):
        selection.apply_selection(store, history['history'], ident, 'erase')
    assert len(list((store.path / 'blobs').iterdir())) == count


def test_locked_layer_rejected_before_host(tmp_path, monkeypatch):
    store = Store(tmp_path)
    p = project()
    p['layers'][0]['locked'] = True
    saved = construction.save_project(store, p)
    monkeypatch.setattr(selection, '_run_host', lambda *_: pytest.fail('Locked layer reached host'))
    with pytest.raises(ValidationError, match='locked'):
        selection.create_selection(store, saved['project'], 'a', [0, 0])


def test_transparent_hidden_source_rgb_is_not_normalized_away(prepared):
    store, saved, _, _ = prepared
    result = selection.create_selection(store, saved['project'], 'a', [2, 2], 0)
    doc, mask = selection.load_selection(store, result['selection'])
    assert doc['selected_pixels'] == 1
    assert np.argwhere(mask[..., 3]).tolist() == [[2, 2]]
    # Other transparent pixels have different hidden RGB and stay unselected.
    assert construction.load_project(store, saved['project'])['palette'][5] == [11, 22, 33, 0]


def test_invalid_action_index_and_mask_rgb_refuse_before_edit(prepared, monkeypatch):
    store, _, history, selected = prepared
    monkeypatch.setattr(construction, 'edit_history', lambda *_: pytest.fail('Invalid edit reached toolkit'))
    for action, index in [('unknown', None), ('paint', None), ('paint', 999), ('paint', True), ('erase', 1)]:
        with pytest.raises(ValidationError):
            selection.apply_selection(store, history['history'], selected['selection'], action, index)
    doc, mask = selection.load_selection(store, selected['selection'])
    bad = mask.copy()
    bad[0, 0, :3] = 0  # Alpha0 is still unselected, but the typed convention must hold.
    doc.update(mask_raster=store.put_raster(bad), mask_rgba_sha256=digest(bad.tobytes()))
    with pytest.raises(ValidationError, match='binary-alpha white'):
        selection.load_selection(store, store.put_json(doc))


@pytest.mark.parametrize('seed,tol', [([-1, 0], 0), ([4, 0], 0), ([True, 0], 0), ([1.5, 1], 0),
    ([0, 0], float('nan')), ([0, 0], float('inf')), ([0, 0], -0.01), ([0, 0], 1.01), ([0, 0], True), ([0, 0], 10**400)])
def test_invalid_controls_before_host(tmp_path, monkeypatch, seed, tol):
    store = Store(tmp_path)
    saved = construction.save_project(store, project())
    monkeypatch.setattr(selection, '_run_host', lambda *_: pytest.fail('Invalid controls reached host'))
    with pytest.raises(ValidationError):
        selection.create_selection(store, saved['project'], 'a', seed, tol)


def test_canvas_resource_bound_before_host(tmp_path, monkeypatch):
    p = project()
    p['canvas']['width'], p['canvas']['height'] = 513, 1
    for cel in p['cels'].values():
        cel['pixels'] = [0] * 513
    store = Store(tmp_path)
    saved = construction.save_project(store, p)
    monkeypatch.setattr(selection, '_run_host', lambda *_: pytest.fail('Oversize reached host'))
    with pytest.raises(ValidationError, match='512'):
        selection.create_selection(store, saved['project'], 'a', [0, 0])


def test_missing_engine_timeout_and_bad_return_are_explicit(tmp_path, monkeypatch):
    rgba = np.zeros((2, 2, 4), dtype=np.uint8)
    with monkeypatch.context() as m:
        m.setattr(selection.shutil, 'which', lambda _: None)
        with pytest.raises(UnsupportedCapability, match='Godot4'):
            selection._run_host(rgba, [0, 0], 0)
    with monkeypatch.context() as m:
        def timeout(*_, **__):
            raise subprocess.TimeoutExpired('supplied fake process', 30)
        m.setattr(selection.subprocess, 'run', timeout)
        with pytest.raises(UnsupportedCapability, match='timed out'):
            selection._run_host(rgba, [0, 0], 0)
    with monkeypatch.context() as m:
        m.setattr(selection.subprocess, 'run', lambda *a, **k: subprocess.CompletedProcess(a, 1))
        with pytest.raises(UnsupportedCapability, match='resource limits'):
            selection._run_host(rgba, [0, 0], 0)


def test_packaged_source_tamper_rejected(tmp_path, monkeypatch):
    path = tmp_path / 'vendor'
    shutil.copytree(selection._VENDOR, path)
    (path / 'FloodFillObject.gd').write_bytes(b'changed')
    monkeypatch.setattr(selection, '_VENDOR', path)
    with pytest.raises(ValidationError, match='source integrity'):
        selection.source_provenance()


def test_mask_integrity_and_service_export_contract(prepared, tmp_path):
    store, _, _, selected = prepared
    summary = invoke_selection(store, 'get', {'selection': selected['selection']})
    assert summary['selected_pixels'] == 3 and summary['shared_frames'] == ['f0', 'f1']
    out = invoke_selection(store, 'export_mask', {'selection': selected['selection'], 'path': 'mask.png'}, base_dir=tmp_path)
    assert out['sha256'] == digest((tmp_path / 'mask.png').read_bytes())
    with pytest.raises(FileExistsError):
        selection.export_mask(store, selected['selection'], tmp_path / 'mask.png')
    with pytest.raises(ValidationError):
        invoke_selection(store, 'get', {'selection': selected['selection'], 'extra': 1})
    bad = store.get_json(selected['selection'])
    bad['selected_pixels'] += 1
    with pytest.raises(ValidationError, match='count/hash'):
        selection.load_selection(store, store.put_json(bad))


def test_raster_size_rejected_before_blob_decode(prepared, monkeypatch):
    store, _, _, selected = prepared
    doc = store.get_json(selected['selection'])
    doc['mask_raster'] = store.put_json({'kind': 'rgba', 'version': 1, 'width': 4096, 'height': 4096})
    ident = store.put_json(doc)
    monkeypatch.setattr(store, 'get_raster', lambda *_: pytest.fail('Oversized raster decoded'))
    with pytest.raises(ValidationError, match='dimensions differ'):
        selection.load_selection(store, ident)


def test_receipt_validation_is_cold_replay_without_godot_or_new_blobs(prepared, monkeypatch):
    store, _, history, selected = prepared
    edited = selection.apply_selection(store, history['history'], selected['selection'], 'erase')
    count = len(list((store.path / 'blobs').iterdir()))
    monkeypatch.setattr(selection, '_run_host', lambda *_: pytest.fail('Receipt validation reran Godot'))
    receipt = selection.validate_edit_receipt(Store(store.path), edited['selection_receipt'])
    assert receipt['history_after'] == edited['history']
    assert len(list((store.path / 'blobs').iterdir())) == count


@pytest.mark.parametrize('change', ['truncated', 'action', 'index', 'before', 'count', 'outside', 'extra'])
def test_forged_edit_receipts_reject_before_replay_or_new_blobs(prepared, monkeypatch, change):
    store, _, history, selected = prepared
    edited = selection.apply_selection(store, history['history'], selected['selection'], 'erase')
    doc = store.get_json(edited['selection_receipt'])
    if change == 'truncated':
        doc = {k: doc[k] for k in ('kind', 'history_after', 'project_after')}
    elif change == 'action':
        doc['action'], doc['palette_index'] = 'paint', 3
    elif change == 'index':
        doc['palette_index'] = 3
    elif change == 'before':
        doc['history_before'] = edited['history']
    elif change == 'count':
        doc['changed_indices'] = 0
    elif change == 'outside':
        doc['outside_indices_and_rgba_preserved'] = False
    else:
        doc['unexpected'] = True
    ident = store.put_json(doc)
    monkeypatch.setattr(selection, 'apply_selection', lambda *_: pytest.fail('Invalid receipt reached replay'))
    count = len(list((store.path / 'blobs').iterdir()))
    with pytest.raises(ValidationError):
        selection.validate_edit_receipt(store, ident)
    assert len(list((store.path / 'blobs').iterdir())) == count


def test_actual_godot_corrected_source_fixture():
    raw = base64.b64decode(CORRECTED_PNG)
    assert digest(raw) == 'f8929723b17cdc39254ced84549817f4c36f9a71a7d66958f13bf27b1f566338'
    rgba = np.array(Image.open(BytesIO(raw)).convert('RGBA'))
    mask, execution = selection._run_host(rgba, [0, 0], 32 / 255)
    assert np.count_nonzero(mask[..., 3]) == 5889
    assert digest(mask.tobytes()) == CORRECTED_MASK_RGBA_SHA
    assert execution['source_image_unchanged'] is True


# Supplied diagnostic from the frozen corrected-connectivity plan, embedded so
# tests and installed code need neither an artifact tree nor a research checkout.
CORRECTED_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAACE0lEQVR4nO3dLU4DQRxAcUqWBIdDNpwBboDFQILBo/YQGO5QVVGHIUFhewM4Q3VdHQkCBKlg0q/Jzsybdt/PQiaTvPx3uu1SBsPJ7c+RMMf0BvrOADADwJpBxwU8QLpxAmAGgBkA1ngNZzkBsOa04wJfSbbRX04AzAAwA8Aar+EsJwDWXHRcYJZgE33mBMAMADMArJklXnDeThOvWJfz0XXS9ZwAWENvIPTy9p51/Ye7m6zrx3ICYNkn4PXyKur3vzPtYyl2P/efH5l28scJgBkAVt0hHAoPzW2HdOzv05wAmAFgBoBVfwbEXsNrv+aHnACYAWAGgBkAVt0hfPL8RG+hKCcAVt0EdNU+nm38+Wi8KLST3TgBMAPADABLfgaETw20idev7RrelRMAMwDMALDkZ0D4ZFzsUwhd7dsZ4QTAkgdI/ezkoUseYN5OjRAhyyXICLvLdgYYYTdZD+F5O9367mTfZX8VNBovjLBBkZehRliv2H2AEVYr+onYMkINd6vhc/+l79iXit8JOwn/IZ8Jr4tQw2SU5ntBsIN7KmJX1DU/5ATADADDLkF9PHBXcQJgBoAZAGYAmAFgBoAZAGYAWPYbsdzft7PvnACYAWAGgGX/C5l1Yr9fNPYhr9zrp+IEwAwAMwDMADADwAwAMwDMADADwAwAMwBsMJzc+i+FQU4AzAAwA8AMADMAzAAwA8B+ARDjXvV8IfZKAAAAAElFTkSuQmCC'
CORRECTED_MASK_RGBA_SHA = '5cddc2a5d03669ec8b240035252793311bad97e3a40c5aba2cd26c225c3bbfd0'
