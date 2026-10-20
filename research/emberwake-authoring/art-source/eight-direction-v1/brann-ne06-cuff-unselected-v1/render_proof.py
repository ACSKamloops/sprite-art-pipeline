from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent
grounds={'light':(232,231,218,255),'dark':(24,27,25,255),'game':(39,57,47,255)}
forest=Image.open(R/'inputs/forest-ground-crop.png').convert('RGBA')
grounds['forest']=None
def backdrop(bg):return forest.copy()if bg is None else Image.new('RGBA',(128,128),bg)
for size in (128,256,84):
 for ground,bg in grounds.items():
  sh=Image.new('RGBA',(size*3,(size+20)*2),(40,43,48,255));d=ImageDraw.Draw(sh)
  for row in (0,1):
   for col,i in enumerate((5,6,7)):
    p=R/'final/06.png'if row==1 and i==6 else R/f'inputs/current/{i:02}.png'
    z=backdrop(bg);z.alpha_composite(Image.open(p).convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST)
    sh.alpha_composite(z,(col*size,row*(size+20)+20));d.text((col*size+3,row*(size+20)+3),f'{"selected"if row==0 else"cuff trial"} NE{i:02}',fill='white')
  sh.save(R/f'proof/05-06-07-{size}-{ground}.png')
 for ground,bg in grounds.items():
  if size!=128:continue
  sh=Image.new('RGBA',(4*260,260),(40,43,48,255));d=ImageDraw.Draw(sh)
  for col,(label,p)in enumerate([('current06',R/'inputs/current/06.png'),('raw current exact',R/'raw/06.png'),('literal source layer',R/'raw/charcoal-repair-layer.png'),('final one cuff trial',R/'final/06.png')]):
   z=backdrop(bg);z.alpha_composite(Image.open(p).convert('RGBA'));sh.alpha_composite(z.crop((54,81,74,99)).resize((260,234),Image.Resampling.NEAREST),(col*260,24));d.text((col*260+2,3),label,fill='white')
  sh.save(R/f'proof/current-raw-layer-final-joint-13x-{ground}.png')
# Literal changes only; pink=RGB shading, cyan=new charcoal coverage.
base=np.array(Image.open(R/'inputs/current/06.png').convert('RGBA'));owner=np.array(Image.open(R/'masks/literal-edit-owner.png'))>0;under=np.array(Image.open(R/'masks/new-charcoal-coverage.png'))>0
over=base.copy();over[owner]=[255,30,220,255];over[under]=[30,220,245,255]
sh=Image.new('RGBA',(640,340),(232,231,218,255));d=ImageDraw.Draw(sh)
for col,(label,im)in enumerate([('literal18 edits: pink13 RGB / cyan5 coverage',Image.fromarray(over)),('actual final',Image.open(R/'final/06.png').convert('RGBA'))]):
 z=Image.new('RGBA',(128,128),(232,231,218,255));z.alpha_composite(im);sh.alpha_composite(z.crop((52,79,84,110)).resize((320,310),Image.Resampling.NEAREST),(col*320,24));d.text((col*320+2,2),label,fill='black')
sh.save(R/'proof/literal-diff-and-result-10x.png')
(R/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#282b30;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Brann NE06 one local cuff repair, unselected</h1><p>13literal current-source shaded cloth replacements+5declared charcoal cuff coverage samples. Existing positive boot paint, upper/sash and otherleg fixed. No model/editor/fullbank/rating.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">'for n in ['05-06-07-128-light','05-06-07-256-light','05-06-07-84-light','05-06-07-84-dark','05-06-07-84-game','current-raw-layer-final-joint-13x-light','literal-diff-and-result-10x']))
print('One cuff candidate proofs rendered')
