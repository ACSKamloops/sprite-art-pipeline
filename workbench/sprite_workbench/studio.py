"""End-to-end supplied-art sessions with explicit loss policy and checked exports.

This is local orchestration, not a reconstruction of a private neural model.
Raw inputs stay immutable; editable copies and all clocks are declared.
"""
from fractions import Fraction
from io import BytesIO
import json
import math
from pathlib import Path
import tempfile
import uuid
import zipfile

import numpy as np
from PIL import Image

from .core import Store, ValidationError, canonical_json, digest, load_sequence, validate_id
from . import construction
from .export import export_sequence, import_editable, sequence_timeline

EXAMPLES = Path(__file__).with_name('studio_examples')
POLICY = 'explicit editable-copy normalization; raw retained'


def catalog():
    examples = []
    for p in sorted(EXAMPLES.glob('*/manifest.json')):
        d = json.loads(p.read_text())
        examples.append({k: d[k] for k in ('id', 'title', 'clock_note', 'loop', 'visual_acceptance')} |
                        {'frames': d['frame_count'], 'provider': d['provider']})
    return {'examples': examples, 'generation': 'Use Model Lab to prepare interchangeable model handoffs; no provider is launched here',
            'boundary': 'Supplied frames, precise editing and playback; no inferred rig, hidden surfaces or private model equivalence'}


def from_sequence(store, sequence, *, animation_id='clip', normalize_hidden_rgb=False):
    """Create an editable derivative, changing hidden RGB only on explicit opt-in."""
    if type(normalize_hidden_rgb) is not bool:
        raise ValidationError('normalize_hidden_rgb must be an explicit boolean')
    doc, arrays = load_sequence(store, sequence)
    sequence_timeline(doc)
    counts = [int(np.count_nonzero((a[..., 3] == 0) & np.any(a[..., :3] != 0, axis=2))) for a in arrays]
    if sum(counts) and not normalize_hidden_rgb:
        raise ValidationError('Raw frames contain nonzero transparent RGB; explicitly request normalize_hidden_rgb for an editable derivative. Raw frames will be retained.')
    editable = sequence
    receipt = store.put_json({'kind': 'studio-normalization', 'version': 1, 'source_sequence': sequence,
        'changed_hidden_rgb_pixels': sum(counts), 'per_frame': counts, 'explicit_opt_in': normalize_hidden_rgb,
        'policy': POLICY, 'visible_rgba_and_alpha': 'unchanged'})
    derivative = json.loads(canonical_json(doc))
    if normalize_hidden_rgb:
        for f, a in zip(derivative['frames'], arrays):
            b = a.copy(); b[b[..., 3] == 0, :3] = 0
            f['raster'] = store.put_raster(b)
    derivative['metadata'] |= {'parent_sequence': sequence, 'source_ids': [sequence, receipt],
                               'studio_normalization': receipt}
    editable = store.put_json(derivative)
    saved = construction.from_sequence(store, editable, animation_id=animation_id)
    history = construction.create_history(store, saved['project'])
    rendered = construction.render_animation(store, saved['project'], animation_id)
    result = {**saved, **history, 'animation_id': animation_id, 'sequence': rendered['sequence'],
              'source_sequence': sequence, 'normalization': {'changed_hidden_rgb_pixels': sum(counts),
                    'policy': POLICY, 'receipt': receipt},
              'clock_note': doc.get('metadata', {}).get('clock_note', 'Exact supplied rational holds; source clock provenance retained')}
    session = store.put_json({'kind': 'studio-session', 'version': 1, 'source_sequence': sequence,
        'editable_sequence': editable, 'normalization': receipt, 'project': saved['project'],
        'history': history['history'], 'animation_id': animation_id})
    result['session'] = session
    return result


