"""Bounded source/motif/rigid-geometry checks, not sprite art approval."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import build as b
P=b.P
ap=argparse.ArgumentParser();ap.add_argument('pack',type=Path);a=ap.parse_args();d=json.loads((a.pack/'manifest.json').read_text());src=np.array(Image.open(P/'source/upper/source/native-256.png').convert('RGBA'));palette={tuple(c)for c in src.reshape(-1,4)if c[3]};extra=0;alpha=set();max_radius_error=0;owned={};counts=np.zeros((256,256),int);reconstructed=np.zeros_like(src)
for n in ['far','near']:
 legalpha=np.array(Image.open(a.pack/'upper-parts/source-owned'/f'{n}_leg.png'))[:,:,3]>0;recon=np.zeros_like(src);cc=np.zeros((256,256),int)
 for k in ['thigh','shin','cap','boot']:
  part=np.array(Image.open(a.pack/'parts'/f'{n}_{k}-source.png'));occupied=part[:,:,3]>0;cc+=occupied;recon[occupied]=part[occupied]
 assert np.array_equal(cc[legalpha],np.ones(cc[legalpha].shape)) and not (cc>1).any()
 expected=np.array(Image.open(a.pack/'upper-parts/source-owned'/f'{n}_leg.png'));assert np.array_equal(recon,expected)
 owned[n]={'source_partition_RGBA_exact':True,'source_partition_overlap_pixels':0}
for record in d['records']:
 for name in ['far_shin','far_cap','near_shin','near_cap','far_boot','near_boot']:
  arr=np.array(Image.open(a.pack/record['layers'][name]['file']));alpha.update(arr[:,:,3].reshape(-1).tolist());extra+=sum(tuple(c)not in palette for c in arr.reshape(-1,4)if c[3])
 for name,mesh in record['meshes'].items():
  
  if name not in d['surfaces']:continue
  local=np.array([v[1]for v in d['surfaces'][name]['UV_local_vertices']]);world=np.array(mesh['vertices_world']);origin=np.mean(world-local.mean(axis=0),axis=0) # pairwise distances avoid requiring pose packet.
  for i in range(len(local)-1):max_radius_error=max(max_radius_error,abs(np.linalg.norm(world[i+1]-world[i])-np.linalg.norm(local[i+1]-local[i])))
assert extra==0 and alpha=={0,255} and max_radius_error<1e-10
# Actual neutral pixels versus the declared affine UV baseline, same pixel-center sampler.
pose=json.loads((P/'source/poses.json').read_text())['neutral_bind'];cam=np.array(json.loads((P/'source/poses.json').read_text())['camera']['matrix_2x3']);yy,xx=np.mgrid[:256,:256];grid=np.stack([xx+.5,yy+.5],axis=-1);neutral={}
for n in ['far','near']:
 c=d['source_anchors'][n];leg=pose['legs'][n];M=b.core.bone_matrix(c['knee'],c['ankle'],np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array([-.8,-.6,0]));uv=(grid-np.array(leg['pixels']['knee']))@np.linalg.inv(M).T+np.array(c['knee']);u=np.clip(np.floor(uv[:,:,0]).astype(int),0,255);v=np.clip(np.floor(uv[:,:,1]).astype(int),0,255)
 for k in ['shin','cap']:
  im=np.array(Image.open(a.pack/'layers'/f'000-{n}_{k}.png'));tex=np.array(Image.open(a.pack/'parts'/f'{n}_{k}-extended-UV.png'));ref=tex[v,u];vis=im[:,:,3]>0;equal=(im==ref).all(axis=2);neutral[n+'_'+k]={'opaque_pixels':int(vis.sum()),'equal_to_fixed_neutral_UV_paint':int((vis&equal).sum()),'different':int((vis&~equal).sum()),'scope':'nearest-color preservation against declared neutral affine UV calibration; not original silhouette identity'}
if d['poses_sha256']!=d['fixed_UV_bind_poses_sha256']:neutral={'not_applicable':'motion pose differs from the fixed neutral UV bind; do not compare this posed image to the neutral card. Fixed UV/local mesh equality is audited separately.'}
report={'scope':'source ownership, actual texture colors and fixed volume; no art/gait/wholeactor contact certificate','source_partition':owned,'new_opaque_RGBA_colors':extra,'alpha_values':sorted(alpha),'max_mesh_neighbor_distance_error':max_radius_error,'neutral_paint_reference':neutral,'pose_sha256':d['poses_sha256'],'fixed_bind_sha256':d['fixed_UV_bind_poses_sha256']}
(a.pack/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
