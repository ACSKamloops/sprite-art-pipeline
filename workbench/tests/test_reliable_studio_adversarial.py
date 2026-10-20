"""Supplied diagnostic markers through real source/edit/history/export modules.

These checks require the packaged recovered selector and local Godot. No image
generator, provider, credential, research checkout or private service is used.
"""
import copy
from fractions import Fraction
from io import BytesIO
from pathlib import Path
import zipfile

import numpy as np
import pytest

from sprite_workbench import construction, selection, studio
from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, load_sequence, save_sequence
from sprite_workbench.export import import_editable
from sprite_workbench.studio_services import invoke_studio


def marker_sequence(store, *, hidden=True, play_count=1):
    a = np.zeros((3, 4, 4), dtype=np.uint8)
    a[0, :2] = [240, 20, 40, 255]
    a[1, 2] = [20, 180, 70, 128]
    if hidden:
        a[2, 3] = [9, 10, 11, 0]
    b = a.copy()
    b[0, :2] = [30, 40, 210, 255]
    arrays = [a, a.copy(), b]
    ident = save_sequence(store, arrays, [Fraction(1, 7), Fraction(2, 9), Fraction(1, 7)],
        pivots=[[2, 1]] * 3, loop=False, play_count=play_count,
        directions=['supplied diagnostic'] * 3, metadata={'classification': 'supplied-diagnostic'})
    return ident, arrays


@pytest.fixture
def edited(tmp_path):
    store = Store(tmp_path / 'store')
    source, arrays = marker_sequence(store)
    opened = invoke_studio(store, 'from_sequence', {'sequence': source, 'normalize_hidden_rgb': True})
    project = construction.load_project(store, opened['project'])
    cel = project['frames'][0]['cels']['paint']
    selected = selection.create_selection(store, opened['project'], cel, [0, 0], 0)
    result = selection.apply_selection(store, opened['history'], selected['selection'], 'erase')
    return store, source, arrays, opened, project, selected, result


def test_explicit_normalization_retains_raw_and_only_clears_hidden_rgb(tmp_path):
    store = Store(tmp_path / 'store')
    source, original = marker_sequence(store)
    with pytest.raises(ValidationError, match='explicitly request'):
        studio.from_sequence(store, source)
    opened = studio.from_sequence(store, source, normalize_hidden_rgb=True)
    session = store.get_json(opened['session'])
    receipt = store.get_json(session['normalization'])
    assert receipt['explicit_opt_in'] is True
    assert receipt['changed_hidden_rgb_pixels'] == 3 and receipt['per_frame'] == [1, 1, 1]
    raw, raw_arrays = load_sequence(store, source)
    derivative, arrays = load_sequence(store, session['editable_sequence'])
    assert session['source_sequence'] == source and derivative['metadata']['parent_sequence'] == source
    for before, raw_after, after in zip(original, raw_arrays, arrays):
        assert np.array_equal(before, raw_after)
        expected = before.copy(); expected[expected[..., 3] == 0, :3] = 0
        assert np.array_equal(expected, after)
    assert [f['duration'] for f in derivative['frames']] == [f['duration'] for f in raw['frames']]


def test_real_mask_edit_shared_cel_exact_clock_undo_redo_and_cold_reopen(edited):
    store, source, arrays, opened, before, selected, result = edited
    assert selected['selected_pixels'] == 2
    assert selected['shared_frames'] == ['frame-0', 'frame-1']
    after = construction.load_project(store, result['project'])
    cel = before['frames'][0]['cels']['paint']
    assert before['frames'][1]['cels']['paint'] == cel
    expected = copy.deepcopy(before)
    expected['cels'][cel]['pixels'][:2] = [0, 0]
    assert after == expected
    assert after['palette'] == before['palette']  # Outside partial alpha remains 128.
    report = studio.verify(store, result['project'], result['history'], 'clip', [result['selection_receipt']])
    assert report['mechanical_ready'] and report['visual_acceptance'] == 'unreviewed'
    doc, output = load_sequence(store, report['sequence'])
    assert [f['duration'] for f in doc['frames']] == [[1, 7], [2, 9], [1, 7]]
    assert report['consecutive_duplicate_indices'] == [1]
    assert np.all(output[0][0, :2] == 0) and output[0][1, 2, 3] == 128
    undone = construction.move_history(store, result['history'], 'undo')
    assert undone['project'] == opened['project']
    # Future receipt remains on this journal's undo/redo branch.
    studio.verify(store, undone['project'], undone['history'], 'clip', [result['selection_receipt']])
    redone = construction.move_history(store, undone['history'], 'redo')
    assert redone['project'] == result['project']
    cold = Store(store.path)
    assert construction.load_history(cold, redone['history']) == construction.load_history(store, result['history'])
    assert selection.validate_edit_receipt(cold, result['selection_receipt'])['selection'] == selected['selection']
    assert np.array_equal(load_sequence(cold, source)[1][0], arrays[0])


