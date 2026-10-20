from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:assert args.output.is_absolute()and not args.output.exists();args.output.mkdir(parents=True)
inputs=json.loads((P/'INPUTS.json').read_text())
for f in inputs['files']:assert sha(P/f['path'])==f['sha256']
source=[arr(P/f'inputs/frames/{i:02}.png')for i in range(8)];recipe=json.loads((P/'RECIPE.json').read_text());changed={r['phase']:r for r in recipe['phase_repairs']};results=[]
for i in range(8):
 out=source[i].copy()
 if i in changed:
  data=np.load(P/f'maps/{i:02}-literal-source-map.npz',allow_pickle=False);sid=data['source_phase'];xy=data['source_xy'];out=np.zeros_like(source[i])
  for y in range(128):
   for x in range(128):
    sp=int(sid[y,x]);sx,sy=map(int,xy[y,x])
    if sp>=0:out[y,x]=source[sp][sy,sx]
    else:assert sp==-2 and data['erased'][y,x]and sx==-1 and sy==-1
  for op in changed[i]['operations']:
   x,y=op['target'];assert data['allowed'][y,x]
   if op['op']=='copy':sx,sy=op['source'];assert source[op['source_phase']][sy,sx].tolist()==op['source_RGBA'];assert out[y,x].tolist()==op['source_RGBA']
   else:assert out[y,x].tolist()==[0,0,0,0]
  upper=np.array(Image.open(P/f'masks/{i:02}-protected-upper.png').convert('L'))>0;boot=np.array(Image.open(P/f'masks/{i:02}-exact-complete-boot.png').convert('L'))>0;allowed=data['allowed'];assert np.array_equal(out[upper],source[i][upper]);assert np.array_equal(out[boot],source[i][boot]);assert np.array_equal(out[~allowed],source[i][~allowed])
 else:assert (P/f'candidate/{i:02}.png').read_bytes()==(P/f'inputs/frames/{i:02}.png').read_bytes()
 assert np.array_equal(out,arr(P/f'candidate/{i:02}.png'))
 if args.output:
  dest=args.output/f'{i:02}.png'
  if i in changed:Image.fromarray(out).save(dest)
  else:dest.write_bytes((P/f'inputs/frames/{i:02}.png').read_bytes())
  assert sha(dest)==sha(P/f'candidate/{i:02}.png')
 results.append({'phase':i,'source_map_RGBA_exact':True,'PNG_sha256':sha(P/f'candidate/{i:02}.png'),'changed_RGBA_pixels':int(np.any(out!=source[i],axis=2).sum())})
r={'status':'PASS source witness/map reconstruction only; visual improvement not established','all8':results,'upper_torso_head_arms_gloves_exact':True,'all_original_complete_boot_owners_exact':True,'unchanged_PNG_byte_phases':[0,1,2,3,7],'generation_calls':0,'editor_packaged':False,'clock':'9/160s each;.45s loop','03_rounded_patch_rejected_and_retained':True}
if args.output:(args.output/'SOURCE-REPLAY-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS all8 literal source-map RGBA/PNG; torso/arms/gloves and complete boot owners exact; no art acceptance.')
