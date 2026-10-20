#!/usr/bin/env python3
"""A literal donor RGB repair; alpha and all unowned pixels remain exact."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent
def digest(a):
    return hashlib.sha256(a.tobytes()).hexdigest()
def apply(source, donor, plan):
    a, b = np.array(source.convert('RGBA')), np.array(donor.convert('RGBA'))
    if a.shape != (128,128,4) or b.shape != a.shape:
        raise ValueError('Expected native 128px cels')
    if digest(a) != plan['source_cel_rgba_sha256'] or digest(b) != plan['donor_cel_rgba_sha256']:
        raise ValueError('Source or donor changed; rebase required')
    mask = np.zeros((128,128), bool)
    for y,x in plan['mask_yx']:
        if not (0 <= y < 128 and 0 <= x < 128):
            raise ValueError('Invalid mask coordinate')
        mask[y,x] = True
    result = a.copy()
    result[:,:,:3][mask] = b[:,:,:3][mask]
    assert np.array_equal(result[:,:,3], a[:,:,3])
    assert np.array_equal(result[~mask], a[~mask])
    for y,x0,x1 in plan['excluded_head_rows']:
        assert np.array_equal(result[y,x0:x1], a[y,x0:x1])
    assert digest(result) == plan['expected_rgba_sha256']
    changed = np.any(result != a, axis=2)
    journal = [{'target_xy':[int(x),int(y)],'rgb_source_xy':[int(x),int(y)],
        'rgb_owner':'donor.png','alpha_owner':'source.png',
        'before':a[y,x].tolist(),'after':result[y,x].tolist()}
        for y,x in zip(*np.nonzero(changed))]
    assert len(journal) == plan['changed_pixels']
    return Image.fromarray(result), journal
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit('Output must be a fresh nonexistent directory')
    result,journal=apply(Image.open(ROOT/'source.png'),Image.open(ROOT/'donor.png'),json.loads((ROOT/'plan.json').read_text()))
    args.output.mkdir(parents=True)
    result.save(args.output/'candidate.png')
    (args.output/'journal.json').write_text(json.dumps(journal,indent=2)+'\n')
    print('Replayed',len(journal),'RGB edits; alpha, head and all outside pixels exact')
if __name__=='__main__':main()
