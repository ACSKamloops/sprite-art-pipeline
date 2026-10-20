from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime,numpy as np
ROOT=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/input');OUT=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/review')
m=json.loads((ROOT/'INPUTS.json').read_text())
entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context']
check=[]
for e in entries:
 im=Image.open(ROOT/e['path']);got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();check.append({**e,'actual_sha256':got,'verified':got==e['sha256'],'size':list(im.size),'mode':im.mode})
assert len(check)==79 and all(e['verified'] for e in check)
(OUT/'input-hashes-before.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':check},indent=2)+'\n')
BG={'light':(232,231,219,255),'dark':(24,30,39,255),'ground':(87,101,70,255)}
def tile(im,size,bg):
 im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST);out=Image.new('RGBA',(size,size),bg);out.alpha_composite(im);return out.convert('RGB')
for scale,size in [('native',128),('nearest2x',256),('proxy84',84)]:
 for bgname,bg in BG.items():
  left=118;rowh=size+25;sheet=Image.new('RGB',(left+8*size+20,32+4*rowh+20),(47,50,55));d=ImageDraw.Draw(sheet);d.text((10,8),f'FOLLOW-UP B/C | {scale} | {bgname} | nearest sampling',(245,245,245));row=0
  for variant in ['B','C']:
   for direction in ['southeast','southwest']:
    y=32+row*rowh;d.text((10,y+size//2),f'{variant} {direction}',(245,245,245))
    for i in range(8):
     im=Image.open(ROOT/f'{variant}/{direction}/{i:02}.png');sheet.paste(tile(im,size,bg),(left+i*size,y));d.text((left+i*size+4,y+size+5),f'{i:02}',(245,245,245))
    row+=1
  sheet.save(OUT/f'sheet-{scale}-{bgname}.png')
# Whole-body and lower-body source-bound A/B comparison: only the two actually changed cels.
for cropname,crop,mult in [('whole',(0,0,128,128),2),('legs',(32,70,96,118),4)]:
 w=(crop[2]-crop[0])*mult;h=(crop[3]-crop[1])*mult;sheet=Image.new('RGB',(4*w+40,2*(h+32)+30),(47,50,55));d=ImageDraw.Draw(sheet)
 for row,direction in enumerate(['southeast','southwest']):
  for col,(v,k) in enumerate([('A','03'),('B','03'),('A','07'),('B','07')]):
   im=Image.open(ROOT/f'{v}/{direction}/{k}.png').convert('RGBA').crop(crop).resize((w,h),Image.Resampling.NEAREST);t=Image.new('RGBA',(w,h),BG['light']);t.alpha_composite(im);x=10+col*(w+6);y=10+row*(h+32);d.text((x,y),f'{v} {direction} {k}',(245,245,245));sheet.paste(t.convert('RGB'),(x,y+20))
 sheet.save(OUT/f'compare-A-B-{cropname}.png')
metrics={}
for variant in ['B','C']:
 for direction in ['southeast','southwest']:
  ims=[Image.open(ROOT/f'{variant}/{direction}/{i:02}.png').convert('RGBA') for i in range(8)];sheet=Image.new('RGB',(1096,932),(47,50,55));d=ImageDraw.Draw(sheet);d.text((12,8),f'{variant} {direction}: all cyclic pairs; crop x32..95 y70..117 nearest4x; ground',(245,245,245));seq=[]
  for i in range(8):
   j=(i+1)%8;x=12+(i%2)*544;y=32+(i//2)*224;d.text((x,y),f'{i:02} -> {j:02}',(245,245,245))
   for k,idx in enumerate([i,j]):
    im=ims[idx].crop((32,70,96,118)).resize((256,192),Image.Resampling.NEAREST);t=Image.new('RGBA',im.size,BG['ground']);t.alpha_composite(im);sheet.paste(t.convert('RGB'),(x+k*264,y+18))
   a=np.array(ims[i]);b=np.array(ims[j]);mask=np.any(a!=b,axis=2);seq.append({'pair':f'{i:02}->{j:02}','raw_rgba_changed_pixels':int(mask.sum()),'exact_duplicate':bool(not mask.any())})
  sheet.save(OUT/f'pairs-{variant}-{direction}-lower4x-ground.png');metrics[f'{variant}/{direction}']=seq
ab=[]
for direction in ['southeast','southwest']:
 for i in range(8):
  a=np.array(Image.open(ROOT/f'A/{direction}/{i:02}.png'));b=np.array(Image.open(ROOT/f'B/{direction}/{i:02}.png'));mask=np.any(a!=b,axis=2);yy,xx=np.where(mask);ab.append({'direction':direction,'cel':f'{i:02}','changed_pixels':int(mask.sum()),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None})
upper=[]
for direction in ['southeast','southwest']:
 ims=[np.array(Image.open(ROOT/f'C/{direction}/{i:02}.png').convert('RGBA')) for i in range(8)]
 for i in [2,4,6]:
  upper.append({'direction':direction,'C00_vs':f'C{i:02}','raw_rgba_changed_pixels_above_y70':int(np.any(ims[0][:70]!=ims[i][:70],axis=2).sum())})
(OUT/'diagnostic-pixel-facts.json').write_text(json.dumps({'A_B_changes':ab,'B_C_pairs':metrics,'C_upper_body_comparison':upper},indent=2)+'\n')
print('Verified79 hashes; generated9 B/C full-cel sheets,4 cyclic-pair sheets and2 A/B change comparisons.')
