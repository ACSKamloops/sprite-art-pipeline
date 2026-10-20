#!/usr/bin/env python3
"""Rebuild one retained ImageGen rear release. No generation or game writes."""
import argparse
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source = Path(__file__).resolve().parent / 'raw.png'
raw = Image.open(source).convert('RGBA')
assert raw.size == (1254, 1254), raw.size
pixels = np.array(raw.resize((256, 256), Image.Resampling.NEAREST))
components, count = label(pixels[:, :, 3] > 20, np.ones((3, 3)))
assert count > 0
sizes = np.bincount(components.ravel())
sizes[0] = 0
pixels[components != sizes.argmax()] = 0
pixels[pixels[:, :, 3] < 24] = 0
pixels[pixels[:, :, 3] > 245, 3] = 255
result = Image.new('RGBA', (256, 256))
result.alpha_composite(Image.fromarray(pixels), (0, -3))
assert not args.output.exists(), 'Use a fresh output; frozen files are preserved.'
args.output.parent.mkdir(parents=True, exist_ok=True)
result.save(args.output)
print(hashlib.sha256(args.output.read_bytes()).hexdigest())
