from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
out=Path(__file__).parent;src=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-articulated-craft-v7');phases=[41,46,51,56,60];receipt=[]
for size in [256,384]:
 for kind in ['colour','silhouette']:
  c=Image.new('RGB',(size*5,(size+30)*3),(35,40,45));d=ImageDraw.Draw(c)
  for row,name in enumerate(['baseline','yaw35','yaw45']):
   for col,cel in enumerate(phases):
    p=out/f'{name}-{size}-cel{cel:02}.png';a=Image.open(p).convert('RGBA');im=Image.new('RGB',a.size,(35,40,45));
    if kind=='colour':im.paste(a,mask=a.getchannel('A'))
    else:im.paste((255,255,255),(0,0,size,size),a.getchannel('A'))
    x=col*size;y=row*(size+30);c.paste(im,(x,y));d.text((x,y+size),f'{name} cel{cel} source{cel*2+1}',fill='white')
    if name=='baseline' and kind=='colour':
     original=Image.open(src/f'native{size}'/f'frame-{cel:03}.png').convert('RGBA');aa=list(a.getdata());bb=list(original.getdata());receipt.append({'native':size,'cel':cel,'baseline_changed_RGBA_pixels':sum(v!=w for v,w in zip(aa,bb)),'max_channel_delta':max(abs(x-y)for v,w in zip(aa,bb)for x,y in zip(v,w))})
  c.save(out/f'comparison-{size}-{kind}.png')
(out/'baseline-comparison.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
(out/'source-binding.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'native384'/'full-captain-diagnostic.blend',src/'SHA256.json',src/'source-module-manifest.json',src/'native384'/'integration-contract.json']},indent=2)+'\n')
