from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
forest=Image.open(R/'inputs/forest-ground-stage-crop.png').convert('RGBA')
bgs={'game':forest,'dark':Image.new('RGBA',(128,128),(18,30,25,255)),'light':Image.new('RGBA',(128,128),(233,233,222,255))}
seq=[2,3,4,5]
for name,bg in bgs.items():
 for size in (128,256,84):
  sh=Image.new('RGBA',(len(seq)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(sh)
  for row,folder in enumerate(('inputs/control','candidate')):
   for col,i in enumerate(seq):
    z=bg.copy();z.alpha_composite(Image.open(R/folder/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST)
    sh.alpha_composite(z,(col*size,row*(size+18)+18));d.text((col*size+2,row*(size+18)+2),f'{"base"if row==0 else"depth"} {i:02}',fill='white')
  sh.save(R/f'proof/02-03-04-05-{name}-{size}.png')
 # Fixed lower crop; no perpose fit.
 sh=Image.new('RGBA',(448,332),(29,34,43,255));d=ImageDraw.Draw(sh)
 for row,folder in enumerate(('inputs/control','candidate')):
  for col,i in enumerate((3,4)):
   z=bg.copy();z.alpha_composite(Image.open(R/folder/f'{i:02}.png').convert('RGBA'))
   sh.alpha_composite(z.crop((42,82,98,119)).resize((224,148),Image.Resampling.NEAREST),(col*224,row*166+18))
   d.text((col*224+2,row*166+2),f'{"base"if row==0 else"depth"} {i:02} fixed crop4x',fill='white')
 sh.save(R/f'proof/lower-before-after-{name}-4x.png')
# Source-owned boundary and literal edits. Cyan=Q, red=P, yellow=overlap,
# magenta=actual changed pixels, not newly transparent separators.
sh=Image.new('RGBA',(2*320,3*216),(233,233,222,255));d=ImageDraw.Draw(sh)
for col,i in enumerate((3,4)):
 a=np.array(Image.open(R/f'inputs/control/{i:02}.png').convert('RGBA'))
 p=np.array(Image.open(R/f'inputs/parts/{i:02}-P.png').convert('RGBA'))
 q=np.array(Image.open(R/f'inputs/parts/{i:02}-Q.png').convert('RGBA'))
 owner=np.array(Image.open(R/f'masks/{i:02}-literal-RGB-owner.png'))>0
 ov=a.copy();pm=p[:,:,3]>0;qm=q[:,:,3]>0
 ov[pm]=[240,60,80,255];ov[qm]=[40,220,220,255];ov[pm&qm]=[250,220,40,255]
 dif=a.copy();dif[owner]=[255,40,225,255]
 for row,(label,z)in enumerate((('retained layer coverage',ov),('literal RGB edits',dif),('actual result',np.array(Image.open(R/f'candidate/{i:02}.png'))))):
  tile=Image.new('RGBA',(320,192),(233,233,222,255));tile.alpha_composite(Image.fromarray(z).crop((48,88,88,112)).resize((320,192),Image.Resampling.NEAREST));sh.alpha_composite(tile,(col*320,row*216+24));d.text((col*320+3,row*216+3),f'{i:02} {label}',fill='black')
sh.save(R/'proof/layer-boundary-and-RGB-diff-8x.png')
(R/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Unselected Brann03/04 overlap-depth trial</h1><p>One fixed source-palette contact-shadow plan. Alpha, contours, boot positions/volume, upper/cloth/gloves and clock unchanged. No model. These newly authored RGB strokes do not reveal hidden anatomy.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">'for n in ('02-03-04-05-game-128','02-03-04-05-game-256','02-03-04-05-game-84','02-03-04-05-light-84','02-03-04-05-dark-84','lower-before-after-game-4x','layer-boundary-and-RGB-diff-8x')))
print('native128/256/84 threeground comparison proofs ready')