def load_example(store, ident):
    if ident not in ('hero-walk', 'hero-slash'):
        raise ValidationError('Unknown packaged Studio example')
    directory = EXAMPLES / ident
    manifest = json.loads((directory / 'manifest.json').read_text())
    raw_ids, arrays, slot0 = [], [], None
    # Check every packaged source before creating an editable project.
    records = []
    for record in manifest['files']:
        raw = (directory / record['file']).read_bytes()
        if digest(raw) != record['sha256']:
            raise ValidationError('Packaged example source hash mismatch')
        with Image.open(BytesIO(raw)) as image:
            a = np.array(image.convert('RGBA'))
        records.append((record, raw, a))
    for record, raw, a in records:
        raw_ids.append(store.put_bytes(raw))
        slot = record.get('source_slot')
        if slot == 0:
            slot0 = store.put_raster(a)
        elif slot in manifest['generated_slots']:
            arrays.append(a)
    from .core import save_sequence
    source = save_sequence(store, arrays, [Fraction(*manifest['duration'])] * len(arrays),
        pivots=[[128, 128]] * len(arrays), loop=manifest['loop'],
        directions=['supplied three-quarter view'] * len(arrays),
        metadata={'source_ids': raw_ids + [slot0, store.put_json(manifest)],
            'provider': manifest['provider'], 'reference_slot': slot0,
            'clock_note': manifest['clock_note'], 'fps': 8, 'duration_ticks': [1]*len(arrays),
            'native_fps': None, 'registration': manifest['registration'], 'visual_acceptance': 'unreviewed'})
    return from_sequence(store, source, animation_id=ident, normalize_hidden_rgb=True)


def _render(store, project, history, animation_id, selection_receipts=()):
    h = construction.load_history(store, history)
    if h['project'] != project:
        raise ValidationError('Project and history refer to different revisions; reopen or use the current matching history')
    current = store.get_json(history)
    if len(selection_receipts) > 1024:
        raise ValidationError('Selection receipt budget exceeded')
    for ident in selection_receipts:
        from .selection import validate_edit_receipt
        receipt = validate_edit_receipt(store, validate_id(ident))
        after = construction.load_history(store, receipt['history_after'])
        # An undo may keep a future receipt; branches must not attach unrelated edits.
        n = after['journal']['cursor']
        if (after['initial_project'] != h['initial_project'] or
            after['journal']['receipts'][:n] != h['journal']['receipts'][:n] or
            receipt['project_after'] not in current['checkpoints']):
            raise ValidationError('Selection receipt belongs to another history branch')
    result = construction.render_animation(store, project, animation_id)
    doc = store.get_json(result['sequence'])
    doc['metadata'] |= {'construction_history': history, 'selection_receipts': list(selection_receipts),
                         'source_ids': [project, history, *selection_receipts]}
    result['sequence'] = store.put_json(doc)
    return result


def verify(store, project, history, animation_id, selection_receipts=()):
    rendered = _render(store, project, history, animation_id, selection_receipts)
    doc, arrays = load_sequence(store, rendered['sequence'])
    timeline = sequence_timeline(doc)
    repeated = [i for i in range(1, len(arrays)) if np.array_equal(arrays[i-1], arrays[i])]
    checks = [
        {'id': 'history', 'status': 'passed', 'detail': 'Matching immutable project and replay-validated history'},
        {'id': 'rational_clock', 'status': 'passed', 'detail': 'Positive exact holds, ordered frames, declared loop/play count'},
        {'id': 'full_canvas', 'status': 'passed', 'detail': f"{len(arrays)} full-canvas RGBA frames; no trim or automatic alignment"},
        {'id': 'selection_provenance', 'status': 'passed', 'detail': f'{len(selection_receipts)} receipts attached to matching history branch'},
    ]
    report = {'kind': 'studio-verification', 'version': 1, 'status': 'passed', 'mechanical_ready': True,
        'visual_acceptance': 'unreviewed', 'checks': checks, 'frame_count': len(arrays),
        'duration': timeline['total'], 'sequence': rendered['sequence'], 'project': project,
        'history': history, 'consecutive_duplicate_indices': repeated,
        'limitations': ['Art/anatomy/motion quality requires timed visual review',
                        'Events are preserved declarations, not inferred contacts',
                        'One supplied composite layer; no automatic articulated rig']}
    return report | {'verification': store.put_json(report)}


