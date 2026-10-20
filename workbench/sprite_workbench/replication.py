"""Bounded local replay, file-integrity verification and supplied-input comparison."""
from datetime import datetime, timezone
from fractions import Fraction
from importlib import import_module, metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import numpy as np

from .core import Store, ValidationError, canonical_json, digest, load_sequence, validate_id
from .export import export_sequence, sequence_timeline

FLOW_NAMES = {
    'F01': 'Import, preparation and guarded refinement',
    'F02': 'Owned parts, tracks and fine editing',
    'F03': 'Source-specific pose math and supplied motion',
    'F04': 'Directions, states and animation library',
    'F05': 'Candidate review, suffix selection and promotion',
    'F06': 'Supplied tiles, topology and guarded map edits',
    'F07': 'References, masks, alpha and request preparation',
    'F08': 'Supplied UI, glyphs and viseme clocks',
    'F09': 'Pinned procedural effects and composition',
    'F10': 'Editable exchange, playback data and engine import',
    'F11': 'Durable local jobs and offline vendor boundaries',
}


def flow_module(flow):
    if flow in ('F01', 'F03', 'F06', 'F07', 'F08'):
        return 'replay_methods'
    if flow in ('F02', 'F09', 'F10'):
        return 'replay_geometry'
    if flow in ('F04', 'F05', 'F11'):
        return 'replay_state'
    raise ValidationError('Flow must be F01..F11')


def catalog():
    return {'kind': 'local-replay-catalog', 'version': 1,
            'whole_vendor_replication_complete': False, 'artistic_acceptance': 'unreviewed',
            'flows': [{'id': flow, 'name': name, 'recipe': 'sprite_workbench.' + flow_module(flow) + '.run_flow',
                       'command': f'sprite-workbench lab replay --flow {flow} --output ABSENT_DIRECTORY',
                       'coverage': 'bounded diagnostic subset', 'whole_flow_completed': False}
                      for flow, name in FLOW_NAMES.items()]}


def write_json(path, value):
    Path(path).write_bytes(json.dumps(value, indent=2, allow_nan=False).encode() + b'\n')


def fresh_directory(path):
    path = Path(path).absolute()
    if path.is_symlink() or path.exists():
        raise ValidationError('Use an absent output directory; existing work is preserved')
    path.mkdir(parents=True, exist_ok=False)
    return path.resolve()


def package_snapshot():
    root = Path(__file__).resolve().parent
    return [{'file': p.relative_to(root).as_posix(), 'sha256': digest(p.read_bytes())}
            for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()
            and p.suffix in {'.py', '.json', '.js', '.cjs'} and '__pycache__' not in p.parts]


def doctor():
    from packaging.version import Version
    packages = []
    for name, minimum in [('numpy', '2'), ('Pillow', '11'), ('jsonschema', '4.20'), ('packaging', '23')]:
        try:
            installed = metadata.version(name)
            available = Version(installed) >= Version(minimum)
        except metadata.PackageNotFoundError:
            installed, available = None, False
        packages.append({'name': name, 'version': installed, 'minimum': minimum, 'available': available})
    tools = []
    for name, scope in [('node', 'F09 procedural effects'), ('godot', 'F10 engine check')]:
        executable = shutil.which(name) or (shutil.which('godot4') if name == 'godot' else None)
        result = {'name': name, 'path': executable, 'scope': scope, 'available': False}
        if executable:
            try:
                completed = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=10)
                result.update(available=completed.returncode == 0, version=completed.stdout.strip()[:512], exit=completed.returncode)
            except (OSError, subprocess.TimeoutExpired) as exc:
                result['error'] = type(exc).__name__
        tools.append(result)
    ready = sys.version_info >= (3, 11) and all(p['available'] for p in packages)
    return {'kind': 'local-environment-check', 'status': 'completed' if ready and all(t['available'] for t in tools) else 'incomplete',
            'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
            'packages': packages, 'tools': tools, 'python_ready': ready,
            'dependency_versions': {d.metadata['Name']: d.version for d in metadata.distributions()},
            'all_replay_dependencies_ready': ready and all(t['available'] for t in tools),
            'network_or_credentials_used': False,
            'scope': 'Prerequisite probes only; replay verifies actual behavior. F08 uses supplied glyphs, not ambient fonts.'}


def _inventory(root, exclusions=()):
    records = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValidationError('Replay evidence must not contain symlinks')
        if path.is_file() and relative not in exclusions:
            records.append({'file': relative, 'bytes': path.stat().st_size, 'sha256': digest(path.read_bytes())})
    return records


