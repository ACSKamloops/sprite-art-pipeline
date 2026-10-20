from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,hashlib
S=Path('/home/astra/artifacts/emberwake-brann-ne-jab-fist-v1/action-review/input');O=Path(__file__).parent;D=O/'proofs';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(S.rglob('*.png'))+[S/'INPUTS.json'];ledger=[{'path':str(p.relative_to(S)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files];(O/'input-before.json').write_text(json.dumps(ledger,indent=2)+'\n')
m=json.loads((S/'INPUTS.json').read_text());expected=[e for byview in m['variants'].values() for entries in byview.values() for e in entries]+m['context'];assert len(expected)==57 and len(files)==58;assert all(sha(S/e['path'])==e['sha256'] for e in expected)
clips=[(v,d) for v in ('A','B') for d in ('northeast','northwest')];bgmap={'light':'#e7e3d6','dark':'#22252b','game':'#27392f'};font=ImageFont.load_default()
def stage(path,n,bg):
 im=Image.open(S/path).convert('RGBA');assert im.size==(128,128)
 return Image.alpha_composite(Image.new('RGBA',(n,n),bg),im.resize((n,n),Image.Resampling.NEAREST)).convert('RGB')
for n in (128,256,84):
 for ground,bg in bgmap.items():
  fg='#151515' if ground=='light' else '#eee9df';cw=n+8;rh=n+26
  sheet=Image.new('RGB',(8*cw+8,4*rh+30),bg);dr=ImageDraw.Draw(sheet);dr.text((8,5),f'Complete A/B NE/NW action | {n}px whole canvas NEAREST | {ground} | nonloop .41s',fill=fg,font=font)
  for row,(v,d) in enumerate(clips):
   code='NE' if d=='northeast' else 'NW'
   for f in range(8):
    x=8+f*cw;y=30+row*rh;dr.text((x,y),f'{v} {code} {f:02}',fill=fg,font=font);sheet.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+18))
  sheet.save(D/f'cels-{n}-{ground}.png')
  pcw=2*n+24;pairs=Image.new('RGB',(4*pcw+8,8*rh+30),bg);dr=ImageDraw.Draw(pairs);dr.text((8,5),f'28 within-action pairs + 4 neutral-entry pairs | {n}px | {ground} | 07->00 is ENTRY, not autoloop',fill=fg,font=font)
  for k,(v,d) in enumerate(clips):
   code='NE' if d=='northeast' else 'NW'
   for f in range(8):
    g=f+1 if f<7 else 0;row=k*2+f//4;col=f%4;x=8+col*pcw;y=30+row*rh
    label=f'{v} {code} {f:02}->{g:02}'+(' ENTRY' if f==7 else '')
    dr.text((x,y),label,fill=fg,font=font);pairs.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+18));pairs.paste(stage(f'{v}/{d}/{g:02}.png',n,bg),(x+n+8,y+18))
  pairs.save(D/f'pairs-{n}-{ground}.png')
  focused=Image.new('RGB',(3*cw+8,4*rh+30),bg);dr=ImageDraw.Draw(focused);dr.text((8,5),f'02 -> 03 -> 04 | {n}px | {ground}',fill=fg,font=font)
  for row,(v,d) in enumerate(clips):
   code='NE' if d=='northeast' else 'NW'
   for col,f in enumerate((2,3,4)):
    x=8+col*cw;y=30+row*rh;dr.text((x,y),f'{v} {code} {f:02}',fill=fg,font=font);focused.paste(stage(f'{v}/{d}/{f:02}.png',n,bg),(x,y+18))
  focused.save(D/f'hand-{n}-{ground}.png')
for n,ground in ((256,'light'),(84,'light'),(84,'dark'),(84,'game')):
 bg=bgmap[ground];fg='#151515' if ground=='light' else '#eee9df';cw=n+8;rh=n+26
 entries=[e['path'] for e in m['context'] if e['path']!='context/appearance.png'];assert len(entries)==24
 sheet=Image.new('RGB',(8*cw+8,3*rh+30),bg);dr=ImageDraw.Draw(sheet);dr.text((8,5),f'Cardinal action context only | {n}px | {ground}',fill=fg,font=font)
 for i,path in enumerate(entries):
  x=8+i%8*cw;y=30+i//8*rh;dr.text((x,y),Path(path).stem,fill=fg,font=font);sheet.paste(stage(path,n,bg),(x,y+18))
 sheet.save(D/f'context-{n}-{ground}.png')
differences=[]
for d in ('northeast','northwest'):
 for f in range(8):
  a=Image.open(S/f'A/{d}/{f:02}.png').convert('RGBA');b=Image.open(S/f'B/{d}/{f:02}.png').convert('RGBA');diff=ImageChops.difference(a,b);mask=diff.getchannel('R')
  for channel in ('G','B','A'):mask=ImageChops.lighter(mask,diff.getchannel(channel))
  differences.append({'direction':d,'frame':f,'bbox_exclusive':mask.getbbox(),'changed_pixels':sum(v!=0 for v in mask.get_flattened_data())})
(O/'differences.json').write_text(json.dumps(differences,indent=2)+'\n')
print(json.dumps({'pngs':len(expected),'manifest_sha256':sha(S/'INPUTS.json'),'different_cels':[r for r in differences if r['changed_pixels']],'proofs':len(list(D.glob('*.png')))},indent=2))
