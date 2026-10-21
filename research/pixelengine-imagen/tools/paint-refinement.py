#!/usr/bin/env python3
"""Explicit whole-sheet sampling/alpha/palette experiments, with existing exports."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'workbench'))
from sprite_workbench.calibrated_palette import reference_palette, remap_rgba


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(args):
    source, out = args.sheet.resolve(), args.output.absolute()
    if out.exists():
        raise ValueError('Fresh output required')
    source_pin = sha(source)
    image = Image.open(source).convert('RGBA')
    if image.width != image.height or image.width % 3:
        raise ValueError('Expected divisible3x3 square sheet')
    edge = image.width // 3
    cels = [image.crop((i % 3 * edge, i // 3 * edge, (i % 3 + 1) * edge, (i // 3 + 1) * edge)) for i in range(9)]
    boxes = [cel.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox() for cel in cels]
    if boxes[-1] is not None or any(b is None for b in boxes[:8]):
        raise ValueError('Expected eight complete populated cells and empty ninth')
    cels = cels[:8]
    scale = 64 / max(b[3] - b[1] for b in boxes[:8])
    size = round(edge * scale)
    effective_scale = size / edge
    floor = max(b[3] for b in boxes[:8])
    offset = [40 - size // 2, 72 - round(floor * effective_scale)]
    palette = reference_palette(np.array(Image.open(args.reference).convert('RGBA')))
    base = load_module('comparison_recipe', Path(__file__).with_name('run-comparison.py'))
    out.mkdir(parents=True)
    for folder in ['projects', 'clips']:
        (out / folder).mkdir()
    rows = []
    for name, sampling, threshold, use_palette in [
        ('nearest-source-alpha', Image.Resampling.NEAREST, 0, False),
        ('nearest-binary64-reference', Image.Resampling.NEAREST, 64, True),
        ('box-binary64-reference', Image.Resampling.BOX, 64, True),
        ('box-binary128-reference', Image.Resampling.BOX, 128, True),
        ('box-binary128-paint', Image.Resampling.BOX, 128, False),
    ]:
        images = []
        for cel in cels:
            small = cel.resize((size, size), sampling)
            canvas = Image.new('RGBA', (80, 80))
            canvas.paste(small, tuple(offset))
            array = np.array(canvas)
            if use_palette:
                array = remap_rgba(array, palette)
            if threshold:
                array[..., 3] = np.where(array[..., 3] >= threshold, 255, 0)
                array[array[..., 3] == 0] = 0
            images.append(Image.fromarray(array))
        row = base.export_clip(out, name, images,
            {'source_sheet_sha256': sha(source), 'sampling': sampling.name,
             'threshold_candidate_not_default': threshold,
             'fixed_reference_palette': use_palette,
             'uniform_cell_scale': effective_scale, 'uniform_offset': offset,
             'clock': 'Unchanged8x1/8second', 'operation': 'Authored raster sampling/alpha study, not recovered provider algorithm'})
        rows.append(row)
    montage = Image.new('RGB', (1280, len(rows) * 190), (125, 125, 125))
    draw = ImageDraw.Draw(montage)
    for r, row in enumerate(rows):
        draw.text((4, r * 190 + 3), row['id'], fill='white')
        for i in range(8):
            frame = Image.open(out / 'clips' / row['id'] / 'frames' / f'{i:04d}.png').convert('RGBA')
            frame = frame.resize((160, 160), Image.Resampling.NEAREST)
            montage.paste(frame, (160 * i, r * 190 + 22), frame)
    montage.save(out / 'chronology.png')
    result = {'sheet': str(source), 'sheet_sha256': sha(source), 'recipe_sha256': sha(__file__),
              'reference_sha256': sha(args.reference), 'measured_size': list(image.size),
              'alpha8_measurement_boxes': boxes, 'canvas': [80, 80], 'cell': edge,
              'common_scaled_cell': size, 'common_scale': effective_scale, 'common_offset': offset,
              'per_frame_fitting': False, 'palette_rgba': palette.tolist(), 'clips': rows,
              'approval': 'Unreviewed, no inherited rating', 'source_unchanged': sha(source) == source_pin}
    if not result['source_unchanged']:
        raise ValueError('Source changed during export')
    write(out / 'RESULTS.json', result)
    print(json.dumps({'output': str(out), 'clips': [r['id'] for r in rows]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
