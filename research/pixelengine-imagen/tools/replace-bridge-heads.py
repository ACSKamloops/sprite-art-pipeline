#!/usr/bin/env python3
"""Insert two painted bridges and test source-owned head replacement only."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from fractions import Fraction

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


recipe = module('bridge_head_exports', Path(__file__).with_name('author-pixel-candidates.py'))
sha, write, require = recipe.sha, recipe.write, recipe.require


def run(args):
    project_path, plan_path, bridges = args.project.resolve(), args.plan.resolve(), args.bridges.resolve()
    out = args.output.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    plan = json.loads(plan_path.read_text())
    require(plan['schema'] == 'painted-bridge-head-test/v1' and sha(project_path) == plan['source_project_file_sha256'], 'Invalid/stale source plan')
    source = load_project(project_path.read_text())
    anim = source['animations'][0]
    require(len(source['animations']) == 1 and anim['fps'] == 8 and len(anim['frames']) == 8 and anim['loop'] and not anim['events'], 'Bounded test requires one8-key8Hz loop without events')
    require({x['id'] for x in source['layers']} == {'body', 'join-underpaint', 'owner'}, 'Expected body, join-underpaint and owned head source layers')
    byid = {f['id']: f for f in source['frames']}
    require(all(byid[fid]['duration_ticks'] == 1 for fid in anim['frames']), 'Source keys require one tick each')
    require([b['after_key'] for b in plan['bridges']] == [2, 3], 'Only the authorized2.5 and3.5 bridges are supported')
    width, height = source['canvas']['width'], source['canvas']['height']
    out.mkdir(parents=True)
    frozen, construction = out / 'source', out / 'construction'
    frozen.mkdir()
    construction.mkdir()
    shutil.copy2(project_path, frozen / 'project.json')
    shutil.copy2(plan_path, out / 'plan.json')
    frame_specs = []
    bridge_info = {}
    for i, fid in enumerate(anim['frames']):
        image = render_frame(source, fid)
        image.save(frozen / f'key-{i:02d}.png')
        bindings = {}
        for layer in source['layers']:
            cid = byid[fid]['cels'].get(layer['id'])
            art = render_cel(source, cid) if cid else Image.new('RGBA', (width, height))
            filename = f'key-{i:02d}-{layer["id"]}.png'
            art.save(construction / filename)
            bindings[layer['id']] = {'image': filename, 'at': [0, 0]}
        frame_specs.append({'id': fid, 'duration_ticks': 1 if i in [2, 3] else 2, 'cels': bindings, 'landmarks': byid[fid]['landmarks']})
        if i not in [2, 3]:
            continue
        entry = plan['bridges'][i-2]
        filename = entry['file']
        require(Path(filename).name == filename and sha(bridges / filename) == entry['file_sha256'], 'Stale/unsafe bridge pin')
        shutil.copy2(bridges / filename, frozen / filename)
        art = Image.open(bridges / filename).convert('RGBA')
        require(art.size == (width, height), 'Bridge stage differs; registration is not allowed')
        mask = set(map(tuple, entry['owner_mask']))
        require(len(mask) == len(entry['owner_mask']) and all(type(x) is int and type(y) is int and 0 <= x < width and 0 <= y < height and art.getpixel((x, y))[3] == 255 for x, y in mask), 'Invalid visible bridge head owner')
        body, head = art.copy(), Image.new('RGBA', art.size)
        for point in mask:
            head.putpixel(point, art.getpixel(point))
            body.putpixel(point, (0, 0, 0, 0))
        bid = entry['frame_id']
        bindings = {}
        for lid, part in [('body', body), ('join-underpaint', Image.new('RGBA', art.size)), ('owner', head)]:
            name = f'{bid}-{lid}.png'
            part.save(construction / name)
            bindings[lid] = {'image': name, 'at': [0, 0]}
        require(Image.alpha_composite(body, head).tobytes() == art.tobytes(), 'Bridge decomposition differs')
        frame_specs.append({'id': bid, 'duration_ticks': 1, 'cels': bindings, 'landmarks': {}})
        bridge_info[bid] = {'plan': entry, 'image': art, 'body': body, 'mask': mask}
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': source['canvas'],
            'layers': [dict(layer, locked=layer['id'] == 'body') for layer in source['layers']],
            'frames': frame_specs,
            'animations': [dict(anim, fps=16, frames=[f['id'] for f in frame_specs])],
            'provenance': {'operation': 'Two retained ImageGen body bridges with explicit source-owned crisp head replacement; no new generation or automatic registration',
                           'original_project_file_sha256': sha(project_path), 'plan_sha256': sha(plan_path)}}
    write(construction / 'spec.json', spec)
    initial = recipe.constructor.construct(construction / 'spec.json')
    (construction / 'project.json').write_text(canonical_json(initial) + '\n')
    initial_byid = {f['id']: f for f in initial['frames']}
    donor_frame = byid[plan['donor_frame_id']]
    donor = render_cel(source, donor_frame['cels']['owner'])
    donor_mask = {(i % width, i // width) for i, p in enumerate(donor.get_flattened_data()) if p[3]}
    journal_dir = out / 'journal'
    journal_dir.mkdir()
    history = History(initial)
    checks = []
    for bid, info in bridge_info.items():
        entry = info['plan']
        require(render_frame(initial, bid).tobytes() == info['image'].tobytes(), 'Before bridge pixels differ')
        dx = entry['anchor'][0] - plan['donor_anchor'][0]
        dy = entry['anchor'][1] - plan['donor_anchor'][1]
        head = Image.new('RGBA', (width, height))
        target, source_map = set(), []
        for sx, sy in sorted(donor_mask):
            x, y = sx + dx, sy + dy
            require(0 <= x < width and 0 <= y < height, 'Head clipping forbidden')
            head.putpixel((x, y), donor.getpixel((sx, sy)))
            target.add((x, y))
            source_map.append([x, y, sx, sy, list(donor.getpixel((sx, sy)))])
        allowed = info['mask'] | target
        cid = initial_byid[bid]['cels']['owner']
        tx = candidate_transaction(history.project, cid, head, [list(p) for p in sorted(allowed)])
        tx['reason'] = entry['reason']
        write(journal_dir / f'{bid}-head-receipt.json', history.apply(tx))
        underpaint = Image.new('RGBA', (width, height))
        under_mask = set()
        for paint in entry.get('underpaint', []):
            point, witness = tuple(paint['at']), tuple(paint['source_bridge_pixel'])
            require(point in info['mask'] - target, 'Underpaint must be a newly exposed owned head pixel')
            underpaint.putpixel(point, info['image'].getpixel(witness))
            under_mask.add(point)
        if under_mask:
            cid = initial_byid[bid]['cels']['join-underpaint']
            tx = candidate_transaction(history.project, cid, underpaint, [list(p) for p in sorted(under_mask)])
            tx['reason'] = 'Explicit newly authored neck-join pixel with recorded neighboring bridge scarf-color witness'
            write(journal_dir / f'{bid}-underpaint-receipt.json', history.apply(tx))
        actual = render_frame(history.project, bid)
        changes = set(map(tuple, recipe.changed(info['image'], actual)))
        require(changes <= allowed | under_mask, 'Outside head/join change')
        require(render_cel(history.project, initial_byid[bid]['cels']['owner']).tobytes() == head.tobytes(), 'Source-owned head paint differs')
        overlaps = [list(p) for p in sorted(target) if info['body'].getpixel(p)[3]]
        evidence = {'frame_id': bid, 'old_owner_mask': [list(p) for p in sorted(info['mask'])],
                    'target_owner_mask': [list(p) for p in sorted(target)], 'allowed_union_mask': [list(p) for p in sorted(allowed)],
                    'source_head_frame_id': plan['donor_frame_id'], 'source_map': source_map, 'anchor': entry['anchor'], 'translation': [dx, dy],
                    'underpaint': entry.get('underpaint', []), 'new_head_occludes_bridge_collar_pixels': overlaps,
                    'former_owner_now_exposes_background': [list(p) for p in sorted(info['mask'] - target - under_mask)]}
        write(journal_dir / f'{bid}-masks-source-map.json', evidence)
        checks.append({'frame_id': bid, 'head_pixels': len(target), 'changed_pixels': len(changes), 'covered_bridge_collar_pixels': len(overlaps), 'new_underpaint_pixels': len(under_mask)})
    final = history.project
    ticks, onset_checks = 0, []
    for frame in final['frames']:
        fid = frame['id']
        if fid in byid:
            index = anim['frames'].index(fid)
            require(Fraction(ticks, 16) == Fraction(index, 8), 'Original key onset moved')
            require(render_frame(final, fid).tobytes() == render_frame(source, fid).tobytes(), 'Original key pixels changed')
            onset_checks.append({'frame_id': fid, 'onset': [Fraction(ticks,16).numerator, Fraction(ticks,16).denominator], 'pixels_exact': True})
        ticks += frame['duration_ticks']
        cid = frame['cels']['body']
        require(initial['cels'][cid] == final['cels'][cid], 'Bridge or original body cel changed')
    require(ticks == 16, 'Cycle period changed')
    journal = history.journal()
    write(journal_dir / 'journal.json', journal)
    require(project_hash(History.replay(initial, journal).project) == project_hash(final), 'Journal replay differs')
    final_hash = project_hash(final)
    while history.cursor:
        history.undo()
    require(project_hash(history.project) == project_hash(initial), 'Undo differs')
    while history.cursor < len(history.records):
        history.redo()
    require(project_hash(history.project) == final_hash, 'Redo differs')
    outputs = {name: recipe.package(project, out / name, anim['id'], args.native_editor)
               for name, project in [('original-control', source), ('painted-before', initial), ('head-repaired', final)]}
    require(sha(project_path) == plan['source_project_file_sha256'] and all(sha(bridges/e['file']) == e['file_sha256'] for e in plan['bridges']), 'Source mutated')
    result = {'schema': 'painted-bridge-head-results/v1', 'source_unchanged': True, 'source8_keys_pixels_and_onsets_exact': True,
              'outside_head_join_masks_unchanged': True, 'all_body_cels_unchanged': True,
              'source_head_pixels_exact_at_declared_anchors': True, 'journal_replay_undo_redo_exact': True,
              'canvas': [width,height], 'duration': [1,1], 'sequence_frame_count': 10,
              'onset_checks': onset_checks, 'bridge_checks': checks, 'outputs': outputs,
              'limits': 'Authored head component repair of two retained full-body ImageGen drawings. Body/clothing drift, pose semantics and normal-speed motion require separate review; no generation or art score.'}
    write(out / 'RESULTS.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--bridges', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-editor')
    run(parser.parse_args())
