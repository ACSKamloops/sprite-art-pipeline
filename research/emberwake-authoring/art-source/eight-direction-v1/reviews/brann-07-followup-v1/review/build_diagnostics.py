from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json
ROOT=Path('/home/astra/artifacts/emberwake-brann-07-followup-review-v1');INP=ROOT/'input';OUT=ROOT/'review';BGS={'light':(231,228,218,255),'dark':(25,29,38,255),'ground':(103,114,86,255)}
def tile(im,size,bg,method=Image.Resampling.NEAREST):
 back=Image.new('RGBA',(128,128),BGS[bg])
 if bg=='ground':
  d=ImageDraw.Draw(back)
  for y in range(80,128,8):d.line((0,y,127,y),fill=(111,122,94,255))
  for x in range(0,128,16):d.line((x,80,x,127),fill=(111,122,94,255))
 back.alpha_composite(im);return back.resize((size,size),method).convert('RGB')
for v in ['A','B']:
 for dr in ['southeast','southwest']:
  ims=[Image.open(INP/v/dr/f'{i:02}.png').convert('RGBA') for i in range(8)];specs=[(128,b,Image.Resampling.NEAREST,'native128') for b in BGS]+[(84,b,Image.Resampling.NEAREST,'proxy84-NN') for b in BGS]+[(84,'ground',Image.Resampling.BILINEAR,'proxy84-bilinear')]
  sh=Image.new('RGB',(1120,sum(s+24 for s,_,_,_ in specs)+30),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr}: native/0.66 proxy, grounds diagnostic only',fill='white');y=30
  for size,bg,method,label in specs:
   for i,im in enumerate(ims):
    x=8+i*138;d.text((x,y),f'{i:02} {label} {bg}',fill='white');sh.paste(tile(im,size,bg,method),(x,y+18))
   y+=size+24
  sh.save(OUT/f'{v}-{dr}-native-proxy.png')
  for bg in BGS:
   sh=Image.new('RGB',(1080,592),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr} nearest2x/{bg}',fill='white')
   for i,im in enumerate(ims):
    x=8+(i%4)*266;y=30+(i//4)*280;d.text((x,y),f'{i:02}',fill='white');sh.paste(tile(im,256,bg),(x,y+16))
   sh.save(OUT/f'{v}-{dr}-2x-{bg}.png')
  sh=Image.new('RGB',(724,588),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr}: all8 cyclic lower pairs nearest2x',fill='white')
  for i in range(8):
   j=(i+1)%8;x=8+(i%2)*354;y=28+(i//2)*140;d.text((x,y),f'{i:02}->{j:02}',fill='white')
   for k,idx in enumerate([i,j]):sh.paste(tile(ims[idx],128,'ground').crop((24,70,106,124)).resize((164,108),Image.Resampling.NEAREST),(x+k*170,y+18))
  sh.save(OUT/f'{v}-{dr}-cyclic-pairs.png')
stats=[];cleanup=[]
for dr in ['southeast','southwest']:
 sh=Image.new('RGB',(1120,610),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{dr}: A06/07/00 and B06/07/00, nearest3x source x40..96 y78..122',fill='white')
 for r,bg in enumerate(BGS):
  for c,(v,i) in enumerate([(v,i) for v in ['A','B'] for i in [6,7,0]]):
   x=8+c*184;y=30+r*190;d.text((x,y),f'{v}{i:02} {bg}',fill='white');im=Image.open(INP/v/dr/f'{i:02}.png').convert('RGBA');sh.paste(tile(im,128,bg).crop((40,78,96,122)).resize((168,132),Image.Resampling.NEAREST),(x,y+18))
 sh.save(OUT/f'{dr}-06-07-00-closure-detail.png')
 sh=Image.new('RGB',(940,520),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{dr}07 joint/volume alpha check nearest5x, source x36..96 y78..122',fill='white')
 for r,v in enumerate(['A','B']):
  im=Image.open(INP/v/dr/'07.png').convert('RGBA');crop=im.crop((36,78,96,122))
  for c,mode in enumerate(['light','dark','alpha']):
   x=8+c*310;y=30+r*244;d.text((x,y),v+'07 '+mode,fill='white')
   if mode=='alpha':
    a=crop.getchannel('A');pic=Image.merge('RGB',(a,a,a))
   else:
    bg=Image.new('RGBA',crop.size,BGS[mode]);bg.alpha_composite(crop);pic=bg.convert('RGB')
   sh.paste(pic.resize((300,220),Image.Resampling.NEAREST),(x,y+18))
 sh.save(OUT/f'{dr}-07-volume-alpha-check.png')
 for i in range(8):
  a=Image.open(INP/'A'/dr/f'{i:02}.png').convert('RGBA');b=Image.open(INP/'B'/dr/f'{i:02}.png').convert('RGBA');ch=ImageChops.difference(a,b).split();mask=ImageChops.lighter(ImageChops.lighter(ch[0],ch[1]),ImageChops.lighter(ch[2],ch[3]));stats.append({'direction':dr,'cel':f'{i:02}','difference_bbox':mask.getbbox(),'different_pixels':sum(v!=0 for v in mask.get_flattened_data())})
  if i==3:
   for y in range(128):
    for x in range(128):
     if a.getpixel((x,y))!=b.getpixel((x,y)):cleanup.append({'direction':dr,'xy':[x,y],'A_rgba':a.getpixel((x,y)),'B_rgba':b.getpixel((x,y))})
(OUT/'pixel-scope.json').write_text(json.dumps(stats,indent=2)+'\n');(OUT/'03-seam-cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\n')
context=[p for p in sorted((INP/'context').glob('*.png')) if p.name!='appearance.png'];sh=Image.new('RGB',(1396,478),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),'CARDINAL CONTEXT: identity/facing only',fill='white')
for i,p in enumerate(context):
 x=8+(i%10)*138;y=28+(i//10)*150;d.text((x,y),p.stem,fill='white');sh.paste(tile(Image.open(p).convert('RGBA'),128,'light'),(x,y+18))
sh.save(OUT/'context-identity-turn.png');print('25 bounded diagnostic sheets created.');print(json.dumps([s for s in stats if s['difference_bbox']],indent=2));print('03 cleanup:',json.dumps(cleanup))
