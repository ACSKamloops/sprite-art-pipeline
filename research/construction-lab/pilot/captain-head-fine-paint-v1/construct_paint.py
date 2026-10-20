"""Bounded, replayable UV paint candidates; no frame redraw or art approval."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / 'pilot/captain-head-uv-diagnosis-v1'
OUT = Path(__file__).resolve().parent / 'candidates'
SOURCE = Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/body-side-polish-v2/Material_0-side-polish-UV.png')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert sha(SOURCE) == '3f4db5046bda0e20194b2a8dbf5364176a9712bb2cc4e6ff9cd533a120a2f5d3'
    if OUT.exists():
        raise FileExistsError('Preserve earlier paint candidates')
    original = Image.open(SOURCE).convert('RGBA')
    before = np.asarray(original)
    assert np.array_equal(before, np.asarray(Image.open(DIAG / 'packed-source-texture.png').convert('RGBA')))
    safe_path = DIAG / 'proposed-head-owned-edit-footprint.png'
    safe = np.asarray(Image.open(safe_path).convert('L')) == 255
    mask = Image.new('L', original.size)
    painter = ImageDraw.Draw(mask)
    regions = [(1490, 210, 1599, 339), (1860, 380, 2019, 529), (0, 1760, 139, 1949)]
    for region in regions:
        painter.rectangle(region, fill=255)
    owned = safe & (np.asarray(mask) == 255)
    # Sharpen existing paint detail only, leaving the entire other atlas exact.
    sharpened = np.asarray(original.filter(ImageFilter.UnsharpMask(radius=1.25, percent=160, threshold=4))).copy()
    sharpened[:, :, 3] = before[:, :, 3]
    candidate_a = before.copy()
    candidate_a[owned] = sharpened[owned]
    candidate_b_image = Image.fromarray(candidate_a)
    draw = ImageDraw.Draw(candidate_b_image)
    # Explicit new authored plate outline in the side chart, guided by traced
    # eye/temple UVs. This is a candidate design, not recovered original paint.
    plate = [(43, 1797), (73, 1806), (88, 1830), (95, 1848),
             (119, 1869), (113, 1899), (84, 1893), (66, 1877),
             (59, 1848), (39, 1844), (23, 1825), (28, 1804)]
    draw.polygon(plate, fill=(52, 60, 72, 255))
    draw.line(plate + [plate[0]], fill=(100, 111, 125, 255), width=2)
    draw.line([(73, 1808), (65, 1830), (75, 1852), (100, 1877)], fill=(28, 34, 43, 255), width=2)
    draw.line([(60, 1850), (77, 1857), (84, 1875), (105, 1885)], fill=(126, 137, 147, 255), width=1)
    draw.ellipse((27, 1805, 47, 1826), fill=(18, 22, 29, 255))
    draw.ellipse((30, 1808, 44, 1823), fill=(135, 146, 156, 255))
    draw.ellipse((33, 1811, 42, 1821), fill=(126, 22, 24, 255))
    draw.ellipse((35, 1812, 40, 1817), fill=(212, 48, 36, 255))
    draw.point((36, 1813), fill=(245, 140, 100, 255))
    proposed_b = np.asarray(candidate_b_image).copy()
    candidate_b = before.copy()
    candidate_b[owned] = proposed_b[owned]
    candidate_b[:, :, 3] = before[:, :, 3]
    OUT.mkdir(parents=True)
    Image.fromarray(owned.astype(np.uint8) * 255).save(OUT / 'owned-head-edit-mask.png')
    receipts = []
    for name, array in [('detail-sharpen', candidate_a), ('authored-temple-plate', candidate_b)]:
        assert np.array_equal(array[~owned], before[~owned])
        assert np.array_equal(array[:, :, 3], before[:, :, 3])
        changed = np.any(array != before, axis=2)
        path = OUT / f'{name}.png'
        Image.fromarray(array).save(path)
        Image.fromarray(changed.astype(np.uint8) * 255).save(OUT / f'{name}-changed-mask.png')
        receipts.append({'file': path.name, 'SHA256': sha(path), 'changed_texels': int(changed.sum()),
                         'outside_owned_texels_exact': True, 'alpha_exact': True})
    receipt = {'state': 'UNAPPROVED_SOURCE_PAINT_CANDIDATES', 'source_SHA256': sha(SOURCE),
               'diagnosis_mask_SHA256': sha(safe_path), 'script_SHA256': sha(__file__),
               'owned_chart_rectangles_inclusive': regions, 'owned_texel_count': int(owned.sum()),
               'unsharp_recipe': {'radius': 1.25, 'percent': 160, 'threshold': 4},
               'authored_side_plate_polygon': plate, 'candidates': receipts,
               'limits': ['Source head-only raster footprint excludes2texel nonhead neighborhoods',
                          'Raster ownership is not continuous filtering or seam proof',
                          'Plate is newly authored; no geometry, head/neck pose or unseen anatomy edits',
                          'Actual fixed-view renders and nonhead leakage checks required before selection']}
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipts))


if __name__ == '__main__':
    main()
