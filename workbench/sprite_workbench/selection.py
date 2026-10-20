"""Recovered manual host selection, immutable masks and guarded local indexed edits.

The selector executes unchanged packaged GDScript. Painting/erasing uses the
existing construction toolkit's guarded candidate transaction and history.
"""
from __future__ import annotations

from io import BytesIO
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image

from . import construction, construction_core as toolkit
from .core import UnsupportedCapability, ValidationError, canonical_json, digest
from .core import validate_id

MAX_SIDE = 512
MAX_PIXELS = MAX_SIDE * MAX_SIDE
MAX_SECONDS = 30
MAX_LOG_BYTES = 65536
_VENDOR = Path(__file__).parent / 'vendor' / 'host_selection'
_MANIFEST_SHA = '3494a951e8e45f1be714a07e628e06bdd5db091de54de17ca0d52306de3a3d36'
_EDIT_POLICY = 'Existing guarded toolkit candidate_patch/history; shared cel remains shared; palette alpha unchanged'


def _source_bundle():
    try:
        raw = (_VENDOR / 'manifest.json').read_bytes()
        if digest(raw) != _MANIFEST_SHA:
            raise ValidationError('Packaged selection manifest integrity failed')
        manifest = json.loads(raw)
        files = {}
        for name, expected in manifest['files'].items():
            files[name] = (_VENDOR / name).read_bytes()
            if digest(files[name]) != expected:
                raise ValidationError('Packaged selection source integrity failed')
    except OSError as exc:
        raise UnsupportedCapability('local.selection.create', 'Packaged recovered selection sources are missing') from exc
    return manifest, files


def source_provenance():
    """Verify independent packaged sources; no research-checkout lookup."""
    return _source_bundle()[0]


def _controls(width, height, seed, tolerance):
    if not (type(width) is int and type(height) is int and 1 <= width <= MAX_SIDE
            and 1 <= height <= MAX_SIDE and width * height <= MAX_PIXELS):
        raise ValidationError('Selection canvas must be1..512 per side')
    if (not isinstance(seed, list) or len(seed) != 2 or any(type(v) is not int for v in seed)
            or not 0 <= seed[0] < width or not 0 <= seed[1] < height):
        raise ValidationError('Selection seed must be integer XY inside the cel canvas')
    if type(tolerance) not in (int, float) or not 0 <= tolerance <= 1 or not math.isfinite(tolerance):
        raise ValidationError('Selection tolerance must be finite normalized RGBA0..1')


def _target(project, cel_id):
    if not isinstance(cel_id, str) or cel_id not in project['cels']:
        raise ValidationError('Unknown selection cel')
    cel = project['cels'][cel_id]
    layer = next(layer for layer in project['layers'] if layer['id'] == cel['layer_id'])
    if layer['locked']:
        raise ValidationError('Selection target layer is locked')
    width, height = project['canvas']['width'], project['canvas']['height']
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValidationError('Selection canvas must be1..512 per side')
    indices = np.asarray(cel['pixels'], dtype=np.int64).reshape(height, width)
    # Resolve the active indexed cel directly. Never composite over other layers.
    rgba = np.asarray(project['palette'], dtype=np.uint8)[indices]
    frames = [frame['id'] for frame in project['frames'] if cel_id in frame['cels'].values()]
    return cel, np.ascontiguousarray(rgba), frames


