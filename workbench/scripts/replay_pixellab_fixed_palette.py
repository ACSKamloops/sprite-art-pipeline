#!/usr/bin/env python3
"""Replay a calibrated public fixed-palette behavior; private source not recovered.

The inferred nondithered rule matches retained calibration and held-out probes:
nearest Oklab palette color with distance .25*dL^2+da^2+db^2, preserving alpha.
Only opaque supplied palette entries were tested. No clustering or dithering.
Oklab matrices: https://bottosson.github.io/posts/oklab/ (public-domain/MIT code).
"""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image


POLICY = 'inferred-fixed-palette-oklab-quarter-L-v1'
M1 = np.array([[.4122214708, .5363325363, .0514459929],
               [.2119034982, .6806995451, .1073969566],
               [.0883024619, .2817188376, .6299787005]])
M2 = np.array([[.2104542553, .7936177850, -.0040720468],
               [1.9779984951, -2.4285922050, .4505937099],
               [.0259040371, .7827717662, -.8086757660]])


def oklab(rgb):
    values = np.asarray(rgb, dtype=np.float64) / 255
    linear = np.where(values <= .04045, values / 12.92, ((values + .055) / 1.055)**2.4)
    return np.cbrt(linear @ M1.T) @ M2.T


def remap_rgba(source, palette):
    if source.dtype != np.uint8 or source.ndim != 3 or source.shape[-1] != 4:
        raise ValueError('Expected uint8 RGBA source')
    palette = np.asarray(palette)
    if palette.dtype != np.uint8 or palette.ndim != 2 or palette.shape[-1] != 4 or not 1 <= len(palette) <= 256:
        raise ValueError('Expected 1..256 uint8 RGBA palette colors')
    if np.any(palette[:, 3] != 255):
        raise ValueError('Only opaque supplied palette entries were calibrated')
    colors = palette[:, :3]
    target_lab = oklab(colors)
    flat = source.reshape(-1, 4)
    output = flat.copy()
    for start in range(0, len(flat), 4096):
        block = flat[start:start + 4096]
        delta = oklab(block[:, :3])[:, None, :] - target_lab[None, :, :]
        distance = np.sum(delta**2 * np.array([.25, 1, 1]), axis=2)
        output[start:start + len(block), :3] = colors[np.argmin(distance, axis=1)]
    return output.reshape(source.shape)


def replay(source_path, palette_path, output_path):
    output_path = Path(output_path)
    receipt_path = output_path.with_suffix('.receipt.json')
    if output_path.exists() or output_path.is_symlink() or receipt_path.exists():
        raise ValueError('Output/receipt must be new; existing art is preserved')
    source_bytes, palette_bytes = Path(source_path).read_bytes(), Path(palette_path).read_bytes()
    with Image.open(BytesIO(source_bytes)) as image:
        if image.format != 'PNG':
            raise ValueError('PNG source required')
        source = np.array(image.convert('RGBA'))
    with Image.open(BytesIO(palette_bytes)) as image:
        palette = np.array(image.convert('RGBA')).reshape(-1, 4)
    result = remap_rgba(source, palette)
    with output_path.open('xb') as file:
        Image.fromarray(result).save(file, format='PNG')
    receipt = {'policy': POLICY, 'inferred_behavior_not_private_source': True,
               'source_png_sha256': hashlib.sha256(source_bytes).hexdigest(),
               'palette_png_sha256': hashlib.sha256(palette_bytes).hexdigest(),
               'output_png_sha256': hashlib.sha256(output_path.read_bytes()).hexdigest(),
               'alpha_exact': bool(np.array_equal(source[..., 3], result[..., 3])),
               'untested_service_tie_policy': 'Local replay chooses first supplied palette entry on an exact tie',
               'scope': 'Nondithered supplied opaque palette. Not automatic clustering, PixMiniMax de-flicker, cutout, temporal conversion or model weights.'}
    with receipt_path.open('x') as file:
        file.write(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--palette', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.source, args.palette, args.output)))
