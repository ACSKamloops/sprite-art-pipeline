#!/usr/bin/env python3
"""Compose explicitly owned source tails and literal midpoint texel maps."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import History, candidate_transaction, canonical_json, load_project, project_hash, render_cel, render_frame


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


recipe = module('tail_export_recipe', Path(__file__).with_name('author-pixel-candidates.py'))
clocks = module('tail_component_clocks', REPO / 'skills/sprite-animation-pipeline/scripts/union_component_clocks.py')
sha, write, require = recipe.sha, recipe.write, recipe.require


def rgba_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def run(args):
    path, plan_path, out = args.project.resolve(), args.plan.resolve(), args.output.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    plan = json.loads(plan_path.read_text())
    require(plan['schema'] == 'owned-tail-midpoints/v1' and sha(path) == plan['source_project_file_sha256'], 'Stale or invalid tail plan')
    source = load_project(path.read_text())
    require(len(source['animations']) == 1, 'One animation required')
    anim = source['animations'][0]
    require(anim['fps'] == 8 and anim['loop'] and not anim['events'] and len(anim['frames']) == 8, 'Bounded experiment requires8 equal one-tick looping keys at8Hz without events')
    byid = {f['id']: f for f in source['frames']}
    require(all(byid[fid]['duration_ticks'] == 1 for fid in anim['frames']), 'One-tick original keys required')
    width, height = source['canvas']['width'], source['canvas']['height']
    require(len(plan['keys']) == 8, 'Eight ownership keys required')
    out.mkdir(parents=True)
    frozen, construction = out / 'source', out / 'construction'
    frozen.mkdir()
    construction.mkdir()
    shutil.copy2(path, frozen / 'project.json')
    shutil.copy2(plan_path, out / 'plan.json')
    images, tails, bodies, masks, layer_files = [], [], [], [], []
    tail_layer = plan['tail_source_layer']
    original_ids = {layer['id'] for layer in source['layers']}
    require(tail_layer in original_ids and 'tail-back' not in original_ids, 'Invalid tail layer')
    for i, fid in enumerate(anim['frames']):
        frame = byid[fid]
        image = render_frame(source, fid)
        image.save(frozen / f'{i:02d}.png')
        require(rgba_hash(image) == plan['keys'][i]['rgba_sha256'], 'Stale rendered source pin')
        mask = set(map(tuple, plan['keys'][i]['owner_mask']))
        require(len(mask) == len(plan['keys'][i]['owner_mask']) and all(type(x) is int and type(y) is int and 0 <= x < width and 0 <= y < height for x, y in mask), 'Invalid ownership coordinates')
        tail = Image.new('RGBA', (width, height))
        files = {}
        protected = Image.new('RGBA', (width, height))
        for layer in source['layers']:
            art = render_cel(source, frame['cels'][layer['id']]) if layer['id'] in frame['cels'] else Image.new('RGBA', (width, height))
            if layer['id'] == tail_layer:
                for point in mask:
                    require(art.getpixel(point)[3] == 255 and image.getpixel(point) == art.getpixel(point), 'Tail owner is not visible opaque source-layer paint')
                    tail.putpixel(point, art.getpixel(point))
                    art.putpixel(point, (0, 0, 0, 0))
            name = f'key-{i:02d}-{layer["id"]}.png'
            art.save(construction / name)
            files[layer['id']] = name
            protected.alpha_composite(art)
        (Image.alpha_composite(tail, protected)).save(construction / f'reassembled-{i:02d}.png')
        require(Image.alpha_composite(tail, protected).tobytes() == image.tobytes(), 'Tail split/reassembly changed source pixels')
        for half in range(2):
            tail.save(construction / f'tail-{2*i+half:02d}.png')
        images.append(image)
        tails.append(tail)
        bodies.append(protected)
        masks.append(mask)
        layer_files.append(files)
    layers = [{'id': 'tail-back', 'name': 'Independent rear scarf-tail track', 'locked': False}]
    layers += [dict(layer, locked=True) for layer in source['layers']]
    frames = []
    for state in range(16):
        key = state // 2
        bindings = {'tail-back': {'image': f'tail-{state:02d}.png', 'at': [0, 0]}}
        bindings.update({lid: {'image': name, 'at': [0, 0]} for lid, name in layer_files[key].items()})
        frames.append({'id': f'state-{state:02d}', 'duration_ticks': 1,
                       'landmarks': byid[anim['frames'][key]]['landmarks'], 'cels': bindings})
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': source['canvas'], 'layers': layers,
            'frames': frames, 'animations': [{'id': anim['id'], 'frames': [f['id'] for f in frames], 'fps': 16, 'loop': True, 'events': []}],
            'provenance': {'source_project_file_sha256': sha(path), 'plan_sha256': sha(plan_path),
                           'operation': 'Visible scarf-tail ownership plus explicit new midpoint cloth states. Original body/head/bib remain8Hz; independent cloth16Hz. No hidden reconstruction.'}}
    write(construction / 'spec.json', spec)
    initial = recipe.constructor.construct(construction / 'spec.json')
    (construction / 'project.json').write_text(canonical_json(initial) + '\n')
    require(all(render_frame(initial, f'state-{i:02d}').tobytes() == images[i//2].tobytes() for i in range(16)), 'Duplicate-exposure control differs from original')
    history = History(initial)
    journal_dir = out / 'journal'
    journal_dir.mkdir()
    new_tails = [tails[i//2].copy() for i in range(16)]
    source_tail_hashes = {rgba_hash(tail) for tail in tails}
    authored_tail_hashes = set()
    edits = {entry['state']: entry for entry in plan['midpoints']}
    require(len(edits) == len(plan['midpoints']) and all(type(n) is int and 0 <= n < 16 and n % 2 for n in edits), 'Only unique odd half-states may change')
    for state, entry in sorted(edits.items()):
        art = Image.new('RGBA', (width, height))
        actual_mask, witnesses = set(), []
        for x, y, donor, sx, sy in entry['source_texel_map']:
            require(all(type(n) is int for n in [x, y, donor, sx, sy]) and 0 <= donor < 8 and 0 <= x < width and 0 <= y < height, 'Invalid midpoint witness')
            require((sx, sy) in masks[donor] and (x, y) not in actual_mask, 'Witness is not uniquely owned source-tail paint')
            color = images[donor].getpixel((sx, sy))
            art.putpixel((x, y), color)
            actual_mask.add((x, y))
            witnesses.append([x, y, donor, sx, sy, list(color)])
        if plan.get('require_new_tail_rasters', False):
            art_hash = rgba_hash(art)
            require(art_hash not in source_tail_hashes | authored_tail_hashes, 'Authored midpoint duplicates an original or another authored tail raster')
            authored_tail_hashes.add(art_hash)
        cel = initial['frames'][state]['cels']['tail-back']
        union = masks[state//2] | actual_mask
        tx = candidate_transaction(history.project, cel, art, [list(p) for p in sorted(union)])
        tx['reason'] = entry['reason']
        receipt = history.apply(tx)
        write(journal_dir / f'{state:02d}-receipt.json', receipt)
        write(journal_dir / f'{state:02d}-masks-witnesses.json', {'source_texel_map': witnesses,
              'allowed_mask': [list(p) for p in sorted(union)], 'tail_target_mask': [list(p) for p in sorted(actual_mask)],
              'body_key': state//2, 'attachment': entry['attachment'],
              'tail_pixels_occluded_by_original_body': [list(p) for p in sorted(actual_mask) if bodies[state//2].getpixel(p)[3]]})
        new_tails[state] = art
    final = history.project
    for frame in initial['frames']:
        for layer in source['layers']:
            cid = frame['cels'][layer['id']]
            require(initial['cels'][cid] == final['cels'][cid], 'Protected original layer changed')
    checks = []
    for state in range(16):
        image = render_frame(final, f'state-{state:02d}')
        key = state//2
        require(all(after == original for p, after, original in zip(bodies[key].get_flattened_data(), image.get_flattened_data(), images[key].get_flattened_data()) if p[3]), 'Original visible non-tail body pixel changed')
        coords = set(map(tuple, recipe.changed(images[key], image)))
        target = {(i % width, i // width) for i, p in enumerate(new_tails[state].get_flattened_data()) if p[3]}
        visible_tail = {p for p in target if not bodies[key].getpixel(p)[3]}
        require(coords <= masks[key] | target, 'Change outside tail union')
        if state % 2 == 0:
            require(not coords, 'Original even-key pixels changed')
        checks.append({'state': state, 'body_key': key, 'changed_visible_pixels': len(coords),
                       'tail_pixels': len(target), 'visible_new_state': bool(coords), 'tail_rgba_sha256': rgba_hash(new_tails[state])})
        checks[-1].update({'authored_midpoint': state in edits, 'visible_tail_pixels': len(visible_tail),
                           'occluded_tail_pixels': len(target - visible_tail),
                           'visible_tail_bounds': [min(p[0] for p in visible_tail), min(p[1] for p in visible_tail),
                                                   max(p[0] for p in visible_tail) + 1, max(p[1] for p in visible_tail) + 1] if visible_tail else None})
    journal = history.journal()
    write(journal_dir / 'journal.json', journal)
    require(project_hash(History.replay(initial, journal).project) == project_hash(final), 'Tail replay mismatch')
    after_hash = project_hash(final)
    while history.cursor:
        history.undo()
    require(project_hash(history.project) == project_hash(initial), 'Tail undo mismatch')
    while history.cursor < len(history.records):
        history.redo()
    require(project_hash(history.project) == after_hash, 'Tail redo mismatch')
    tracks = out / 'component-tracks'
    tracks.mkdir()
    for name, arts, den in [('body', bodies, 8), ('tail', new_tails, 16)]:
        records = []
        for i, art in enumerate(arts):
            filename = f'{name}-{i:02d}.png'
            art.save(tracks / filename)
            records.append({'file': filename, 'sha256': sha(tracks / filename), 'hold': [1, den]})
        write(tracks / f'{name}.json', {'loop': True, 'duration': [1, 1], 'frames': records})
    schedule = clocks.schedule([('body', tracks/'body.json'), ('tail', tracks/'tail.json')])
    require(schedule['clock_hz'] == 16 and schedule['cycle_ticks'] == 16 and len(schedule['states']) == 16, 'Unexpected component union')
    require(all(row['components'] == {'body': i//2, 'tail': i} for i, row in enumerate(schedule['states'])), 'Union source phases differ')
    write(out / 'component-union.json', schedule)
    outputs = {name: recipe.package(project, out / name, anim['id'], args.native_editor)
               for name, project in [('original-control', source), ('duplicate-control', initial), ('scarf-candidate', final)]}
    require(sha(path) == plan['source_project_file_sha256'], 'Original project changed')
    result = {'schema': 'owned-tail-midpoint-results/v1', 'source_project_file_sha256': sha(path),
              'source_unchanged': True, 'decomposition_exact': True, 'even8keys_exact': True,
              'all_visible_non_tail_source_pixels_exact': True, 'outside_tail_union_unchanged': True,
              'journal_replay_undo_redo_exact': True, 'body_rate_hz': 8, 'tail_rate_hz': 16,
              'duration': [1, 1], 'actual_new_visible_midpoint_count': sum(c['visible_new_state'] for c in checks),
              'distinct_tail_rasters': len(set(c['tail_rgba_sha256'] for c in checks)),
              'underpaint': 'None authored or inferred. Removed source tail owns visible cloth only; exposed pixels become background or are covered by explicitly authored new cloth.',
              'frames': checks, 'outputs': outputs,
              'limits': 'Clock and literal pixel checks do not establish smoother motion, art score or timed human acceptance. All16 adjacency/wrap pairs require visual review.'}
    write(out / 'RESULTS.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-editor')
    run(parser.parse_args())
