"""Compact source-map/timing check for theguideonly; no editor/generation."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=d.copy();use=sa>0
 for k in range(3):o[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 o[:,:,3][use]=(n[use]+127)//255
 return o.astype(np.uint8)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists();out.mkdir(parents=True);source={i:a(f'inputs/control/{i:02}.png') for i in [2,3]};upper=np.array(Image.open(R/'masks/02-exact-upper-armcuffs-gloves-owner.png'))>0;body=source[2].copy();body[~upper]=0;recipe=json.loads((R/'RECIPE.json').read_text())
 for c in recipe['parts']:
  name=f'{c["id"]}-{c["name"]}';z=np.load(R/'maps'/f'{name}.npz');part=np.zeros_like(body);src=source[c['source_phase']]
  for y,x in np.argwhere(z['owner']):sx,sy=z['source_xy'][y,x];part[y,x]=src[sy,sx]
  assert np.array_equal(part,a(f'layers/{name}.png'));body=over(body,part)
 body[upper]=source[2][upper];assert np.array_equal(body,a('frames/02.5.png'));assert np.array_equal(body[upper],source[2][upper]);timing=json.loads((R/'TIMING.json').read_text());clock=0;starts={};rows=[]
 for n,hold in zip(timing['order'],timing['hold_ticks']):
  starts[n]=clock;clock+=hold
  if n=='02.5':Image.fromarray(body).save(out/f'{n}.png')
  else:assert (R/'frames'/f'{n}.png').read_bytes()==(R/'inputs/control'/f'{n}.png').read_bytes();shutil.copy2(R/'inputs/control'/f'{n}.png',out/f'{n}.png')
  assert sha(out/f'{n}.png')==sha(R/'frames'/f'{n}.png');rows.append({'drawing':n,'PNG_RGBA_exact':True,'hold_ticks320':hold,'sha256':sha(out/f'{n}.png')})
 assert clock==144;assert starts['02.5']==45;assert all(starts[f'{i:02}']==i*18 for i in range(8));receipt={'status':'GUIDE ONLY, sourceconstruction and clock evidence; noartacceptance','source_part_inverse_map_RGBA_exact':True,'all9_composite_PNG_RGBA_exact':True,'all8_original_PNG_bytes_exact':True,'exact02_upper_armcuffs_gloves_RGBA':True,'original8_start_times_exact':True,'02_only_hold_split':[9,9],'clock_fps':320,'cycle_ticks':144,'model_calls':0,'new_authored_paint':0,'rows':rows};(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
