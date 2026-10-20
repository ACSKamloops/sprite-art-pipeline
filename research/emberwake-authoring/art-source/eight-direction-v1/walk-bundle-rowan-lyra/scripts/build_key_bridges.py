#!/usr/bin/env python3
"""Replayable four-painted-key, four-visible-part-bridge candidate.
No generator, hidden surface reconstruction, timing interpolation or API calls.
"""
import json,argparse,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
from animation_media import emit_media
from rigid_boot_mesh import make_map

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return np.array(Image.open(p).convert('RGBA'))
def owners(key,im):
 if 'frozen_owners' in key:
  f=key['frozen_owners']; masks=[]
  for v in (f['A'],f['B'],f['lower']):
   assert sha(v['path'])==v['sha256'],('stale mask',v['path']);masks.append(np.array(Image.open(v['path']))>0)
  return masks[:2],masks[2]
 Y,X=np.indices((128,128));lower=(Y>=key['lower_top'])&(Y<124)&(X>=28)&(X<104)
 for rect in key.get('raised_rects',[]):
  x0,y0,x1,y1=rect;lower[y0:y1,x0:x1]=True
 for rect in key.get('glove_protection',[]):
  x0,y0,x1,y1=rect;lower[y0:y1,x0:x1]=False
 if 'protect_polygons' in key:
  p=Image.new('1',(128,128));d=ImageDraw.Draw(p)
  for poly in key['protect_polygons']:d.polygon(poly,fill=1)
  lower &= ~np.array(p,dtype=bool)
 split=np.interp(Y[:,0],np.array(key['split_curve'])[:,0],np.array(key['split_curve'])[:,1])[:,None]
 far=(X<split) if key['far_side']=='left' else (X>=split)
 if 'owner_a_polygons' in key:
  own=Image.new('1',(128,128));drawer=ImageDraw.Draw(own)
  for poly in key['owner_a_polygons']:drawer.polygon(poly,fill=1)
  far=np.array(own,dtype=bool)
 return [lower&far,lower&~far],lower

def boot_owner(key,source,sourceowner,leg):
 if 'frozen_boots' in key:
  r=key['frozen_boots'][leg];assert sha(r['path'])==r['sha256'],('stale bootmask',r['path']);return np.array(Image.open(r['path']))>0
 mask=np.zeros((128,128),bool)
 if 'boot_rects' not in key:return mask
 x0,y0,x1,y1=key['boot_rects'][leg];mask[y0:y1,x0:x1]=True;mask &= sourceowner
 r,g,b=[source[:,:,j].astype(float) for j in range(3)]
 leather=(r>g*1.18)&(g>b*1.05)&(r>b*1.5)&(source[:,:,3]>0)
 cloth=(g>=r*.76)&(b>=g*.60)&(g>25)
 return mask&binary_dilation(leather&mask,iterations=1)&~cloth&(source[:,:,3]>0)

def resolve_paths(cfg,config_path):
 base=(Path(config_path).resolve().parent/cfg.get('path_root','.')).resolve()
 def resolve(p):return str((base/p).resolve()) if not Path(p).is_absolute() else p
 for view in cfg['views'].values():
  view['baseline_dir']=resolve(view['baseline_dir'])
  for key in view['keys'].values():
   key['path']=resolve(key['path'])
   if 'frozen_owners' in key:
    for record in key['frozen_owners'].values():record['path']=resolve(record['path'])
   if 'frozen_boots' in key:
    for record in key['frozen_boots']:record['path']=resolve(record['path'])
 return cfg

