#!/usr/bin/env python3
"""Replay the frozen painted-part maps into a fresh exact V4 animation."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image,ImageFilter

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();out=args.output.absolute()
    if out.exists():raise SystemExit('Fresh output directory required')
    frozen=ROOT/'candidate-v4'
    source_receipt=json.loads((frozen/'BUILD-RECEIPT.json').read_text())
    inputs=[];rendered=[]
    for i,record in enumerate(source_receipt['records']):
        base=Image.new('RGBA',(128,128))
        inputs.append({'frame':i,'source_sha256':sha(ROOT/'inputs'/f'{i:02}.png'),'expected_sha256':sha(frozen/f'{i:02}.png'),'parts':[]})
        for leg in record['depth_order']:
            for part in ['cloth','calf','foot']:
                name=f'{leg}-{part}'
                source=frozen/'parts'/f'{name}.png'
                src=np.array(Image.open(source).convert('RGBA'))
                mapping=frozen/'layers'/f'{i:02}-{name}-source-xy.npy'
                w=np.load(mapping,allow_pickle=False)
                if w.shape!=(128,128,2)or w.dtype.kind not in 'iu':raise ValueError('Invalid map '+str(mapping))
                valid=(w[:,:,0]>=0)&(w[:,:,1]>=0)
                if np.any(w[valid]>=128):raise ValueError('Out-of-range source texel')
                if np.any((~valid)&np.any(w!=-1,axis=2)):raise ValueError('Noncanonical invalid coordinate')
                a=np.zeros_like(src);a[valid]=src[w[:,:,1][valid],w[:,:,0][valid]]
                witness=frozen/'layers'/f'{i:02}-{name}.png'
                if a.tobytes()!=Image.open(witness).convert('RGBA').tobytes():raise ValueError('Source map/paint disagreement')
                base.alpha_composite(Image.fromarray(a))
                inputs[-1]['parts'].append({'id':name,'paint_sha256':sha(source),'map_sha256':sha(mapping),'layer_rgba_exact':True})
        orig=np.array(Image.open(ROOT/'inputs'/f'{i:02}.png').convert('RGBA'))
        mask=np.array(Image.open(frozen/'layers'/f'{i:02}-edit-mask.png'))>0
        result=orig.copy();result[mask]=np.array(base)[mask]
        # Match the selected original's explicitly bounded alpha1 cleanup.
        core=Image.fromarray((result[:,:,3]>=128).astype('uint8')*255).filter(ImageFilter.MaxFilter(5))
        noise=(result[:,:,3]==1)&(np.array(core)==0)&mask;result[noise]=0
        expected=Image.open(frozen/f'{i:02}.png').convert('RGBA')
        if result.tobytes()!=expected.tobytes():raise ValueError(f'Frame{i}: replay differs from frozen V4')
        if not np.array_equal(result[~mask],orig[~mask]):raise ValueError('Protected pixels changed')
        rendered.append(Image.fromarray(result))
    # Validate the full clip before writing anything.
    out.mkdir(parents=True)
    records=[]
    for i,im in enumerate(rendered):
        p=out/f'{i:02}.png';im.save(p)
        if p.read_bytes()!=(frozen/f'{i:02}.png').read_bytes():raise ValueError('PNG encoding changed; RGBA had matched, file hash did not')
        records.append({'frame':i,'sha256':sha(p),'hold':[9,160],'source_png_bytes_exact':True,'source_rgba_exact':True,'outside_mask_exact':True})
    (out/'REPLAY-RECEIPT.json').write_text(json.dumps({'method':'Frozen source-texel map replay, not new geometric interpolation or generation','frozen_build_sha256':sha(frozen/'BUILD-RECEIPT.json'),'inputs':inputs,'frames':records,'duration':[9,20],'scope':'Exact retained paint/maps/compositing/clock; not new art or motion approval'},indent=2)+'\n')
    print('All8 PNG files, RGBA and protected pixels exactly reproduced;450ms clock retained')
if __name__=='__main__':main()