def replay(output, flows=None):
    flows = list(FLOW_NAMES) if flows is None else list(flows)
    if not flows or len(flows) != len(set(flows)) or any(f not in FLOW_NAMES for f in flows):
        raise ValidationError('Choose nonempty unique F01..F11 flows')
    out = fresh_directory(output)
    source = package_snapshot()
    specification = {'kind': 'local-replay-specification', 'version': 1, 'flows': flows,
                     'frozen_at_utc': datetime.now(timezone.utc).isoformat(), 'package_files': source,
                     'environment': doctor(), 'scope': 'Deterministic supplied-art diagnostic subsets only',
                     'whole_vendor_replication_complete': False, 'artistic_acceptance': 'unreviewed'}
    write_json(out / 'SPECIFICATION.json', specification)
    reports = []
    for flow in flows:
        try:
            module = import_module('.' + flow_module(flow), __package__)
            result = module.run_flow(flow, Store(out / 'stores' / flow), out / flow)
            canonical_json(result)
            checks = result.get('checks', [])
            passed = bool(checks) and all(isinstance(c, dict) and c.get('passed') is True for c in checks)
            status = 'completed' if passed else 'incomplete'
            report = {'flow': flow, 'status': status, 'whole_flow_completed': False, **result}
            # A recipe cannot override the orchestrator's gate or broad completion boundary.
            report.update(flow=flow, status=status, whole_flow_completed=False)
        except Exception as exc:
            error = exc.to_dict() if isinstance(exc, ValidationError) else {
                'status': 'technical_failure', 'exception_type': type(exc).__name__, 'reason': str(exc)[:1000]}
            report = {'flow': flow, 'status': 'failed', 'error': error, 'whole_flow_completed': False}
        write_json(out / (flow + '-RECEIPT.json'), report)
        reports.append(report)
    stable = source == package_snapshot()
    result = {'kind': 'local-replay-run', 'version': 1,
              'status': 'completed' if stable and all(r['status'] == 'completed' for r in reports) else 'incomplete',
              'output': str(out), 'selected_flows': flows, 'source_unchanged_during_run': stable,
              'flows': [{'flow': r['flow'], 'status': r['status'], 'receipt': r['flow'] + '-RECEIPT.json',
                         'checks': len(r.get('checks', []))} for r in reports],
              'provider_calls': 0, 'continuous_motion_viewed': False, 'artistic_acceptance': 'unreviewed',
              'whole_vendor_replication_complete': False,
              'completion_meaning': 'Selected diagnostic recipes completed their explicit checks; original whole flows remain incomplete.'}
    write_json(out / 'RUN.json', result)
    rows = ''.join(f'<li>{r["flow"]}: {r["status"]} — <a href="{r["flow"]}-RECEIPT.json">receipt</a></li>' for r in reports)
    review_paths = sorted(p.relative_to(out).as_posix() for p in out.rglob('review.html'))
    import html
    links = ''.join(f'<li><a href="{html.escape(p, quote=True)}">{html.escape(p)}</a></li>' for p in review_paths)
    (out / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Local replication evidence</title>'
        '<h1>Local replication evidence</h1><p>Diagnostic mechanics only. Artwork and full vendor replication remain unaccepted.</p>'
        '<ul>' + rows + '</ul><h2>Frame and playback review pages</h2><ul>' + links + '</ul>')
    write_json(out / 'MANIFEST.json', {'kind': 'local-run-file-manifest', 'version': 1,
               'files': _inventory(out, ('MANIFEST.json',)), 'scope': 'File integrity, not semantic or aesthetic approval'})
    return result


def verify_run(directory):
    root = Path(directory).resolve()
    manifest_path = root / 'MANIFEST.json'
    if manifest_path.stat().st_size > 32 * 1024 * 1024:
        raise ValidationError('Replay manifest exceeds 32MiB')
    manifest = json.loads(manifest_path.read_text())
    if (not isinstance(manifest, dict) or manifest.get('kind') != 'local-run-file-manifest'
            or type(manifest.get('version')) is not int or manifest['version'] != 1
            or not isinstance(manifest.get('files'), list) or len(manifest['files']) > 100_000):
        raise ValidationError('Expected a local replay file manifest')
    expected = {}
    for row in manifest['files']:
        if (not isinstance(row, dict) or set(row) != {'file', 'bytes', 'sha256'}
                or not isinstance(row['file'], str) or not row['file']
                or type(row['bytes']) is not int or row['bytes'] < 0):
            raise ValidationError('Invalid manifest file record')
        validate_id(row['sha256'])
        name = row['file']
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or path.as_posix() != name or name in expected:
            raise ValidationError('Manifest paths must be unique relative paths without traversal')
        expected[name] = row
    actual = {r['file']: r for r in _inventory(root, ('MANIFEST.json',))}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(k for k in set(expected) & set(actual) if expected[k] != actual[k])
    return {'kind': 'local-run-integrity', 'status': 'completed' if not (missing or extra or changed) else 'failed',
            'files_checked': len(expected), 'missing': missing, 'extra': extra, 'changed': changed,
            'manifest_sha256': digest((root / 'MANIFEST.json').read_bytes()),
            'scope': 'Integrity relative to retained manifest; not independent authenticity, behavior or art acceptance.'}


