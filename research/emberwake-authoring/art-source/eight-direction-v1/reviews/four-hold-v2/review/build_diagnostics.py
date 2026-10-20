from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime,numpy as np
ROOT=Path('/home/astra/artifacts/emberwake-four-hold-review-v2/input');OUT=Path('/home/astra/artifacts/emberwake-four-hold-review-v2/review')
m=json.loads((ROOT/'INPUTS.json').read_text());entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];check=[]
for e in entries:
 im=Image.open(ROOT/e['path']);got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();check.append({**e,'actual_sha256':got,'verified':got==e['sha256'],'size':list(im.size),'mode':im.mode})
assert len(check)==63 and all(e['verified'] for e in check)
(OUT/'input-hashes-before.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':check},indent=2)+'\n')
BG={'light':(232,231,219,255),'dark':(24,30,39,255),'ground':(87,101,70,255)}
def tile(im,size,bg):
 im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST);out=Image.new('RGBA',(size,size),bg);out.alpha_composite(im);return out.convert('RGB')
for scale,size in [('native',128),('nearest2x',256),('proxy84',84)]:
 for bgname,bg in BG.items():
  left=118;rowh=size+25;sheet=Image.new('RGB',(left+8*size+20,32+4*rowh+20),(47,50,55));d=ImageDraw.Draw(sheet);d.text((10,8),f'FOUR-HOLD FOLLOW-UP | {scale} | {bgname} | A retained anchor, B new sequence',(245,245,245));row=0
  for variant in ['A','B']:
   for direction in ['southeast','southwest']:
    y=32+row*rowh;d.text((10,y+size//2),f'{variant} {direction}',(245,245,245))
    for i in range(8):
     im=Image.open(ROOT/f'{variant}/{direction}/{i:02}.png');sheet.paste(tile(im,size,bg),(left+i*size,y));d.text((left+i*size+4,y+size+5),f'{i:02}',(245,245,245))
    row+=1
  sheet.save(OUT/f'sheet-{scale}-{bgname}.png')
metrics={}
for direction in ['southeast','southwest']:
 ims=[Image.open(ROOT/f'B/{direction}/{i:02}.png').convert('RGBA') for i in range(8)];sheet=Image.new('RGB',(1096,932),(47,50,55));d=ImageDraw.Draw(sheet);d.text((12,8),f'B {direction}: all cyclic pairs; crop x32..95 y70..117 nearest4x; ground',(245,245,245));seq=[]
 for i in range(8):
  j=(i+1)%8;x=12+(i%2)*544;y=32+(i//2)*224;d.text((x,y),f'{i:02} -> {j:02}',(245,245,245))
  for k,idx in enumerate([i,j]):
   im=ims[idx].crop((32,70,96,118)).resize((256,192),Image.Resampling.NEAREST);t=Image.new('RGBA',im.size,BG['ground']);t.alpha_composite(im);sheet.paste(t.convert('RGB'),(x+k*264,y+18))
  a=np.array(ims[i]);b=np.array(ims[j]);mask=np.any(a!=b,axis=2);seq.append({'pair':f'{i:02}->{j:02}','raw_rgba_changed_pixels':int(mask.sum()),'exact_duplicate':bool(not mask.any())})
 sheet.save(OUT/f'pairs-B-{direction}-lower4x-ground.png');metrics[f'B/{direction}']=seq
source=[]
for direction in ['southeast','southwest']:
 hashes={hashlib.sha256((ROOT/f'A/{direction}/{i:02}.png').read_bytes()).hexdigest():f'{i:02}' for i in range(8)}
 for i in range(8):
  got=hashlib.sha256((ROOT/f'B/{direction}/{i:02}.png').read_bytes()).hexdigest();source.append({'direction':direction,'B_slot':f'{i:02}','byte_identical_A_key':hashes.get(got)})
(OUT/'diagnostic-pixel-facts.json').write_text(json.dumps({'B_pairs':metrics,'nominated_pose_selection':source,'warning':'Raw RGBA counts and byte identity are provenance/diagnostics, not aesthetic scores.'},indent=2)+'\n')
print('Verified 63 image hashes; generated 9 scale/background sheets and 2 B cyclic-pair sheets.')
