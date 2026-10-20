#!/usr/bin/env python3
"""Read-only preservation/alias/paint-provenance verification."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAMES=['south_A','south_B','north_A','north_B']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    frozen=json.loads((ROOT/'provenance/frozen-inputs.json').read_text())
    report={}
    for name in NAMES:
        src=ROOT/'inputs'/(name+'.png')
        assert sha(src)==frozen[name]['sha256']
        original=np.asarray(Image.open(src).convert('RGBA'))
        mask=np.asarray(Image.open(ROOT/'masks'/(name+'.png')))>0
        assert int(mask.sum())==1680
        assert np.array_equal(mask[81:121,45:87],np.ones((40,42),dtype=bool))
        variants={}
        for loc in ['output/fixed-grid','output/passing','output/semantic-adjusted']:
            p=ROOT/loc/(name+'.png');im=Image.open(p).convert('RGBA');a=np.asarray(im)
            assert im.size==(128,128)
            assert np.array_equal(original[~mask],a[~mask])
            assert np.array_equal(original[:81],a[:81])
            yy,xx=np.where(a[:,:,3]>127)
            variants[loc]={'sha256':sha(p),'changed_rgba_pixels':int(np.any(a!=original,axis=2).sum()),
                'outside_mask_exact_rgba':True,'support_x_below_y105':float(xx[yy>105].mean())}
        assert variants['output/passing']['sha256']==variants['output/fixed-grid']['sha256']
        report[name]=variants
    print(json.dumps({'passed':True,'scope':'pixel preservation, alias identity and measured support centers only','frames':report},indent=2))

if __name__=='__main__':main()