def _run_host(rgba, seed, tolerance):
    provenance, files = _source_bundle()
    height, width = rgba.shape[:2]
    _controls(width, height, seed, tolerance)
    godot, prlimit = shutil.which('godot'), shutil.which('prlimit')
    if not godot or not prlimit:
        raise UnsupportedCapability('local.selection.create', 'Godot4 and Linux prlimit must be installed on PATH')
    with tempfile.TemporaryDirectory(prefix='workbench-selection-') as directory:
        root = Path(directory)
        Image.fromarray(rgba).save(root / 'input.png', format='PNG')
        (root / 'flood.gd').write_bytes(files['FloodFillObject.gd'] + files['stubs.gd.fragment'])
        (root / 'similar.gd').write_bytes(b'extends RefCounted\n\n' + files['similar_colors.gd.fragment'])
        runner = files['runner.gd.template'].decode()
        for key, value in {'__X__': str(seed[0]), '__Y__': str(seed[1]), '__TOLERANCE__': json.dumps(tolerance)}.items():
            runner = runner.replace(key, value)
        (root / 'main.gd').write_text(runner)
        (root / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="Recovered manual selection"\n[threading]\nworker_pool/max_threads=2\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
        for name in ('home', 'data', 'cache', 'config'):
            (root / name).mkdir()
        env = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'HOME': str(root / 'home'),
               'XDG_DATA_HOME': str(root / 'data'), 'XDG_CACHE_HOME': str(root / 'cache'),
               'XDG_CONFIG_HOME': str(root / 'config')}
        # OS limits are external to Godot:4GiB address space,20CPU seconds,
        #2MiB per output file,128 descriptors; wall timeout is separately30s.
        command = [prlimit, '--as=4294967296', '--cpu=20', '--fsize=2097152', '--nofile=128',
                   '--', godot, '--headless', '--quit-after', '1800', '--path', directory, '--script', 'res://main.gd']
        with (root / 'engine.log').open('w+b') as log:
            try:
                result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        env=env, timeout=MAX_SECONDS, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise UnsupportedCapability('local.selection.create', 'Bounded Godot selection execution unavailable or timed out') from exc
            log.seek(0)
            raw_log = log.read(MAX_LOG_BYTES + 1)
        lines = raw_log.decode('utf8', errors='replace').splitlines()
        observations = [line[len('SELECTOR_OK '):] for line in lines if line.startswith('SELECTOR_OK ')]
        if result.returncode != 0 or len(raw_log) > MAX_LOG_BYTES or len(observations) != 1 or not (root / 'mask.png').exists():
            raise UnsupportedCapability('local.selection.create', 'Recovered Godot selection execution failed within resource limits')
        try:
            observed = json.loads(observations[0])
            mask_bytes = (root / 'mask.png').read_bytes()
            if len(mask_bytes) > 2 * 1024 * 1024:
                raise ValueError('Mask output exceeds limit')
            with Image.open(BytesIO(mask_bytes)) as image:
                if image.format != 'PNG' or image.size != (width, height) or getattr(image, 'n_frames', 1) != 1:
                    raise ValueError('Mask format/dimensions differ')
                mask = np.array(image.convert('RGBA'))
        except (ValueError, OSError, KeyError) as exc:
            raise ValidationError('Invalid recovered selector output') from exc
        count = _mask_count(mask, width, height)
        if observed.get('source_image_unchanged') is not True or observed.get('selected_pixels') != count:
            raise ValidationError('Recovered selector observation differs from mask')
        return mask, {'engine': next((line for line in lines if line.startswith('Godot Engine')), 'Godot4'),
            'source_image_unchanged': True, 'segments': observed.get('segments'),
            'limits': {'side': MAX_SIDE, 'pixels': MAX_PIXELS, 'wall_seconds': MAX_SECONDS,
                       'cpu_seconds': 20, 'address_space_bytes': 4294967296, 'file_bytes': 2097152},
            'source_manifest_sha256': _MANIFEST_SHA}


def _mask_count(mask, width, height):
    if (mask.dtype != np.uint8 or mask.shape != (height, width, 4)
            or not np.all(mask[..., :3] == 255) or not np.all(np.isin(mask[..., 3], [0, 255]))):
        raise ValidationError('Selection mask must be binary-alpha white; consume alpha only')
    return int(np.count_nonzero(mask[..., 3]))


