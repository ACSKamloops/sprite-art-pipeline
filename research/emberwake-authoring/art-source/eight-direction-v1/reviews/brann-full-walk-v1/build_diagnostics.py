from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json,hashlib,math
root=Path(__file__).resolve().parent
src=root.parent/'input-v1'
data=json.loads((src/'INPUTS.json').read_text())
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
entries=[]
def collect(o):
 if isinstance(o,dict):
  if 'path' in o and 'sha256' in o: entries.append(o)
  else:
   for v in o.values():collect(v)
 elif isinstance(o,list):
  for v in o:collect(v)
collect(data)
checks=[]
for x in entries:
 p=src/x['path']; actual=hashlib.sha256(p.read_bytes()).hexdigest()
 im=Image.open(p)
 checks.append(dict(path=x['path'],expected=x['sha256'],actual=actual,match=actual==x['sha256'],size=list(im.size),mode=im.mode))
(root/'input-verification.json').write_text(json.dumps({'listed_count':len(checks),'all_match':all(x['match'] for x in checks),'files':checks},indent=2)+'\n')
assert all(x['match'] for x in checks)
print('Verified',len(checks),'listed PNG hashes')
print('Diagonal size/mode:',sorted({(tuple(x['size']),x['mode']) for x in checks if any('/'+d+'/' in x['path'] for d in data['actors']['brann']['diagonals'])}))
(root/'diagnostics').mkdir(exist_ok=True)
bgs={'light':(230,228,217),'dark':(27,30,39),'ground':(94,96,63)}
scales={'native':128,'nearest2x':256,'game066':84}
def tile(path,size,bg):
 im=Image.open(src/path).convert('RGBA').resize((size,size),Image.Resampling.NEAREST)
 out=Image.new('RGB',(size,size),bg);out.paste(im,(0,0),im);return out
for direction,frames in data['actors']['brann']['diagonals'].items():
 for scale,size in scales.items():
  pad=8; head=42; label=22; cell=size+pad; row=size+label+pad
  sheet=Image.new('RGB',(8*cell+pad,head+3*row+pad),(245,245,245));dr=ImageDraw.Draw(sheet)
  dr.text((8,8),f'{direction} | {scale} | all keys | backgrounds: light / dark / ground',font=font,fill='black')
  for j,(bgname,bg) in enumerate(bgs.items()):
   for i,x in enumerate(frames):
    xx=pad+i*cell;yy=head+j*row
    sheet.paste(tile(x['path'],size,bg),(xx,yy))
    dr.text((xx,yy+size+2),f'{i:02d} {bgname}',font=small,fill='black')
  sheet.save(root/'diagnostics'/f'keys-{direction}-{scale}.png')
  # Every cyclic pair appears once for each of the three backgrounds.
  pairw=2*size+6; pairh=size+label; gap=10
  sheet=Image.new('RGB',(4*(pairw+gap)+gap,head+6*(pairh+gap)+gap),(245,245,245));dr=ImageDraw.Draw(sheet)
  dr.text((8,8),f'{direction} | {scale} | cyclic pairs incl 07 > 00 | each background',font=font,fill='black')
  for j,(bgname,bg) in enumerate(bgs.items()):
   for i in range(8):
    xx=gap+(i%4)*(pairw+gap);yy=head+(j*2+i//4)*(pairh+gap)
    sheet.paste(tile(frames[i]['path'],size,bg),(xx,yy))
    sheet.paste(tile(frames[(i+1)%8]['path'],size,bg),(xx+size+6,yy))
    dr.text((xx,yy+size+2),f'{i:02d} > {(i+1)%8:02d} | {bgname}',font=small,fill='black')
  sheet.save(root/'diagnostics'/f'pairs-{direction}-{scale}.png')
# Identity and turn context: all cardinal keys and idles, no scoring of these loops.
card=data['actors']['brann']['cardinal_context']
size=128;cell=140;row=156;head=40
sheet=Image.new('RGB',(10*cell+8,4*row+head+8),(245,245,245));dr=ImageDraw.Draw(sheet)
dr.text((8,8),'Cardinal context only | walk keys 00-07, idle keys 00-01 | ground',font=font,fill='black')
for j,(direction,sets) in enumerate(card.items()):
 seq=sets['walk']+sets['idle']
 for i,x in enumerate(seq):
  xx=8+i*cell;yy=head+j*row
  sheet.paste(tile(x['path'],size,bgs['ground']),(xx,yy))
  dr.text((xx,yy+size+2),f'{direction} '+('walk ' if i<8 else 'idle ')+f'{i if i<8 else i-8:02d}',font=small,fill='black')
sheet.save(root/'diagnostics'/'cardinal-context-native.png')
# Native coordinate rulers for exact region descriptions.
for direction,frames in data['actors']['brann']['diagonals'].items():
 size=256;pad=24;cell=size+pad;head=42
 sheet=Image.new('RGB',(8*cell+pad,size+head+34),(245,245,245));dr=ImageDraw.Draw(sheet)
 dr.text((8,8),f'{direction} | key coordinates native x/y | 2x nearest',font=font,fill='black')
 for i,x in enumerate(frames):
  xx=pad+i*cell;yy=head
  sheet.paste(tile(x['path'],size,bgs['light']),(xx,yy))
  for c in range(0,129,16):
   dx=xx+c*2;dy=yy+c*2
   dr.line((dx,yy-3,dx,yy),fill='black');dr.text((dx,yy-17),str(c),font=small,fill='black')
   if i==0:dr.text((xx-23,dy-6),str(c),font=small,fill='black')
  dr.text((xx,yy+size+5),f'key {i:02d}',font=font,fill='black')
 sheet.save(root/'diagnostics'/f'coordinates-{direction}.png')
print('Created 29 diagnostic sheets')
