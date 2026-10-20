#!/usr/bin/env python3
"""Import actual isolated rig renders into the lossless pixel editor."""
import argparse
import hashlib
import json
import runpy
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sprite_lab import History, canonical_json, project_hash, render_frame


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path):
    return Image.open(path).convert('RGBA').tobytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('rig_directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rig = args.rig_directory.resolve()
    generated = rig / 'generated'
    isolated_file = generated / 'isolated/manifest.json'
    isolated = json.loads(isolated_file.read_text())
    if args.output.exists():
        raise ValueError('Use a fresh output directory; keep earlier projects/journals')
    required_sources = {'rig.gd', 'design.json', 'clips.json', 'bake.gd'}
    if set(isolated.get('source_bindings', {})) != required_sources:
        raise ValueError('Isolation manifest requires all four source bindings')
    full_manifest = json.loads((generated / 'manifest.json').read_text())
    if any(full_manifest['source_bindings'].get(name) != isolated['source_bindings'][name] for name in required_sources):
        raise ValueError('Isolation bindings do not match current complete export')
    for file, expected in isolated['source_bindings'].items():
        if sha((rig / file).read_bytes()) != expected:
            raise ValueError('Stale isolation source: ' + file)
    output = args.output.resolve()
    output.mkdir(parents=True)
    def contained(root, relative):
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or Path(relative).is_absolute():
            raise ValueError('Asset path escapes its project directory')
        return path
    # Validate every path before creating any asset files.
    for sample in isolated['poses']:
        for name in [sample['full_png'], *[row['png'] for row in sample['layers']]]:
            contained(generated, name)
            contained(output, name)
    layers = isolated['layer_order']
    frames = []
    checks = []
    for sample in isolated['poses']:
        bindings = {}
        actual = {x['id']: x for x in sample['layers']}
        for layer in layers:
            entry = actual[layer]
            source = generated / entry['png']
            if sha(rgba(source)) != entry['pixel_sha256']:
                raise ValueError('Changed isolated pixels: ' + entry['png'])
            destination = output / entry['png']
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            bindings[layer] = {'image': entry['png'], 'at': [0, 0]}
        full = generated / sample['full_png']
        if sha(rgba(full)) != sample['full_pixel_sha256']:
            raise ValueError('Changed complete pose')
        destination = output / sample['full_png']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(full, destination)
        frames.append({'id': sample['id'], 'duration_ticks': 1,
                       'landmarks': {'ground': [96, 170]}, 'cels': bindings})
    spec = {'schema': 'sprite-construction-spec/v1',
            'canvas': {'width': 192, 'height': 192, 'render_pivot': [96, 96], 'ground_pivot': [96, 170]},
            'layers': [{'id': x, 'name': x.replace('_', ' ').title(), 'locked': False} for x in layers],
            'frames': frames,
            'animations': [{'id': f['id'] + '-sample', 'frames': [f['id']], 'fps': 60, 'loop': False, 'events': []} for f in frames],
            'provenance': {'source_bindings': isolated['source_bindings'],
                           'isolation_manifest_sha256': sha(isolated_file.read_bytes()),
                           'scope': 'Five isolated poses for fine editing, not five complete animations.',
                           'quality_approved': False}}
    spec_file = output / 'construction.json'
    spec_file.write_text(json.dumps(spec, indent=2) + '\n')
    construct = runpy.run_path(str(ROOT / 'scripts/sprite_construct.py'))['construct']
    project = construct(spec_file)
    (output / 'project.json').write_text(canonical_json(project) + '\n')
    for sample in isolated['poses']:
        composed = render_frame(project, sample['id']).tobytes()
        full = rgba(output / sample['full_png'])
        checks.append({'id': sample['id'], 'scalar_composite_equals_full_gpu': composed == full,
                       'rgba_sha256': sha(composed)})
    if not all(x['scalar_composite_equals_full_gpu'] for x in checks):
        raise ValueError('Named isolated layers do not reconstruct full GPU poses')
    # A bounded material-detail candidate demonstrates exact, reversible edits.
    frame = project['frames'][0]
    layer = 'torso' if 'torso' in frame['cels'] else layers[len(layers) // 2]
    cel_id = frame['cels'][layer]
    pixels = project['cels'][cel_id]['pixels']
    layer_index = layers.index(layer)
    above = [project['cels'][frame['cels'][name]]['pixels']
             for name in layers[layer_index + 1:] if name in frame['cels']]
    selected = [i for i, v in enumerate(pixels) if v != 0
                and not any(project['palette'][c[i]][3] for c in above)][:2]
    if len(selected) != 2:
        raise ValueError('Demonstration layer has fewer than two visible pixels')
    target = next(i for i, color in enumerate(project['palette']) if i and color[3] == 255
                  and i not in {pixels[n] for n in selected})
    points = [[i % 192, i // 192, target] for i in selected]
    edit = {'schema': 'sprite-edit-transaction/v1', 'expected_project_sha256': project_hash(project),
            'reason': 'Two-pixel material detail candidate; demonstration only, requires artistic review',
            'operations': [{'op': 'paint', 'cel_id': cel_id, 'points': points, 'mask': [p[:2] for p in points]}]}
    history = History(project)
    receipt = history.apply(edit)
    changed = history.project
    altered = render_frame(changed, frame['id'])
    altered.save(output / 'fine-edit-candidate.png')
    original_pixels = render_frame(project, frame['id']).get_flattened_data()
    visible_changes = [i for i, (a, b) in enumerate(zip(original_pixels, altered.get_flattened_data())) if a != b]
    if set(visible_changes) != set(selected):
        raise ValueError('Correction did not change exactly the two intended visible composite pixels')
    changed_indices = [i for i, (a, b) in enumerate(zip(pixels, changed['cels'][cel_id]['pixels'])) if a != b]
    if not set(changed_indices) <= set(selected):
        raise ValueError('Fine edit escaped declared coordinates')
    journal = history.journal()
    if project_hash(History.replay(project, journal).project) != project_hash(changed):
        raise ValueError('Journal replay does not reproduce candidate')
    if project_hash(history.undo()) != project_hash(project):
        raise ValueError('Undo does not restore exact project')
    (output / 'fine-edit.json').write_text(json.dumps(edit, indent=2) + '\n')
    (output / 'fine-edit-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (output / 'fine-edit-journal.json').write_text(json.dumps(journal, indent=2) + '\n')
    (output / 'fine-edited-project.json').write_text(canonical_json(changed) + '\n')
    report = {'schema': 'rig-editable-sample-proof/v1', 'source_bindings': isolated['source_bindings'],
              'project_sha256': project_hash(project), 'layers': len(layers), 'frames': len(frames),
              'composite_checks': checks, 'fine_edit': {'changed_coordinates': [[i % 192, i // 192] for i in changed_indices],
                  'visible_composite_changed_coordinates': [[i % 192, i // 192] for i in visible_changes],
                  'outside_mask_changes': 0, 'undo_exact': True, 'replay_exact': True,
                  'candidate_art_approved': False}, 'full_animation_coverage': False}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'frames': len(frames), 'layers': len(layers), 'composites_equal': True,
                      'undo_replay_equal': True, 'output': str(output)}))


if __name__ == '__main__':
    main()
