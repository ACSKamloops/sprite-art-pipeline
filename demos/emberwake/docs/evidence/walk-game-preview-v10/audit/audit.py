#!/usr/bin/env python3
"""Read-only v9/v10 bake/runtime delta audit; writes only beside this script.

Requires Python 3 and Pillow. Run: python /absolute/path/to/audit.py
Generated .godot/output and .git trees are excluded. No engine is invoked.
"""
from pathlib import Path
from fractions import Fraction
import collections
import datetime
import hashlib
import json
import re
import sys

from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = Path('/home/astra/artifacts')
ROOTS = {v: BASE / f'emberwake-walk-game-preview-{v}' for v in ('v9', 'v10')}
ACTORS = ('rowan', 'lyra', 'brann')
EXPECTED = list(range(136, 144)) + list(range(232, 240))
CHECKS = []


def digest(data):
    return hashlib.sha256(data).hexdigest()


def readj(path):
    return json.loads(path.read_text())


def writej(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def check(name, ok, detail=None):
    CHECKS.append({'check': name, 'passed': bool(ok), 'detail': detail})


def inventory(root):
    rows = {}
    for tree in ('bake', 'project'):
        for p in sorted((root / tree).rglob('*')):
            rel = p.relative_to(root)
            if not p.is_file() or any(x in ('.godot', 'output', '.git') for x in rel.parts):
                continue
            st = p.stat()
            rows[rel.as_posix()] = {'sha256': digest(p.read_bytes()), 'bytes': st.st_size,
                                   'uid': st.st_uid, 'symlink': p.is_symlink()}
    return rows


def differences(a, b, path=''):
    if type(a) is not type(b):
        return [{'path': path, 'v9': a, 'v10': b}]
    if isinstance(a, dict):
        result = []
        for key in sorted(set(a) | set(b)):
            p = path + '/' + str(key)
            if key not in a or key not in b:
                result.append({'path': p, 'v9': a.get(key), 'v10': b.get(key)})
            else:
                result.extend(differences(a[key], b[key], p))
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [{'path': path, 'v9': a, 'v10': b}]
        return [row for i, (x, y) in enumerate(zip(a, b))
                for row in differences(x, y, path + '/' + str(i))]
    return [] if a == b else [{'path': path, 'v9': a, 'v10': b}]


def category(path):
    if path.startswith('project/docs/'):
        return 'documentation_or_saved_evidence'
    if path.startswith('project/tests/'):
        return 'test_helper'
    if path.startswith('project/scripts/') and path.endswith('.py'):
        return 'offline_python_helper'
    return 'bake' if path.startswith('bake/') else 'runtime_or_project_config'


def png(path):
    image = Image.open(path)
    image.load()
    return image, {'format': image.format, 'mode': image.mode, 'size': list(image.size)}


def cell(image, index, columns=16):
    x, y = index % columns * 128, index // columns * 128
    return image.crop((x, y, x + 128, y + 128))


before = {v: inventory(r) for v, r in ROOTS.items()}
writej('inventory-start.json', before)
paths = sorted(set(before['v9']) | set(before['v10']))
file_diffs = []
json_diffs = []
for path in paths:
    a, b = before['v9'].get(path), before['v10'].get(path)
    if a is None or b is None or a['sha256'] != b['sha256']:
        state = 'added' if a is None else 'removed' if b is None else 'changed'
        file_diffs.append({'path': path, 'status': state, 'category': category(path),
                           'v9': a, 'v10': b})
        if state == 'changed' and path.endswith('.json'):
            json_diffs.append({'file': path, 'differences': differences(
                readj(ROOTS['v9'] / path), readj(ROOTS['v10'] / path))})
writej('file-differences.json', file_diffs)
writej('json-differences.json', json_diffs)

atlas_rows = []
binding_rows = []
manifests = {}
for actor in ACTORS:
    images = {}
    headers = {}
    lineage_bad = []
    for version, root in ROOTS.items():
        folder = root / 'bake' / actor
        image, header = png(folder / 'atlas.png')
        images[version], headers[version] = image, header
        manifest = readj(folder / 'animations.json')
        manifests[version, actor] = manifest
        check(f'{version}/{actor}: actual PNG RGBA atlas and 128px grid',
              header['format'] == 'PNG' and header['mode'] == 'RGBA'
              and manifest['cell'] == [128, 128] and manifest['columns'] == 16
              and image.width == 2048 and image.height % 128 == 0, header)
        lineage = readj(folder / 'lineage.json')
        for i, entry in enumerate(lineage):
            if entry.get('rgba_sha256') != digest(cell(image, i).tobytes()):
                lineage_bad.append([version, i])
        replay = readj(root / 'bake/REPLAY.json')['actors'][actor]
        check(f'{version}/{actor}: REPLAY binds actual atlas and manifest',
              replay['atlas_sha256'] == digest((folder / 'atlas.png').read_bytes())
              and replay['manifest_sha256'] == digest((folder / 'animations.json').read_bytes()))
        catalog = readj(root / 'project/assets/characters/catalog.json')
        entry = next(x for x in catalog['characters'] if x['id'] == actor)
        row = {'version': version, 'actor': actor}
        for key, filename in (('atlas', 'atlas.png'), ('manifest', 'animations.json')):
            target = root / 'project' / entry[key].removeprefix('res://')
            equal = (folder / filename).read_bytes() == target.read_bytes()
            row[key + '_bake_project_byte_identical'] = equal
            check(f'{version}/{actor}: catalog {key} is exact bake copy', equal)
        binding_rows.append(row)
    check(f'{actor}: all recorded lineage RGBA hashes bind actual cells', not lineage_bad, lineage_bad)
    a, b = images['v9'], images['v10']
    check(f'{actor}: atlas format/dimensions unchanged', headers['v9'] == headers['v10'])
    changed = []
    for i in range(a.width // 128 * (a.height // 128)):
        ac, bc = cell(a, i), cell(b, i)
        ar, br = ac.tobytes(), bc.tobytes()
        if ar != br:
            changed.append({'index': i, 'row': i // 16, 'column': i % 16,
                            'rect_xywh': [i % 16 * 128, i // 16 * 128, 128, 128],
                            'v9_rgba_sha256': digest(ar), 'v10_rgba_sha256': digest(br),
                            'changed_RGBA_pixels': sum(ar[n:n+4] != br[n:n+4]
                                                      for n in range(0, len(ar), 4))})
    expected = EXPECTED if actor == 'brann' else []
    check(f'{actor}: exact expected changed atlas cells', [x['index'] for x in changed] == expected,
          [x['index'] for x in changed])
    atlas_rows.append({'actor': actor, 'headers': headers,
                       'PNG_bytes_identical': before['v9'][f'bake/{actor}/atlas.png']['sha256']
                       == before['v10'][f'bake/{actor}/atlas.png']['sha256'],
                       'physical_grid_cells_including_padding': a.width // 128 * (a.height // 128),
                       'changed_cells': changed})
    am, bm = manifests['v9', actor], manifests['v10', actor]
    semantic_a = {k: v for k, v in am.items() if k != 'directional_source'}
    semantic_b = {k: v for k, v in bm.items() if k != 'directional_source'}
    check(f'{actor}: entire animation manifest unchanged except directional_source', semantic_a == semantic_b)
    check(f'{actor}: all 48 clip definitions and hand tracks unchanged',
          len(am['animations']) == len(bm['animations']) == 48
          and am['animations'] == bm['animations']
          and am['cast_hand_tracks'] == bm['cast_hand_tracks']
          and am['cast_hand'] == bm['cast_hand'])
writej('atlas-cell-deltas.json', atlas_rows)
writej('bake-project-bindings.json', binding_rows)

frame_checks = []
for version, root in ROOTS.items():
    folder = root / 'bake/brann'
    atlas = Image.open(folder / 'atlas.png')
    strip, header = png(folder / 'southeast-native.png')
    check(f'{version}: southeast-native actual PNG layout',
          header == {'format': 'PNG', 'mode': 'RGBA', 'size': [1024, 512]}, header)
    manifest = manifests[version, 'brann']
    replay = readj(root / 'bake/REPLAY.json')['actors']['brann']['source_registration']['southeast']['walk_override']
    ownership = readj(folder / 'source-ownership.json')['southeast']['walk_override']
    check(f'{version}: REPLAY and ownership agree on selected override', replay == ownership)
    for direction, indices in (('southeast', list(range(136, 144))),
                               ('southwest', list(range(232, 240)))):
        clip = manifest['animations'][direction + '_walk']
        check(f'{version}: {direction} frame order, holds and loop exact',
              clip == {'frames': indices, 'holds': [0.05625] * 8, 'loop': True}
              and sum(Fraction(str(h)) for h in clip['holds']) == Fraction(9, 20))
    for i in range(32):
        p = folder / 'southeast' / f'{i:02d}.png'
        im, header = png(p)
        x, y = i % 8 * 128, i // 8 * 128
        check(f'{version}: native strip cel {i:02d} binds individual PNG',
              im.tobytes() == strip.crop((x, y, x+128, y+128)).tobytes())
        if i >= 8:
            continue
        mirror = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        mirror.paste(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (1, 0))
        ok = (header == {'format': 'PNG', 'mode': 'RGBA', 'size': [128, 128]}
              and im.tobytes() == cell(atlas, 136+i).tobytes()
              and mirror.tobytes() == cell(atlas, 232+i).tobytes()
              and digest(p.read_bytes()) == replay['frames'][i]['sha256'])
        frame_checks.append({'version': version, 'frame': i, 'SE_and_pivot_mirrored_SW_bind': ok})
        check(f'{version}: selected SE cel {i:02d}, mirrored SW and source hash bind actual pixels', ok)
writej('frame-bindings.json', frame_checks)

jd = {r['file']: r['differences'] for r in json_diffs}
allowed_lineage = {f'/{i}/{field}' for i in EXPECTED
                   for field in ('rgba_sha256', 'selected_override/path', 'selected_override/sha256')}
check('Brann lineage changes only intended cells and source/hash metadata',
      {r['path'] for r in jd['bake/brann/lineage.json']} == allowed_lineage)
allowed_ownership = {f'/southeast/walk_override/frames/{i}/{k}' for i in range(8) for k in ('path', 'sha256')}
allowed_ownership.add('/southeast/walk_override/scope')
check('Brann ownership changes only selected SE source binding/scope',
      {r['path'] for r in jd['bake/brann/source-ownership.json']} == allowed_ownership)
allowed_replay = {'/config_sha256', '/actors/brann/atlas_sha256'}
allowed_replay.update(f'/actors/{a}/manifest_sha256' for a in ACTORS)
allowed_replay.update('/actors/brann/source_registration' + p for p in allowed_ownership)
check('REPLAY changes only expected configuration/source/artifact binding metadata',
      {r['path'] for r in jd['bake/REPLAY.json']} == allowed_replay)
expected_bake_pngs = {f'bake/brann/southeast/{i:02d}.png' for i in range(8)}
expected_bake_pngs.update(('bake/brann/atlas.png', 'bake/brann/southeast-native.png'))
check('All other bake PNG files byte-identical',
      {r['path'] for r in file_diffs if r['path'].startswith('bake/') and r['path'].endswith('.png')}
      == expected_bake_pngs)
runtime_allowed = {'project/assets/characters/brann/atlas.png',
                   'project/assets/characters/brann/animations.json',
                   'project/assets/characters/lyra/animations.json',
                   'project/assets/hero/animations.json'}
runtime_diffs = [r for r in file_diffs if r['category'] == 'runtime_or_project_config']
check('Runtime/project-config differences limited to Brann atlas and three source-pointer manifests',
      {r['path'] for r in runtime_diffs} == runtime_allowed
      and all(r['status'] == 'changed' for r in runtime_diffs))
for r in runtime_diffs:
    if r['path'].endswith('.json'):
        check(r['path'] + ': only source pointer changed',
              [d['path'] for d in jd[r['path']]] == ['/directional_source'])

nonruntime = [r for r in file_diffs if r['category'] in
              ('documentation_or_saved_evidence', 'test_helper', 'offline_python_helper')]
runtime_text = []
for rel in before['v10']:
    if category(rel) == 'runtime_or_project_config' and Path(rel).suffix in ('.gd', '.godot', '.tscn', '.tres', '.cfg'):
        runtime_text.append((rel, (ROOTS['v10'] / rel).read_text()))
references = [{'file': rel, 'needle': Path(d['path']).name}
              for rel, content in runtime_text for d in nonruntime
              if Path(d['path']).name in content]
check('Changed/added/removed helpers or evidence are not referenced by runtime text', not references, references)
check('directional_source is absent from runtime script/resource/config consumers',
      not any('directional_source' in content for _, content in runtime_text))
reference_rows = [{'file': rel, 'line': i, 'text': line.strip()}
                  for rel, content in runtime_text for i, line in enumerate(content.splitlines(), 1)
                  if 'res://' in line or 'FileAccess' in line or 'DirAccess' in line]
writej('runtime-reference-evidence.json', {'helper_references': references,
                                         'static_runtime_references': reference_rows})

after = {v: inventory(r) for v, r in ROOTS.items()}
writej('inventory-end.json', after)
drift = []
for version in ROOTS:
    for rel in sorted(set(before[version]) | set(after[version])):
        a, b = before[version].get(rel), after[version].get(rel)
        if a != b:
            drift.append({'version': version, 'path': rel, 'start': a, 'end': b})
check('All audited bake/project files stable during this script execution', not drift, drift)
writej('checks.json', CHECKS)
summary = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'audit_script_sha256': digest(Path(__file__).read_bytes()),
           'roots': {k: str(v) for k, v in ROOTS.items()},
           'excluded_tree_components': ['.godot', 'output', '.git'],
           'inventory_counts': {v: len(x) for v, x in before.items()},
           'file_diff_counts': dict(collections.Counter(x['status'] for x in file_diffs)),
           'whole_audited_directory_equal': not file_diffs,
           'runtime_delta_matches_intended_scope': all(x['passed'] for x in CHECKS),
           'checks_passed': sum(x['passed'] for x in CHECKS), 'checks_total': len(CHECKS),
           'failed_checks': [x for x in CHECKS if not x['passed']],
           'expected_Brann_changed_cells': EXPECTED,
           'source_config_and_source_art_files_outside_scope': 'Binding strings/hashes inspected; external files not opened.',
           'nonruntime_directory_differences': nonruntime,
           'limits': ['Read-only static file, JSON semantic and decoded RGBA verification.',
                      'No engine/browser/runtime test or art rerating.',
                      'Generated .godot/output excluded while import may be running.',
                      'Static references support helper classification; full directory equality is false.']}
writej('receipt.json', summary)
(OUT / 'SHA256SUMS').write_text(''.join(f"{digest((OUT/n).read_bytes())}  {n}\n"
    for n in ('audit.py', 'receipt.json', 'checks.json', 'inventory-start.json', 'inventory-end.json',
              'file-differences.json', 'json-differences.json', 'atlas-cell-deltas.json',
              'bake-project-bindings.json', 'frame-bindings.json', 'runtime-reference-evidence.json')))
print(json.dumps({k: summary[k] for k in ('inventory_counts', 'file_diff_counts',
      'runtime_delta_matches_intended_scope', 'checks_passed', 'checks_total', 'failed_checks')}, indent=2))
sys.exit(0 if summary['runtime_delta_matches_intended_scope'] else 1)
