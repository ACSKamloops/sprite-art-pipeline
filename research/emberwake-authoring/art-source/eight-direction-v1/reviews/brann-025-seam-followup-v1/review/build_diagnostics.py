from pathlib import Path
from PIL import Image,ImageDraw
from fractions import Fraction
import json,math
ROOT=Path('/home/astra/artifacts/emberwake-brann-025-seam-followup-review-v1');INP=ROOT/'input';OUT=ROOT/'review';M=json.loads((INP/'INPUTS.json').read_text());BGS={'light':(231,228,218,255),'dark':(25,29,38,255),'ground':(103,114,86,255)}
def tile(im,s,bg,method=Image.Resampling.NEAREST):
 back=Image.new('RGBA',(128,128),BGS[bg])
 if bg=='ground':
  d=ImageDraw.Draw(back)
  for y in range(80,128,8):d.line((0,y,127,y),fill=(111,122,94,255))
  for x in range(0,128,16):d.line((x,80,x,127),fill=(111,122,94,255))
 back.alpha_composite(im);return back.resize((s,s),method).convert('RGB')
def key(v,i):return ('mid02.5' if i==3 else f'old{i if i<3 else i-1:02}') if v=='B' else f'old{i:02}'
for v in ['A','B']:
 hs=[float(Fraction(*h)*1000) for h in M.get('variant_holds',{}).get(v,M['holds'])]
 for dr in ['southeast','southwest']:
  ims=[Image.open(INP/e['path']).convert('RGBA') for e in M['variants'][v][dr]];n=len(ims);specs=[(128,b,Image.Resampling.NEAREST,'128') for b in BGS]+[(84,b,Image.Resampling.NEAREST,'84NN') for b in BGS]+[(84,'ground',Image.Resampling.BILINEAR,'84bilinear')]
  sh=Image.new('RGB',(n*146+16,sum(s+38 for s,_,_,_ in specs)+30),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr} STATIC chronology with actual holds; no timed human perception',fill='white');y=30
  for s,bg,method,label in specs:
   for i,im in enumerate(ims):
    x=8+i*146;d.text((x,y),f'{i:02} {key(v,i)} {label} {bg}',fill='white');d.text((x,y+13),f'{hs[i]:g}ms',fill='white');sh.paste(tile(im,s,bg,method),(x,y+30))
   y+=s+38
  sh.save(OUT/f'{v}-{dr}-native-proxy.png');cols=4 if n==8 else 3;rows=math.ceil(n/cols)
  for bg in BGS:
   sh=Image.new('RGB',(cols*266+16,rows*290+32),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr} nearest2x/{bg}, STATIC actual holds labeled',fill='white')
   for i,im in enumerate(ims):
    x=8+i%cols*266;y=30+i//cols*290;d.text((x,y),f'{i:02} {key(v,i)} {hs[i]:g}ms',fill='white');sh.paste(tile(im,256,bg),(x,y+20))
   sh.save(OUT/f'{v}-{dr}-2x-{bg}.png')
  cols=2 if n==8 else 3;rows=math.ceil(n/cols);sh=Image.new('RGB',(cols*354+16,rows*140+28),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{v} {dr}: all{n} cyclic pairs lower nearest2x STATIC',fill='white')
  for i in range(n):
   j=(i+1)%n;x=8+i%cols*354;y=28+i//cols*140;d.text((x,y),f'{i:02}({key(v,i)})->{j:02}({key(v,j)})',fill='white')
   for k,idx in enumerate([i,j]):sh.paste(tile(ims[idx],128,'ground').crop((24,70,106,124)).resize((164,108),Image.Resampling.NEAREST),(x+k*170,y+18))
  sh.save(OUT/f'{v}-{dr}-cyclic-pairs.png')
for dr in ['southeast','southwest']:
 cells=[('A',2),('A',3),('B',2),('B',3),('B',4)];sh=Image.new('RGB',(936,610),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{dr}: A02/03 vs B02/repairedmid/old03, nearest3x lower; actual holds labeled',fill='white')
 for r,bg in enumerate(BGS):
  for c,(v,i) in enumerate(cells):
   x=8+c*184;y=30+r*190;h=float(Fraction(*M.get('variant_holds',{}).get(v,M['holds'])[i])*1000);d.text((x,y),f'{v}{i:02} {key(v,i)} {h:g}ms',fill='white');im=Image.open(INP/v/dr/f'{i:02}.png').convert('RGBA');sh.paste(tile(im,128,bg).crop((40,78,96,122)).resize((168,132),Image.Resampling.NEAREST),(x,y+18))
 sh.save(OUT/f'{dr}-02-mid-03-recovery-detail.png');sh=Image.new('RGB',(874,700),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),f'{dr}: A02 / repairedmid / A03; volume+alpha nearest5x x40..94 y80..118',fill='white')
 for r,mode in enumerate(['light','dark','alpha']):
  for c,(v,i) in enumerate([('A',2),('B',3),('A',3)]):
   im=Image.open(INP/v/dr/f'{i:02}.png').convert('RGBA');crop=im.crop((40,80,94,118));x=8+c*286;y=30+r*220;d.text((x,y),f'{v}{i:02} {key(v,i)} {mode}',fill='white')
   if mode=='alpha':
    a=crop.getchannel('A');pic=Image.merge('RGB',(a,a,a))
   else:
    back=Image.new('RGBA',crop.size,BGS[mode]);back.alpha_composite(crop);pic=back.convert('RGB')
   sh.paste(pic.resize((270,190),Image.Resampling.NEAREST),(x,y+18))
 sh.save(OUT/f'{dr}-repairedmid-volume-alpha-check.png')
context=[p for p in sorted((INP/'context').glob('*.png')) if p.name!='appearance.png'];sh=Image.new('RGB',(1396,478),(50,54,61));d=ImageDraw.Draw(sh);d.text((8,6),'CARDINAL CONTEXT identity/facing only',fill='white')
for i,p in enumerate(context):
 x=8+i%10*138;y=28+i//10*150;d.text((x,y),p.stem,fill='white');sh.paste(tile(Image.open(p).convert('RGBA'),128,'light'),(x,y+18))
sh.save(OUT/'context-identity-turn.png');print('25 bounded diagnostic PNGs created from current inputs only.')