def verify_export(store, sequence, directory, *, project=None, history=None):
    """Read the actual emitted files back; reject corruption and metadata drift."""
    directory = Path(directory)
    doc, arrays = load_sequence(store, sequence)
    if directory.is_symlink() or any(p.is_symlink() for p in directory.rglob('*')):
        raise ValidationError('Export files and directories cannot use symlinks')
    report = json.loads((directory / 'export-report.json').read_text())
    if report['sequence_id'] != sequence or any(report['formats'].get(k, {}).get('status') != 'written'
            for k in ('png','sheet','manifest','apng','editable','godot','review')):
        raise ValidationError('Required export formats were not all written for this sequence')
    expected_files = {r['file'] for r in report['files']} | {'export-report.json'}
    actual_files = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    if {'verification.json', 'PACKAGE.json'} <= actual_files:
        package = json.loads((directory / 'PACKAGE.json').read_text())
        raw_verification = (directory / 'verification.json').read_bytes()
        verification = json.loads(raw_verification)
        if (package.get('kind') != 'studio-package' or package.get('version') != 1 or
            package.get('sequence') != sequence or package.get('verification') != digest(raw_verification) or
            verification.get('status') != 'passed' or verification.get('sequence') != sequence or
            {r['file'] for r in package['files']} != actual_files-{'PACKAGE.json'}):
            raise ValidationError('Final package verification inventory is invalid')
        for row in package['files']:
            path = directory / row['file']
            if not path.resolve().is_relative_to(directory.resolve()):
                raise ValidationError('Unsafe final package path')
            raw = path.read_bytes()
            if row['bytes'] != len(raw) or row['sha256'] != digest(raw):
                raise ValidationError('Final package file hash mismatch')
        expected_files |= {'verification.json', 'PACKAGE.json'}
    if expected_files != actual_files:
        raise ValidationError('Export file inventory differs from report')
    for record in report['files']:
        p = directory / record['file']
        if not p.resolve().is_relative_to(directory.resolve()) or p.is_symlink():
            raise ValidationError('Export contains an unsafe file path')
        raw = p.read_bytes()
        if len(raw) != record['bytes'] or digest(raw) != record['sha256']:
            raise ValidationError('Export file hash mismatch: '+record['file'])
    manifest = json.loads((directory / 'manifest.json').read_text())
    timeline = sequence_timeline(doc)
    columns = max(1, math.ceil(math.sqrt(len(arrays))))
    if (manifest['sequence_id'] != sequence or manifest['canvas'] != doc['canvas'] or
        manifest['loop'] != doc['loop'] or manifest['play_count'] != doc.get('play_count', 0 if doc['loop'] else 1) or
        manifest['metadata'] != doc['metadata'] or len(manifest['frames']) != len(arrays) or
        manifest['total'] != timeline['total'] or manifest['play_total'] != timeline['play_total'] or
        manifest['sheet_columns'] != columns or manifest['sheet_rows'] != math.ceil(len(arrays)/columns)):
        raise ValidationError('Export manifest differs from source sequence')
    w, h = doc['canvas']
    expected_sheet = np.zeros((manifest['sheet_rows']*h, manifest['sheet_columns']*w, 4), dtype=np.uint8)
    for i, (entry, source, array) in enumerate(zip(manifest['frames'], doc['frames'], arrays)):
        if (any(entry[k] != source[k] for k in ('index', 'raster', 'duration', 'pivot', 'direction')) or
            any(entry[k] != timeline['frames'][i][k] for k in ('start','end'))):
            raise ValidationError('Export frame metadata changed')
        with Image.open(directory / entry['file']) as image:
            decoded = np.array(image.convert('RGBA'))
        if not np.array_equal(decoded, array):
            raise ValidationError('Export PNG decoded RGBA differs')
        x, y, rw, rh = entry['rectangle']
        if (rw, rh) != (w, h) or [x, y] != [i % manifest['sheet_columns']*w, i // manifest['sheet_columns']*h]:
            raise ValidationError('Export sheet rectangle changed')
        expected_sheet[y:y+h, x:x+w] = array
    with Image.open(directory / 'sheet.png') as image:
        if not np.array_equal(np.array(image.convert('RGBA')), expected_sheet):
            raise ValidationError('Sheet pixels or transparent padding differ')
    from .acquisition import import_image
    with tempfile.TemporaryDirectory(prefix='studio-cold-readback-') as temporary:
        cold = Store(Path(temporary) / 'store')
        apng = import_image(cold, directory / 'animation.apng')
        imported, decoded = load_sequence(cold, apng['sequence'])
        if ([f['duration'] for f in imported['frames']] != [f['duration'] for f in doc['frames']] or
            imported['play_count'] != manifest['play_count'] or len(decoded) != len(arrays) or
            any(not np.array_equal(a,b) for a,b in zip(decoded,arrays))):
            raise ValidationError('APNG reimport changed frames, exact holds or play count')
        if import_editable(cold, directory / 'editable') != sequence:
            raise ValidationError('Editable reimport identity mismatch')
        if project is not None:
            if construction.load_project(cold, project) != construction.load_project(store, project):
                raise ValidationError('Cold editable project differs')
        if history is not None:
            if construction.load_history(cold, history) != construction.load_history(store, history):
                raise ValidationError('Cold editable history replay differs')
    checks = [{'id': name, 'status': 'passed'} for name in (
        'complete_file_hash_inventory', 'png_rgba_readback', 'sheet_regions_and_padding',
        'apng_rgba_and_exact_clock_reimport', 'cold_editable_reimport_and_history_replay')]
    return {'kind': 'studio-export-verification', 'version': 1, 'status': 'passed',
        'sequence': sequence, 'checks': checks, 'frame_count': len(arrays),
        'visual_acceptance': 'unreviewed', 'godot_runtime': 'Resource driver covered by separate runtime tests; not executed by each export'}


def export(store, project, history, animation_id, *, base_dir, selection_receipts=()):
    readiness = verify(store, project, history, animation_id, selection_receipts)
    sequence = readiness['sequence']
    directory = Path(base_dir).resolve() / 'exports' / ('studio-'+uuid.uuid4().hex)
    export_sequence(store, sequence, directory,
                    formats=('png','sheet','manifest','apng','editable','godot','review'))
    verification = verify_export(store, sequence, directory, project=project, history=history)
    verification_id = store.put_json(verification)
    (directory / 'verification.json').write_bytes(canonical_json(verification))
    files = [{'file': str(p.relative_to(directory)), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
             for p in sorted(directory.rglob('*')) if p.is_file()]
    inventory = {'kind': 'studio-package', 'version': 1, 'sequence': sequence,
                 'verification': verification_id, 'files': files, 'visual_acceptance': 'unreviewed'}
    (directory / 'PACKAGE.json').write_bytes(canonical_json(inventory))
    target = BytesIO()
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in sorted(directory.rglob('*')):
            if p.is_file():
                archive.write(p, str(p.relative_to(directory)))
    zipped = store.put_bytes(target.getvalue())
    record = {'kind': 'studio-export', 'version': 1, 'sequence': sequence, 'project': project,
              'history': history, 'zip': zipped, 'verification': verification_id,
              'directory': str(directory), 'files': len(files)+1,
              'visual_acceptance': 'unreviewed'}
    ident = store.put_json(record)
    # Separate immutable names avoid a concurrent export replacing another's receipt.
    store.set_head('studio-export/'+ident, ident, None)
    return record | {'export': ident, 'download_url': '/api/studio/download/'+ident+'.zip',
                     'bytes': len(target.getvalue()), 'status': 'passed'}


def download(store, export_id):
    record = store.get_json(validate_id(export_id))
    if (record.get('kind') != 'studio-export' or record.get('version') != 1 or
            store.get_head('studio-export/'+export_id) != export_id):
        raise ValidationError('Download requires a verified Studio export receipt')
    proof = store.get_json(record['verification'])
    if (proof.get('kind') != 'studio-export-verification' or proof.get('version') != 1 or
            proof.get('status') != 'passed' or proof.get('sequence') != record['sequence']):
        raise ValidationError('Studio export proof does not match its sequence')
    return store.get_bytes(record['zip'])
