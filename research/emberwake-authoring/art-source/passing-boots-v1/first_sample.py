from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
BASE=Path(__file__).resolve().parent
im=Image.open(BASE/'inputs/brann/atlas.png').convert('RGBA')
def cel(frame):return im.crop((frame%8*128,frame//8*128,frame%8*128+128,frame//8*128+128))
original=cel(112);donor=cel(121);result=original.copy()
# One toe/heel material variant, two foreground-ordered literal source copies.
# Explicit rows own only far toe band then foreground support toe/ankle band.
ops=[{'part':'screen-left lifted foot, far first','dx':4,'dy':3,'rows':[[y,49,64] for y in range(100,108)]},
     {'part':'screen-right support toe and heel, foreground second','dx':0,'dy':-1,'rows':[[y,63,81] for y in range(101,111)]}]
witness=[]
for op in ops:
 for ty,x0,x1 in op['rows']:
  for tx in range(x0,x1):
   sx,sy=tx-op['dx'],ty-op['dy'];rgba=donor.getpixel((sx,sy));result.putpixel((tx,ty),rgba);witness.append([tx,ty,121,sx,sy])
result.save(BASE/'brann-south-first-sample-f112.png')
sheet=Image.new('RGBA',(3*256,518),(24,42,47,255));d=ImageDraw.Draw(sheet)
for i,(c,label) in enumerate([(donor,'f121 preceding source'),(original,'f112 current'),(result,'f112 toe+heel variant')]):
 sheet.alpha_composite(c.resize((256,256),Image.Resampling.NEAREST),(i*256,26));d.text((i*256+5,5),label,fill='white')
 sheet.alpha_composite(c.crop((44,88,84,116)).resize((240,168),Image.Resampling.NEAREST),(i*256+8,292));d.text((i*256+5,476),'Same128px canvas; no fit',fill='white')
sheet.convert('RGB').save(BASE/'brann-first-paired-sample.png')
(BASE/'first-sample-plan.json').write_text(json.dumps({'status':'Exploratory first paired sample, not selected for expansion','source':121,'target':112,'operations':ops,'witness':witness},indent=2)+'\n')
print('first sample',sum(a!=b for a,b in zip(original.tobytes()[::4],result.tobytes()[::4])),'R-channel changed samples')
