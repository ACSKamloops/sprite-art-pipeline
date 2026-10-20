"""Fresh local replay of one frozen source-pixel P07 affine and19texel join."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();assert not out.exists(),'Fresh output only.'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def a(p):return np.array(Image.open(p).convert('RGBA'))
def over(dst,src):
 s=src.astype(np.int64);d=dst.astype(np.int64);sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);v=sa>0;o=d.copy()
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 o[:,:,3][v]=(n[v]+127)//255
 return o.astype(np.uint8)
for item in json.loads((R/'INPUTS.json').read_text()):assert sha(R/item['local'])==item['sha256']
src=a(R/'inputs/current/07.png');z=np.load(R/'maps/P07-positive-affine.npz');owner=z['source_owner'];inv=np.linalg.inv(z['matrix']);part=np.zeros_like(src);mp=np.full((128,128,2),-1,np.int16)
# Independent scalar inverse sampling, rather than copying the retained output.
for y in range(128):
 for x in range(128):
  u,v,_=inv@np.array([x,y,1]);sx=int(np.floor(u+.5));sy=int(np.floor(v+.5))
  if 0<=sx<128 and 0<=sy<128 and owner[sy,sx]:part[y,x]=src[sy,sx];mp[y,x]=[sx,sy]
assert np.array_equal(mp,z['source_xy']);assert np.array_equal(part,a(R/'raw/P07-affine-layer.png'))
under=src.copy();under[owner]=0;raw=over(under,part);protected=np.array(Image.open(R/'masks/upper-Q-protected.png'))>0;raw[protected]=src[protected]
assert np.array_equal(raw,a(R/'raw/07-affine-protected.png'))
joinmap=np.load(R/'cuff-join-v1/charcoal-cuff-join-map.npz');mask=joinmap['owner'];jmp=joinmap['source_xy'];field=np.zeros_like(src);field[mask]=src[jmp[mask,1],jmp[mask,0]]
assert np.array_equal(field,a(R/'cuff-join-v1/charcoal-cuff-join-layer.png'));assert not np.any(mask&protected)
# Field lies behind affine P and fixed upper/Q, not over an existing boot.
joined=over(over(under,field),part);joined[protected]=src[protected]
assert np.array_equal(joined,a(R/'cuff-join-v1/07.png'));assert np.array_equal(joined[protected],src[protected])
union=owner|(mp[:,:,0]>=0)|mask;assert np.array_equal(joined[~union],src[~union])
out.mkdir(parents=True);frames=[]
for name,image,expected in [('raw07',raw,R/'raw/07-affine-protected.png'),('joined07',joined,R/'cuff-join-v1/07.png')]:
 p=out/f'{name}.png';Image.fromarray(image).save(p);assert p.read_bytes()==expected.read_bytes();(out/f'{name}.rgba').write_bytes(image.tobytes())
 frames.append({'file':p.name,'sha256':sha(p),'PNG_bytes_exact':True,'RGBA_bytes_exact':True,'RGBA_sha256':hashlib.sha256(image.tobytes()).hexdigest()})
receipt={'status':'one frozen source construction replay, no quality/wholecycle approval','scalar_inverse_affine_map_exact':True,'source_palette_and_partial_alpha_exact':True,'upper_Q_exact':True,'outside_declared_owner_exact':True,'raw_gap_stage_preserved':True,'join_texels':int(mask.sum()),'body_timing_registration_changed':False,'model_calls':0,'editor':False,'fullbank_built':False,'outputs':frames}
(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
