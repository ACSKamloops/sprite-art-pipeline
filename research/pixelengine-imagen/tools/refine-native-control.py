#!/usr/bin/env python3
"""Replay explicit native-pixel controls without generation or resampling.

Original source packages stay external. Exact connected matte erasure and
source-colored pencil/eraser recipes use the existing guarded editor toolkit.
"""
import argparse
from collections import deque
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, __version__ as pillow_version

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import (History, canonical_json, export_aseprite,
                        import_aseprite, load_project, project_hash)
from sprite_lab.core import render_frames


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


delivery = module('control_delivery', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng = module('control_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def matte_regions(image, rgba):
    """Four-connected exact RGBA components; erasure requires a border witness."""
    w, h = image.size
    pixels = image.load()
    seen, components = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or pixels[x, y] != tuple(rgba):
                continue
            q, points = deque([(x, y)]), []
            seen.add((x, y))
            while q:
                a, b = q.popleft()
                points.append([a, b])
                for c, d in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
                    if 0 <= c < w and 0 <= d < h and (c, d) not in seen and pixels[c, d] == tuple(rgba):
                        seen.add((c, d))
                        q.append((c, d))
            points.sort(key=lambda p: (p[1], p[0]))
            border = [p for p in points if p[0] in (0, w - 1) or p[1] in (0, h - 1)]
            components.append({'points': points, 'border_connected': bool(border),
                               'border_witness': border[0] if border else None})
    return components


def apply(history, operations, reason):
    return history.apply({'schema': 'sprite-edit-transaction/v1',
                          'expected_project_sha256': project_hash(history.project),
                          'reason': reason, 'operations': operations})


def save_variant(out, name, history, source_images, native_editor):
    folder = out / 'variants' / name
    folder.mkdir(parents=True)
    project = history.project
    project_path = folder / 'editable-project.json'
    project_path.write_text(canonical_json(project) + '\n')
    write(folder / 'journal.json', history.journal())
    replay = History.replay(history.initial, history.journal())
    assert project_hash(replay.project) == project_hash(project)
    for _ in range(history.cursor):
        replay.undo()
    assert project_hash(replay.project) == project_hash(history.initial)
    while replay.cursor < history.cursor:
        replay.redo()
    assert project_hash(replay.project) == project_hash(project)
    delivery.export(project_path, folder / 'delivery', 'walk', TOOLKIT, actor=name)
    apng.convert(folder / 'delivery/manifest.json', folder / 'delivery/apng')
    export_aseprite(project, folder / 'hero.aseprite', 'walk')
    assert project_hash(import_aseprite(folder / 'hero.aseprite')) == project_hash(project)
    images = render_frames(project, project['animations'][0]['frames'])
    changed = []
    for i, (before, after) in enumerate(zip(source_images, images)):
        coords = [[x, y] for y in range(80) for x in range(80) if before.getpixel((x, y)) != after.getpixel((x, y))]
        changed.append({'frame': i, 'count': len(coords), 'coordinates': coords})
    write(folder / 'source-diff.json', changed)
    editor_receipt = {'ase_toolkit_roundtrip_exact': True, 'external_editor_run': False}
    if native_editor:
        editor = folder / 'editor-roundtrip'
        editor.mkdir()
        command = [native_editor, '-b', str(folder / 'hero.aseprite'), '--save-as', str(editor / 'saved.aseprite'),
                   '--sheet', str(editor / 'sheet.png'), '--sheet-type', 'horizontal',
                   '--data', str(editor / 'sheet.json'), '--format', 'json-array']
        result = subprocess.run(command, capture_output=True, text=True)
        write(editor / 'invocation.json', {'argv': command, 'returncode': result.returncode,
                                          'stdout': result.stdout, 'stderr': result.stderr})
        result.check_returncode()
        imported = import_aseprite(editor / 'saved.aseprite', folder / 'hero.aseprite.sprite-lab.json')
        assert project_hash(imported) == project_hash(project)
        sheet = Image.open(editor / 'sheet.png').convert('RGBA')
        assert sheet.size == (640, 80)
        assert all(sheet.crop((i * 80, 0, (i + 1) * 80, 80)).tobytes() == image.tobytes() for i, image in enumerate(images))
        data = json.loads((editor / 'sheet.json').read_text())
        assert [f['duration'] for f in data['frames']] == [125] * 8
        editor_receipt = {'ase_toolkit_roundtrip_exact': True, 'external_editor_run': True,
                          'saved_ase_sha256': sha(editor / 'saved.aseprite'),
                          'all_eight_actual_tool_rgba_exact': True, 'actual_tool_holds_ms': [125] * 8,
                          'whole_project_reimport_exact': True}
    receipt = {'id': name, 'project_canonical_sha256': project_hash(project),
               'project_file_sha256': sha(project_path),
               'atlas_sha256': sha(folder / 'delivery/atlas.png'),
               'apng_sha256': sha(folder / 'delivery/apng/animation.apng.png'),
               'journal_replay_undo_redo_exact': True, 'editor': editor_receipt,
               'canvas': [80, 80], 'holds_ms': [125] * 8,
               'per_pose_recenter_or_retime': False,
               'boundary': 'Source-preserving control or manual candidate. Mechanical checks do not establish art acceptance.'}
    write(folder / 'CONTROL-RECEIPT.json', receipt)
    return receipt, images


def contact(out, case, rows):
    sheet = Image.new('RGB', (1280, 180 * len(rows)), (50, 57, 77))
    draw = ImageDraw.Draw(sheet)
    for r, (name, images) in enumerate(rows):
        draw.text((4, r * 180 + 3), name, fill='white')
        for i, image in enumerate(images):
            full = Image.new('RGBA', (160, 160), (50, 57, 77, 255))
            full.alpha_composite(image.resize((160, 160), Image.Resampling.NEAREST))
            sheet.paste(full, (i * 160, r * 180 + 18))
    sheet.save(out / f'{case}-ordered-2x.png')
    # Eight affected predecessor/current pairs, with explicit wrap and control.
    for name, images in rows[1:]:
        pairs = Image.new('RGB', (8 * 320, 184), (50, 57, 77))
        d = ImageDraw.Draw(pairs)
        for i in range(8):
            d.text((i * 320 + 4, 2), f'{(i - 1) % 8} -> {i}' + (' WRAP' if i == 0 else ''), fill='white')
            for p, f in enumerate(((i - 1) % 8, i)):
                full = Image.new('RGBA', (160, 160), (50, 57, 77, 255))
                full.alpha_composite(images[f].resize((160, 160), Image.Resampling.NEAREST))
                pairs.paste(full, (i * 320 + p * 160, 22))
        pairs.save(out / f'{name}-all-pairs-2x.png')


def run(args):
    root, out = args.inputs.resolve(), args.output.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('Output must be fresh')
    recipe = json.loads(args.recipe.read_text())
    if recipe['schema'] != 'native-source-pixel-control/v1':
        raise ValueError('Unsupported recipe')
    # Bind all inputs before creating the candidate directory.
    hashes = {}
    appearance = recipe['appearance_reference']
    if sha(root / appearance['file']) != appearance['sha256']:
        raise ValueError('Frozen appearance reference mismatch')
    hashes[appearance['file']] = appearance['sha256']
    for case in recipe['cases'].values():
        for key, relative in [('webp', case['webp']), ('project', case['project'])]:
            actual = sha(root / relative)
            if key == 'webp' and actual != case['webp_sha256']:
                raise ValueError('Frozen native WebP mismatch')
            hashes[relative] = actual
    # Reject stale/manual sample coordinates before making an output folder.
    for candidate in recipe['candidates']:
        case = recipe['cases'][candidate['case']]
        with Image.open(root / case['webp']) as animation:
            for edit in candidate['edits']:
                for paint in edit.get('paint', []):
                    frame, x, y = paint['source']
                    animation.seek(frame)
                    if list(animation.convert('RGBA').getpixel((x, y))) != paint['expected_rgba']:
                        raise ValueError('Source sample coordinate does not match its declared RGBA')
    out.mkdir(parents=True)
    shutil.copy2(args.recipe, out / 'recipe.json')
    shutil.copy2(__file__, out / 'runner.py')
    receipts, rows = [], {}
    for key, case in recipe['cases'].items():
        initial = load_project((root / case['project']).read_text())
        assert initial['canvas']['width'] == initial['canvas']['height'] == 80
        assert len(initial['frames']) == 8 and len(initial['animations']) == 1
        assert initial['animations'][0]['fps'] == 8 and initial['animations'][0]['loop']
        assert all(f['duration_ticks'] == 1 for f in initial['frames'])
        assert len(initial['layers']) == 1
        decoded, holds = [], []
        with Image.open(root / case['webp']) as animation:
            for i in range(animation.n_frames):
                animation.seek(i)
                decoded.append(animation.convert('RGBA'))
                holds.append(animation.info['duration'])
        assert len(decoded) == 8 and holds == [125] * 8
        assert all(i.size == (80, 80) for i in decoded)
        rendered = render_frames(initial, initial['animations'][0]['frames'])
        assert all(a.tobytes() == b.tobytes() for a, b in zip(decoded, rendered))
        original = out / 'immutable-baseline' / key
        original.mkdir(parents=True)
        shutil.copy2(root / case['webp'], original / 'original.webp')
        shutil.copy2(root / case['project'], original / 'original-project.json')
        history = History(initial)
        receipt, images = save_variant(out, key + '-baseline', history, decoded, None)
        receipts.append(receipt)
        rows[key] = [(receipt['id'], images)]
        if key == 'A':
            colors = {tuple(p) for p in recipe['source_scarf_track']['tail_rgba']}
            track = copy.deepcopy(recipe['source_scarf_track'])
            for frame in track['frames']:
                image = decoded[frame['index']]
                visible = [[x, y] for y in range(26, 40) for x in range(20, 31)
                           if image.getpixel((x, y)) in colors]
                frame['visible_tail_color_coordinates_in_declared_window'] = visible
                frame['visible_color_tip'] = min(visible, key=lambda p: (p[0], -p[1])) if visible else None
                frame['collar_proxy_rgba'] = list(image.getpixel(tuple(frame['collar_proxy'])))
            track['webp_sha256'] = case['webp_sha256']
            write(out / 'A-source-scarf-track.json', track)
        masks, operations = [], []
        for i, image in enumerate(decoded):
            regions = matte_regions(image, case['matte_rgba'])
            points = [p for r in regions if r['border_connected'] for p in r['points']]
            retained = [p for r in regions if not r['border_connected'] for p in r['points']]
            cel = initial['frames'][i]['cels'][initial['layers'][0]['id']]
            operations.append({'op': 'erase', 'cel_id': cel, 'points': points, 'mask': points})
            masks.append({'frame': i, 'erase_coordinates': points, 'retained_enclosed_gray': retained,
                          'components': [{'count': len(r['points']), 'border_connected': r['border_connected'],
                                          'border_witness': r['border_witness']} for r in regions]})
        apply(history, operations, 'Exact RGBA four-connected border matte only; enclosed same-color pixels are protected')
        write(out / f'{key}-matte-masks.json', {'rgba': case['matte_rgba'], 'connectivity': 4, 'frames': masks})
        cutout = copy.deepcopy(history.project)
        cutout_images = render_frames(cutout, cutout['animations'][0]['frames'])
        for before, after, mask in zip(decoded, cutout_images, masks):
            erased = {tuple(p) for p in mask['erase_coordinates']}
            assert all(after.getpixel((x, y)) == ((0, 0, 0, 0) if (x, y) in erased else before.getpixel((x, y))) for y in range(80) for x in range(80))
        receipt, images = save_variant(out, key + '-cutout', history, decoded, args.native_editor)
        receipt['matte_only_nonmatte_rgba_unchanged'] = True
        write(out / 'variants' / receipt['id'] / 'CONTROL-RECEIPT.json', receipt)
        receipts.append(receipt)
        rows[key].append((receipt['id'], images))
        for candidate in (c for c in recipe['candidates'] if c['case'] == key):
            edited = History.replay(initial, history.journal())
            witnesses, changes = [], []
            for edit in candidate['edits']:
                i = edit['frame']
                cel = initial['frames'][i]['cels'][initial['layers'][0]['id']]
                ops, owned = [], []
                for paint in edit.get('paint', []):
                    sf, sx, sy = paint['source']
                    color = decoded[sf].getpixel((sx, sy))
                    assert list(color) == paint['expected_rgba'] and color[3] == 255
                    index = edited.project['palette'].index(list(color))
                    points = paint['points']
                    ops.append({'op': 'paint', 'cel_id': cel, 'points': [p + [index] for p in points], 'mask': points})
                    owned.extend(points)
                    witnesses.append({'frame': i, 'destinations': points, 'source_pixel': paint['source'], 'rgba': list(color)})
                if edit.get('erase'):
                    points = edit['erase']
                    ops.append({'op': 'erase', 'cel_id': cel, 'points': points, 'mask': points})
                    owned.extend(points)
                apply(edited, ops, edit['reason'])
                changes.append({'frame': i, 'allowed_mask': sorted(set(map(tuple, owned)), key=lambda p: (p[1], p[0])), 'reason': edit['reason']})
            candidate_images = render_frames(edited.project, edited.project['animations'][0]['frames'])
            for i, (before, after) in enumerate(zip(cutout_images, candidate_images)):
                owned = {tuple(p) for m in changes if m['frame'] == i for p in m['allowed_mask']}
                assert all(before.getpixel((x, y)) == after.getpixel((x, y)) for y in range(80) for x in range(80) if (x, y) not in owned)
            write(out / (candidate['id'] + '-paint-masks.json'), {'source_samples': witnesses, 'edits': changes,
                                                               'outside_mask_rgba_unchanged': True})
            receipt, images = save_variant(out, candidate['id'], edited, decoded, args.native_editor)
            receipts.append(receipt)
            rows[key].append((receipt['id'], images))
        contact(out, key, rows[key])
    assert all(sha(root / relative) == before for relative, before in hashes.items())
    write(out / 'RESULTS.json', {'schema': 'native-source-pixel-control-results/v1',
                               'recipe_sha256': sha(args.recipe), 'runner_sha256': sha(__file__),
                               'runtime': {'python': sys.version, 'pillow': pillow_version},
                               'dependency_sha256': {str(p.relative_to(REPO)): sha(p) for p in [
                                   TOOLKIT / 'sprite_lab/core.py', TOOLKIT / 'sprite_lab/history.py',
                                   TOOLKIT / 'sprite_lab/aseprite.py', TOOLKIT / 'sprite_lab/canonical.py',
                                   REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py',
                                   REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py',
                                   Path(__file__).with_name('review-native-controls.html')]},
                               'source_sha256': hashes, 'source_immutable': True, 'variants': receipts,
                               'generated_or_provider_calls': 0, 'art_acceptance': 'pending'})
    shutil.copy2(Path(__file__).with_name('review-native-controls.html'), out / 'index.html')
    write(out / 'SHA256.json', {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps({'output': str(out), 'variants': [r['id'] for r in receipts], 'source_immutable': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--recipe', type=Path, default=Path(__file__).with_name('native-control-recipe.json'))
    parser.add_argument('--native-editor', default=None)
    run(parser.parse_args())
