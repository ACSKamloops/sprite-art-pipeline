"""The previously measured fixed-palette rule, not private clustering/deflicker.

Forward Oklab matrices follow https://bottosson.github.io/posts/oklab/.
The quarter-lightness distance is a retained calibration hypothesis. Source
calibration and held-out cases live in recovery-next-20261014; tie behavior and
general automatic palette construction remain unestablished.
"""
import numpy as np
from .core import ValidationError, validate_raster

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
    validate_raster(source)
    palette = np.asarray(palette)
    if (palette.dtype != np.uint8 or palette.ndim != 2 or palette.shape[-1] != 4 or
            not 1 <= len(palette) <= 256 or np.any(palette[:, 3] != 255)):
        raise ValidationError('Calibrated mapper requires 1..256 opaque uint8 RGBA palette entries')
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


def reference_palette(rgba):
    """Declare opaque reference colors in first-appearance order, without fitting."""
    validate_raster(rgba)
    if rgba.shape[0]*rgba.shape[1]>512*512:
        raise ValidationError('Fixed-palette reference exceeds the512x512 local reference budget')
    visible = rgba[rgba[..., 3] > 0]
    if not len(visible) or np.any(visible[:, 3] != 255):
        raise ValidationError('Fixed reference palette needs visible, fully opaque colors only')
    colors = list(dict.fromkeys(map(tuple, visible.tolist())))
    if len(colors) > 256:
        raise ValidationError('Reference has more than256 colors; no automatic clustering is substituted')
    return np.asarray(colors, dtype=np.uint8)
