from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path('/home/astra/artifacts/emberwake-brann-front-seams-review-v1/input');O=R.parent/'review';M=json.loads((R/'INPUTS.json').read_text())
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);S=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
G={'light':(234,231,222),'dark':(27,31,38),'muted':(111,123,113)};C=[('A','southeast'),('B','southeast'),('A','southwest'),('B','southwest')]
def cel(v,d,i,s,bg):
 im=Image.open(R/M['variants'][v][d][i]['path']).convert('RGBA')
 if s!=128:im=im.resize((s,s),Image.Resampling.NEAREST)
 out=Image.new('RGB',(s,s),bg);out.paste(im,mask=im.getchannel('A'));return out
coverage=[]
for s in (128,256,84):
 for ground,bg in G.items():
  cell=s+6;rh=s+24;pw=2*s+16
  out=Image.new('RGB',(4*pw+24,40+4*(3*rh+30)),(50,52,56));dr=ImageDraw.Draw(out)
  dr.text((12,8),f'Bound seam follow-up inputs | {s}px NEAREST | {ground} {bg} | all cels + explicit cyclic pairs',font=F,fill='white')
  for ci,(v,d) in enumerate(C):
   top=36+ci*(3*rh+30);dr.text((12,top),f'{v} {d} | fixed native stage; A is the frozen prior control',font=F,fill='white');y=top+23
   for i in range(8):
    x=12+i*cell;out.paste(cel(v,d,i,s,bg),(x,y+18));dr.text((x,y),f'{i:02d}',font=S,fill='white')
   for i in range(8):
    j=(i+1)%8;x=12+(i%4)*pw;py=y+rh+(i//4)*rh
    dr.text((x,py),f'{v} {d[:2].upper()} {i:02d}->{j:02d}'+(' WRAP' if j==0 else ''),font=S,fill='white')
    out.paste(cel(v,d,i,s,bg),(x,py+18));out.paste(cel(v,d,j,s,bg),(x+s+8,py+18))
    coverage.append({'variant':v,'direction':d,'from':i,'to':j,'size':s,'ground':ground,'sheet':f'coverage-{s}-{ground}.png','left_origin':[x,py+18],'right_origin':[x+s+8,py+18]})
  out.save(O/f'coverage-{s}-{ground}.png')
# Actual anatomical context at 2x; no overlays obscure the edited pixels.
out=Image.new('RGB',(1000,590),(50,52,56));dr=ImageDraw.Draw(out)
dr.text((12,8),'Actual seam-area crops | NEAREST 2x | source x34..93,y62..99 | A then B | no pixel overlays',font=F,fill='white')
for row,(d,i) in enumerate((('southeast',2),('southeast',6),('southwest',2),('southwest',6))):
 y=38+row*135
 dr.text((12,y),f'{d.upper()} {i:02d} | '+('02 changed at SE(50,83..84), SW(78,83..84)' if i==2 else '06 changed at SE(80,79..80), SW(48,79..80); opposite clearance remains open'),font=S,fill='white')
 for col,(g,bg) in enumerate(G.items()):
  x=12+col*326;dr.text((x,y+20),g+' : A                             B',font=S,fill='white')
  for vi,v in enumerate(('A','B')):
   im=cel(v,d,i,128,bg).crop((34,62,94,100)).resize((120,76),Image.Resampling.NEAREST)
   out.paste(im,(x+vi*150,y+40))
   dr.text((x+vi*150,y+118),'x34                    x93',font=S,fill='white')
out.save(O/'seam-anatomy-2x.png')
(O/'coverage.json').write_text(json.dumps({'unique_animation_cels':32,'unique_cyclic_pairs':32,'sizes':[128,256,84],'grounds':G,'pairs':coverage},indent=2)+'\n')
