#!/usr/bin/env python3
"""Test a literal source-owned component track without fitting whole poses."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import History, candidate_transaction, canonical_json, load_project, project_hash, render_frame


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


recipe = module('owned_component_export', Path(__file__).with_name('author-pixel-candidates.py'))
constructor = recipe.constructor
sha, write, require = recipe.sha, recipe.write, recipe.require


def coordinates(mask, width, height):
    require(isinstance(mask, list) and all(isinstance(p, list) and len(p) == 2 and
            all(type(v) is int for v in p) and 0 <= p[0] < width and 0 <= p[1] < height for p in mask), 'Invalid explicit ownership mask')
    result = set(map(tuple, mask))
    require(len(result) == len(mask), 'Duplicate ownership coordinate')
    return result


def run(args):
    plan_path, source, out = args.plan.resolve(), args.source.resolve(), args.output.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh output required')
    plan = json.loads(plan_path.read_text())
    require(plan['schema'] == 'owned-source-component-track/v1', 'Unknown plan')
    require(sha(source / 'project.json') == plan['source_project_file_sha256'], 'Stale project pin')
    original = load_project((source / 'project.json').read_text())
    anim = next(a for a in original['animations'] if a['id'] == plan['animation'])
    byid = {f['id']: f for f in original['frames']}
    width, height = original['canvas']['width'], original['canvas']['height']
    require(len(plan['frames']) == len(anim['frames']), 'Ownership frame count mismatch')
    out.mkdir(parents=True)
    frozen, decomposed = out / 'source', out / 'decomposition'
    frozen.mkdir()
    decomposed.mkdir()
    shutil.copy2(source / 'project.json', frozen / 'project.json')
    shutil.copy2(plan_path, out / 'plan.json')
    source_pins = {'project.json': sha(source / 'project.json')}
    images, masks, frame_specs = [], [], []
    for i, (fid, record) in enumerate(zip(anim['frames'], plan['frames'])):
        require(record['frame_id'] == fid, 'Ownership order mismatch')
        filename = f'frames/{i:04d}.png'
        require(sha(source / filename) == record['png_sha256'], 'Stale PNG pin')
        source_pins[filename] = sha(source / filename)
        (frozen / 'frames').mkdir(exist_ok=True)
        shutil.copy2(source / filename, frozen / filename)
        image = Image.open(source / filename).convert('RGBA')
        require(image.size == (width, height) and render_frame(original, fid).tobytes() == image.tobytes(), 'Source project/PNG mismatch')
        mask = coordinates(record['owner_mask'], width, height)
        require(all(image.getpixel(p)[3] for p in mask), 'Owner includes empty source pixels')
        body, owner = image.copy(), Image.new('RGBA', image.size)
        for point in mask:
            owner.putpixel(point, image.getpixel(point))
            body.putpixel(point, (0, 0, 0, 0))
        blank = Image.new('RGBA', image.size)
        cels = {}
        for layer, art in [('body', body), ('join-underpaint', blank), ('owner', owner)]:
            name = f'{i:02d}-{layer}.png'
            art.save(decomposed / name)
            cels[layer] = {'image': name, 'at': [0, 0]}
        frame_specs.append({'id': fid, 'duration_ticks': byid[fid]['duration_ticks'],
                            'landmarks': byid[fid]['landmarks'], 'cels': cels})
        images.append(image)
        masks.append(mask)
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': original['canvas'],
            'layers': [{'id': 'body', 'name': 'Protected original body and cloth', 'locked': True},
                       {'id': 'join-underpaint', 'name': 'Explicit authored join underpaint', 'locked': False},
                       {'id': 'owner', 'name': plan['component'] + ': explicit source ownership', 'locked': False}],
            'frames': frame_specs, 'animations': [anim],
            'provenance': {'operation': 'Exact component ownership decomposition, then authored rigid attachment track; no hidden geometry recovery',
                           'original_project_file_sha256': source_pins['project.json'], 'plan_sha256': sha(plan_path)}}
    write(decomposed / 'spec.json', spec)
    initial = constructor.construct(decomposed / 'spec.json')
    (decomposed / 'project.json').write_text(canonical_json(initial) + '\n')
    require(all(render_frame(initial, fid).tobytes() == images[i].tobytes() for i, fid in enumerate(anim['frames'])), 'Ownership decomposition changed visible source')
    history = History(initial)
    initial_byid = {f['id']: f for f in initial['frames']}
    master_index = plan['master_frame_index']
    master, master_mask = images[master_index], masks[master_index]
    source_anchor = plan['master_anchor']
    master_source_id = 'original-source'
    donor_project, donor_pins = None, {}
    if args.donor:
        donor = args.donor.resolve()
        donor_plan = plan['external_donor']
        require(sha(donor / 'project.json') == donor_plan['project_file_sha256'], 'Stale donor project pin')
        donor_project = load_project((donor / 'project.json').read_text())
        require(donor_project['canvas'] == original['canvas'] and donor_project['animations'] == original['animations'], 'Donor stage/clock differs')
        donor_pins['project.json'] = sha(donor / 'project.json')
        donor_frozen = out / 'donor-source'
        donor_frozen.mkdir()
        shutil.copy2(donor / 'project.json', donor_frozen / 'project.json')
        (donor_frozen / 'frames').mkdir()
        for i, fid in enumerate(anim['frames']):
            name = f'frames/{i:04d}.png'
            donor_pins[name] = sha(donor / name)
            require(donor_pins[name] == donor_plan['frames_sha256'][i], 'Stale donor PNG pin')
            require(render_frame(donor_project, fid).tobytes() == Image.open(donor / name).convert('RGBA').tobytes(), 'Donor PNG/project mismatch')
            shutil.copy2(donor / name, donor_frozen / name)
        master_index = donor_plan['frame_index']
        master = Image.open(donor / f'frames/{master_index:04d}.png').convert('RGBA')
        master_mask = coordinates(donor_plan['owner_mask'], width, height)
        require(all(master.getpixel(p)[3] for p in master_mask), 'Donor owner includes empty pixels')
        source_anchor = donor_plan['anchor']
        master_source_id = 'external-donor'
    checks = []
    journal_dir = out / 'journal'
    journal_dir.mkdir()
    for i, record in enumerate(plan['frames']):
        anchor = record['attachment_anchor']
        require(len(anchor) == len(source_anchor) == 2 and all(type(v) is int for v in anchor + source_anchor), 'Integer component anchors required')
        dx, dy = anchor[0] - source_anchor[0], anchor[1] - source_anchor[1]
        art = Image.new('RGBA', (width, height))
        mapping = []
        for sx, sy in sorted(master_mask, key=lambda p: (p[1], p[0])):
            tx, ty = sx + dx, sy + dy
            require(0 <= tx < width and 0 <= ty < height, 'Component clipping forbidden')
            art.putpixel((tx, ty), master.getpixel((sx, sy)))
            mapping.append([tx, ty, master_index, sx, sy])
        target_mask = {(r[0], r[1]) for r in mapping}
        union = masks[i] | target_mask
        fid = record['frame_id']
        cel = initial_byid[fid]['cels']['owner']
        tx = candidate_transaction(history.project, cel, art, [list(p) for p in sorted(union)])
        tx['reason'] = record['reason'] + '; erase old explicit owner and compose literal source component with declared translation only'
        receipt = history.apply(tx)
        write(journal_dir / f'{i:02d}-owner-receipt.json', receipt)
        additions = record.get('underpaint', [])
        patch = Image.new('RGBA', (width, height))
        underpaint_mask = set()
        for entry in additions:
            x, y = entry['at']
            si, sx, sy = entry['source_pixel']
            require((x, y) in masks[i] - target_mask, 'Underpaint must be a newly exposed owned pixel')
            patch.putpixel((x, y), images[si].getpixel((sx, sy)))
            underpaint_mask.add((x, y))
        if underpaint_mask:
            undercel = initial_byid[fid]['cels']['join-underpaint']
            tx = candidate_transaction(history.project, undercel, patch, [list(p) for p in sorted(underpaint_mask)])
            tx['reason'] = 'Explicit new join underpaint using recorded source-color witnesses; no inferred hidden surface'
            write(journal_dir / f'{i:02d}-underpaint-receipt.json', history.apply(tx))
        after = render_frame(history.project, fid)
        changes = set(map(tuple, recipe.changed(images[i], after)))
        require(changes <= union | underpaint_mask, 'Outside ownership/attachment region changed')
        body_image = Image.open(decomposed / f'{i:02d}-body.png').convert('RGBA')
        overlap = [list(p) for p in sorted(target_mask) if body_image.getpixel(p)[3]]
        gaps = [list(p) for p in sorted(masks[i] - target_mask - underpaint_mask)]
        witness = {'frame_id': fid, 'attachment_anchor': anchor, 'translation': [dx, dy],
                   'master_source_id': master_source_id, 'master_frame_index': master_index, 'source_texel_map': mapping,
                   'old_owner_mask': [list(p) for p in sorted(masks[i])],
                   'target_owner_mask': [list(p) for p in sorted(target_mask)],
                   'allowed_union_mask': [list(p) for p in sorted(union)],
                   'new_owner_occludes_original_body_pixels': overlap,
                   'old_owner_now_exposes_background': gaps, 'underpaint': additions}
        write(journal_dir / f'{i:02d}-ownership-and-source-map.json', witness)
        checks.append({'frame_id': fid, 'changed_pixels': len(changes), 'owner_pixels': len(target_mask),
                       'underpaint_pixels': len(underpaint_mask), 'occluded_original_body_pixels': len(overlap),
                       'exposed_background_pixels': len(gaps)})
    final = history.project
    for frame in initial['frames']:
        cid = frame['cels']['body']
        require(initial['cels'][cid] == final['cels'][cid], 'Protected body/cloth changed')
    require(final['frames'] == initial['frames'] and final['canvas'] == initial['canvas'] and final['animations'] == initial['animations'], 'Clock/registration changed')
    journal = history.journal()
    write(journal_dir / 'journal.json', journal)
    require(project_hash(History.replay(initial, journal).project) == project_hash(final), 'Component replay mismatch')
    final_hash = project_hash(final)
    while history.cursor:
        history.undo()
    require(project_hash(history.project) == project_hash(initial), 'Component undo mismatch')
    while history.cursor < len(history.records):
        history.redo()
    require(project_hash(history.project) == final_hash, 'Component redo mismatch')
    outputs = {name: recipe.package(project, out / name, anim['id'], args.native_editor)
               for name, project in [('control', initial), ('head-track', final)]}
    if donor_project:
        outputs['donor-control'] = recipe.package(donor_project, out / 'donor-control', anim['id'], args.native_editor)
        require(all(sha(args.donor / name) == pin for name, pin in donor_pins.items()), 'Donor source mutated')
    require(all(sha(source / name) == pin for name, pin in source_pins.items()), 'Source mutated')
    result = {'schema': 'owned-component-track-results/v1', 'source_pins': source_pins,
              'source_unchanged': True, 'donor_pins': donor_pins, 'decomposition_composite_exact': True,
              'body_and_cloth_layer_cels_unchanged': True, 'outside_union_masks_unchanged': True,
              'registration_and_clock_unchanged': True, 'replay_undo_redo_exact': True,
              'frames': checks, 'outputs': outputs,
              'limit': 'Authored component-rig experiment. Literal source pixels and declared attachment anchors do not establish hidden anatomy, good joins, art approval or motion parity.'}
    write(out / 'RESULTS.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-editor')
    parser.add_argument('--donor', type=Path, help='Optional explicitly pinned external source component; keeps full donor control')
    run(parser.parse_args())
