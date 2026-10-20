from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path('/home/astra/artifacts/emberwake-brann-three-pose-review-v1')
INP=ROOT/'input';OUT=ROOT/'review'
FONT=ImageFont.load_default()
BGS={'light':(228,226,214,255),'dark':(25,29,37,255),'ground':(99,111,80,255)}
def tile(im,size,bg,resample=Image.Resampling.NEAREST):
 back=Image.new('RGBA',(128,128),BGS[bg])
 if bg=='ground':
  d=ImageDraw.Draw(back)
  for y in range(80,128,8): d.line((0,y,127,y),fill=(106,118,88,255))
  for x in range(0,128,16): d.line((x,80,x,127),fill=(106,118,88,255))
 back.alpha_composite(im)
 return back.resize((size,size),resample).convert('RGB')
for v in ['A','B']:
 for direction in ['southeast','southwest']:
  ims=[Image.open(INP/v/direction/f'{i:02}.png').convert('RGBA') for i in range(8)]
  specs=[(128,bg,Image.Resampling.NEAREST,'native128') for bg in BGS]+[(84,bg,Image.Resampling.NEAREST,'proxy84-nearest') for bg in BGS]+[(84,'ground',Image.Resampling.BILINEAR,'proxy84-bilinear')]
  sheet=Image.new('RGB',(8*138+16,sum(s+24 for s,_,_,_ in specs)+30),(52,55,61));d=ImageDraw.Draw(sheet)
  d.text((8,6),f'{v} {direction}: chronological 00..07; 128 canvas / 84 proxy. Ground is diagnostic only.',font=FONT,fill='white')
  y=30
  for size,bg,resample,label in specs:
   for i,im in enumerate(ims):
    x=8+i*138
    d.text((x,y),f'{i:02} {label} {bg}',font=FONT,fill='white')
    sheet.paste(tile(im,size,bg,resample),(x,y+18))
   y+=size+24
  sheet.save(OUT/f'{v}-{direction}-native-proxy.png')
  for bg in BGS:
   sh=Image.new('RGB',(4*266+16,2*280+32),(52,55,61));dr=ImageDraw.Draw(sh)
   dr.text((8,6),f'{v} {direction} nearest 2x / {bg}',font=FONT,fill='white')
   for i,im in enumerate(ims):
    x=8+(i%4)*266;y=30+(i//4)*280
    dr.text((x,y),f'{i:02}',font=FONT,fill='white')
    sh.paste(tile(im,256,bg),(x,y+16))
   sh.save(OUT/f'{v}-{direction}-2x-{bg}.png')
  sh=Image.new('RGB',(2*354+16,4*140+28),(52,55,61));dr=ImageDraw.Draw(sh)
  dr.text((8,6),f'{v} {direction}: all eight cyclic pairs, crop x24..106 y70..124, nearest2x',font=FONT,fill='white')
  for i in range(8):
   j=(i+1)%8;x=8+(i%2)*354;y=28+(i//2)*140
   dr.text((x,y),f'{i:02} -> {j:02}',font=FONT,fill='white')
   for k,idx in enumerate([i,j]):
    t=tile(ims[idx],128,'ground').crop((24,70,106,124)).resize((164,108),Image.Resampling.NEAREST)
    sh.paste(t,(x+k*170,y+18))
  sh.save(OUT/f'{v}-{direction}-cyclic-feet-pairs.png')
# Context only for face, palette, kit, facing and turn continuity; never cycle comparator.
context=[p for p in sorted((INP/'context').glob('*.png')) if p.name!='appearance.png']
sh=Image.new('RGB',(10*138+16,3*150+28),(52,55,61));dr=ImageDraw.Draw(sh)
dr.text((8,6),'CARDINAL CONTEXT ONLY: identity and turn orientation',font=FONT,fill='white')
for i,p in enumerate(context):
 x=8+(i%10)*138;y=28+(i//10)*150
 dr.text((x,y),p.stem,font=FONT,fill='white')
 sh.paste(tile(Image.open(p).convert('RGBA'),128,'light'),(x,y+18))
sh.save(OUT/'context-identity-turn.png')
print('Built 21 bounded diagnostic sheets from nominated images only.')
