"""Replay the literal matte erasures from retained inputs; no model or editor."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 recipe=json.loads((R/'cleaned/MATTE-RECEIPT.json').read_text());total=0;rows=[]
 for row in recipe['rows']:
  source=R/'cleaned'/row['retained_source'];assert sha(source)==row['source_sha256'];original=np.array(Image.open(source).convert('RGBA'));out=original.copy();allowed=np.zeros((128,128),bool)
  for entry in row['erased_pixels']:
   x,y=entry['xy'];assert original[y,x].tolist()==entry['before'];assert original[y,x,3]in[1,2] and not original[y,x,:3].any();assert entry['after']==[0,0,0,0]
   # Independent local-radius check: all alpha24 surfaces within a3pixel
   # Euclidean radius stay untouched, including disconnected real features.
   for yy in range(max(0,y-3),min(128,y+4)):
    for xx in range(max(0,x-3),min(128,x+4)):
     if (xx-x)**2+(yy-y)**2<=9:assert original[yy,xx,3]<24
   out[y,x]=0;allowed[y,x]=True;total+=1
  assert np.array_equal(out[~allowed],original[~allowed])
  restored=out.copy()
  for entry in row['erased_pixels']:
   x,y=entry['xy'];restored[y,x]=entry['before']
  assert np.array_equal(restored,original)
  target=a.out/row['output'];target.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(out).save(target)
  assert sha(target)==row['output_sha256']
  bbox=Image.fromarray(out).getbbox();assert bbox and min(bbox[:2])>0 and max(bbox[2:])<128
  rows.append({'bank':row['bank'],'phase':row['phase'],'RGBA_PNG_exact':True,'literal_erasure_undo_exact':True,'outside_mask_exact':True,'stage_interior':True})
 receipt={'passed':True,'frames':rows,'erased_pixels':total,'all_other_RGBA_exact':True,'actual_external_editor_or_GUI_tested':False,'scope':'Literal reversible matte erasure export; no art score or inferred original speck cause.'};(a.out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'PASS {len(rows)} matte PNGs, {total} literal erasures, exact undo and all protectedRGBA')
if __name__=='__main__':main()
