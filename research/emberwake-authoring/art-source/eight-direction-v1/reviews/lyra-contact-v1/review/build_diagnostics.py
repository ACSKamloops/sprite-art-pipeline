from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path('/home/astra/artifacts/emberwake-lyra-contact-review-v1');INP=ROOT/'input';OUT=ROOT/'review'
BGS={'light':(231,228,218,255),'dark':(25,29,38,255),'ground':(103,114,86,255)}
def tile(im,size,bg,method=Image.Resampling.NEAREST):
 back=Image.new('RGBA',(128,128),BGS[bg])
 if bg=='ground':
  d=ImageDraw.Draw(back)
  for y in range(80,128,8):d.line((0,y,127,y),fill=(111,122,94,255))
  for x in range(0,128,16):d.line((x,80,x,127),fill=(111,122,94,255))
 back.alpha_composite(im)
 return back.resize((size,size),method).convert('RGB')
for v in ['A','B']:
 for direction in ['southeast','southwest']:
  ims=[Image.open(INP/v/direction/f'{i:02}.png').convert('RGBA') for i in range(8)]
  specs=[(128,bg,Image.Resampling.NEAREST,'native128') for bg in BGS]+[(84,bg,Image.Resampling.NEAREST,'proxy84-NN') for bg in BGS]+[(84,'ground',Image.Resampling.BILINEAR,'proxy84-bilinear')]
  sh=Image.new('RGB',(1120,sum(s+24 for s,_,_,_ in specs)+30),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {direction} native and 0.66-scale proxy. Diagnostic grounds only.',fill='white');y=30
  for size,bg,method,label in specs:
   for i,im in enumerate(ims):
    x=8+i*138;d.text((x,y),f'{i:02} {label} {bg}',fill='white');sh.paste(tile(im,size,bg,method),(x,y+18))
   y+=size+24
  sh.save(OUT/f'{v}-{direction}-native-proxy.png')
  for bg in BGS:
   sh=Image.new('RGB',(1080,592),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {direction} nearest2x / {bg}',fill='white')
   for i,im in enumerate(ims):
    x=8+(i%4)*266;y=30+(i//4)*280;d.text((x,y),f'{i:02}',fill='white');sh.paste(tile(im,256,bg),(x,y+16))
   sh.save(OUT/f'{v}-{direction}-2x-{bg}.png')
  sh=Image.new('RGB',(724,588),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {direction}: all eight cyclic pairs, lower body nearest2x',fill='white')
  for i in range(8):
   j=(i+1)%8;x=8+(i%2)*354;y=28+(i//2)*140;d.text((x,y),f'{i:02} -> {j:02}',fill='white')
   for k,idx in enumerate([i,j]):sh.paste(tile(ims[idx],128,'ground').crop((24,70,106,124)).resize((164,108),Image.Resampling.NEAREST),(x+k*170,y+18))
  sh.save(OUT/f'{v}-{direction}-cyclic-feet-pairs.png')
context=[p for p in sorted((INP/'context').glob('*.png')) if p.name!='appearance.png'];sh=Image.new('RGB',(1396,478),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),'CARDINAL CONTEXT: identity and facing only, not a diagonal gait benchmark',fill='white')
for i,p in enumerate(context):
 x=8+(i%10)*138;y=28+(i//10)*150;d.text((x,y),p.stem,fill='white');sh.paste(tile(Image.open(p).convert('RGBA'),128,'light'),(x,y+18))
sh.save(OUT/'context-identity-turn.png')
print('21 bounded sheets created.')
