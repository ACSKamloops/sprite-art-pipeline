from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent;C=O/'cels';D=O/'proofs';FONT=ImageFont.load_default()
rows=[('brann','northeast','attack',[10,11,12]),('brann','northwest','attack',[10,11,12]),('rowan','northeast','cast',[22,17,18,19,20,22]),('rowan','southeast','cast',[22,17,18,19,20,22])]
for n in (128,84,256):
 for name,bg in {'light':'#e7e3d6','dark':'#22252b','game':'#27392f'}.items():
  cw=n+8;rh=n+26;fg='#161616' if name=='light' else '#eee9df'
  sheet=Image.new('RGB',(6*cw+8,4*rh+30),bg);draw=ImageDraw.Draw(sheet)
  draw.text((8,5),f'Action defect focus | actual v10 cels | {n}px whole canvas NEAREST | {name}',fill=fg,font=FONT)
  for row,(actor,view,action,ids) in enumerate(rows):
   for col,cell in enumerate(ids):
    x=8+col*cw;y=30+row*rh
    code={'southeast':'SE','northeast':'NE','northwest':'NW'}[view]
    draw.text((x,y),f'{actor[:2]} {code} {action[0]} c{cell}',fill=fg,font=FONT)
    im=Image.open(C/actor/view/f'{cell:02}.png').convert('RGBA').resize((n,n),Image.Resampling.NEAREST)
    sheet.paste(Image.alpha_composite(Image.new('RGBA',(n,n),bg),im).convert('RGB'),(x,y+18))
  sheet.save(D/f'findings-{n}-{name}.png')
