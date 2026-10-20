#!/usr/bin/env python3
"""Retain old upper + actual source02 rear leg, shear new full foreleg paint."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
S=Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11/bake/rowan/southeast')
Y,X=np.mgrid[:128,:128]
gen=np.array(Image.open(R/'raw/generated03-native128.png').convert('RGBA'))
old=np.array(Image.open(S/'07.png').convert('RGBA'))
rear=np.array(Image.open(S/'02.png').convert('RGBA'))
out=R/'repurposed07-reach-v2';(out/'frames').mkdir(parents=True,exist_ok=True)
for i in range(8):shutil.copyfile(S/f'{i:02}.png',out/'frames'/f'{i:02}.png')
# Visible foreground chain in the generated drawing, not semantic auto-masking.
poly=[(60,80),(75,80),(76,88),(74,94),(80,100),(80,110),(61,111),(58,100),(58,92),(56,86)]
maskim=Image.new('1',(128,128));ImageDraw.Draw(maskim).polygon(poly,fill=1)
foremask=np.array(maskim)&(gen[:,:,3]>0)
# The short receding left chain is actual pose02; no exposed hidden paint filled.
rearmask=(Y>=80)&(Y<=104)&(X>=47)&(X<=62)&(rear[:,:,3]>0)
rearmask[(Y<=84)&(X<49)]=False
uppermask=(Y<80)|((Y<=84)&(X<49))|((Y<=81)&(X>=82))
fore=np.zeros_like(gen);fmap=np.full((128,128,2),-1,np.int16)
for sy in range(80,112):
    # One modest shear in cream trouser, full brown shoe translated rigidly.
    dx=int(np.floor(3+3*np.clip((sy-81)/10,0,1)+.5))
    for sx in np.where(foremask[sy])[0]:
        tx=int(sx+dx)
        if tx<128:fore[sy,tx]=gen[sy,sx];fmap[sy,tx]=[sx,sy]
parts=[]
for arr,mask in [(rear,rearmask),(fore,fore[:,:,3]>0),(old,uppermask)]:
    layer=np.zeros_like(arr);layer[mask]=arr[mask];parts.append(Image.fromarray(layer))
result=Image.new('RGBA',(128,128))
for im in parts:result.alpha_composite(im)
result.save(out/'frames/07.png')
for i,im in enumerate(parts):im.save(out/f'layer-{i}.png')
for name,m in [('new-fore',foremask),('source02-rear',rearmask),('upper',uppermask)]:Image.fromarray(m.astype('uint8')*255).save(out/f'owner-{name}.png')
np.save(out/'foreground-source-map.npy',fmap)
for size,bg,label in [(84,(38,62,50),'84-game'),(256,(238,236,226),'256-light')]:
    sheet=Image.new('RGB',(5*(size+8),size+24),bg);d=ImageDraw.Draw(sheet)
    for n,(im,name) in enumerate([(Image.open(S/'06.png'),'06'),(Image.open(S/'07.png'),'old07'),(result,'new07'),(Image.open(S/'00.png'),'00'),(Image.open(S/'01.png'),'01')]):
        cel=im.resize((size,size),Image.Resampling.NEAREST);sheet.paste(cel,(n*(size+8),20),cel);d.text((n*(size+8)+2,2),name,fill='white'if size==84 else'black')
    sheet.save(out/f'neighbors-{label}.png')
(out/'METHOD.json').write_text(json.dumps({'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'02.png',S/'07.png',R/'raw/generated03-native128.png']},'upper':'literal original07 mask','rear':'literal complete visible source02 left leg mask','fore':'generated drawing reassigned to actually delivered07 role, trouser shear3→6px, rigid shoe+6px','paint_sampling':'integer source samples retained in map; no invented fill/blending','scope':'unselected actual-art gate, other7 cels/times unchanged; no score'},indent=2)+'\n')
print('Wrote source-owned reaching07 gate.')
