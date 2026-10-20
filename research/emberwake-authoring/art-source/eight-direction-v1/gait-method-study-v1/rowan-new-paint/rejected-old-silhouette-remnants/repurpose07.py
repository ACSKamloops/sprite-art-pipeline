#!/usr/bin/env python3
"""Test the rejected03 paint in the opposite07 role it actually depicts."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
S=Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11/bake/rowan/southeast')
P=np.array(Image.open(R/'raw/generated03-native128.png').convert('RGBA'))
A=np.array(Image.open(S/'07.png').convert('RGBA'))
Y,X=np.mgrid[:128,:128]
for seam in (79,80,81):
    out=R/f'repurposed07-seam{seam}';(out/'frames').mkdir(parents=True,exist_ok=True)
    for i in range(8):shutil.copyfile(S/f'{i:02}.png',out/'frames'/f'{i:02}.png')
    # Declared lower-art replacement. Exact native scale, no recentering.
    # Glove pixels from old upper are intentionally above replacement layer.
    oldlower=(Y>=seam)&(X>=49)&(X<=82)
    newowner=(Y>=seam)&(Y<=111)&(X>=45)&(X<=82)&(P[:,:,3]>0)
    base=A.copy();base[oldlower]=0
    new=np.zeros_like(P);new[newowner]=P[newowner]
    result=Image.fromarray(base);result.alpha_composite(Image.fromarray(new))
    # Old glove overhang at x45..48 stays above the inserted leg silhouette.
    oldglove=(Y<=84)&(X<49)&(A[:,:,3]>0)
    atop=np.zeros_like(A);atop[oldglove]=A[oldglove]
    result.alpha_composite(Image.fromarray(atop));result.save(out/'frames/07.png')
    Image.fromarray(np.uint8(oldlower)*255).save(out/'old-lower-owner.png')
    Image.fromarray(np.uint8(newowner)*255).save(out/'new-lower-owner.png')
    Image.fromarray(new).save(out/'generated-lower-part.png')
    for size,bg,label in [(84,(38,62,50),'84-game'),(256,(238,236,226),'256-light')]:
        sheet=Image.new('RGB',(5*(size+8),size+24),bg);d=ImageDraw.Draw(sheet)
        for n,(im,name) in enumerate([(Image.open(S/'06.png'),'06'),(Image.open(S/'07.png'),'old07'),(result,'new07'),(Image.open(S/'00.png'),'00'),(Image.open(S/'01.png'),'01')]):
            cel=im.resize((size,size),Image.Resampling.NEAREST);sheet.paste(cel,(n*(size+8),20),cel);d.text((n*(size+8)+2,2),name,fill='white' if size==84 else 'black')
        sheet.save(out/f'neighbors-{label}.png')
    (out/'METHOD.json').write_text(json.dumps({'intent':'Reuse the observed generated right-leading descending pose as07, not as originally requested03. This semantic reassignment is explicit and not generator conformance.','source07_sha256':hashlib.sha256((S/'07.png').read_bytes()).hexdigest(),'generated_native_sha256':hashlib.sha256((R/'raw/generated03-native128.png').read_bytes()).hexdigest(),'lower_seam_y':seam,'map':'one-to-one native pixels, no scale/translation; literal retained masks','retained':'other7 cels exact, original upper except declared lower rectangle','scope':'new representative/fullcycle candidate, no art grade/editor/engine test'},indent=2)+'\n')
print('Created three seam gates; no selection/quality claim.')
