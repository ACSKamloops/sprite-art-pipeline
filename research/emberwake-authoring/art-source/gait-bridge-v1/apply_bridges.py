#!/usr/bin/env python3
"""Append frozen gait bridge cels while preserving every existing atlas cell.
Requires Python3, Pillow and NumPy. Never edits input files. No model/network calls.
"""
from pathlib import Path
import argparse,json,copy,hashlib,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
VARIANTS={'a':'trial-a-down','b':'trial-b-boot-preserved'}
def sha(b):return hashlib.sha256(b).hexdigest()
def extract(a,i):return a[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128].copy()
def apply(atlas_path,manifest_path,actor,out,variant='b'):
 out=Path(out)
 if out.exists() or out.is_symlink():raise ValueError('Output must be a new nonexistent directory')
 ab=Path(atlas_path).read_bytes();mb=Path(manifest_path).read_bytes()
 import io
 src=np.array(Image.open(io.BytesIO(ab)).convert('RGBA'));manifest=json.loads(mb)
 if manifest.get('character_id')!=actor or manifest.get('cell')!=[128,128] or manifest.get('columns')!=8 or src.shape[1]!=1024 or src.shape[0]%128:raise ValueError('Unsupported actor/canvas contract')
 jobs=json.loads((R/VARIANTS[variant]/actor/'jobs.json').read_text());prepared=[]
 for job in jobs:
  if job['actor']!=actor:raise ValueError('Actor mismatch')
  clip=manifest['animations'][job['view']+'_walk']
  if len(clip['frames'])!=8 or clip['holds']!=[0.05625]*8 or clip['loop'] is not True:raise ValueError('Expected the unchanged eight-slot 9/160-s looping walk clock')
  if clip['frames'][job['phase']]!=job['body_frame']:raise ValueError('Walk phase frame assignment has changed; rebase required')
  donor=extract(src,job['donor_frame'])
  if donor.shape!=(128,128,4) or sha(donor.tobytes())!=job['donor_rgba_sha256']:raise ValueError(f"Donor cel changed: {job['key']}; rebase required")
  md=R/VARIANTS[variant]/'maps'/job['key'];map_bytes=(md/'source-xy.npy').read_bytes()
  if sha(map_bytes)!=job['map_sha256']:raise ValueError('Frozen map checksum mismatch')
  xy=np.load(io.BytesIO(map_bytes),allow_pickle=False)
  if xy.shape!=(128,128,2) or xy.dtype.kind not in 'iu' or xy.min()<0 or xy.max()>=128:raise ValueError('Invalid frozen source map')
  candidate=donor[xy[:,:,1],xy[:,:,0]]
  if sha(candidate.tobytes())!=job['expected_rgba_sha256']:raise ValueError('Frozen map did not replay its expected RGBA')
  prepared.append((job,candidate))
 # Include every occupied tile as well as manifest references. This tolerates
 # unrelated action/waist/settle additions without overwriting their cells.
 used={i for clip in manifest['animations'].values() for i in clip['frames']}
 used.update(x['frame'] for x in manifest.get('lineage',[]) if 'frame' in x)
 used.update(i for i in range(src.shape[0]//128*8) if np.any(extract(src,i)))
 start=max(used,default=-1)+1;count=len(prepared);height=max(src.shape[0],math.ceil((start+count)/8)*128)
 dst=np.zeros((height,1024,4),np.uint8);dst[:len(src)]=src;m=copy.deepcopy(manifest);records=[]
 for offset,(job,candidate) in enumerate(prepared):
  index=start+offset;dst[index//8*128:(index//8+1)*128,index%8*128:(index%8+1)*128]=candidate
  m['animations'][job['view']+'_walk']['frames'][job['phase']]=index
  entry={'frame':index,'source':str(Path(atlas_path).resolve()),'source_sha256':sha(ab),'source_cell':job['donor_frame'],'rgba_sha256':job['expected_rgba_sha256'],'experimental_source_pixel_bridge':{'package':str(R),'variant':VARIANTS[variant],'key':job['key'],'donor_rgba_sha256':job['donor_rgba_sha256'],'map_sha256':job['map_sha256'],'roi':job['roi'],'protected_support_unchanged':True,'quality_status':'experimental; independent motion acceptance required'}}
  m.setdefault('lineage',[]).append(entry);records.append(entry)
 if not np.array_equal(dst[:len(src)],src):
  # Appending may use previously empty padding slots, but must preserve all
  # preexisting nonzero/manifest-owned cells byte-for-byte.
  for i in used:
   if not np.array_equal(extract(dst,i),extract(src,i)):raise AssertionError('Existing cel changed')
 # Input byte snapshots are the authority; fail if they drift during preflight.
 if Path(atlas_path).read_bytes()!=ab or Path(manifest_path).read_bytes()!=mb:raise ValueError('Input changed during preflight')
 receipt={'schema':'emberwake-gait-bridge-apply/v1','actor':actor,'variant':VARIANTS[variant],'input_atlas_sha256':sha(ab),'input_manifest_sha256':sha(mb),'append_start':start,'appended':count,'existing_occupied_or_referenced_cells_preserved':len(used),'clock':'8 x 9/160 = 9/20 s','records':records}
 out.mkdir(parents=True);Image.fromarray(dst).save(out/'atlas.png');(out/'animations.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt['output_atlas_sha256']=sha((out/'atlas.png').read_bytes());receipt['output_manifest_sha256']=sha((out/'animations.json').read_bytes());(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--atlas',required=True);p.add_argument('--manifest',required=True);p.add_argument('--actor',choices=['lyra','brann'],required=True);p.add_argument('--out',required=True);p.add_argument('--variant',choices=VARIANTS,default='b');a=p.parse_args()
 try:r=apply(a.atlas,a.manifest,a.actor,a.out,a.variant)
 except (ValueError,AssertionError) as e:p.exit(2,str(e)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
