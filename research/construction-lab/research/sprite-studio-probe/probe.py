#!/usr/bin/env python3
"""Exercise pinned upstream raster primitives, without launching agent CLIs."""
import argparse
import contextlib
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    upstream = args.repository.resolve()
    resources = upstream / 'src-tauri/resources'
    sys.path.insert(0, str(resources))
    from sprite_rig_raster import prepare_layers, render_frame, alpha_component_sizes
    from sprite_rig_matrix import resolve_frame_matrices, local_matrix, apply_matrix
    from sprite_rig_schema import validate_mesh

    output = Path(__file__).parent / 'evidence'
    output.mkdir(exist_ok=True)
    source_path = root / 'study/layered-cutout/assets/front_arm.png'
    arm = Image.open(source_path).convert('RGBA')
    master = Image.new('RGBA', (96, 96))
    master.paste(arm, (30, 38))
    master.save(output / 'master.png')
    source = master.tobytes()
    parts = [
        {'name': 'upper', 'mask': {'rect': [30, 38, 14, 18]}, 'pivot': [35, 46], 'z': 1},
        {'name': 'lower', 'mask': {'rect': [44, 38, 14, 18]}, 'pivot': [44, 46], 'parent': 'upper', 'z': 2},
    ]
    base, layers = prepare_layers(source, 96, 96, parts, 2)
    cases = [
        ('rest', {'transforms': {}}),
        ('rigid', {'transforms': {'upper': {'rotate': 35}}}),
        ('bent', {'transforms': {'upper': {'rotate': 35}, 'lower': {'rotate': -70}}}),
        ('folded', {'transforms': {'upper': {'rotate': -30}, 'lower': {'rotate': -120}}}),
    ]
    results = []
    sheet = Image.new('RGB', (96 * len(cases), 114), '#20303e')
    sheet_draw = ImageDraw.Draw(sheet)
    for index, (name, frame) in enumerate(cases):
        canvas, matrices = render_frame(96, 96, base, layers, parts, frame, {})
        repeat, _ = render_frame(96, 96, base, layers, parts, frame, {})
        pixels = bytes(canvas.data)
        assert pixels == bytes(repeat.data), 'repeat differs'
        if name == 'rest':
            assert pixels == source, 'rest does not preserve the original RGBA'
        image = Image.frombytes('RGBA', (96, 96), pixels)
        image.save(output / f'{name}.png')
        sheet.paste(image, (index * 96, 0), image)
        sheet_draw.text((index * 96 + 5, 98), name, fill='white')
        results.append({'name': name, 'rgba_sha256': hashlib.sha256(pixels).hexdigest(),
                        'alpha_component_sizes_8connected': alpha_component_sizes(pixels, 96, 96),
                        'wrist': apply_matrix(matrices['lower'], (56, 46)),
                        'repeat_rgba_equal': True})
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.Resampling.NEAREST).save(output / 'comparison-3x.png')

    negatives = []
    def rejects(name, fn):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                fn()
        except SystemExit as error:
            negatives.append({'name': name, 'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError(f'{name} accepted')
    rejects('parent_cycle', lambda: resolve_frame_matrices([
        {'name': 'a', 'parent': 'b'}, {'name': 'b', 'parent': 'a'}], {}))
    rejects('zero_scale', lambda: local_matrix([0, 0], {'scaleX': 0}))
    rejects('invalid_mesh_weights', lambda: validate_mesh({
        'vertices': [[0, 0], [10, 0], [0, 10]], 'triangles': [[0, 1, 2]],
        'weights': [{'upper': .1}] * 3}, 96, 96, ['upper'], 'probe'))
    rejects('overlapping_mask_empty_owner', lambda: prepare_layers(source, 96, 96, [
        {'name': 'a', 'mask': {'rect': [0, 0, 96, 96]}, 'z': 0},
        {'name': 'b', 'mask': {'rect': [0, 0, 96, 96]}, 'z': 1}], 2))
    # A planted mathematical anchor is insufficient under a continuous world root.
    anchor_world = []
    for fraction in [0, .25, .5, .75, 1]:
        root_x = .8 * fraction
        rendered_x = round(40 - root_x)
        anchor_world.append({'fraction': fraction, 'root_x': root_x,
                             'rendered_x': rendered_x, 'world_x': root_x + rendered_x})
    report = {
        'scope': 'Python raster/ownership/hierarchy primitives; Rust engine, app, AI generation and full quality validator NOT executed',
        'upstream': {'url': 'https://github.com/JohnKinyanjui/sprite-maker',
                     'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=upstream, text=True).strip(),
                     'commit_date': subprocess.check_output(['git', 'show', '-s', '--format=%cI'], cwd=upstream, text=True).strip(),
                     'files': {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                               for f in [*resources.glob('sprite_rig*.py'), resources / 'sprite_tool.py']}},
        'source': str(source_path.relative_to(root)), 'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'cases': results, 'negative_checks': negatives,
        'analytic_raster_contact_counterexample': anchor_world,
        'lessons': [
            'Same pixels and transformations produce identical RGBA in this bounded test.',
            'Parent chains produce real local elbow articulation; they do not invent missing joint texture or hidden anatomy.',
            'Nearest raster transforms preserve sharp edges but change sampled colors and silhouette; inspect each bent pose.',
            'Full timeline world-root/raster contact checks remain necessary after IK.',
            'Do not use upstream finalize-degraded to label quality failures approved.',
        ],
    }
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'repeat_cases': len(results), 'negative_checks': len(negatives),
                      'report': str(output / 'report.json'), 'scope': report['scope']}))


if __name__ == '__main__':
    main()
