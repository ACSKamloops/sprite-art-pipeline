from pathlib import Path
from PIL import Image,ImageDraw
import json, numpy as np
ROOT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/input');OUT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/review')
BG=(87,101,70,255); crop=(32,70,96,118)
metrics={}
for variant in ['A','B']:
    for direction in ['southeast','southwest']:
        ims=[Image.open(ROOT/f'{variant}/{direction}/{i:02}.png').convert('RGBA') for i in range(8)]
        sheet=Image.new('RGB',(1096,932),(47,50,55));d=ImageDraw.Draw(sheet)
        d.text((12,8),f'{variant} {direction}: every cyclic pair; source crop x32..95 y70..117, nearest4x; ground',(245,245,245))
        seq=[]
        for i in range(8):
            j=(i+1)%8;x=12+(i%2)*544;y=32+(i//2)*224
            d.text((x,y),f'{i:02} -> {j:02}',(245,245,245))
            for k,idx in enumerate([i,j]):
                im=ims[idx].crop(crop).resize((256,192),Image.Resampling.NEAREST)
                tile=Image.new('RGBA',im.size,BG);tile.alpha_composite(im)
                sheet.paste(tile.convert('RGB'),(x+k*264,y+18))
            a=np.asarray(ims[i]);b=np.asarray(ims[j]);m=np.any(a!=b,axis=2)
            yy,xx=np.where(m);seq.append({'pair':f'{i:02}->{j:02}','changed_pixels':int(m.sum()),'changed_pixels_y_ge_70':int(m[70:].sum()),'difference_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None})
        sheet.save(OUT/f'pairs-{variant}-{direction}-lower4x-ground.png');metrics[f'{variant}/{direction}']=seq
compare=[]
for direction in ['southeast','southwest']:
    for i in range(8):
        a=np.array(Image.open(ROOT/f'A/{direction}/{i:02}.png'));b=np.array(Image.open(ROOT/f'B/{direction}/{i:02}.png'));m=np.any(a!=b,axis=2);yy,xx=np.where(m)
        compare.append({'direction':direction,'cel':f'{i:02}','changed_pixels':int(m.sum()),'difference_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None})
(OUT/'diagnostic-pixel-counts.json').write_text(json.dumps({'adjacent_pairs':metrics,'A_B_differences':compare},indent=2)+'\n')
print('Four pair sheets cover all32 cyclic adjacent pairs. Counts are diagnostic only.')
