"""One literal same-actor clenched-hand transplant; no image generation."""
from pathlib import Path
import hashlib
import json
import argparse
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
out = args.out.resolve()
assert not out.exists(), 'Fresh output only'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

inputs = json.loads((ROOT / 'INPUTS.json').read_text())
for name, expected in inputs['files_sha256'].items():
    assert sha(ROOT / 'inputs' / name) == expected
donor = np.array(Image.open(ROOT / 'inputs/10.png').convert('RGBA'))
source = np.array(Image.open(ROOT / 'inputs/11.png').convert('RGBA'))
yy, xx = np.indices(source.shape[:2])
# Literal hand/cuff seam from the actual source-pixel inspection. It is a
# declared painting owner, not an automatically inferred anatomical boundary.
donor_owner = ((yy >= 31) & (yy <= 49) & (xx >= 94) & (xx <= 114)
               & (2 * xx >= yy + 153) & (donor[:, :, 3] > 0))
old_owner = ((yy >= 28) & (yy <= 48) & (xx >= 94) & (xx <= 115)
             & (2 * xx >= yy + 157) & (source[:, :, 3] > 0))
layer = np.zeros_like(source)
source_xy = np.full((128, 128, 2), -1, dtype=np.int16)
ys, xs = np.where(donor_owner)
tx, ty = xs + 1, ys - 2
layer[ty, tx] = donor[ys, xs]
source_xy[ty, tx] = np.stack([xs, ys], axis=1)
target_owner = source_xy[:, :, 0] >= 0
candidate = source.copy()
candidate[old_owner] = 0
candidate[target_owner] = layer[target_owner]
union = old_owner | target_owner
assert np.array_equal(candidate[~union], source[~union])
assert np.array_equal(candidate[yy >= 50], source[yy >= 50])
assert np.array_equal(layer[target_owner], donor[source_xy[target_owner, 1], source_xy[target_owner, 0]])
out.mkdir(parents=True)
for n, a in [('11', candidate), ('donor-hand', np.where(donor_owner[:, :, None], donor, 0)), ('translated-hand', layer)]:
    Image.fromarray(a).save(out / f'{n}.png')
for n, a in [('donor-owner', donor_owner), ('old-owner', old_owner), ('target-owner', target_owner), ('change-domain', union)]:
    Image.fromarray((a * 255).astype(np.uint8)).save(out / f'{n}.png')
np.savez_compressed(out / 'SOURCE-MAP.npz', source_xy=source_xy, old_owner=old_owner, target_owner=target_owner)
# Source-sized comparison plus nearest magnification on three exact grounds.
for size in [84, 128, 256]:
    for name, ground in [('light', '#e7e3d6'), ('dark', '#22252b'), ('game', '#27392f')]:
        im = Image.new('RGB', (size * 3, (size + 20) * 2), ground)
        d = ImageDraw.Draw(im)
        for row in range(2):
            for col, index in enumerate([10, 11, 12]):
                a = candidate if row == 1 and index == 11 else np.array(Image.open(ROOT / 'inputs' / f'{index:02d}.png').convert('RGBA'))
                tile = Image.fromarray(a).resize((size, size), Image.Resampling.NEAREST)
                bg = Image.new('RGBA', tile.size, ground)
                bg.alpha_composite(tile)
                im.paste(bg.convert('RGB'), (col * size, row * (size + 20) + 20))
                d.text((col * size + 3, row * (size + 20) + 3), f'{"current" if row == 0 else "trial"} {index:02d}', fill='white' if name != 'light' else 'black')
        im.save(out / f'10-11-12-{size}-{name}.png')
receipt = {
    'status': 'First bounded source-fist construction; visual and wholeaction review pending',
    'donor': 'inputs/10.png', 'target': 'inputs/11.png', 'translation': [1, -2],
    'donor_samples': int(donor_owner.sum()), 'old_hand_samples': int(old_owner.sum()),
    'actual_changed_RGBA_pixels': int(np.any(candidate != source, axis=2).sum()),
    'all_other_pixels_exact': True, 'source_palette_and_partial_alpha_exact': True,
    'body_and_timing_changed': False, 'model_calls': 0, 'new_painted_RGB': 0,
    'candidate_sha256': sha(out / '11.png'),
}
(out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
