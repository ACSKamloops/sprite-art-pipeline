"""Compact local replay for a rejected RGB-only art trial; no editor package."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args();out=args.output.resolve()
assert not out.exists(),'Fresh replay directory required.'
recipe=json.loads((R/'RGB-DEPTH-RECIPE.json').read_text())
inputs=json.loads((R/'INPUTS.json').read_text())
for record in inputs:assert sha(R/record['local'])==record['sha256']
# Verify actual retained P/Q layers against their local inverse source maps.
maps=[]
for i in (3,4):
 for role in ('P','Q'):
  z=np.load(R/f'inputs/parts/{i:02}-{role}-map.npz');mp=z['source_xy'];part=arr(R/f'inputs/parts/{i:02}-{role}.png')
  source=z['source_rgba'] if 'source_rgba'in z.files else arr(R/'inputs/parts/donor00.png')
  valid=mp[:,:,0]>=0;rebuilt=np.zeros_like(part);rebuilt[valid]=source[mp[valid,1],mp[valid,0]]
  assert np.array_equal(rebuilt,part)
  maps.append({'frame':i,'role':role,'all_layer_RGBA_from_map_exact':True,'positive_samples':int((part[:,:,3]>0).sum())})
out.mkdir(parents=True);frames=[]
for i in range(8):
 original=R/f'inputs/control/{i:02}.png';a=arr(original);b=a.copy();owner=np.zeros((128,128),bool)
 for op in recipe['operations']:
  if op['frame']!=i:continue
  x,y=op['destination'];sx,sy=op['color_source_xy'];donor=arr(R/op['color_source'])
  assert a[y,x].tolist()==op['old_RGBA'];assert donor[sy,sx].tolist()==op['color_source_RGBA']
  assert op['new_RGBA'][3]==op['old_RGBA'][3]
  b[y,x,:3]=donor[sy,sx,:3];owner[y,x]=True;assert b[y,x].tolist()==op['new_RGBA']
 assert np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[~owner],b[~owner])
 p=out/f'{i:02}.png'
 if owner.any():Image.fromarray(b).save(p)
 else:shutil.copy2(original,p)
 expected=R/f'candidate/{i:02}.png';assert p.read_bytes()==expected.read_bytes();assert np.array_equal(arr(p),arr(expected))
 frames.append({'frame':i,'PNG_and_RGBA_exact':True,'changed_RGB_samples':int(owner.sum()),'sha256':sha(p)})
(out/'REPLAY-RECEIPT.json').write_text(json.dumps({'status':'reproduced rejected/unselected trial, no art approval','models':0,'layers':maps,'frames':frames,'all8_alpha_exact':True,'six_original_PNG_bytes_exact':True},indent=2)+'\n')
print(json.dumps({'all8_PNG_RGBA_exact':True,'four_retained_part_maps_exact':True,'changed_RGB_samples':sum(x['changed_RGB_samples']for x in frames),'output':str(out)}))
