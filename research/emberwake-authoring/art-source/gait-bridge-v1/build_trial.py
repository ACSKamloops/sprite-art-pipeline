#!/usr/bin/env python3
"""Bounded source-pixel bridge study. Writes only below this script's folder."""
from pathlib import Path
import json,hashlib,copy,struct,subprocess,zlib,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
SRC=Path('/home/astra/projects/emberwake-demo/art-source/characters-v2/bake-v3')
W=H=128
ROI=(43,82,86,121)
ACTORS=('lyra','brann'); VIEWS=('south','north')
def sha(b):return hashlib.sha256(b).hexdigest()
def writej(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def cel(a,i):return a[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128].copy()
def save(a,p):Image.fromarray(a).save(p)
def mapwarp(a,split,bottom,plateau,side,dy,dx,seam_end=None):
    yy,xx=np.mgrid[:H,:W];inside=(xx>=ROI[0])&(xx<ROI[2])&(yy>=ROI[1])&(yy<ROI[3])
    # Authored visible-part assignment. Below the measured short boot bottom,
    # original visible paint belongs to the standing leg, never the swing leg.
    seam=np.full((H,W),float(split)) if seam_end is None else np.broadcast_to(np.interp(np.arange(H),[82,plateau,bottom,121],[split,split,seam_end,seam_end])[:,None],(H,W))
    owner=inside & ((xx<seam) if side=='left' else (xx>=seam)) & ((yy<=bottom)|(a[:,:,3]==0))
    support=inside & (a[:,:,3]>0) & ~owner
    # Three rectangular strips, frozen controls/triangle order; distal two
    # rows share the same translation, so the full boot is a rigid plateau.
    ys=[82,plateau,121];sv=[];tv=[]
    for y in ys:
      shift=0 if y==82 else 1
      for x in [43,85]:sv.append([x,y]);tv.append([x+dx*shift,y+dy*shift])
    tris=[[0,1,3],[0,3,2],[2,3,5],[2,5,4]]
    source=np.stack((xx,yy),-1).astype(np.int16);ownership=np.zeros((H,W),np.uint8)
    # Erase the displaced source part with the exact transparent source texel.
    source[owner]=[0,0];ownership[owner]=2
    triangle=np.full((H,W),-1,np.int16);mapped=np.zeros((H,W),bool);det=[]
    for ti,tr in enumerate(tris):
      s=np.array([sv[i] for i in tr],float);t=np.array([tv[i] for i in tr],float)
      sd=np.linalg.det(np.column_stack((s[1]-s[0],s[2]-s[0])));td=np.linalg.det(np.column_stack((t[1]-t[0],t[2]-t[0])));assert sd*td>0
      det.append([float(sd),float(td)])
      inv=np.linalg.inv(np.vstack((t.T,np.ones(3))))
      for y in range(max(82,int(np.floor(t[:,1].min()))),min(121,int(np.ceil(t[:,1].max()))+1)):
       for x in range(max(43,int(np.floor(t[:,0].min()))),min(86,int(np.ceil(t[:,0].max()))+1)):
        bary=inv@np.array([x,y,1.]);
        if min(bary)<-1e-8:continue
        p=bary@s;sx,sy=np.floor(p+.5).astype(int)
        if 0<=sx<W and 0<=sy<H and owner[sy,sx]:source[y,x]=[sx,sy];ownership[y,x]=1;triangle[y,x]=ti;mapped[y,x]=True
    source[support]=np.stack((xx,yy),-1)[support];ownership[support]=0;triangle[support]=-1
    out=a[source[:,:,1],source[:,:,0]]
    boot=owner&(yy>=plateau)&(a[:,:,3]>0)
    by,bx=np.where(boot);tx=bx+dx;ty=by+dy
    boot_ok=(tx>=0)&(tx<W)&(ty>=0)&(ty<H)
    exact=np.zeros(len(tx),bool);exact[boot_ok]=np.all(out[ty[boot_ok],tx[boot_ok]]==a[by[boot_ok],bx[boot_ok]],axis=1)
    changed=np.any(a!=out,axis=2)
    assert not changed[~inside].any();assert not changed[support].any()
    spec={'roi':list(ROI),'side':side,'split_x':split,'seam_end_x':seam_end,'visible_swing_bottom_inclusive':bottom,'rigid_plateau_y':plateau,'translation':[dx,dy],'source_vertices':sv,'target_vertices':tv,'triangles':tris,'signed_determinants':det,'ownership_rule':'swing side of split inside ROI; below short-boot bottom only original transparent texels are swing owned; nonowned visible source remains support/body','clear_source_xy':[0,0],'source_sampling':'pixel centers; inverse barycentric; floor(value+0.5); last valid source-owned triangle wins; support paint restored at identity','boot_owned_visible_pixels':len(tx),'boot_pixels_not_preserved_after_translation':int((~exact).sum()),'actual_changed_pixels':int(changed.sum()),'outside_roi_changed':0,'support_changed':0,'source_visible_swing_pixels':int((owner&(a[:,:,3]>0)).sum()),'output_visible_swing_pixels':int(((ownership==1)&(out[:,:,3]>0)).sum())}
    return out,source,ownership,owner,support,triangle,spec,boot
# Actor/view/half source ownership measured from coordinate contact sheets.
# (vertical split, short swing boot bottom inclusive, boot plateau starts).
GEO={
 'lyra':{'south':{1:(63,95,89),2:(62,95,89),5:(65,97,90),6:(66,93,87)},
         'north':{1:(60,97,89),2:(62,98,89),5:(67,99,91),6:(68,99,91)}},
 'brann':{'south':{1:(63,101,93),2:(64,101,94),5:(69,102,94),6:(69,101,94)},
          'north':{1:(63,101,91),2:(64,95,88),5:(68,95,87),6:(68,101,91)}}}
def make_variant(name,outward):
 dest=ROOT/name;dest.mkdir();(dest/'maps').mkdir();summary=[]
 for actor in ACTORS:
  ad=dest/actor;ad.mkdir();base=np.array(Image.open(ROOT/'inputs'/actor/'atlas.png').convert('RGBA'));m=json.loads((ROOT/'inputs'/actor/'animations.json').read_text());atlas=np.zeros((2048,1024,4),np.uint8);atlas[:base.shape[0]]=base
  jobs=[];idx=116
  for view in VIEWS:
   orig=m['animations'][view+'_walk']['frames'][:]
   for phase in (1,2,5,6):
    donor=orig[phase];a=cel(base,donor);split,bottom,plateau=GEO[actor][view][phase];side='left' if phase<4 else 'right';dy=2 if phase%4==1 else 4;dx=0 if outward is None else (-outward if side=='left' else outward)
    seam_end=None
    if outward is None:
     # Second/final trial: improve the source-part seam assignment and choose
     # only the least outward translation that preserves the whole owned boot.
     if side=='left':
      if actor=='brann' and (view=='south' or phase==1):seam_end=60
      elif actor=='lyra':
       if view=='north' and phase==2:pass
       seam_end=split-1
      else:seam_end=split
     else:seam_end=split
     valid=[]
     for mag in range(4):
      tx=(-mag if side=='left' else mag)
      candidate=mapwarp(a,split,bottom,plateau,side,dy,tx,seam_end)
      if candidate[-2]['boot_pixels_not_preserved_after_translation']==0:valid.append(candidate);break
     if not valid:raise RuntimeError(f'No bounded unoccluded rigid boot: {key if "key" in locals() else (actor,view,phase)}')
     out,xy,own,owner,support,tri,spec,boot=valid[0]
    else:out,xy,own,owner,support,tri,spec,boot=mapwarp(a,split,bottom,plateau,side,dy,dx)
    key=f'{actor}-{view}-p{phase}';md=dest/'maps'/key;md.mkdir()
    np.save(md/'source-xy.npy',xy,allow_pickle=False);np.save(md/'ownership.npy',own,allow_pickle=False);np.save(md/'triangle.npy',tri,allow_pickle=False)
    save((owner.astype(np.uint8)*255),md/'source-owner.png');save((support.astype(np.uint8)*255),md/'protected-support.png');save((boot.astype(np.uint8)*255),md/'rigid-boot.png');save(a,md/'body-donor.png');save(out,md/'expected.png')
    cy,cx=np.where(np.any(a!=out,axis=2));diff=[{'at':[int(x),int(y)],'before':a[y,x].tolist(),'after':out[y,x].tolist(),'source_xy':xy[y,x].tolist(),'owner':int(own[y,x])} for y,x in zip(cy,cx)]
    writej(md/'changed-pixels.json',diff)
    spec.update({'key':key,'actor':actor,'view':view,'phase':phase,'donor_frame':donor,'body_frame':donor,'candidate_frame':idx,'donor_rgba_sha256':sha(a.tobytes()),'expected_rgba_sha256':sha(out.tobytes()),'source_atlas_sha256':sha((ROOT/'inputs'/actor/'atlas.png').read_bytes()),'map_sha256':sha((md/'source-xy.npy').read_bytes()),'changed_pixel_journal_sha256':sha((md/'changed-pixels.json').read_bytes())})
    writej(md/'spec.json',spec);jobs.append(spec);summary.append(spec)
    atlas[idx//8*128:(idx//8+1)*128,idx%8*128:(idx%8+1)*128]=out;m['animations'][view+'_walk']['frames'][phase]=idx
    m['lineage'].append({'frame':idx,'source':str(SRC/actor/'atlas.png'),'source_sha256':spec['source_atlas_sha256'],'source_cell':donor,'rgba_sha256':spec['expected_rgba_sha256'],'experimental_source_pixel_bridge':{'spec':f'../maps/{key}/spec.json','source_xy':f'../maps/{key}/source-xy.npy','body_and_limb_donor_frame':donor,'protected_roi':list(ROI),'passing_key_unchanged':True,'quality_status':'experimental-unreviewed'}});idx+=1
  save(atlas,ad/'atlas.png');writej(ad/'animations.json',m);writej(ad/'jobs.json',jobs)
 writej(dest/'summary.json',summary)
 return summary
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--variant',choices=['a','b'],required=True)
 parser.add_argument('--out-name',required=True,help='Fresh child folder of this artifact root')
 args=parser.parse_args()
 if Path(args.out_name).name!=args.out_name or args.out_name in ('.','..'):parser.error('Use one fresh child directory name')
 inp=ROOT/'inputs';inp.mkdir(exist_ok=True)
 for actor in ACTORS:
  (inp/actor).mkdir(exist_ok=True)
  for file in ('atlas.png','animations.json'):
   target=inp/actor/file
   if not target.exists():shutil.copyfile(SRC/actor/file,target)
 result=make_variant(args.out_name,0 if args.variant=='a' else None)
 print('built',args.variant,'changed pixels',sum(x['actual_changed_pixels'] for x in result))
