#!/usr/bin/env python3
"""Read-only verification of frozen leg layers and final pixel preservation."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import source_warp as warp

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))

def main():
    source=json.loads((ROOT/'inputs/source-receipt.json').read_text())
    for name,expected in source['source_files'].items():assert sha(ROOT/'inputs'/name)==expected
    mask=np.array(Image.open(ROOT/'masks/roi.png'))>0
    report={'passed':True,'scope':'Source hashes, frozen-map replay, rigid isolated boots, horizontal identity, final outside-mask and seam RGBA. No art rating.','layers':{},'candidates':{}}
    yy,xx=np.indices(mask.shape)
    for specpath in sorted((ROOT/'maps').rglob('spec.json')):
        path,spec,body,donor,owner=warp.load(specpath)
        with np.load(path.parent/spec['map'],allow_pickle=False) as f:xy=f['source_xy'];stored=f['source_kind']
        assert np.array_equal(xy[:,:,0],xx)
        result,edits,changed=warp.render(spec,body,donor,owner,xy,stored)
        assert np.array_equal(result,rgba(path.parent/spec['expected']))
        report['layers'][str(specpath.relative_to(ROOT))]={'frozen_map_replay':True,'rigid_boot_rgba_exact':True,'source_x_identity':True}
    receipt=json.loads((ROOT/'receipt.json').read_text())
    for name,f in receipt['frames'].items():
        src=ROOT/f['source_png'];assert sha(src)==f['source_sha256'];a=rgba(src)
        for variant,r in f['variants'].items():
            path=ROOT/r['candidate'];b=rgba(path)
            assert sha(path)==r['sha256']
            assert np.array_equal(a[~mask],b[~mask])
            assert np.array_equal(a[:82],b[:82])
            report['candidates'][name+'/'+variant]={'outside_roi_and_y_le_81_exact':True,
                'measured_soles':{leg:v['actual_final_sole_alpha_gt_127'] for leg,v in r['legs'].items()},
                'final_boot_visible_pixel_mismatches':{leg:v['final_visible_boot_pixel_mismatches'] for leg,v in r['legs'].items()}}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