def select_raster(store, raster, seed, tolerance=0.0):
    """Run the same recovered selector before indexed-project construction."""
    meta = store.get_json(raster)
    if (meta.get('kind') != 'rgba' or type(meta.get('width')) is not int or
            type(meta.get('height')) is not int):
        raise ValidationError('Selection requires an RGBA raster')
    _controls(meta['width'], meta['height'], seed, tolerance)
    rgba = store.get_raster(raster)
    mask, execution = _run_host(rgba, seed, tolerance)
    count = _mask_count(mask, meta['width'], meta['height'])
    receipt = {'kind': 'raster-selection', 'version': 1, 'source_raster': raster,
        'source_rgba_sha256': digest(rgba.tobytes()), 'mask_raster': store.put_raster(mask),
        'mask_rgba_sha256': digest(mask.tobytes()), 'selected_pixels': count,
        'seed': seed, 'tolerance': tolerance, 'source_provenance': source_provenance(),
        'execution': execution, 'boundary': 'Recovered manual seed selection; not neural cutout'}
    return {'selection': store.put_json(receipt), **receipt}


def create_selection(store, project, cel_id, seed, tolerance=0.0):
    document = construction.load_project(store, project)
    cel, rgba, frames = _target(document, cel_id)
    height, width = rgba.shape[:2]
    _controls(width, height, seed, tolerance)
    mask, execution = _run_host(rgba, seed, tolerance)
    count = _mask_count(mask, width, height)
    provenance = source_provenance()
    artifact = {'kind': 'construction-selection', 'version': 1, 'source_project': project,
        'source_project_hash': construction.project_hash(document), 'cel_id': cel_id, 'layer_id': cel['layer_id'],
        'source_cel_hash': toolkit.cel_hash(document, cel_id),
        'source_cel_indices_sha256': digest(canonical_json({'pixels': cel['pixels']})),
        'source_cel_rgba_sha256': digest(rgba.tobytes()), 'width': width, 'height': height,
        'seed': seed, 'tolerance': tolerance, 'mask_raster': store.put_raster(mask),
        'mask_rgba_sha256': digest(mask.tobytes()), 'selected_pixels': count, 'shared_frames': frames,
        'source_provenance': provenance, 'execution': execution}
    ident = store.put_json(artifact)
    return {'selection': ident, **{k: artifact[k] for k in ('mask_raster', 'selected_pixels', 'source_project',
        'source_project_hash', 'source_cel_rgba_sha256', 'cel_id', 'shared_frames')}, 'source_manifest_sha256': _MANIFEST_SHA}


_FIELDS = {'kind', 'version', 'source_project', 'source_project_hash', 'cel_id', 'layer_id',
    'source_cel_hash', 'source_cel_indices_sha256', 'source_cel_rgba_sha256', 'width', 'height', 'seed',
    'tolerance', 'mask_raster', 'mask_rgba_sha256', 'selected_pixels', 'shared_frames', 'source_provenance', 'execution'}


def load_selection(store, selection):
    doc = store.get_json(selection)
    if set(doc) != _FIELDS or doc.get('kind') != 'construction-selection' or type(doc.get('version')) is not int or doc['version'] != 1:
        raise ValidationError('Expected construction-selection version1')
    _controls(doc['width'], doc['height'], doc['seed'], doc['tolerance'])
    if (doc['source_provenance'] != source_provenance() or not isinstance(doc['execution'], dict)
            or doc['execution'].get('source_manifest_sha256') != _MANIFEST_SHA
            or doc['execution'].get('source_image_unchanged') is not True):
        raise ValidationError('Selection recovered-source provenance differs')
    original = construction.load_project(store, doc['source_project'])
    cel, rgba, frames = _target(original, doc['cel_id'])
    expected = (construction.project_hash(original), toolkit.cel_hash(original, doc['cel_id']),
        digest(canonical_json({'pixels': cel['pixels']})), digest(rgba.tobytes()), cel['layer_id'], frames)
    actual = tuple(doc[k] for k in ('source_project_hash', 'source_cel_hash', 'source_cel_indices_sha256',
        'source_cel_rgba_sha256', 'layer_id', 'shared_frames'))
    if expected != actual or rgba.shape != (doc['height'], doc['width'], 4):
        raise ValidationError('Selection source project/cel identity differs')
    meta = store.get_json(doc['mask_raster'])
    if meta.get('width') != doc['width'] or meta.get('height') != doc['height']:
        raise ValidationError('Selection raster dimensions differ')
    mask = store.get_raster(doc['mask_raster'])
    count = _mask_count(mask, doc['width'], doc['height'])
    if type(doc['selected_pixels']) is not int or count != doc['selected_pixels'] or digest(mask.tobytes()) != doc['mask_rgba_sha256']:
        raise ValidationError('Selection mask count/hash differs')
    return doc, mask


