from pathlib import Path
from PIL import Image,ImageDraw
from fractions import Fraction
import json,hashlib,datetime,numpy as np
ROOT=Path('/home/astra/artifacts/emberwake-midpoint-timing-review-v1/input');OUT=Path('/home/astra/artifacts/emberwake-midpoint-timing-review-v1/review')
m=json.loads((ROOT/'INPUTS.json').read_text());entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];check=[]
for e in entries:
 im=Image.open(ROOT/e['path']);got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();check.append({**e,'actual_sha256':got,'verified':got==e['sha256'],'size':list(im.size)})
assert len(check)==99 and all(e['verified'] for e in check)
(OUT/'input-hashes-before.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':check},indent=2)+'\n')
H={v:[Fraction(*h) for h in m.get('variant_holds',{}).get(v,m['holds'])] for v in m['variants']};timeline={}
for v,holds in H.items():
 assert sum(holds)==Fraction(9,20);t=Fraction(0);timeline[v]=[]
 for i,h in enumerate(holds):timeline[v].append({'exposure':f'{i:02}','start_rational':[t.numerator,t.denominator],'start_ms':float(t*1000),'hold_rational':[h.numerator,h.denominator],'hold_ms':float(h*1000)});t+=h
# Provenance assertions supporting the declared 2x2 design, not quality scores.
for direction in ['southeast','southwest']:
 a=[(ROOT/e['path']).read_bytes() for e in m['variants']['A'][direction]];b=[(ROOT/e['path']).read_bytes() for e in m['variants']['B'][direction]];c=[(ROOT/e['path']).read_bytes() for e in m['variants']['C'][direction]];d=[(ROOT/e['path']).read_bytes() for e in m['variants']['D'][direction]]
 assert a==c and b==d and b[:5]==a[:5] and b[6:]==a[5:]
BG={'light':(232,231,219,255),'dark':(24,30,39,255),'ground':(87,101,70,255)}
def tile(im,size,bg):
 im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST);out=Image.new('RGBA',(size,size),bg);out.alpha_composite(im);return out.convert('RGB')
for direction in ['southeast','southwest']:
 for scale,size in [('native',128),('nearest2x',256),('proxy84',84)]:
  for bgname,bg in BG.items():
   left=72;rowh=size+34;sheet=Image.new('RGB',(left+9*size+12,30+4*rowh+12),(47,50,55));d=ImageDraw.Draw(sheet);d.text((10,8),f'{direction} | {scale} | {bgname} | every exposure, hold ms below',(245,245,245))
   for row,v in enumerate(['A','B','C','D']):
    y=30+row*rowh;d.text((10,y+size//2),f'{v}',(245,245,245))
    for i,e in enumerate(m['variants'][v][direction]):
     im=Image.open(ROOT/e['path']);sheet.paste(tile(im,size,bg),(left+i*size,y));d.text((left+i*size+3,y+size+3),f'{i:02}: {float(H[v][i]*1000):g}ms',(245,245,245))
   sheet.save(OUT/f'sheet-{direction}-{scale}-{bgname}.png')
# Identical-art comparisons A/C and B/D are paired explicitly with BOTH schedules.
for direction in ['southeast','southwest']:
 for v,other in [('A','C'),('B','D')]:
  ims=[Image.open(ROOT/e['path']).convert('RGBA') for e in m['variants'][v][direction]];n=len(ims);rows=(n+1)//2;sheet=Image.new('RGB',(1100,32+rows*238),(47,50,55));draw=ImageDraw.Draw(sheet);draw.text((12,8),f'{direction} | {v}/{other}: all cyclic pairs, same images; nearest4x lower crop x32..95 y70..117',(245,245,245))
  for i in range(n):
   j=(i+1)%n;x=12+(i%2)*544;y=32+(i//2)*238
   draw.text((x,y),f'{i:02}->{j:02} | {v} {float(H[v][i]*1000):g}/{float(H[v][j]*1000):g}ms | {other} {float(H[other][i]*1000):g}/{float(H[other][j]*1000):g}ms',(245,245,245))
   for k,idx in enumerate([i,j]):
    im=ims[idx].crop((32,70,96,118)).resize((256,192),Image.Resampling.NEAREST);t=Image.new('RGBA',im.size,BG['ground']);t.alpha_composite(im);sheet.paste(t.convert('RGB'),(x+k*264,y+22))
  sheet.save(OUT/f'pairs-{direction}-{v}-{other}-lower4x-ground.png')
# Larger actual local transition, no synthesized interpolation.
sheet=Image.new('RGB',(3*320+36,2*286+30),(47,50,55));draw=ImageDraw.Draw(sheet)
for row,direction in enumerate(['southeast','southwest']):
 for col,(v,k,label) in enumerate([('A','04','A04 / B04 endpoint'),('B','05','B05 actual midpoint'),('A','05','A05 / B06 endpoint')]):
  im=Image.open(ROOT/f'{v}/{direction}/{k}.png').convert('RGBA').crop((32,68,96,118)).resize((320,250),Image.Resampling.NEAREST);t=Image.new('RGBA',im.size,BG['light']);t.alpha_composite(im);x=12+col*324;y=12+row*286;draw.text((x,y),f'{direction}: {label}',(245,245,245));sheet.paste(t.convert('RGB'),(x,y+20))
sheet.save(OUT/'actual-04-mid-05-lower5x.png')
(OUT/'timing-facts.json').write_text(json.dumps({'comparison_conditions':m['comparison_conditions'],'timeline':timeline,'verified_design':{'A_equals_C_pngs':True,'B_equals_D_pngs':True,'original_B_endpoint_starts_equal_A':all(timeline['B'][i+(i>4)]['start_rational']==timeline['A'][i]['start_rational'] for i in range(8)),'C_first_half_ms':float(sum(H['C'][:4])*1000),'C_second_half_ms':float(sum(H['C'][4:])*1000),'D_first_half_ms':float(sum(H['D'][:4])*1000),'D_second_half_ms':float(sum(H['D'][4:])*1000)}},indent=2)+'\n')
print('Verified 99 image hashes; 18 exposure sheets, 4 dual-schedule cyclic-pair sheets, 1 actual-midpoint sheet.')
print(json.dumps({v:[float(h*1000) for h in x] for v,x in H.items()}))
