from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path('/home/astra/artifacts/emberwake-lyra-se03-spur-review-v1/review'); I=R.parent/'input'
M=json.loads((I/'INPUTS.json').read_text())
NN=Image.Resampling.NEAREST
BG={'light':(231,229,219,255),'dark':(24,29,39,255)}
def sprite(v,d,n):return Image.open(I/f'{v}/{d}/{n:02}.png').convert('RGBA')
def comp(im,bg):
 out=Image.new('RGBA',im.size,BG[bg]);out.alpha_composite(im);return out.convert('RGB')
def label(d,xy,s):d.text(xy,s,fill=(240,240,240))
for v in ['A','B']:
 for direction in ['southeast','southwest']:
  out=Image.new('RGB',(1100,550),(47,51,58));draw=ImageDraw.Draw(out)
  label(draw,(8,6),f'{v} {direction}: STATIC chronology, native128 and84NN, light/dark')
  for row,(size,bg) in enumerate([(128,'light'),(128,'dark'),(84,'light'),(84,'dark')]):
   y=30+row*128
   label(draw,(5,y),f'{size}/{bg}')
   for n in range(8):
    x=66+n*129;label(draw,(x,y),f'{n:02}')
    im=sprite(v,direction,n).resize((size,size),NN);out.paste(comp(im,bg),(x,y+16))
  out.save(R/f'{v}-{direction}-native84.png')
  for bg in BG:
   out=Image.new('RGB',(1072,594),(47,51,58));draw=ImageDraw.Draw(out)
   label(draw,(8,6),f'{v} {direction}: nearest2x/{bg}, STATIC,56.25ms each')
   for n in range(8):
    x=8+(n%4)*266;y=30+(n//4)*282
    label(draw,(x,y),f'{n:02}');out.paste(comp(sprite(v,direction,n).resize((256,256),NN),bg),(x,y+16))
   out.save(R/f'{v}-{direction}-2x-{bg}.png')
  out=Image.new('RGB',(920,654),(47,51,58));draw=ImageDraw.Draw(out)
  label(draw,(8,6),f'{v} {direction}: all8 cyclic pairs, torso/hand/leg nearest2x STATIC')
  for n in range(8):
   x=8+(n%2)*456;y=30+(n//2)*154
   label(draw,(x,y),f'{n:02}->{(n+1)%8:02}')
   for j,k in enumerate([n,(n+1)%8]):
    im=sprite(v,direction,k).crop((20,54,108,120)).resize((176,132),NN)
    out.paste(comp(im,'light'),(x+j*184,y+16))
  out.save(R/f'{v}-{direction}-cyclic-pairs.png')
for direction,box in [('southeast',(34,67,68,102)),('southwest',(60,67,94,102))]:
 out=Image.new('RGB',(880,710),(47,51,58));draw=ImageDraw.Draw(out)
 label(draw,(8,6),f'{direction} changed edge: crop{box},nearest6x;02/A03/B03/04')
 for row,bg in enumerate(['light','dark','alpha']):
  y=30+row*226
  for col,(v,n) in enumerate([('A',2),('A',3),('B',3),('A',4)]):
   x=8+col*218;label(draw,(x,y),f'{v}{n:02} {bg}')
   im=sprite(v,direction,n).crop(box)
   if bg=='alpha':im=im.getchannel('A').convert('RGB')
   else:im=comp(im,bg)
   out.paste(im.resize((204,210),NN),(x,y+16))
 out.save(R/f'{direction}-edge-neighbors-detail.png')
ctx=[x for x in M['context'] if x['path']!='context/appearance.png']
out=Image.new('RGB',(1392,488),(47,51,58));draw=ImageDraw.Draw(out)
label(draw,(8,6),'CARDINAL CONTEXT: identity/facing only')
for i,x in enumerate(ctx):
 col=i%10;row=i//10;xx=8+col*138;yy=30+row*150
 label(draw,(xx,yy),Path(x['path']).stem);out.paste(comp(Image.open(I/x['path']).convert('RGBA'),'light'),(xx,yy+16))
out.save(R/'context-identity-turn.png')
print('diagnostic_pngs',len(list(R.glob('*.png'))))