def apply_selection(store, history, selection, action, palette_index=None):
    if action not in ('erase', 'paint'):
        raise ValidationError('Selection action must be erase or paint')
    doc, mask = load_selection(store, selection)
    current = construction.load_history(store, history)
    if current['project'] != doc['source_project'] or current['project_hash'] != doc['source_project_hash']:
        raise ValidationError('Stale selection: current project differs from selection source')
    project = construction.load_project(store, current['project'])
    cel, rgba, frames = _target(project, doc['cel_id'])
    if toolkit.cel_hash(project, doc['cel_id']) != doc['source_cel_hash'] or digest(rgba.tobytes()) != doc['source_cel_rgba_sha256']:
        raise ValidationError('Stale selection: current cel differs')
    if action == 'erase':
        if palette_index is not None:
            raise ValidationError('Erase does not accept palette_index')
        index = 0
    else:
        if type(palette_index) is not int or not 0 <= palette_index < len(project['palette']):
            raise ValidationError('Paint needs an existing palette index')
        index = palette_index
    if not doc['selected_pixels']:
        raise ValidationError('Cannot apply an empty selection')
    selected = mask[..., 3].reshape(-1) > 0
    candidate = list(cel['pixels'])
    points = []
    for i in np.flatnonzero(selected):
        i = int(i)
        points.append([i % doc['width'], i // doc['width']])
        candidate[i] = index
    transaction = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': current['project_hash'],
        'reason': 'Explicit local masked edit using recovered host manual selection', 'operations': [{
            'op': 'candidate_patch', 'cel_id': doc['cel_id'], 'expected_cel_sha256': doc['source_cel_hash'],
            'mask': points, 'candidate_pixels': candidate}]}
    result = construction.edit_history(store, history, transaction)
    after = construction.load_project(store, result['project'])
    outside = ~selected
    before_indices = np.asarray(cel['pixels'])
    after_indices = np.asarray(after['cels'][doc['cel_id']]['pixels'])
    if not np.array_equal(before_indices[outside], after_indices[outside]) or after['palette'] != project['palette']:
        raise ValidationError('Construction masked edit violated outside-pixel preservation')
    receipt = {'kind': 'construction-selection-edit', 'version': 1, 'selection': selection,
        'history_before': history, 'history_after': result['history'], 'project_before': current['project'],
        'project_after': result['project'], 'cel_id': doc['cel_id'], 'action': action, 'palette_index': index,
        'selected_pixels': doc['selected_pixels'], 'changed_indices': int(np.count_nonzero(before_indices != after_indices)),
        'outside_indices_and_rgba_preserved': True, 'shared_frames': frames,
        'policy': _EDIT_POLICY}
    return {**result, 'selection': selection, 'selection_receipt': store.put_json(receipt),
            'selected_pixels': doc['selected_pixels'], 'changed_indices': receipt['changed_indices'], 'shared_frames': frames}


def validate_edit_receipt(store, receipt_id):
    """Bind a selection edit to its source mask and exact existing history replay.

    Invalid schema/source/before/after guards fail without publishing blobs.
    A valid replay is idempotent in the immutable Store; Godot is not rerun.
    """
    receipt = store.get_json(receipt_id)
    fields = {'kind', 'version', 'selection', 'history_before', 'history_after', 'project_before',
        'project_after', 'cel_id', 'action', 'palette_index', 'selected_pixels', 'changed_indices',
        'outside_indices_and_rgba_preserved', 'shared_frames', 'policy'}
    if (set(receipt) != fields or receipt.get('kind') != 'construction-selection-edit'
            or type(receipt.get('version')) is not int or receipt['version'] != 1
            or receipt['outside_indices_and_rgba_preserved'] is not True or receipt['policy'] != _EDIT_POLICY):
        raise ValidationError('Invalid selection-edit receipt schema/policy')
    for field in ('selection', 'history_before', 'history_after', 'project_before', 'project_after'):
        validate_id(receipt[field])
    if (receipt['action'] not in ('erase', 'paint') or type(receipt['palette_index']) is not int
            or type(receipt['selected_pixels']) is not int or not 1 <= receipt['selected_pixels'] <= MAX_PIXELS
            or type(receipt['changed_indices']) is not int or not 0 <= receipt['changed_indices'] <= receipt['selected_pixels']):
        raise ValidationError('Invalid selection-edit receipt values')
    selected, mask = load_selection(store, receipt['selection'])
    before = construction.load_history(store, receipt['history_before'])
    after = construction.load_history(store, receipt['history_after'])
    if (before['project'] != receipt['project_before'] or after['project'] != receipt['project_after']
            or before['project'] != selected['source_project']
            or before['project_hash'] != selected['source_project_hash']
            or receipt['cel_id'] != selected['cel_id'] or receipt['selected_pixels'] != selected['selected_pixels']
            or receipt['shared_frames'] != selected['shared_frames']):
        raise ValidationError('Selection-edit source/before/after identities differ')
    cursor = before['journal']['cursor']
    if (after['initial_project'] != before['initial_project'] or after['journal']['cursor'] != cursor + 1
            or len(after['journal']['receipts']) != cursor + 1
            or after['journal']['receipts'][:cursor] != before['journal']['receipts'][:cursor]):
        raise ValidationError('Selection-edit histories are not one exact edit apart')
    document = construction.load_project(store, before['project'])
    actual = construction.load_project(store, after['project'])
    index = receipt['palette_index']
    if not 0 <= index < len(document['palette']) or (receipt['action'] == 'erase' and index != 0):
        raise ValidationError('Selection-edit action/palette index differs')
    # Compare the exact masked indexed result before invoking immutable replay.
    old_pixels = document['cels'][receipt['cel_id']]['pixels']
    candidate = list(old_pixels)
    for i in np.flatnonzero(mask[..., 3].reshape(-1)):
        candidate[int(i)] = index
    expected = {**document, 'cels': {**document['cels'], receipt['cel_id']: {
        **document['cels'][receipt['cel_id']], 'pixels': candidate}}}
    changed = sum(a != b for a, b in zip(old_pixels, candidate))
    if expected != actual or changed != receipt['changed_indices']:
        raise ValidationError('Selection-edit receipt does not match the guarded masked result')
    replay = apply_selection(store, receipt['history_before'], receipt['selection'], receipt['action'],
        None if receipt['action'] == 'erase' else index)
    if replay['selection_receipt'] != receipt_id:
        raise ValidationError('Selection-edit receipt differs from exact immutable replay')
    return receipt


def export_mask(store, selection, path):
    doc, mask = load_selection(store, selection)
    buffer = BytesIO()
    Image.fromarray(mask).save(buffer, format='PNG')
    raw = buffer.getvalue()
    target = Path(path)
    with target.open('xb') as stream:
        stream.write(raw)
    return {'selection': selection, 'path': str(target), 'sha256': digest(raw),
            'selected_pixels': doc['selected_pixels'], 'mask_convention': 'White RGB, binary alpha; consume alpha only'}
