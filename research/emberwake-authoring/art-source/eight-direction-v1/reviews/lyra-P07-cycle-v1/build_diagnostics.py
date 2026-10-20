from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
SRC=Path('/home/astra/artifacts/emberwake-lyra-P07-whole-walk-v1/packet/input')
OUT=Path(__file__).parent/'diagnostics'
FONT=ImageFont.load_default()
BACKGROUNDS={'light':'#e7e3d6','dark':'#22252b','game':'#27392f'}
CLIPS=[(v,d) for v in ('A','B') for d in ('southeast','southwest')]

def stage(rel,n,bg):
    im=Image.open(SRC/rel).convert('RGBA')
    assert im.size==(128,128), (rel,im.size)
    scaled=im.resize((n,n),Image.Resampling.NEAREST)
    return Image.alpha_composite(Image.new('RGBA',(n,n),bg),scaled).convert('RGB')

for n in (128,256,84):
  for name,bg in BACKGROUNDS.items():
    fg='#151515' if name=='light' else '#f3ede4'
    pad=8; label=18; cw=n+pad; rh=n+label+pad
    cel=Image.new('RGB',(8*cw+pad,4*rh+30),bg);draw=ImageDraw.Draw(cel)
    draw.text((pad,5),f'All 32 cels | {n}px whole canvas | {name} {bg} | nearest',fill=fg,font=FONT)
    for r,(v,d) in enumerate(CLIPS):
      code='SE' if d=='southeast' else 'SW'
      for f in range(8):
        x=pad+f*cw;y=30+r*rh
        draw.text((x,y),f'{v} {code} {f:02}',fill=fg,font=FONT)
        cel.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+label))
    cel.save(OUT/f'cels-{n}-{name}.png')
    pcw=2*n+3*pad;prh=n+label+pad
    pairs=Image.new('RGB',(4*pcw+pad,8*prh+30),bg);draw=ImageDraw.Draw(pairs)
    draw.text((pad,5),f'All 32 cyclic pairs | {n}px whole canvas | {name} {bg} | nearest | 9/160s each',fill=fg,font=FONT)
    for c,(v,d) in enumerate(CLIPS):
      code='SE' if d=='southeast' else 'SW'
      for f in range(8):
        nxt=(f+1)%8;r=c*2+f//4;col=f%4;x=pad+col*pcw;y=30+r*prh
        draw.text((x,y),f'{v} {code} {f:02} -> {nxt:02}',fill=fg,font=FONT)
        pairs.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+label))
        pairs.paste(stage(f'{v}/{d}/{nxt:02}.png',n,bg),(x+n+pad,y+label))
    pairs.save(OUT/f'pairs-{n}-{name}.png')
manifest=json.loads((SRC/'INPUTS.json').read_text())
for n,name in ((256,'light'),(84,'light'),(84,'dark'),(84,'game')):
  bg=BACKGROUNDS[name];fg='#151515' if name=='light' else '#f3ede4';pad=8;label=18;cw=n+pad;rh=n+label+pad
  card=[e['path'] for e in manifest['context'] if e['path']!='context/appearance.png']
  sheet=Image.new('RGB',(10*cw+pad,3*rh+30),bg);draw=ImageDraw.Draw(sheet)
  draw.text((pad,5),f'All 30 cardinal context cels | {n}px | {name} | nearest',fill=fg,font=FONT)
  for i,rel in enumerate(card):
    x=pad+(i%10)*cw;y=30+(i//10)*rh
    draw.text((x,y),Path(rel).stem,fill=fg,font=FONT)
    sheet.paste(stage(rel,n,bg),(x,y+label))
  sheet.save(OUT/f'context-{n}-{name}.png')
# Supplemental closure detail, preserving whole 256px canvases.
n=256;bg=BACKGROUNDS['light'];cw=264;rh=282;label=18
closure=Image.new('RGB',(3*cw+8,4*rh+30),bg);draw=ImageDraw.Draw(closure)
draw.text((8,5),'Closure detail: 06 -> 07 -> 00 | exact whole-canvas nearest 2x',fill='#151515',font=FONT)
for row,(v,d) in enumerate([(v,d) for d in ('southeast','southwest') for v in ('A','B')]):
  for col,f in enumerate((6,7,0)):
    x=8+col*cw;y=30+row*rh
    draw.text((x,y),f'{v} {d} {f:02}',fill='#151515',font=FONT)
    closure.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+label))
closure.save(OUT/'closure-256-light.png')
