from pathlib import Path
from PIL import Image,ImageDraw
import json
BASE=Path(__file__).resolve().parent
im=Image.open(BASE/'inputs/brann/atlas.png').convert('RGBA')
def cel(frame):return im.crop((frame%8*128,frame//8*128,frame%8*128+128,frame//8*128+128))
original=cel(112);donor=cel(121);result=original.copy();witness=[]
# Preserve the existing raised/far foot contour, cuff and upper seam exactly.
# Only its already opaque distal leather receives same-role donor detail.
for ty in range(102,108):
 for tx in range(50,64):
  sx,sy=tx-4,ty-3
  if original.getpixel((tx,ty))[3]==255 and donor.getpixel((sx,sy))[3]==255:
   result.putpixel((tx,ty),donor.getpixel((sx,sy)));witness.append([tx,ty,121,sx,sy,'far-distal-material'])
# The foreground support shoe may recover one contour pixel at each side;
# no pixel below its current sole row is touched.
for ty in range(101,111):
 for tx in range(63,81):
  sx,sy=tx,ty+1
  result.putpixel((tx,ty),donor.getpixel((sx,sy)));witness.append([tx,ty,121,sx,sy,'support-toe-heel'])
result.save(BASE/'brann-south-first-sample-f112-refined.png')
sheet=Image.new('RGBA',(3*256,518),(24,42,47,255));d=ImageDraw.Draw(sheet)
for i,(c,label) in enumerate([(donor,'f121 preceding source'),(original,'f112 current'),(result,'f112 bounded toe variant')]):
 sheet.alpha_composite(c.resize((256,256),Image.Resampling.NEAREST),(i*256,26));d.text((i*256+5,5),label,fill='white')
 sheet.alpha_composite(c.crop((44,88,84,116)).resize((240,168),Image.Resampling.NEAREST),(i*256+8,292));d.text((i*256+5,476),'Same128px canvas; no fit',fill='white')
sheet.convert('RGB').save(BASE/'brann-first-paired-sample-refined.png')
(BASE/'first-sample-plan-refined.json').write_text(json.dumps({'status':'First bounded sample, root review before expansion','source':121,'target':112,'witness':witness},indent=2)+'\n')
print('paired sample refined')