def compare_sequences(baseline_store, baseline, candidate_store, candidate, output):
    """Compare supplied sequence pixels and clocks; no scoring/generation/alignment."""
    for path in (baseline_store, candidate_store):
        root = Path(path)
        if not (root / 'state.sqlite').is_file() or not (root / 'blobs').is_dir():
            raise ValidationError('Comparison requires existing input Stores')
    left_store, right_store = Store(baseline_store), Store(candidate_store)
    left, a = load_sequence(left_store, baseline)
    right, b = load_sequence(right_store, candidate)
    sequence_timeline(left)
    sequence_timeline(right)
    out = fresh_directory(output)
    frames = []
    for i in range(max(len(a), len(b))):
        row = {'index': i, 'baseline_present': i < len(a), 'candidate_present': i < len(b)}
        if i < len(a) and i < len(b):
            row['same_shape'] = a[i].shape == b[i].shape
            if row['same_shape']:
                rgb_changed = np.any(a[i][..., :3] != b[i][..., :3], axis=2)
                both_visible = (a[i][..., 3] > 0) & (b[i][..., 3] > 0)
                both_hidden = (a[i][..., 3] == 0) & (b[i][..., 3] == 0)
                row.update(rgba_changed_pixels=int(np.any(a[i] != b[i], axis=2).sum()),
                           alpha_changed_pixels=int((a[i][..., 3] != b[i][..., 3]).sum()),
                           both_visible_rgb_changed_pixels=int((rgb_changed & both_visible).sum()),
                           both_hidden_rgb_changed_pixels=int((rgb_changed & both_hidden).sum()))
                if a[i].shape[0] * a[i].shape[1] <= 1_048_576:
                    palettes = [np.unique(v[v[..., 3] > 0], axis=0) for v in (a[i], b[i])]
                    row['visible_rgba_palette'] = {'baseline_count': len(palettes[0]), 'candidate_count': len(palettes[1]),
                                                   'equal': bool(np.array_equal(*palettes))}
                else:
                    row['visible_rgba_palette'] = {'status': 'unsupported', 'reason': 'Palette analysis budget is 1048576 pixels; full pixel equality is still checked'}
            for key in ('duration', 'pivot', 'direction'):
                av, bv = left['frames'][i][key], right['frames'][i][key]
                row[key + '_equal'] = Fraction(*av) == Fraction(*bv) if key == 'duration' else av == bv
        frames.append(row)
    equal = len(a) == len(b) and left['play_count'] == right['play_count'] and all(
        r.get('same_shape') and r.get('rgba_changed_pixels') == 0 and all(r.get(k + '_equal') for k in ('duration', 'pivot', 'direction')) for r in frames)
    report = {'kind': 'supplied-sequence-comparison', 'version': 1, 'status': 'completed', 'exact_sequence_match': equal,
              'baseline': {'sequence': baseline, 'canvas': left['canvas'], 'play_count': left['play_count']},
              'candidate': {'sequence': candidate, 'canvas': right['canvas'], 'play_count': right['play_count']},
              'frames': frames, 'registration_policy': 'Original ordered full canvases; no alignment, resampling or coalescing',
              'artistic_acceptance': 'unreviewed', 'continuous_motion_viewed': False,
              'scope': 'Exact pixels, alpha, pivots, direction labels, rational holds and play count only; no quality score.'}
    report['exports'] = {}
    review_links = []
    import html
    for label, store, ident in [('baseline', left_store, baseline), ('candidate', right_store, candidate)]:
        exported = export_sequence(store, ident, out / label, ['png', 'manifest', 'review'])
        report['exports'][label] = exported
        preview = out / label / 'review' / 'review.html'
        if preview.is_file():
            review_links.append(f'<p><a href="{label}/review/review.html">{label} review</a></p>')
        else:
            review = exported['formats'].get('review', {})
            reason = review.get('reason', 'Review player unavailable; inspect exact PNGs and manifest')
            review_links.append(f'<p>{label} player unavailable: {html.escape(reason)}</p>')
    write_json(out / 'COMPARISON.json', report)
    (out / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Supplied comparison</title>'
        '<h1>Supplied comparison</h1><p>Separate players use their own declared clocks. Pixel equality does not establish animation quality.</p>'
        '<a href="COMPARISON.json">Pixel and clock comparison</a>' + ''.join(review_links))
    write_json(out / 'MANIFEST.json', {'kind': 'local-run-file-manifest', 'version': 1,
                                     'files': _inventory(out, ('MANIFEST.json',))})
    return report
