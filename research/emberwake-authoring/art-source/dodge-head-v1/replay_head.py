#!/usr/bin/env python3
"""Replay the single frozen dodge-specific head-layer candidate, offline.

The supplied head row ownership is literal. Clear the old owned region, then
copy every shifted nonzero-alpha source head texel exactly. Transparent shifted
texels preserve underlying body outside old ownership. No alpha blending,
resizing, new paint, registration or source-file mutation occurs.
"""
from pathlib import Path
import json,hashlib,argparse,io
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
JOBS=(('south',116,3,26,27),('east',117,3,54,55),('north',118,4,82,83),('west',119,4,110,111))
def sha(b):return hashlib.sha256(b).hexdigest()
def writej(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def cell(a,i):return a[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128].copy()
def compose(source,rows,dy):
 mask=np.zeros((128,128),bool)
 for y,x0,x1 in rows:
  if not(0<=y<128 and 0<=x0<x1<=128):raise ValueError('Invalid literal row ownership')
  mask[y,x0:x1]=True
 sy,sx=np.where(mask);ny=sy+dy
 if len(sy)==0 or ny.min()<0 or ny.max()>=128:raise ValueError('Head ownership clips canvas')
 if not np.array_equal(source[0,0],[0,0,0,0]):raise ValueError('Expected a literal transparent zero source texel')
 if np.any(source[source[:,:,3]==0,:3]):raise ValueError('Source has nonzero hidden RGB')
 shifted=np.zeros_like(mask);shifted[ny,sx]=True
 foreground=np.zeros_like(mask);nonzero=source[sy,sx,3]>0;foreground[ny[nonzero],sx[nonzero]]=True
 yy,xx=np.mgrid[:128,:128];xy=np.stack((xx,yy),axis=-1).astype(np.int16);owner=np.zeros((128,128),np.uint8)
 xy[mask]=[0,0];owner[mask]=1
 xy[ny[nonzero],sx[nonzero]]=np.stack((sx[nonzero],sy[nonzero]),axis=-1);owner[foreground]=2
 out=source[xy[:,:,1],xy[:,:,0]]
 union=mask|shifted;changed=np.any(source!=out,axis=2)
 if np.any(changed&~union):raise AssertionError('Outside union changed')
 original_nonhead=(~mask)&(source[:,:,3]>0);damaged=original_nonhead&changed
 if np.any(damaged&(out[:,:,3]==0)):raise AssertionError('Transparent shifted ownership deleted non-head body')
 if np.any(out[out[:,:,3]==0,:3]):raise AssertionError('Nonzero hidden RGB')
 if not np.array_equal(out[foreground],source[xy[:,:,1][foreground],xy[:,:,0][foreground]]):raise AssertionError('Head texel mismatch')
 return out,xy,owner,mask,shifted,foreground

def replay(atlas_path,mask_path,out_dir):
 out=Path(out_dir)
 if out.exists() or out.is_symlink():raise ValueError('Output must be a new nonexistent directory')
 ab=Path(atlas_path).read_bytes();mb=Path(mask_path).read_bytes();plan=json.loads((R/'frozen-plan.json').read_text());m=json.loads(mb)
 if sha(mb)!=plan['mask_sha256']:raise ValueError('Head ownership source changed')
 atlas=np.array(Image.open(io.BytesIO(ab)).convert('RGBA'))
 if atlas.shape[1]!=1024 or atlas.shape[0]%128 or m['native_stage']!=[128,128]:raise ValueError('Canvas contract changed')
 prepared=[]
 for job in plan['jobs']:
  a=cell(atlas,job['source_frame'])
  if a.shape!=(128,128,4) or sha(a.tobytes())!=job['source_cel_rgba_sha256']:raise ValueError('Settle donor changed: '+job['view'])
  candidate,xy,owner,old,new,fg=compose(a,m['views'][job['view']]['rows_y_x0_x1'],job['dy'])
  if sha(candidate.tobytes())!=job['candidate_rgba_sha256']:raise ValueError('Candidate replay hash mismatch')
  prepared.append((job,a,candidate,xy,owner,old,new,fg))
 if Path(atlas_path).read_bytes()!=ab or Path(mask_path).read_bytes()!=mb:raise ValueError('Input changed during preflight')
 out.mkdir(parents=True);(out/'witnesses').mkdir();receipts=[]
 for job,a,b,xy,owner,old,new,fg in prepared:
  view=job['view'];p=out/'witnesses'/view;p.mkdir();Image.fromarray(b).save(out/f'{view}.png')
  for name,mask in (('old-head-owner',old),('shifted-owner-union-extent',new),('shifted-nonzero-foreground',fg),('affected-union',old|new)):
   Image.fromarray(mask.astype(np.uint8)*255).save(p/f'{name}.png')
  np.save(p/'source-xy.npy',xy,allow_pickle=False);np.save(p/'owner.npy',owner,allow_pickle=False)
  yy,xx=np.where(np.any(a!=b,axis=2));journal=[]
  for y,x in zip(yy,xx):
   sx,sy=xy[y,x];journal.append({'at':[int(x),int(y)],'before':a[y,x].tolist(),'after':b[y,x].tolist(),'source_frame':job['source_frame'],'source_xy':[int(sx),int(sy)],'operation':('body_identity','old_owned_clear','shifted_nonzero_head_copy')[int(owner[y,x])]})
  writej(p/'changed-pixels.json',journal)
  nonhead=(~old)&(a[:,:,3]>0);changed=np.any(a!=b,axis=2);touched=nonhead&changed;transparent_preserved=new&~old&~fg&(a[:,:,3]>0)
  original_partial_over_body=fg&nonhead&(b[:,:,3]<255)
  rec={**job,'changed_pixels':len(journal),'old_head_clear_writes':int(old.sum()),'old_head_visible_pixels_cleared_after_overlay':int((old&(a[:,:,3]>0)&(b[:,:,3]==0)).sum()),'shifted_owner_extent_pixels':int(new.sum()),'nonzero_head_copy_writes':int(fg.sum()),'union_pixels':int((old|new).sum()),'nonhead_visible_pixels_changed':int(touched.sum()),'nonhead_visible_pixels_erased':int((touched&(b[:,:,3]==0)).sum()),'nonhead_visible_body_pixels_preserved_by_zero_alpha_skip':int(transparent_preserved.sum()),'semi_transparent_head_copies_over_visible_nonhead':int(original_partial_over_body.sum()),'outside_union_changed':int((changed&~(old|new)).sum()),'y_ge_64_body_and_feet_unchanged':bool(np.array_equal(a[64:],b[64:])),'hidden_rgb_zero':True,'head_map_sha256':sha((p/'source-xy.npy').read_bytes()),'changed_pixel_journal_sha256':sha((p/'changed-pixels.json').read_bytes())}
  writej(p/'receipt.json',rec);receipts.append(rec)
 receipt={'schema':'emberwake-dodge-head-replay/v1','semantics':plan['semantics'],'input_atlas_path':str(Path(atlas_path).resolve()),'input_atlas_sha256':sha(ab),'input_head_ownership_path':str(Path(mask_path).resolve()),'input_head_ownership_sha256':sha(mb),'jobs':receipts,'quality_status':'unrated; not approved; independent seam and motion review required'}
 writej(out/'receipt.json',receipt);return receipt
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--atlas',default=str(R/'inputs'/'atlas.png'));parser.add_argument('--masks',default=str(R/'inputs'/'head-protection.json'));parser.add_argument('--out',required=True);args=parser.parse_args()
 try:r=replay(args.atlas,args.masks,args.out)
 except (ValueError,AssertionError) as e:parser.exit(2,str(e)+'\n')
 print(json.dumps({'output':args.out,'views':[j['view'] for j in r['jobs']],'changed_pixels':sum(j['changed_pixels'] for j in r['jobs']),'nonhead_visible_pixels_erased':sum(j['nonhead_visible_pixels_erased'] for j in r['jobs'])},indent=2))
