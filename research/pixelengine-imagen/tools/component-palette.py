#!/usr/bin/env python3
"""Explicit color-only component composition; preserves alpha, clocks and owners."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(TOOLKIT))
sys.path.insert(0, str(REPO / 'workbench'))
from sprite_lab import load_project, canonical_json
from sprite_lab.core import render_cel
from sprite_workbench.calibrated_palette import reference_palette, remap_rgba


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    source, out = args.project.resolve(), args.output.absolute()
    if out.exists():
        raise ValueError('Fresh output required')
    source_pin = sha(source)
    project = load_project(source.read_text())
    colors = []
    for path in args.palette:
        palette = reference_palette(np.array(Image.open(path).convert('RGBA')))
        for color in palette.tolist():
            if color not in colors:
                colors.append(color)
    if not 1 <= len(colors) <= 256:
        raise ValueError('Combined visible palette must fit existing mapper')
    palette = np.array(colors, dtype=np.uint8)
    out.mkdir(parents=True)
    (out / 'cels').mkdir()
    checks = []
    for cid, cel in project['cels'].items():
        original = render_cel(project, cid)
        mapped = Image.fromarray(remap_rgba(np.array(original), palette))
        alpha_exact = mapped.getchannel('A').tobytes() == original.getchannel('A').tobytes()
        protected = cel['layer_id'] in args.protected_layer
        rgba_exact = mapped.tobytes() == original.tobytes()
        if not alpha_exact or protected and not rgba_exact:
            raise ValueError('Color composition violates protected owner or alpha')
        mapped.save(out / 'cels' / (cid + '.png'))
        checks.append({'cel': cid, 'layer': cel['layer_id'], 'alpha_exact': alpha_exact,
                       'protected': protected, 'rgba_exact': rgba_exact})
    frames = []
    for frame in project['frames']:
        frames.append({k: v for k, v in frame.items() if k != 'cels'} |
                      {'cels': {layer: {'image': f'cels/{cid}.png', 'at': [0, 0]} for layer, cid in frame['cels'].items()}})
    spec = {'schema': 'sprite-construction-spec/v1', 'canvas': project['canvas'],
            'layers': project['layers'], 'frames': frames, 'animations': project['animations'],
            'provenance': {'operation': 'Explicit palette union and fixed mapping on layered source',
                           'source_project_sha256': source_pin,
                           'palette_sources': [{'path': str(p), 'sha256': sha(p)} for p in args.palette],
                           'protected_layers_rgba_exact': args.protected_layer}}
    (out / 'spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    constructor = module('component_constructor', TOOLKIT / 'scripts/sprite_construct.py')
    result = constructor.construct(out / 'spec.json')
    (out / 'project.json').write_text(canonical_json(result) + '\n')
    exporter = module('component_exporter', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
    exporter.export(out / 'project.json', out / 'delivery', 'walk', TOOLKIT, 8, 'hero')
    apng = module('component_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')
    apng.convert(out / 'delivery/manifest.json', out / 'delivery/apng')
    report = {'source_project_sha256': source_pin, 'recipe_sha256': sha(__file__),
              'palette_rgba': colors, 'cels': checks, 'clock_and_canvas_unchanged': result['animations'] == project['animations'] and result['canvas'] == project['canvas'],
              'source_unchanged': sha(source) == source_pin, 'approval': 'Unreviewed color composition'}
    if not report['source_unchanged'] or not report['clock_and_canvas_unchanged']:
        raise ValueError('Source or metadata mismatch')
    (out / 'RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(out), 'palette_colors': len(colors), 'alpha_exact_all_cels': all(c['alpha_exact'] for c in checks)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--palette', type=Path, action='append', required=True)
    p.add_argument('--protected-layer', action='append', default=[])
    p.add_argument('--output', type=Path, required=True)
    run(p.parse_args())
