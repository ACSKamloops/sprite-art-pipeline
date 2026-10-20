"""Merge disjoint, source-bound UV edits; reject ambiguous or leaking layers."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(entry, base):
    path = (base / entry['path']).resolve()
    if sha(path) != entry['sha256']:
        raise ValueError(f'Changed input: {path}')
    return path


def merge(plan_path, output):
    plan = json.loads(plan_path.read_text())
    source = checked_file(plan['source'], plan_path.parent)
    original = np.array(Image.open(source).convert('RGBA'))
    result = original.copy()
    union = np.zeros(original.shape[:2], dtype=bool)
    layers = []
    for layer in plan['layers']:
        texture = checked_file(layer['texture'], plan_path.parent)
        mask_path = checked_file(layer['mask'], plan_path.parent)
        paint = np.array(Image.open(texture).convert('RGBA'))
        mask_image = np.array(Image.open(mask_path).convert('L'))
        if paint.shape != original.shape or mask_image.shape != original.shape[:2]:
            raise ValueError('Mismatched UV dimensions')
        if not np.all((mask_image == 0) | (mask_image == 255)):
            raise ValueError('Only binary owned masks are supported')
        mask = mask_image == 255
        if np.any(mask & union):
            raise ValueError('Overlapping UV edits require explicit reauthoring')
        if not np.array_equal(paint[~mask], original[~mask]):
            raise ValueError('Layer changes source texels outside its mask')
        if not np.array_equal(paint[:, :, 3], original[:, :, 3]):
            raise ValueError('Layer changes source alpha')
        result[mask] = paint[mask]
        union |= mask
        layers.append({'name': layer['name'], 'owned_texels': int(mask.sum()),
                       'changed_texels': int(np.any(paint != original, axis=2).sum()),
                       'texture_sha256': sha(texture), 'mask_sha256': sha(mask_path)})
    if not np.array_equal(result[~union], original[~union]):
        raise AssertionError('Outside-union preservation failure')
    # All checks precede the first output mutation.
    output.mkdir(parents=True, exist_ok=False)
    Image.fromarray(result).save(output / 'combined-body-paint.png')
    Image.fromarray(union.astype('uint8') * 255).save(output / 'owned-union-mask.png')
    receipt = {'state': 'SOURCE_UV_MERGE_NOT_RENDER_OR_ART_APPROVAL',
               'plan_sha256': sha(plan_path), 'source_sha256': sha(source),
               'script_sha256': sha(Path(__file__)), 'layers': layers,
               'outside_union_RGBA_exact': True, 'source_alpha_exact': True,
               'overlap_texels': 0, 'combined_sha256': sha(output / 'combined-body-paint.png'),
               'limits': ['Source-mask ownership inherits bounded component diagnostics',
                          'No combined shader, lighting, motion or art acceptance inferred']}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    merge(args.plan.resolve(), args.output.resolve())
