#!/usr/bin/env python3
"""Union authored body/head/leg poses with a separately owned rear cloth track.

This composes saved paint and exact clocks. It infers no anatomy or motion.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from fractions import Fraction

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
from sprite_lab import canonical_json, load_project, render_cel, render_frame


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def ordered_project(path, manifest_path):
    project = load_project(path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if len(project['animations']) != 1:
        raise ValueError('One animation required')
    animation = project['animations'][0]
    if not animation['loop'] or animation['events'] or manifest['duration'] != [1, 1]:
        raise ValueError('One-second looping event-free tracks required')
    by_id = {f['id']: f for f in project['frames']}
    frames = [by_id[fid] for fid in animation['frames']]
    if len(frames) != len(manifest['frames']):
        raise ValueError('Project/manifest count mismatch')
    for frame, exported in zip(frames, manifest['frames']):
        image = Image.open(manifest_path.parent / exported['file']).convert('RGBA')
        if sha(manifest_path.parent / exported['file']) != exported['sha256']:
            raise ValueError('Manifest image hash mismatch')
        if render_frame(project, frame['id']).tobytes() != image.tobytes():
            raise ValueError('Manifest/project pixels differ')
        if Fraction(frame['duration_ticks'], animation['fps']) != Fraction(*exported['hold']):
            raise ValueError('Manifest/project holds differ')
    return project, frames


def run(args):
    out = args.output.absolute()
    if out.exists():
        raise ValueError('Fresh output required')
    paths = [args.base_project, args.base_manifest, args.tail_project, args.tail_manifest,
             args.tail_plan, args.original_project]
    pins = {str(p.resolve()): sha(p) for p in paths}
    base, base_frames = ordered_project(args.base_project, args.base_manifest)
    cloth, cloth_frames = ordered_project(args.tail_project, args.tail_manifest)
    original = load_project(args.original_project.read_text())
    plan = json.loads(args.tail_plan.read_text())
    if sha(args.original_project) != plan['source_project_file_sha256']:
        raise ValueError('Tail ownership belongs to a different original')
    if base['canvas'] != cloth['canvas'] or base['canvas'] != original['canvas']:
        raise ValueError('Canvas mismatch')
    if base['canvas']['width'] != 80 or base['canvas']['height'] != 80:
        raise ValueError('This frozen recipe is bounded to the native80px comparison')
    if 'tail-back' not in {l['id'] for l in cloth['layers']} or 'tail-back' in {l['id'] for l in base['layers']}:
        raise ValueError('Missing or colliding tail ownership layer')
    clocks = module('owned_union', REPO / 'skills/sprite-animation-pipeline/scripts/union_component_clocks.py')
    clock = clocks.schedule([('base', args.base_manifest), ('cloth', args.tail_manifest)])
    if clock['clock_hz'] != 16 or clock['cycle_ticks'] != 16 or len(cloth_frames) != 16:
        raise ValueError('Expected authored16Hz cloth union')
    original_order = original['animations'][0]['frames']
    if len(original_order) != 8 or original['animations'][0]['fps'] != 8:
        raise ValueError('Expected frozen8key original')
    out.mkdir(parents=True)
    construction = out / 'construction'
    construction.mkdir()
    frames, checks = [], []
    for i, state in enumerate(clock['states']):
        key = state['start_tick'] // 2
        bf = base_frames[state['components']['base']]
        cf = cloth_frames[state['components']['cloth']]
        original_image = render_frame(original, original_order[key])
        base_image = render_frame(base, bf['id'])
        mask = [tuple(p) for p in plan['keys'][key]['owner_mask']]
        tail = render_cel(cloth, cf['cels']['tail-back'])
        body = Image.new('RGBA', (80, 80))
        bindings = {}
        for layer in base['layers']:
            lid = layer['id']
            art = render_cel(base, bf['cels'][lid]) if lid in bf['cels'] else Image.new('RGBA', (80, 80))
            for point in mask:
                if base_image.getpixel(point) != original_image.getpixel(point):
                    raise ValueError('Base changed a source-tail owner pixel')
                art.putpixel(point, (0, 0, 0, 0))
            name = f'{i:02d}-{lid}.png'
            art.save(construction / name)
            bindings[lid] = {'image': name, 'at': [0, 0]}
            body.alpha_composite(art)
        tail_name = f'{i:02d}-tail-back.png'
        tail.save(construction / tail_name)
        bindings['tail-back'] = {'image': tail_name, 'at': [0, 0]}
        result = Image.alpha_composite(tail, body)
        # Removing/reassembling only old visible owners must reproduce the
        # base exactly; new cloth may change only the source/new-tail union.
        old_tail = Image.new('RGBA', (80, 80))
        for point in mask:
            old_tail.putpixel(point, original_image.getpixel(point))
        if Image.alpha_composite(old_tail, body).tobytes() != base_image.tobytes():
            raise ValueError('Tail removal damaged base paint or composition')
        tail_pixels = {(x, y) for y in range(80) for x in range(80) if tail.getpixel((x, y))[3]}
        changed = {(x, y) for y in range(80) for x in range(80)
                   if result.getpixel((x, y)) != base_image.getpixel((x, y))}
        if not changed <= set(mask) | tail_pixels:
            raise ValueError('Composition changed unrelated base pixels')
        even_exact = None
        if state['start_tick'] % 2 == 0:
            even_exact = result.tobytes() == original_image.tobytes()
            if not even_exact:
                raise ValueError('Original even source key changed')
        frame_id = f'state-{i:02d}'
        result.save(construction / f'{i:02d}-expected.png')
        frames.append({'id': frame_id, 'duration_ticks': state['duration_ticks'],
                       'landmarks': bf['landmarks'], 'cels': bindings})
        checks.append({'state': i, 'start_tick': state['start_tick'],
                       'source_key': key, 'base_frame': bf['id'], 'cloth_frame': cf['id'],
                       'tail_union_changed_pixels': len(changed), 'original_key_exact': even_exact,
                       'removed_owner_mask': [list(p) for p in mask]})
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': base['canvas'],
            'layers': [{'id': 'tail-back', 'name': 'Authored independent rear scarf tail', 'locked': False}] + base['layers'],
            'frames': frames, 'animations': [{'id': 'walk', 'fps': 16, 'frames': [f['id'] for f in frames], 'loop': True, 'events': []}],
            'provenance': {'operation': 'Exact owner removal/reassembly and union of saved authored tracks', 'input_sha256': pins}}
    write(construction / 'spec.json', spec)
    constructor = module('owned_constructor', TOOLKIT / 'scripts/sprite_construct.py')
    project = constructor.construct(construction / 'spec.json')
    (out / 'project.json').write_text(canonical_json(project) + '\n')
    for i, frame in enumerate(frames):
        if render_frame(project, frame['id']).tobytes() != Image.open(construction / f'{i:02d}-expected.png').convert('RGBA').tobytes():
            raise ValueError('Layered output differs from witnessed composition')
    exporter = module('owned_exporter', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
    exporter.export(out / 'project.json', out / 'delivery', 'walk', TOOLKIT, 8, 'hero')
    apng = module('owned_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')
    apng.convert(out / 'delivery/manifest.json', out / 'delivery/apng')
    if any(sha(p) != value for p, value in pins.items()):
        raise ValueError('Source mutation detected')
    write(out / 'CLOCK.json', clock)
    write(out / 'RESULTS.json', {'input_sha256': pins, 'recipe_sha256': sha(__file__),
          'all8_original_keys_exact': True, 'all_non_tail_base_pixels_exact': True,
          'layered_reassembly_exact': True, 'frames': checks,
          'approval': 'Unreviewed component composition. More exposures imply no quality improvement.'})
    print(json.dumps({'output': str(out), 'states': len(frames), 'original_keys_exact': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['base-project', 'base-manifest', 'tail-project', 'tail-manifest', 'tail-plan', 'original-project', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    run(parser.parse_args())