def test_stale_masks_mismatched_history_and_diverged_receipts_reject(edited):
    store, _, _, opened, before, selected, result = edited
    with pytest.raises(ValidationError, match='Stale selection'):
        selection.apply_selection(store, result['history'], selected['selection'], 'erase')
    with pytest.raises(ValidationError, match='different revisions'):
        studio.verify(store, opened['project'], result['history'], 'clip')
    undone = construction.move_history(store, result['history'], 'undo')
    partial_alpha = next(i for i, rgba in enumerate(before['palette']) if rgba[3] == 128)
    branch = selection.apply_selection(store, undone['history'], selected['selection'], 'paint', partial_alpha)
    with pytest.raises(ValidationError, match='another history branch'):
        studio.verify(store, branch['project'], branch['history'], 'clip', [result['selection_receipt']])


@pytest.mark.parametrize('mutation', ['truncated', 'action', 'index'])
def test_forged_selection_receipts_never_produce_studio_pass(edited, mutation):
    store, _, _, _, _, _, result = edited
    receipt = store.get_json(result['selection_receipt'])
    if mutation == 'truncated':
        del receipt['selection']
    elif mutation == 'action':
        receipt['action'] = 'paint'; receipt['palette_index'] = 1
    else:
        receipt['palette_index'] = 1
    forged = store.put_json(receipt)
    with pytest.raises(ValidationError):
        studio.verify(store, result['project'], result['history'], 'clip', [forged])


def test_export_cold_closure_final_inventory_and_download(edited, tmp_path):
    store, source, _, opened, _, selected, result = edited
    exported = invoke_studio(store, 'export', {'project': result['project'], 'history': result['history'],
        'animation_id': 'clip', 'selection_receipts': [result['selection_receipt']]}, base_dir=tmp_path)
    directory = Path(exported['directory'])
    assert studio.verify_export(store, exported['sequence'], directory,
        project=result['project'], history=result['history'])['status'] == 'passed'
    with zipfile.ZipFile(BytesIO(studio.download(store, exported['export']))) as archive:
        assert {'PACKAGE.json', 'verification.json', 'animation.apng', 'manifest.json'} <= set(archive.namelist())
    cold = Store(tmp_path / 'fresh-store')
    assert import_editable(cold, directory / 'editable') == exported['sequence']
    assert construction.load_history(cold, result['history']) == construction.load_history(store, result['history'])
    assert selection.validate_edit_receipt(cold, result['selection_receipt']) == store.get_json(result['selection_receipt'])
    assert selection.load_selection(cold, selected['selection'])[0]['source_project'] == opened['project']
    session = store.get_json(opened['session'])
    assert cold.get_json(session['normalization']) == store.get_json(session['normalization'])
    assert np.array_equal(load_sequence(cold, source)[1][0], load_sequence(store, source)[1][0])
    extra = directory / 'unreported.txt'; extra.write_text('not in the inventory')
    with pytest.raises(ValidationError, match='inventory'):
        studio.verify_export(store, exported['sequence'], directory)
    extra.unlink()
    png = next(directory.glob('frame-*.png'), None)
    if png is None:
        png = next((directory / 'frames').glob('*.png'))
    png.write_bytes(b'corrupt diagnostic PNG')
    with pytest.raises(ValidationError, match='hash mismatch'):
        studio.verify_export(store, exported['sequence'], directory)


def test_finite_repeats_are_explicitly_unsupported_not_silently_lost(tmp_path):
    store = Store(tmp_path / 'store')
    source, _ = marker_sequence(store, hidden=False, play_count=4)
    with pytest.raises(UnsupportedCapability, match='finite repeats'):
        studio.from_sequence(store, source)


@pytest.mark.parametrize('fields', [{'normalize_hidden_rgb': 'true'}, {'unexpected': True}])
def test_service_rejects_ambiguous_or_extra_inputs(tmp_path, fields):
    store = Store(tmp_path / 'store')
    source, _ = marker_sequence(store)
    with pytest.raises(ValidationError):
        invoke_studio(store, 'from_sequence', {'sequence': source, **fields})
