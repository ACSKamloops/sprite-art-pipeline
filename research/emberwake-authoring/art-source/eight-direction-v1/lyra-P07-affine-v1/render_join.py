from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent;O=R/'cuff-join-v1'
grounds={'light':'#e7e3d6','dark':'#22252b','game':'#27392f'}
for size in (128,256,84):
 for name,bg in grounds.items():
  sh=Image.new('RGBA',(size*3,(size+20)*2),(46,48,53,255));d=ImageDraw.Draw(sh)
  for row in (0,1):
   for col,i in enumerate((6,7,0)):
    p=O/'07.png'if row==1 and i==7 else R/f'inputs/current/{i:02}.png'
    z=Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(p).convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST)
    sh.alpha_composite(z,(col*size,row*(size+20)+20));d.text((col*size+3,row*(size+20)+3),f'{"base"if row==0 else"P affine+join"} {i:02}',fill='white')
  sh.save(O/f'proof/06-07-00-{size}-{name}.png')
for name,bg in grounds.items():
 sh=Image.new('RGBA',(3*352,2*300),(46,48,53,255));d=ImageDraw.Draw(sh)
 paths=[R/'inputs/current/06.png',R/'inputs/current/07.png',R/'inputs/current/00.png',R/'inputs/current/06.png',O/'07.png',R/'inputs/current/00.png']
 for j,p in enumerate(paths):
  row,col=divmod(j,3);z=Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(p).convert('RGBA'))
  sh.alpha_composite(z.crop((43,79,87,114)).resize((352,280),Image.Resampling.NEAREST),(col*352,row*300+20));d.text((col*352+3,row*300+3),f'{"base"if row==0 else"affine+join"} {[6,7,0][col]:02}',fill='white')
 sh.save(O/f'proof/joint-foot-8x-{name}.png')
base=Image.open(R/'inputs/current/07.png').convert('RGBA');raw=Image.open(R/'raw/07-affine-protected.png').convert('RGBA');out=Image.open(O/'07.png').convert('RGBA');field=Image.open(O/'charcoal-cuff-join-layer.png').convert('RGBA')
sh=Image.new('RGBA',(5*300,260),(231,227,214,255));d=ImageDraw.Draw(sh)
for col,(label,im)in enumerate([('current07',base),('raw affine gap',raw),('literal charcoal field',field),('one joined result',out),('join samples pink',out.copy())]):
 if col==4:
  m=Image.open(O/'charcoal-cuff-join-owner.png');im.paste((255,40,210,255),(0,0,128,128),m)
 bg=Image.new('RGBA',(128,128),'#e7e3d6');bg.alpha_composite(im);sh.alpha_composite(bg.crop((61,80,86,100)).resize((300,240),Image.Resampling.NEAREST),(col*300,20));d.text((col*300+3,2),label,fill='black')
sh.save(O/'proof/current-raw-join-12x.png')
(O/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#2e3035;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>One Lyra07 P affine with19source-connected cuff samples</h1><p>Unselected one-pose prototype. Original raw affine remains separate; this is the one bounded cuff completion, no new paint colors/model/editor/timing.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">'for n in ['06-07-00-128-light','06-07-00-256-light','06-07-00-84-light','06-07-00-84-dark','06-07-00-84-game','joint-foot-8x-light','current-raw-join-12x']))
print('One joined affine proof ready')
