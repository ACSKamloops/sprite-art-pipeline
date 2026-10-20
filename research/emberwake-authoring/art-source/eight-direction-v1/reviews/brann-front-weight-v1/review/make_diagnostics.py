from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path('/home/astra/artifacts/emberwake-brann-front-weight-review-v1/input')
OUT=ROOT.parent/'review'
M=json.loads((ROOT/'INPUTS.json').read_text())
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
GROUNDS={'light':(234,231,222),'dark':(27,31,38),'muted':(111,123,113)}
CYCLES=[('A','southeast'),('B','southeast'),('A','southwest'),('B','southwest')]
coverage=[]
def cel(v,d,i,s,bg):
    src=Image.open(ROOT/M['variants'][v][d][i]['path']).convert('RGBA')
    if s!=128: src=src.resize((s,s),Image.Resampling.NEAREST)
    dst=Image.new('RGB',(s,s),bg)
    dst.paste(src,mask=src.getchannel('A'))
    return dst
for s in (128,256,84):
 for ground,bg in GROUNDS.items():
    cell=s+6
    rowh=s+24
    pairw=2*s+16
    width=4*pairw+24
    height=40+4*(3*rowh+30)
    canvas=Image.new('RGB',(width,height),(50,52,56))
    draw=ImageDraw.Draw(canvas)
    draw.text((12,8),f'Actual bound PNGs | {s}px NEAREST | {ground} {bg} | frames then explicit cyclic pairs',font=FONT,fill='white')
    for ci,(v,d) in enumerate(CYCLES):
        top=36+ci*(3*rowh+30)
        draw.text((12,top),f'{v} {d} | frame positions fixed in their 128px stage',font=FONT,fill='white')
        y=top+23
        for i in range(8):
            x=12+i*cell
            canvas.paste(cel(v,d,i,s,bg),(x,y+18))
            draw.text((x,y),f'{i:02d}',font=SMALL,fill='white')
        for i in range(8):
            x=12+(i%4)*pairw
            py=y+rowh+(i//4)*rowh
            j=(i+1)%8
            draw.text((x,py),f'{v} {d[:2].upper()} {i:02d} -> {j:02d}'+(' WRAP' if j==0 else ''),font=SMALL,fill='white')
            canvas.paste(cel(v,d,i,s,bg),(x,py+18))
            canvas.paste(cel(v,d,j,s,bg),(x+s+8,py+18))
            coverage.append({'variant':v,'direction':d,'from':i,'to':j,'size':s,'ground':ground,'sheet':f'coverage-{s}-{ground}.png','left_stage_origin':[x,py+18],'right_stage_origin':[x+s+8,py+18]})
    canvas.save(OUT/f'coverage-{s}-{ground}.png')
# Context: the appearance image plus all 30 cardinal sprites; context is identity only.
appearance=Image.open(ROOT/'context/appearance.png').convert('RGBA')
maxw=480
ratio=min(1,maxw/appearance.width,480/appearance.height)
a=appearance.resize((int(appearance.width*ratio),int(appearance.height*ratio)),Image.Resampling.NEAREST)
ctx=Image.new('RGB',(1450,1050),(111,123,113)); cd=ImageDraw.Draw(ctx)
cd.text((12,8),'Appearance and cardinal context only (not A/B motion evidence)',font=FONT,fill='white')
ctx.paste(a,(12,36),a.getchannel('A'))
cd.text((12,530),f'Appearance source {appearance.size}; displayed {a.size}',font=FONT,fill='white')
for di,direction in enumerate(('east','south','west')):
    row=[e for e in M['context'] if e['path'].startswith('context/'+direction+'-')]
    for i,e in enumerate(row):
        x=510+(i%5)*180;y=36+di*330+(i//5)*160
        im=Image.open(ROOT/e['path']).convert('RGBA')
        ctx.paste(im,(x,y+20),im.getchannel('A'))
        cd.text((x,y),Path(e['path']).stem,font=SMALL,fill='white')
ctx.save(OUT/'context-identity.png')
(OUT/'coverage.json').write_text(json.dumps({'animation_cels':32,'unique_cyclic_pairs':32,'scales':[128,256,84],'grounds':GROUNDS,'pairs':coverage},indent=2)+'\n')
