#!/usr/bin/env python3
"""Cold installed-wheel parity checks; run with the installed venv, outside repo.

No provider calls. Writes only a new external evidence directory.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(source):
        parser.error('Use a new output directory outside the source checkout')
    output.mkdir(parents=True)

    import numpy as np
    import sprite_workbench
    from sprite_workbench import construction, parity_commands, parity_pixels
    from sprite_workbench.core import Store, save_sequence, load_sequence
    from sprite_workbench.export import _artifact_closure, export_sequence, import_editable
    from sprite_workbench.parity_services import invoke_parity
    from sprite_workbench.readiness import source_fingerprint

    installed = Path(sprite_workbench.__file__).resolve().parent
    assert not installed.is_relative_to(source), 'Imported checkout instead of installed package'
    extensions = {'.py', '.json', '.js', '.cjs', '.css', '.html', '.png', '.gd', '.template', '.fragment', '.mp4'}
    def inventory(root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
                if p.is_file() and not p.is_symlink() and p.suffix in extensions and '__pycache__' not in p.parts}
    expected = inventory(source / 'sprite_workbench')
    actual = inventory(installed)
    with zipfile.ZipFile(args.wheel) as archive:
        wheel = {name.removeprefix('sprite_workbench/'): archive.read(name) for name in archive.namelist()
                 if name.startswith('sprite_workbench/') and not name.endswith('/')}
    assert expected == actual == wheel, 'Source/wheel/installed runtime bytes differ'
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    package = {'schema': 'installed-parity-package-proof/v1', 'passed': True,
        'version': sprite_workbench.__version__, 'source_commit': commit,
        'source_fingerprint': source_fingerprint(), 'wheel': str(args.wheel.resolve()),
        'wheel_sha256': sha(args.wheel.read_bytes()), 'installed_root': str(installed),
        'runtime_files': [{'file': name, 'sha256': sha(raw), 'bytes': len(raw)} for name, raw in sorted(expected.items())],
        'errors': {'missing': [], 'extra': [], 'changed': []}}
    (output / 'PACKAGE-COMPARISON.json').write_text(json.dumps(package, indent=2) + '\n')

    store = Store(output / 'store')
    checks = []
    def check(name, ok, **detail):
        assert ok, name
        checks.append({'name': name, 'passed': True, **detail})
    a = np.array([[[90, 80, 70, 0], [10, 20, 30, 1]],
                  [[5, 6, 7, 128], [255, 0, 0, 255]]], dtype=np.uint8)
    raster = store.put_raster(a)
    result = invoke_parity(store, 'pixels', {'operation': 'serialize', 'request': {'raster': raster}})
    normalized = a.copy(); normalized[0, 0] = 0
    check('Original serialization with unchanged input', np.array_equal(store.get_raster(result['output_raster']), normalized)
          and np.array_equal(store.get_raster(raster), a), receipt=result['receipt'])
    parity_pixels.verify_receipt(store, result['receipt'])
    check('Actual original Godot replay verifies receipt', True)
    still = invoke_parity(store, 'to_sequence', {'receipt': result['receipt'], 'duration': [7, 13]})
    doc, arrays = load_sequence(store, still['sequence'])
    check('Explicit exact still hold', doc['frames'][0]['duration'] == [7, 13] and np.array_equal(arrays[0], normalized))
    export_sequence(store, still['sequence'], output / 'still-export', ['editable', 'png', 'manifest'])
    cold = Store(output / 'cold')
    imported = import_editable(cold, output / 'still-export' / 'editable')
    check('Cold pixel/source/raw closure exact', _artifact_closure(store, still['sequence']) == _artifact_closure(cold, imported))
    for operation in ('transparency', 'reference_palette'):
        r = invoke_parity(store, 'pixels', {'operation': operation, 'request': {'raster': raster}})
        check('Installed original ' + operation, r.get('has_exact_zero_alpha') is True if operation == 'transparency'
              else r['palette_entries'] == 3, receipt=r['receipt'])
    mask = invoke_parity(store, 'pixels', {'operation': 'mask', 'request': {'mask': raster, 'art': raster}})
    check('Opaque request mask encoding', store.get_raster(mask['output_raster']).tolist() ==
          [[[0, 0, 0, 255], [255, 255, 255, 255]], [[255, 255, 255, 255], [255, 255, 255, 255]]])
    decoded = invoke_parity(store, 'pixels', {'operation': 'decode', 'request': {
        'media': store.put_bytes(a.tobytes()), 'width': 2, 'height': 2}})
    check('Installed raw decoder exact', np.array_equal(store.get_raster(decoded['output_raster']), a))
    placed = invoke_parity(store, 'pixels', {'operation': 'place', 'request': {'source': raster, 'destination': raster}})
    check('Installed original blit exact', np.array_equal(store.get_raster(placed['output_raster']), a))
    palette = invoke_parity(store, 'palette', {'raster': raster})
    check('Original palette import first-seen RGB', palette['colors'] == ['#0a141e', '#050607', '#ff0000'])
    marker = np.zeros((16, 16, 4), dtype=np.uint8)
    marker[0, 0] = [200, 40, 80, 255]
    base = save_sequence(store, [marker], [Fraction(1, 12)])
    project = construction.from_sequence(store, base)
    history = construction.create_history(store, project['project'])
    raw = construction.load_project(store, project['project'])
    cel = next(iter(raw['cels']))
    command = {'method': 'ellipse-filled', 'pos': [3, 3], 'size': [5, 5], 'thickness': 1}
    painted = invoke_parity(store, 'paint', {'history': history['history'], 'cel_id': cel, 'command': command, 'palette_index': 1})
    state = construction.load_history(store, painted['history'])
    check('Original shape evidence attached to history', state['source_evidence'] == [{'artifact': painted['footprint'], 'receipt_index': 0}])
    sequence = construction.render_animation(store, painted['project'], raw['animations'][0]['id'])['sequence']
    document = store.get_json(sequence); document['metadata']['construction_history'] = painted['history']
    sequence = store.put_json(document)
    export_sequence(store, sequence, output / 'shape-export', ['editable', 'png', 'manifest'])
    reopened = import_editable(cold, output / 'shape-export' / 'editable')
    cold_state = construction.load_history(cold, painted['history'])
    check('Cold source footprint and history replay', cold_state['source_evidence'] == state['source_evidence']
          and painted['footprint'] in _artifact_closure(cold, reopened))
    undone = construction.move_history(cold, painted['history'], 'undo')
    redone = construction.move_history(cold, undone['history'], 'redo')
    check('Cold exact undo/redo', redone['project'] == painted['project'] and undone['project'] == project['project'])
    cat = invoke_parity(store, 'catalog', {})
    check('Current contract and truthful boundary', cat['public_contract_delta']['current_operations'] == 112 and cat['whole_system_parity'] is False)
    report = {'kind': 'installed-original-client-workflow-proof', 'version': sprite_workbench.__version__,
              'source_fingerprint': package['source_fingerprint'], 'passed': True, 'checks': checks,
              'provider_calls': 0, 'artistic_acceptance': False, 'whole_vendor_parity': False}
    (output / 'INSTALLED-PROOF.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'runtime_files': len(expected), 'workflow_checks': len(checks),
                      'source_fingerprint': package['source_fingerprint']}))


if __name__ == '__main__':
    main()
