from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
BASE=Path('/home/astra/artifacts/emberwake-painted-odd-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-painted-odd-review/review-v1')
M=json.loads((BASE/'INPUTS.json').read_text())
NEAREST=Image.Resampling.NEAREST
FONT=ImageFont.load_default(size=14)
SMALL=ImageFont.load_default(size=12)
BACKGROUNDS={'dark':(24,28,35,255),'light':(235,231,219,255),'ground':(92,102,73,255)}

def tile(rel,side,bg,lower=False):
    im=Image.open(BASE/rel).convert('RGBA')
    canvas=Image.new('RGBA',im.size,bg)
    canvas.alpha_composite(im)
    if lower:
        canvas=canvas.crop((38,72,94,122))
        return canvas.resize((224,200),NEAREST).convert('RGB')
    return canvas.resize((side,side),NEAREST).convert('RGB')

def sheet(rows,side,bg,title,outname,lower=False):
    tw,th=(224,200) if lower else (side,side)
    gap=8; left=100; top=42; rowgap=26
    cols=max(len(items) for _,items in rows)
    canvas=Image.new('RGB',(left+cols*(tw+gap)+gap,top+len(rows)*(th+rowgap)+8),(58,61,67))
    d=ImageDraw.Draw(canvas);d.text((8,10),title,fill='white',font=FONT)
    for r,(label,items) in enumerate(rows):
        y=top+r*(th+rowgap)
        d.text((6,y+th//2),label,fill='white',font=SMALL)
        for c,(rel,lab) in enumerate(items):
            x=left+c*(tw+gap)
            canvas.paste(tile(rel,side,bg,lower),(x,y))
            d.text((x,y+th+3),lab,fill='white',font=SMALL)
    canvas.save(OUT/outname)

for bgname,bg in BACKGROUNDS.items():
 for side in (128,256,84):
  for direction in ('southeast','southwest'):
   rows=[]
   for variant in ('A','B'):
    seq=M['variants'][variant][direction]
    items=[(x['path'],f'{i:02}') for i,x in enumerate(seq)]+[(seq[0]['path'],'00 wrap')]
    rows.append((variant,items))
   sheet(rows,side,bg,f'{direction} | {side}/128 nearest | {bgname} | chronology 00..07 -> 00 | hold 9/160 s',f'{direction}-{side}-{bgname}.png')
 for direction in ('southeast','southwest'):
  rows=[]
  for variant in ('A','B'):
   seq=M['variants'][variant][direction]
   rows.append((variant,[(x['path'],f'{i:02}') for i,x in enumerate(seq)]+[(seq[0]['path'],'00 wrap')]))
  sheet(rows,128,bg,f'{direction} lower body | source crop x38..94 y72..122 at nearest4x | {bgname}',f'{direction}-lower4x-{bgname}.png',lower=True)
 for side in (128,256,84):
  rows=[]
  for direction in ('south','east','west'):
   items=[]
   for i in range(2):items.append((f'context/{direction}-idle-{i:02}.png',f'idle {i:02}'))
   for i in range(8):items.append((f'context/{direction}-walk-{i:02}.png',f'walk {i:02}'))
   items.append((f'context/{direction}-walk-00.png','walk 00 wrap'))
   rows.append((direction,items))
  sheet(rows,side,bg,f'Cardinal identity and turn context | {side}/128 nearest | {bgname}',f'context-{side}-{bgname}.png')
print('Wrote 33 diagnostic PNGs. No inputs changed.')
