"""Unchanged shipped palette-image import, not private smart-palette recovery.

Input is row-major RGBA already equivalent to browser canvas getImageData. PNG
color-management/premultiplied-alpha decoding is outside this operation. The
single-image handler keeps first-seen visible RGBs up to256, otherwise invokes
its original <=32 representative reducer; target count is not configurable.
"""
from pathlib import Path
import base64
import hashlib
import json
import shutil
import subprocess

import numpy as np
from .core import ValidationError, validate_raster

POLICY = 'unchanged-shipped-palette-image-import-v1'
SOURCE_SHA256 = '819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d'
MANIFEST_SHA256 = 'a32ca0ece88e70b9199173f1af0e7ee0c1d1868ea3383df8cc652074565f0d3c'
MAX_PIXELS = 512 * 512


def import_palette_image(rgba):
    """Return exact handler hex colors/warning/error plus declared host metadata.

    A source UI rejection (<2 resulting colors) is an accepted=False result,
    not silently promoted to a synthetic valid palette. Input bytes are retained.
    """
    pixels = validate_raster(rgba)
    height, width = pixels.shape[:2]
    if width * height > MAX_PIXELS:
        raise ValidationError('Recovered palette import exceeds the262144-pixel local budget')
    # Bind execution, hash and histogram to one immutable caller snapshot.
    pixels = np.array(pixels, dtype=np.uint8, order='C', copy=True)
    node = shutil.which('node')
    if node is None:
        raise ValidationError('Node is required for unchanged palette source; no fallback algorithm')
    directory = Path(__file__).parent
    manifest_bytes = (directory / 'parity_palette_source.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise ValidationError('Recovered palette source manifest changed')
    request = json.dumps({'width': width, 'height': height,
                          'rgba': base64.b64encode(pixels.tobytes()).decode()}).encode()
    try:
        completed = subprocess.run([node, str(directory / 'parity_palette_runner.cjs')],
                                   input=request, capture_output=True, timeout=10, check=False)
    except subprocess.TimeoutExpired as error:
        raise ValidationError('Original palette source exceeded the local execution budget') from error
    if completed.returncode:
        raise ValidationError('Original palette source execution failed: ' +
                              completed.stderr.decode(errors='replace')[:400])
    try:
        result = json.loads(completed.stdout)
        if set(result) != {'colors', 'warning', 'error'}:
            raise ValueError('unexpected source result')
        colors = [[int(color[i:i+2], 16) for i in (1, 3, 5)] + [255]
                  for color in result['colors']]
    except (ValueError, KeyError, TypeError) as error:
        raise ValidationError('Invalid result from original palette source') from error
    visible = pixels[pixels[..., 3] > 0, :3]
    found = len(np.unique(visible, axis=0)) if len(visible) else 0
    return {**result, 'accepted': result['error'] is None, 'palette_rgba': colors,
            'policy': POLICY, 'source_asset_sha256': SOURCE_SHA256,
            'source_manifest_sha256': MANIFEST_SHA256,
            'adapter': {'input': 'supplied single-image canvas-equivalent RGBA',
                        'unique_visible_rgb': found, 'source_rgba_sha256':
                        hashlib.sha256(pixels.tobytes()).hexdigest(),
                        'branch': 'original-32-representatives' if found > 256 else 'original-first-seen'},
            'boundary': 'palette-image import only; not private reduce-colors/automatic K/dither/GIF'}
