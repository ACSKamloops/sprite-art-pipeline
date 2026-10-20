#!/usr/bin/env python3
"""Replay the bounded leg composite with one fixed sheet registration."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['south_A', 'south_B', 'north_A', 'north_B']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    raw_path = ROOT / 'raw/request-02-output.png'
    raw = Image.open(raw_path).convert('RGBA')
    assert raw.size == (1254, 1254)
    # Declared uniform full-sheet grid transform, not per-pose bounding-box fitting.
    # PIL nearest sampling: floor((destination + .5) * source_size / dest_size).
    coords = np.floor((np.arange(256) + .5) * 1254 / 256).astype(np.int32)
    sx, sy = np.meshgrid(coords, coords)
    np.savez_compressed(ROOT / 'provenance/sheet-source-map.npz', source_x=sx, source_y=sy)
    registered = np.asarray(raw)[sy, sx]
    Image.fromarray(registered).save(ROOT / 'provenance/registered-request-02.png')
    stats = {}
    # Preserve hem and gloves through native y80; only complete lower-leg area may change.
    mask = np.zeros((128, 128), dtype=bool)
    mask[81:121, 45:87] = True
    outputs = []
    originals = []
    for i, name in enumerate(NAMES):
        source_path = ROOT / 'inputs' / f'{name}.png'
        original = np.asarray(Image.open(source_path).convert('RGBA'))
        x0, y0 = (i % 2) * 128, (i // 2) * 128
        donor = registered[y0:y0+128, x0:x0+128]
        result = original.copy()
        result[mask] = donor[mask]
        outside_equal = bool(np.array_equal(result[~mask], original[~mask]))
        assert outside_equal
        output_path = ROOT / 'output/fixed-grid' / f'{name}.png'
        Image.fromarray(result).save(output_path)
        Image.fromarray((mask * 255).astype(np.uint8)).save(ROOT / 'masks' / f'{name}.png')
        changed = np.any(result != original, axis=2)
        stats[name] = {
            'input_sha256': sha(source_path), 'output_sha256': sha(output_path),
            'mask_sha256': sha(ROOT / 'masks' / f'{name}.png'),
            'mask_pixels': int(mask.sum()), 'changed_rgba_pixels': int(changed.sum()),
            'outside_mask_exact_rgba': outside_equal,
            'preserved_all_rows_y_lt_81': bool(np.array_equal(result[:81], original[:81])),
            'size': [128, 128], 'pivot': [64, 112],
            'bbox': Image.fromarray(result).getbbox(),
        }
        originals.append(Image.fromarray(original))
        outputs.append(Image.fromarray(result))
    receipt = {
        'tool': 'image_gen.imagegen built-in; one initial call plus one targeted repair',
        'selected_raw': 'raw/request-02-output.png', 'selected_raw_sha256': sha(raw_path),
        'registration': {'kind': 'single uniform full-sheet nearest-neighbor grid transform',
                         'raw_sheet': [1254,1254], 'native_sheet': [256,256],
                         'cell_order': NAMES,
                         'source_formula': 'floor((q + 0.5) * 1254 / 256)',
                         'translation': [0,0], 'individual_bbox_fits': False},
        'composite_mask_bounds_half_open': [45,81,87,121],
        'mask_reason': 'Preserve full tunic hem and side gloves through y80; replace lower pants, calves, boots and old-foot transparency below.',
        'alpha': 'Generated donor alpha retained without threshold; original RGBA restored outside mask.',
        'source_map': 'provenance/sheet-source-map.npz', 'frames': stats,
    }
    (ROOT / 'provenance/composite-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    # 2x proof. Each view presents frozen input beside the new passing candidate.
    for label, bg in [('dark',(40,44,53)), ('light',(226,226,218))]:
        proof = Image.new('RGB', (1024, 304), bg)
        d = ImageDraw.Draw(proof)
        for i, (name, old, new) in enumerate(zip(NAMES, originals, outputs)):
            x = i * 256
            d.text((x+4, 4), name + '  input | passing', fill=(255,255,255) if label=='dark' else (0,0,0))
            # Each 128 native frame is shown at exact 2x, in two aligned rows.
            # Layout is four columns; before row is above after row in separate files below.
        proof = Image.new('RGB', (1024, 560), bg)
        d = ImageDraw.Draw(proof)
        for i, (name, old, new) in enumerate(zip(NAMES, originals, outputs)):
            x = i*256
            d.text((x+6, 4), name+' input', fill=(255,255,255) if label=='dark' else (0,0,0))
            for y, sprite in [(20,old),(298,new)]:
                enlarged = sprite.resize((256,256), Image.Resampling.NEAREST)
                proof.paste(enlarged, (x,y), enlarged)
            d.text((x+6,282), name+' passing candidate', fill=(255,255,255) if label=='dark' else (0,0,0))
        proof.save(ROOT / 'output' / f'proof-direct-2x-{label}.png')
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    run()