def main():
 ap=argparse.ArgumentParser();ap.add_argument('config');ap.add_argument('output');args=ap.parse_args();cfg=resolve_paths(json.loads(Path(args.config).read_text()),args.config);out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
 for view,viewcfg in cfg['views'].items():
  dest=out/view;dest.mkdir();keys={int(k):v for k,v in viewcfg['keys'].items()};ims={k:load(v['path']) for k,v in keys.items()};ow={k:owners(v,ims[k]) for k,v in keys.items()}
  for k,v in keys.items():assert sha(v['path'])==v['sha256'],('stale key',k)
  frames=[];receipts=[]
  for idx in range(8):
   if idx%2==0:
    result=ims[idx].copy();receipt={'frame':idx,'role':keys[idx]['role'],'construction':'exact painted key copy','source':keys[idx]['path'],'source_sha256':keys[idx]['sha256']}
   else:
    bridge=viewcfg['bridges'][str(idx)];bodykey=bridge['body_key'];body=ims[bodykey];result=body.copy();oldowners,oldlower=ow[bodykey];result[oldlower]=0
    # All original body paint outside old leg ownership remains protected.
    protected=(body[:,:,3]>0)&~oldlower
    allowed=np.zeros((128,128),bool);allowed[74:125,24:108]=True;allowed &= ~protected
    owner=np.zeros((128,128),np.uint8);owner[oldlower]=3
    sy0,sx0=np.indices((128,128));xy=np.stack((sx0,sy0),axis=-1).astype(np.int16)
    controls=[];rigid=np.zeros((128,128),np.uint8)
    # These characters/angles use near visible owner on top at crossing.
    for leg in (0,1):
     sourcekey=bridge['leg_source_keys'][leg];source=ims[sourcekey];sourceowner=ow[sourcekey][0][leg]
     bootmask=boot_owner(keys[sourcekey],source,sourceowner,leg)
     prev=idx-1;nxt=(idx+1)%8
     previous=np.array(keys[prev]['feet'][leg]);following=np.array(keys[nxt]['feet'][leg]);target=np.rint((previous+following)/2).astype(int)
     sourcefoot=np.array(keys[sourcekey]['feet'][leg]);delta=target-sourcefoot
     sourcehip=keys[sourcekey]['hip_rows'][leg];targethip=keys[bodykey]['hip_rows'][leg]
     cuff=keys[sourcekey]['cuff_rows'][leg];knee=(sourcehip+cuff)/2
     rows=np.array([sourcehip,knee,cuff,127.],float)
     dx=np.array([0.,delta[0]*.5,delta[0],delta[0]])
     dy=np.array([targethip-sourcehip,(targethip-sourcehip+delta[1])/2.,delta[1],delta[1]])
     ty=rows+dy
     if not np.all(np.diff(ty)>0):raise ValueError(('fold',view,idx,leg,rows,ty))
     sy=np.interp(np.arange(128),ty,rows);sxshift=np.interp(sy,rows,dx)
     yy=np.floor(sy+.5).astype(int)[:,None].repeat(128,axis=1);xx=np.floor(np.arange(128)[None,:]-sxshift[:,None]+.5).astype(int)
     valid=(xx>=0)&(xx<128)&(yy>=0)&(yy<128)&(np.arange(128)[:,None]>=ty[0])&(np.arange(128)[:,None]<=ty[-1])
     mesh_controls=None
     if viewcfg.get('map_method',cfg.get('map_method'))=='rigid_boot_mesh':
      try: mapped,mesh_controls=make_map(bootmask,sourcehip,targethip,delta,keys[sourcekey].get('hip_x',[56,72])[leg])
      except ValueError as e: raise ValueError((cfg['actor'],view,idx,leg,sourcekey,str(e))) from e
      xx=mapped[:,:,0];yy=mapped[:,:,1];valid=np.ones((128,128),bool)
     xx=np.clip(xx,0,127);yy=np.clip(yy,0,127);paint=valid&sourceowner[yy,xx]&allowed
     paint &= ~bootmask[yy,xx]
     # Transparent donor pixels do not erase a leg already behind this one.
     paint &= source[yy,xx,3]>0
     result[paint]=source[yy[paint],xx[paint]];owner[paint]=leg+1;xy[paint]=np.stack((xx[paint],yy[paint]),axis=-1);rigid[paint]=0
     # Freeze complete visible boot/AA ownership as a 2D rigid plateau,
     # including an angled boot top at the same y as its separate hip.
     boot_y,boot_x=np.where(bootmask&(source[:,:,3]>0));target_x=boot_x+delta[0];target_y=boot_y+delta[1]
     within=(target_x>=0)&(target_x<128)&(target_y>=0)&(target_y<128)
     boot_y=boot_y[within];boot_x=boot_x[within];target_y=target_y[within];target_x=target_x[within]
     permitted=allowed[target_y,target_x];boot_y=boot_y[permitted];boot_x=boot_x[permitted];target_y=target_y[permitted];target_x=target_x[permitted]
     result[target_y,target_x]=source[boot_y,boot_x];owner[target_y,target_x]=leg+1;xy[target_y,target_x]=np.stack((boot_x,boot_y),axis=-1);rigid[target_y,target_x]=leg+1
     controls.append({'leg_role':'source viewerLEFT hip leg A' if leg==0 else 'source viewerRIGHT hip leg B','source_key':sourcekey,'input_path':keys[sourcekey]['path'],'input_sha256':keys[sourcekey]['sha256'],'map_method':viewcfg.get('map_method',cfg.get('map_method')),'source_rows':rows.tolist(),'target_rows':ty.tolist(),'row_dx':dx.tolist(),'rigid_boot_translation':delta.tolist(),'boot_source_center':sourcefoot.tolist(),'boot_target_center':target.tolist(),'boot_rigid_below_source_y':cuff,'visible_source_owner_only':True,'mesh_controls':mesh_controls})
    assert np.array_equal(result[~allowed&~oldlower],body[~allowed&~oldlower])
    assert np.array_equal(result[protected],body[protected])
    replay=body.copy();replay[owner==3]=0
    for leg in (0,1):
     s=ims[bridge['leg_source_keys'][leg]];m=owner==leg+1;replay[m]=s[xy[:,:,1][m],xy[:,:,0][m]]
    assert np.array_equal(replay,result)
    np.savez_compressed(dest/f'{idx:02d}-map.npz',owner=owner,source_xy=xy,allowed=allowed,old_lower=oldlower,rigid_boot=rigid)
    receipt={'frame':idx,'construction':'independent visible leg source strips; far then near compositing; exact upper/body context outside literal lower ownership','body_key':bodykey,'body_path':keys[bodykey]['path'],'body_sha256':keys[bodykey]['sha256'],'source_replay_equal':True,'protected_body_rgba_equal':True,'controls':controls,'changed_rgba_vs_body':int(np.any(result!=body,axis=2).sum())}
   frame=Image.fromarray(result);frame.save(dest/f'{idx:02d}.png');frames.append(frame)
   lab,n=label(result[:,:,3]>=24);counts=np.bincount(lab.ravel());receipt.update(hold=[9,160],output_sha256=sha(dest/f'{idx:02d}.png'),components_ge3px=[int(n) for n in counts[1:] if n>=3]);receipts.append(receipt)
  sheet=Image.new('RGBA',(1024,256));baseline=[Image.open(viewcfg['baseline_dir']+f'/{i:02d}.png').convert('RGBA') for i in range(8)]
  for i in range(8):sheet.paste(baseline[i],(128*i,0));sheet.paste(frames[i],(128*i,128))
  sheet.save(dest/'baseline-above-candidate-below.png');sheet.resize((2048,512),Image.Resampling.NEAREST).save(dest/'comparison-2x.png')
  for scale,name in ((1,'native'),(.66,'game')):emit_media(frames,dest/f'candidate-{name}',scale)
  for k,op in ow.items():
   a=np.zeros((128,128,4),np.uint8);a[op[0][0]]=(0,220,230,190);a[op[0][1]]=(255,130,30,190);Image.fromarray(a).save(dest/f'key{k}-source-owners.png')
  rec={'schema':'emberwake-four-key-visible-leg-bridges/v1','actor':cfg['actor'],'view':view,'configuration':str(Path(args.config).resolve()),'configuration_sha256':sha(args.config),'builder_sha256':sha(__file__),'native_stage':[128,128],'pivot':[64,112],'holds':[[9,160]]*8,'total_duration':[9,20],'authored_painted_key_roles':{'0':'source wide contact','2':'viewerLEFT lifted passing','4':'narrow contact','6':'viewerRIGHT lifted passing'},'bridge_limits':['nearest source-pixel maps, no hidden surface invention','boot orientation is that of named donor; no rotation or new toe roll; perview method explicitly distinguishes full2Drigidboot from distalstripplateau','source body contexts may differ slightly; exact preservation is per named body context, not one frozen upper for all frames','in-place footpaths are authored, not calibrated ground contacts','alpha connectedness and map replay do not establish art score'],'frames':receipts}
  (dest/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(view,[len(r['components_ge3px']) for r in receipts])
 (out/'config.json').write_text(Path(args.config).read_text())
if __name__=='__main__':main()
