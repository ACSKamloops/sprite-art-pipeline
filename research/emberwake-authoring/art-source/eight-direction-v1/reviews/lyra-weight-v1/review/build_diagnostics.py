from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path('/home/astra/artifacts/emberwake-lyra-weight-review-v1/review');I=R.parent/'input';M=json.loads((I/'INPUTS.json').read_text());NN=Image.Resampling.NEAREST
COL={'light':(231,229,219,255),'dark':(24,29,39,255),'muted':(104,113,83,255)}
def im(v,d,n):return Image.open(I/f'{v}/{d}/{n:02}.png').convert('RGBA')
def bg(a,k):
 b=Image.new('RGBA',a.size,COL[k]);b.alpha_composite(a);return b.convert('RGB')
def text(d,x,y,s):d.text((x,y),s,fill=(240,240,240))
for v in ['A','B']:
 for d in ['southeast','southwest']:
  o=Image.new('RGB',(1100,810),(47,51,58));p=ImageDraw.Draw(o);text(p,8,6,f'{v} {d} STATIC native128 /84NN light/dark/muted')
  for r,(size,k) in enumerate([(128,'light'),(128,'dark'),(128,'muted'),(84,'light'),(84,'dark'),(84,'muted')]):
   y=30+r*128;text(p,4,y,f'{size}/{k}')
   for n in range(8):
    x=66+n*129;text(p,x,y,f'{n:02}');o.paste(bg(im(v,d,n).resize((size,size),NN),k),(x,y+16))
  o.save(R/f'{v}-{d}-native84.png')
  for k in COL:
   o=Image.new('RGB',(1072,594),(47,51,58));p=ImageDraw.Draw(o);text(p,8,6,f'{v} {d} nearest2x/{k} STATIC56.25ms exposures')
   for n in range(8):
    x=8+n%4*266;y=30+n//4*282;text(p,x,y,f'{n:02}');o.paste(bg(im(v,d,n).resize((256,256),NN),k),(x,y+16))
   o.save(R/f'{v}-{d}-2x-{k}.png')
  o=Image.new('RGB',(552,630),(47,51,58));p=ImageDraw.Draw(o);text(p,8,6,f'{v} {d} all8cyclicpairs STATIC native')
  for n in range(8):
   x=8+n%2*274;y=30+n//2*150;text(p,x,y,f'{n:02}->{(n+1)%8:02}')
   for j,z in enumerate([n,(n+1)%8]):o.paste(bg(im(v,d,z),'light'),(x+j*132,y+16))
  o.save(R/f'{v}-{d}-cyclic-pairs.png')
for d in ['southeast','southwest']:
 o=Image.new('RGB',(1208,690),(47,51,58));p=ImageDraw.Draw(o);text(p,8,6,f'{d} hip/knee/cuff/boot crops (28,68)-(100,116),nearest2x')
 for row,(v,k) in enumerate([(v,k) for v in ['A','B'] for k in ['light','dark','alpha']]):
  y=30+row*110
  for n in range(8):
   x=8+n*150;text(p,x,y,f'{v}{n:02} {k}');a=im(v,d,n).crop((28,68,100,116));a=a.getchannel('A').convert('RGB') if k=='alpha' else bg(a,k);o.paste(a.resize((144,96),NN),(x,y+16))
 o.save(R/f'{d}-joints-alpha.png')
ctx=[x for x in M['context'] if x['path']!='context/appearance.png'];o=Image.new('RGB',(1392,488),(47,51,58));p=ImageDraw.Draw(o);text(p,8,6,'CARDINAL CONTEXT identity/facing only')
for n,x in enumerate(ctx):
 xx=8+n%10*138;yy=30+n//10*150;text(p,xx,yy,Path(x['path']).stem);o.paste(bg(Image.open(I/x['path']).convert('RGBA'),'light'),(xx,yy+16))
o.save(R/'context-identity-turn.png');print('diagnostic_pngs',len(list(R.glob('*.png'))))
