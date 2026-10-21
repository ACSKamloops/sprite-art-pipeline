#!/usr/bin/env python3
"""Apply external, hash-bound alpha policies and literal pencil plans offline.

This is a recipe runner, not a drawing model. Artwork, exact masks, source pins
and case-specific pencil coordinates belong in the external plan/artifact tree.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import (History, canonical_json, export_aseprite, import_aseprite,
                        load_json, load_project, project_hash, render_frame)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


constructor = module('pixel_candidate_constructor', TOOLKIT / 'scripts/sprite_construct.py')
delivery = module('pixel_candidate_delivery', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng = module('pixel_candidate_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def changed(before, after):
    require(before.size == after.size, 'Changed canvas')
    return [[i % before.width, i // before.width]
            for i, (a, b) in enumerate(zip(before.get_flattened_data(), after.get_flattened_data())) if a != b]


def alpha_color(color, policy):
    mode = policy['mode']
    if mode == 'cutoff':
        return (0, 0, 0, 0) if color[3] < policy['floor'] else color
    if mode == 'binary':
        return (0, 0, 0, 0) if color[3] < policy['threshold'] else (*color[:3], 255)
    if mode == 'coverage':
        if color[3] < policy['floor']:
            return (0, 0, 0, 0)
        return (*color[:3], 255) if color[3] >= policy['opaque_at'] else color
    raise ValueError('Unknown alpha policy: ' + mode)


def pencil(history, cel_id, pixels, reason, folder, step):
    """Use only guarded palette-add and masked paint transactions."""
    current = history.project
    width = current['canvas']['width']
    lookup = {tuple(c): i for i, c in enumerate(current['palette'])}
    operations, points, before, mask = [], [], [], []
    used = set()
    for x, y, rgba in pixels:
        require(type(x) is int and type(y) is int and 0 <= x < width and 0 <= y < current['canvas']['height'], 'Pencil outside stage')
        require((x, y) not in used, 'Duplicate pencil coordinate')
        used.add((x, y))
        color = tuple(rgba)
        require(len(color) == 4 and all(type(c) is int and 0 <= c <= 255 for c in color), 'Invalid RGBA')
        old = current['palette'][current['cels'][cel_id]['pixels'][y * width + x]]
        if color == tuple(old):
            continue
        if color not in lookup:
            lookup[color] = len(current['palette']) + sum(op['op'] == 'palette_add' for op in operations)
            operations.append({'op': 'palette_add', 'rgba': list(color)})
        points.append([x, y, lookup[color]])
        before.append([x, y, old])
        mask.append([x, y])
    if not points:
        return None
    operations.append({'op': 'paint', 'cel_id': cel_id, 'points': points, 'mask': mask})
    transaction = {'schema': 'sprite-edit-transaction/v1',
                   'expected_project_sha256': project_hash(current), 'reason': reason,
                   'operations': operations}
    receipt = history.apply(transaction)
    write(folder / f'{step:02d}-mask.json', {'cel_id': cel_id, 'mask': mask, 'before_rgba': before,
                                          'after_rgba': [[x, y, history.project['palette'][index]] for x, y, index in points]})
    write(folder / f'{step:02d}-receipt.json', receipt)
    return mask


def package(project, path, animation, native_editor):
    project_path = path.parent / (path.name + '.project.json')
    project_path.write_text(canonical_json(project) + '\n')
    delivery.export(project_path, path, animation, TOOLKIT, actor=path.name)
    apng.convert(path / 'manifest.json', path / 'apng')
    ase = path / 'editable.aseprite'
    export_aseprite(project, ase, animation)
    result = {'canonical_project_sha256': project_hash(project), 'project_file_sha256': sha(path / 'project.json'),
              'atlas_sha256': sha(path / 'atlas.png'), 'apng_sha256': sha(path / 'apng/animation.apng.png')}
    if native_editor:
        native = path / 'native-editor-check'
        native.mkdir()
        saved = native / 'resaved.aseprite'
        command = [native_editor, '-b', str(ase), '--save-as', str(saved), '--sheet', str(native / 'sheet.png'),
                   '--sheet-type', 'horizontal', '--data', str(native / 'frames.json'), '--format', 'json-array']
        process = subprocess.run(command, capture_output=True, text=True)
        write(native / 'invocation.json', {'argv': command, 'returncode': process.returncode,
                                          'stdout': process.stdout, 'stderr': process.stderr})
        require(process.returncode == 0 and saved.is_file() and (native / 'sheet.png').is_file(), 'Native editor did not produce outputs')
        reopened = import_aseprite(saved, Path(str(ase) + '.sprite-lab.json'))
        require(project_hash(reopened) == project_hash(project), 'Native editor changed project/RGBA/clock')
        sheet = Image.open(native / 'sheet.png').convert('RGBA')
        manifest = json.loads((path / 'manifest.json').read_text())
        width, height = manifest['canvas']
        require(sheet.size == (width * len(manifest['frames']), height), 'Native editor horizontal sheet dimensions changed')
        for i, frame in enumerate(manifest['frames']):
            actual = sheet.crop((i * width, 0, (i + 1) * width, height))
            require(actual.tobytes() == Image.open(path / frame['file']).convert('RGBA').tobytes(), 'Native editor sheet mismatch at frame ' + str(i))
        result['native_save_reopen_project_and_sheet_exact'] = True
        write(native / 'verification.json', result)
    return result


def run(args):
    source, plan_path, out = args.source.resolve(), args.plan.resolve(), args.output.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh output directory required')
    plan = load_json(plan_path.read_text())
    require(plan['schema'] == 'literal-pixel-candidates/v1', 'Unknown plan')
    require(sha(source / 'project.json') == plan['source_project_file_sha256'], 'Stale project file pin')
    initial = load_project((source / 'project.json').read_text())
    require(project_hash(initial) == plan['source_project_canonical_sha256'], 'Stale project content pin')
    anim = next(a for a in initial['animations'] if a['id'] == plan['animation'])
    initial_hashes = {'project.json': sha(source / 'project.json')}
    out.mkdir(parents=True)
    frozen = out / 'source'
    frozen.mkdir()
    shutil.copy2(source / 'project.json', frozen / 'project.json')
    shutil.copy2(plan_path, out / 'authoring-plan.json')
    frame_by_id = {f['id']: f for f in initial['frames']}
    spec_frames = []
    for i, frame_id in enumerate(anim['frames']):
        name = f'frames/{i:04d}.png'
        require(sha(source / name) == plan['source_frames_sha256'][i], 'Stale frame pin')
        initial_hashes[name] = sha(source / name)
        (frozen / 'frames').mkdir(exist_ok=True)
        shutil.copy2(source / name, frozen / name)
        actual = Image.open(source / name).convert('RGBA')
        require(render_frame(initial, frame_id).tobytes() == actual.tobytes(), 'Immutable project/frame mismatch')
        spec_frames.append({'id': frame_id, 'duration_ticks': frame_by_id[frame_id]['duration_ticks'],
                            'landmarks': frame_by_id[frame_id]['landmarks'], 'cels': {'body': {'image': name, 'at': [0, 0]}}})
    require(len(initial['layers']) == 1 and initial['layers'][0]['id'] == 'body', 'Recipe source audit currently requires one fused body layer')
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': initial['canvas'], 'layers': initial['layers'],
            'frames': spec_frames, 'animations': [anim], 'provenance': {'role': 'Independent constructor transport of frozen source PNGs; no art approval'}}
    write(frozen / 'construction-spec.json', spec)
    reconstructed = constructor.construct(frozen / 'construction-spec.json')
    require(all(render_frame(reconstructed, fid).tobytes() == render_frame(initial, fid).tobytes() for fid in anim['frames']), 'Constructor source replay mismatch')
    summaries = {'control': package(initial, out / 'control', anim['id'], args.native_editor)}
    for candidate in plan['candidates']:
        name = candidate['id']
        require(re.fullmatch('[A-Za-z0-9_-]+', name) is not None and name not in summaries, 'Invalid/duplicate candidate ID')
        folder = out / (name + '-journal')
        folder.mkdir()
        history = History(initial)
        masks = {cid: set() for cid in initial['cels']}
        step = 0
        policy = candidate['alpha_policy']
        for cel_id, cel in initial['cels'].items():
            pixels = [[i % initial['canvas']['width'], i // initial['canvas']['width'], list(alpha_color(tuple(initial['palette'][index]), policy))]
                      for i, index in enumerate(cel['pixels'])]
            mask = pencil(history, cel_id, pixels, candidate['reason'] + '; alpha policy ' + json.dumps(policy), folder, step)
            step += 1
            masks[cel_id].update(map(tuple, mask or []))
        for local in candidate.get('pencil_steps', []):
            cel_id = frame_by_id[local['frame_id']]['cels']['body']
            mask = pencil(history, cel_id, local['pixels'], local['reason'], folder, step)
            step += 1
            masks[cel_id].update(map(tuple, mask or []))
        journal = history.journal()
        write(folder / 'journal.json', journal)
        require(project_hash(History.replay(initial, journal).project) == project_hash(history.project), 'Journal replay mismatch')
        final = copy.deepcopy(history.project)
        while history.cursor:
            history.undo()
        require(project_hash(history.project) == project_hash(initial), 'Undo mismatch')
        while history.cursor < len(history.records):
            history.redo()
        require(project_hash(history.project) == project_hash(final), 'Redo mismatch')
        for key in ('canvas', 'frames', 'animations', 'layers', 'provenance'):
            require(final[key] == initial[key], 'Unexpected metadata change: ' + key)
        per_frame = []
        for fid in anim['frames']:
            before, after = render_frame(initial, fid), render_frame(final, fid)
            coords = changed(before, after)
            cid = frame_by_id[fid]['cels']['body']
            require(set(map(tuple, coords)) <= masks[cid], 'Outside-mask composited change')
            per_frame.append({'frame_id': fid, 'changed_pixels': len(coords), 'coordinates': coords,
                              'alpha_positive_bounds': after.getchannel('A').getbbox(),
                              'partial_alpha_pixels': sum(0 < a < 255 for a in after.getchannel('A').get_flattened_data())})
        result = package(final, out / name, anim['id'], args.native_editor)
        result.update({'alpha_policy': policy, 'reason': candidate['reason'], 'replay_undo_redo_exact': True,
                       'outside_union_masks_unchanged': True, 'metadata_and_registration_unchanged': True,
                       'frames': per_frame, 'journal_sha256': sha(folder / 'journal.json')})
        write(folder / 'verification.json', result)
        summaries[name] = result
    require(all(sha(source / name) == pin for name, pin in initial_hashes.items()), 'Immutable source changed during run')
    write(out / 'RESULTS.json', {'schema': 'literal-pixel-candidates-results/v1', 'source_unchanged': True,
                                'source_hashes': initial_hashes, 'constructor_pixels_exact': True,
                                'plan_sha256': sha(plan_path), 'candidates': summaries,
                                'limits': 'No generation, hidden anatomy recovery, art score, human timed-motion acceptance or engine-playback claim.'})
    print(json.dumps({'output': str(out), 'candidates': list(summaries), 'source_unchanged': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Frozen delivery with project.json and frames/0000.png etc.')
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-editor', help='Optional existing LibreSprite executable; no install/account flow')
    run(parser.parse_args())
