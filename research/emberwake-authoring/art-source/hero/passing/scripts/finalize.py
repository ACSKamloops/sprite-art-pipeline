#!/usr/bin/env python3
"""Promote the frozen semantic-warp candidates; preserve direct composites."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['south_A', 'south_B', 'north_A', 'north_B']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    (ROOT/'output/semantic-adjusted').mkdir(exist_ok=True)
    receipt = {'selection': 'Two candidates retained for root A/B review. output/passing is the direct fixed-grid ImageGen composite; output/semantic-adjusted is the separate shear experiment.',
               'not_claimed': 'A support foot at root x64 is not universal anatomical correctness. No independent art rating or runtime integration.',
               'allowed_mask_bounds_half_open': [45,81,87,121], 'frames': {}}
    for name in NAMES:
        baked = ROOT / 'provenance' / ('warp-'+name) / 'frame.png'
        final = ROOT / 'output/semantic-adjusted' / (name+'.png')
        final.write_bytes(baked.read_bytes())
        direct=ROOT/'output/fixed-grid'/(name+'.png')
        (ROOT/'output/passing'/(name+'.png')).write_bytes(direct.read_bytes())
        a = np.array(Image.open(final).convert('RGBA'))
        b = np.array(Image.open(ROOT/'inputs'/(name+'.png')).convert('RGBA'))
        mask = np.array(Image.open(ROOT/'masks'/(name+'.png'))) > 0
        assert np.array_equal(a[~mask], b[~mask])
        assert np.array_equal(a[:81], b[:81])
        yy,xx = np.where(a[:,:,3]>127)
        foot = yy > 105
        dx = -4 if name.endswith('A') else 5
        donor = np.array(Image.open(ROOT/'provenance/native-donors'/(name+'.png')).convert('RGBA'))
        rect = [61,94,76,116] if dx<0 else [51,94,67,116]
        x0,y0,x1,y1 = rect
        rigid = np.array_equal(donor[y0:y1,x0:x1], a[y0-1:y1-1,x0+dx:x1+dx])
        assert rigid
        receipt['frames'][name] = {
            'semantic_adjusted_path': str(final.relative_to(ROOT)), 'semantic_adjusted_sha256': sha(final),
            'direct_path': 'output/fixed-grid/'+name+'.png', 'direct_sha256': sha(direct),
            'passing_path': 'output/passing/'+name+'.png', 'passing_sha256': sha(ROOT/'output/passing'/(name+'.png')),
            'changed_rgba_pixels': int(np.any(a!=b,axis=2).sum()),
            'outside_mask_exact_rgba': True, 'all_rows_lt_81_exact_rgba': True,
            'complete_support_boot_exact_rgba': True,
            'support_boot_source_rect_half_open': rect, 'support_boot_translation': [dx,-1],
            'opaque_support_center_x_below_y105': float(xx[foot].mean()),
            'alpha_gt_127_bbox': [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
            'pivot': [64,112], 'size': [128,128],
        }
        # Freeze triangulation, expected output and map for exact read-only replay.
        specpath=ROOT/'provenance/warp-specs'/(name+'.json')
        spec=json.loads(specpath.read_text())
        spec['triangles']=json.loads((ROOT/'provenance'/('warp-'+name)/'triangles.json').read_text())
        spec['map']='../warp-'+name+'/source-map.npz'
        spec['expected']='../../output/semantic-adjusted/'+name+'.png'
        specpath.write_text(json.dumps(spec,indent=2)+'\n')
    for label,bg,textcolor in [('dark',(40,44,53),'white'), ('light',(226,226,218),'black')]:
        proof=Image.new('RGB',(1024,560),bg)
        d=ImageDraw.Draw(proof)
        for i,name in enumerate(NAMES):
            x=i*256
            for y,loc,lab in [(20,'inputs','input contact'),(298,'output/passing','passing candidate')]:
                im=Image.open(ROOT/loc/(name+'.png')).convert('RGBA').resize((256,256),Image.Resampling.NEAREST)
                proof.paste(im,(x,y),im)
                d.text((x+6,y-16),name+' '+lab,fill=textcolor)
        proof.save(ROOT/'output'/('proof-2x-'+label+'.png'))
    # Close-up pants joins, single 6x enlargement without fitting individual bounds.
    for loc,suffix in [('output/passing',''),('output/semantic-adjusted','-semantic')]:
        proof=Image.new('RGB',(1200,312),(45,49,58));d=ImageDraw.Draw(proof)
        for i,name in enumerate(NAMES):
            im=Image.open(ROOT/loc/(name+'.png')).convert('RGBA')
            crop=im.crop((42,72,89,120)).resize((282,288),Image.Resampling.NEAREST)
            proof.paste(crop,(i*300,24),crop)
            d.text((i*300+4,4),name+' seam / boot',fill='white')
        proof.save(ROOT/('output/proof-seams'+suffix+'-6x.png'))
    (ROOT/'provenance/final-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    run()
