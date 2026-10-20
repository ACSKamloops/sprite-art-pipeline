#!/usr/bin/env python3
"""Remove only distant black alpha1/2 specks from explicitly nominated walk cels.

Never changes an input. This is a scoped matte export, not a general cleanup
for art containing particles/accessories. Each literal erasure is retained.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
from scipy import ndimage

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 spec=json.loads(a.sources.read_text());assert not a.out.exists(),'Fresh output required'
 inputs=[]
 for name,entries in spec['banks'].items():
  assert len(entries)==8
  for i,item in enumerate(entries):
   source=(a.sources.parent/item['path']).resolve();assert sha(source)==item['sha256'],source
   image=Image.open(source);assert image.mode=='RGBA' and image.size==(128,128)
   inputs.append((name,i,source,np.array(image)))
 a.out.mkdir(parents=True);rows=[]
 for bank,i,source,rgba in inputs:
  labels,count=ndimage.label(rgba[...,3]>=24,np.ones((3,3)))
  assert count>0
  areas=np.bincount(labels.ravel());areas[0]=0;body=labels==int(areas.argmax());assert body.sum()>1000
  distance=ndimage.distance_transform_edt(~body)
  erase=(rgba[...,3]>0)&(rgba[...,3]<=2)&np.all(rgba[...,:3]==0,axis=-1)&(distance>3)
  target=rgba.copy();target[erase]=0
  assert np.array_equal(target[~erase],rgba[~erase])
  assert not np.any(erase&(distance<=3))
  destination=a.out/bank/f'{i:02}.png';destination.parent.mkdir(parents=True,exist_ok=True)
  original=a.out/'inputs'/bank/f'{i:02}.png';original.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,original)
  if not erase.any():shutil.copyfile(source,destination)
  else:Image.fromarray(target).save(destination)
  coords=[{'xy':[int(x),int(y)],'before':rgba[y,x].tolist(),'after':[0,0,0,0],'distance_from_main_alpha24_body':float(distance[y,x])}for y,x in np.argwhere(erase)]
  rows.append({'bank':bank,'phase':i,'source':str(source),'retained_source':original.relative_to(a.out).as_posix(),'source_sha256':sha(source),'output':destination.relative_to(a.out).as_posix(),'output_sha256':sha(destination),'erased_pixels':coords,'outside_declared_erasure_RGBA_exact':True,'all_RGBA_within3px_of_body_exact':True,'body_alpha24_pixels':int(body.sum()),'bbox_after':Image.fromarray(target).getbbox()})
 recipe={'scope':'Explicit unarmed Brann walk matte export only; no score or physical-contact claim','criterion':'RGBA alpha1or2, RGBexactblack, Euclidean distance>3 from largest8connected alpha>=24 body. No other pixel changes.','source_spec_sha256':sha(a.sources),'script_sha256':sha(Path(__file__)),'scipy_version':__import__('scipy').__version__,'rows':rows,'actual_sprite_editor_tested':False,'literal_reversible_erasure_journal':True}
 (a.out/'MATTE-RECEIPT.json').write_text(json.dumps(recipe,indent=2)+'\n')
 print(json.dumps({'frames':len(rows),'erased_pixels':sum(len(r['erased_pixels'])for r in rows),'all_other_RGBA_exact':True,'output':str(a.out)}))
if __name__=='__main__':main()
