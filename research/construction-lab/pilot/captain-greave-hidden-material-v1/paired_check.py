from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;a=P/'artifacts/shaded-long110';b=P.parent/'captain-greave-mass-calibration-v1/artifacts/calibrated-long110';ma=json.loads((a/'manifest.json').read_text());mb=json.loads((b/'manifest.json').read_text());assert ma['surfaces']==mb['surfaces'];assert ma['poses_sha256']==mb['poses_sha256'];r={'local_vertices_UV_triangles_exact':True,'same_pose_packet':True,'unrelated_layer_pngs_exact':0,'source_owned_texture_pixels_exact':{},'frame_changes':[],'art_approval':False};src=np.array(Image.open(P/'source/upper/source/native-256.png'))
for n in ['far','near']:
 mask=np.array(Image.open(a/'parts'/f'{n}_shin-source.png'))[:,:,3]>0;tex=np.array(Image.open(a/'parts'/f'{n}_shin-extended-UV.png'));assert np.array_equal(tex[mask],src[mask]);r['source_owned_texture_pixels_exact'][n]=int(mask.sum())
for i in range(72):
 for f in (a/'layers').glob(f'{i:03}-*.png'):
  if f.name not in [f'{i:03}-far_shin.png',f'{i:03}-near_shin.png']:assert f.read_bytes()==(b/'layers'/f.name).read_bytes();r['unrelated_layer_pngs_exact']+=1
 x=np.array(Image.open(a/'frames'/f'{i:03}.png'));y=np.array(Image.open(b/'frames'/f'{i:03}.png'));diff=(x!=y).any(axis=2);owner=np.zeros(diff.shape,bool)
 for n in ['far','near']:owner|=np.array(Image.open(a/'layers'/f'{i:03}-{n}_shin.png'))[:,:,3]>0
 assert not (diff&~owner).any();assert np.array_equal(x[:,:,3],y[:,:,3]);r['frame_changes'].append({'index':i,'changed_pixels':int(diff.sum()),'outside_shin_alpha':0,'alpha_changes':0})
(a/'paired-check.json').write_text(json.dumps(r,indent=2)+'\n');print(r['unrelated_layer_pngs_exact'],'unrelated layers exact')
