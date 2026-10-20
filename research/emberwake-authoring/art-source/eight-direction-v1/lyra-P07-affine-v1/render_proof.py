from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path(__file__).resolve().parent
grounds={'light':'#e7e3d6','dark':'#22252b','game':'#27392f'}
for size in (128,256,84):
 for name,bg in grounds.items():
  sh=Image.new('RGBA',(size*3,(size+20)*2),(46,48,53,255));d=ImageDraw.Draw(sh)
  for row in (0,1):
   for col,i in enumerate((6,7,0)):
    p=R/'raw/07-affine-protected.png'if row==1 and i==7 else R/f'inputs/current/{i:02}.png'
    z=Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(p).convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST)
    sh.alpha_composite(z,(col*size,row*(size+20)+20));d.text((col*size+3,row*(size+20)+3),f'{"base"if row==0 else"P affine"} {i:02}',fill='white')
  sh.save(R/f'proof/06-07-00-{size}-{name}.png')
 # Joint/foot full actual bounds and complete pose at same fixed stage.
for name,bg in grounds.items():
 sh=Image.new('RGBA',(3*352,2*300),(46,48,53,255));d=ImageDraw.Draw(sh)
 paths=[R/'inputs/current/06.png',R/'inputs/current/07.png',R/'inputs/current/00.png',R/'inputs/current/06.png',R/'raw/07-affine-protected.png',R/'inputs/current/00.png']
 for j,p in enumerate(paths):
  row,col=divmod(j,3);z=Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(p).convert('RGBA'))
  sh.alpha_composite(z.crop((43,79,87,114)).resize((352,280),Image.Resampling.NEAREST),(col*352,row*300+20));d.text((col*352+3,row*300+3),f'{"base"if row==0 else"P affine"} {[6,7,0][col]:02}; fixed x43..86 y79..1138x',fill='white')
 sh.save(R/f'proof/joint-foot-8x-{name}.png')
# Source rows/cuff ownership versus affine layer, with 07 base and actual result.
base=np.array(Image.open(R/'inputs/current/07.png').convert('RGBA'));own=np.array(Image.open(R/'masks/P07-literal-source-owner.png'))>0;cuff=np.array(Image.open(R/'masks/P07-charcoal-cuff-owner.png'))>0;q=np.array(Image.open(R/'inputs/witnesses/07-Q-visible-boot-literal.png'))>0
ov=base.copy();ov[own]=[255,100,185,255];ov[cuff]=[255,213,55,255];ov[q]=[55,210,255,255]
panels=[('actual07',Image.fromarray(base)),('literal source: P pink/cuff yellow/Q cyan',Image.fromarray(ov)),('raw affine source layer',Image.open(R/'raw/P07-affine-layer.png').convert('RGBA')),('protected composite',Image.open(R/'raw/07-affine-protected.png').convert('RGBA'))]
sh=Image.new('RGBA',(448*4,340),(231,227,214,255));d=ImageDraw.Draw(sh)
for col,(title,z)in enumerate(panels):
 d.text((col*448+3,2),title,fill='black');bg=Image.new('RGBA',(128,128),'#e7e3d6');bg.alpha_composite(z);sh.alpha_composite(bg.crop((38,79,94,118)).resize((448,312),Image.Resampling.NEAREST),(col*448,24))
sh.save(R/'proof/source-owner-raw-result-8x.png')
(R/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#2e3035;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Lyra07 one affine P test, unselected</h1><p>Actual sourceRGBA; exactly one prescribed three-point positive affine. Projected geometry changes; no rigid invariance or anatomical acceptance claim. Original06/00, current upper and Q fixed.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">'for n in ['06-07-00-128-light','06-07-00-256-light','06-07-00-84-light','06-07-00-84-dark','06-07-00-84-game','joint-foot-8x-light','source-owner-raw-result-8x']))
print('One raw affine proof ready at128/256/84 and enlarged joints on three grounds')
