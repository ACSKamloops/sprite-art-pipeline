"""Reproduce the previous3anchor boot warp as a labeled failed control only."""
import numpy as np,json
from PIL import Image,ImageDraw,ImageChops
import build as b
P=b.P;out=P/'artifacts';src=Image.open(P/'source/leg-master-128.png').convert('RGBA');packet=json.loads((P/'source/poses.json').read_text());cfg={'far':{'ankle':[44,90],'heel':[57,118],'toe':[21,122]},'near':{'ankle':[98,91],'heel':[111,115],'toe':[99,120]}};old=[]
mask=Image.new('L',(128,128));ImageDraw.Draw(mask).polygon([(0,0),(62,0),(64,40),(68,128),(0,128)],fill=255)
for f in packet['frames']:
 im=Image.new('RGBA',(256,256));root=np.array(f['physical_root_pixels'])
 for n,c in cfg.items():
  part=src.copy();m=mask if n=='far'else ImageChops.invert(mask);cut=Image.new('L',(128,128));ImageDraw.Draw(cut).rectangle((0,91 if n=='far' else 90,127,127),fill=255);part.putalpha(ImageChops.multiply(src.getchannel('A'),ImageChops.multiply(m,cut)))
  pix={k:np.array(v)-root for k,v in f['legs'][n]['pixels'].items()};sa=np.column_stack([np.array(c[k])-c['ankle']for k in ['heel','toe']]);ta=np.column_stack([pix[k]-pix['ankle']for k in ['heel','toe']]);inv=np.linalg.inv(ta@np.linalg.inv(sa));off=np.array(c['ankle'])-inv@pix['ankle'];co=tuple(inv[0])+tuple([off[0]])+tuple(inv[1])+tuple([off[1]]);im.alpha_composite(part.transform((256,256),Image.Transform.AFFINE,co,Image.Resampling.NEAREST))
 old.append(im)
sheet=Image.new('RGBA',(300,8*80),(38,43,50,255));d=ImageDraw.Draw(sheet)
for j,i in enumerate(range(0,72,9)):
 for col,im in enumerate([old[i],Image.open(out/'surface-v2/frames'/f'{i:03}.png'),Image.open(out/'proxy-v2/frames'/f'{i:03}.png')]):sheet.alpha_composite(im.crop((80,190,180,250)),(col*100,j*80+20))
 for col,label in enumerate(['old affine','UV surface','closed proxy']):d.text((col*100+3,j*80+2),f'{i}: {label}',fill='white')
sheet.resize((600,1280),Image.Resampling.NEAREST).save(out/'comparison-8keys-2x.png')
