#!/usr/bin/env python3
"""Complete fixed-canvas adjacent evidence. Flags require review, never approve art."""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from transition_contract import load_contract,pair_tuple
GROUPS={'outline':['ink'],'fabric':['cloth','cloth_light'],'teal':['teal','teal_light','teal_dark'],'copper':['copper','copper_light','copper_dark'],'cream':['cream','cream_shadow'],'skin':['skin','skin_shadow'],'eye':['eye']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(h):return tuple(bytes.fromhex(h))
def bbox(mask):
 y,x=np.where(mask)
 return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def metric(a,b,pa,pb,palette):
 opaquea=a[:,:,3]>0;opaqueb=b[:,:,3]>0;changed=np.any(a!=b,axis=2)&(opaquea|opaqueb);union=opaquea|opaqueb;inter=opaquea&opaqueb
 colors={rgb(h)for h in palette.values()};rogue=sum(1 for color in np.unique(b[opaqueb,:3],axis=0)if tuple(color)not in colors)
 mats={}
 for group,names in GROUPS.items():
  masks=[]
  for arr in [a,b]:
   mask=np.zeros(arr.shape[:2],bool)
   for n in names:
    if n in palette:mask|=np.all(arr[:,:,:3]==rgb(palette[n]),axis=2)&(arr[:,:,3]>0)
   masks.append(mask)
  x,y=masks;u=int((x|y).sum());aa=int(x.sum());bb=int(y.sum());mats[group]={'area_before':aa,'area_after':bb,'area_delta':bb-aa,'iou':float((x&y).sum()/u)if u else 1.0,'bbox_before':bbox(x),'bbox_after':bbox(y)}
 landmarks={k:math.dist(v,pb.get('landmarks',{}).get(k,v))for k,v in pa.get('landmarks',{}).items()}
 grip=math.dist(pb.get('grip',[0,0]),pb.get('hands',{}).get('front',pb.get('grip',[0,0])))
 flags=[]
 if rogue:flags.append('off_palette_color')
 if grip>0.001:flags.append('grip_target_separation')
 if max(landmarks.values(),default=0)>8:flags.append('large_landmark_step_review')
 for g,m in mats.items():
  if abs(m['area_delta'])>=8 and abs(m['area_delta'])/max(1,m['area_before'])>0.25:flags.append('material_area_step_review:'+g)
 if int(changed.sum())>900:flags.append('large_pixel_step_review')
 return {'visible_changed_pixels':int(changed.sum()),'changed_bbox':bbox(changed),'alpha_added':int((opaqueb&~opaquea).sum()),'alpha_removed':int((opaquea&~opaqueb).sum()),'silhouette_iou':float(inter.sum()/union.sum())if union.any()else 1.0,'color_material_masks':mats,'landmark_step_px':landmarks,'grip_target_separation_px':grip,'new_off_palette_color_count':rogue,'flags':flags}
def motion_contract(pose):
 # Declared source contract, not a measurement of world motion or collision.
 return {k:pose[k]for k in ['view','authored_view','direction_scope','world_root','contact_basis','ground_projection','world_motion_status','material_detail_scope','surface_frames','declared_clip_equipment','effective_equipment','equipment_selection','equipment_selection_mode','equipment_transition_policy']if k in pose}
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=Path('pilot/rigged-character/generated/manifest.json'));p.add_argument('--design',type=Path,default=Path('pilot/rigged-character/design.json'));p.add_argument('--out',type=Path,required=True);p.add_argument('--state-contract',type=Path);args=p.parse_args();base=args.manifest.resolve().parent;out=args.out
 if (out/'pairs.json').exists():raise SystemExit('Choose a fresh revision output; historical review evidence is immutable.')
 out.mkdir(parents=True,exist_ok=True);palette=json.loads(args.design.read_text())['palette'];m=json.loads(args.manifest.read_text());pairs=[];frames={};errors=[]
 for clip,c in m['clips'].items():
  for i,f in enumerate(c['frames']):
   path=base/f['png'];a=np.array(Image.open(path).convert('RGBA'));px=hashlib.sha256(a.tobytes()).hexdigest()
   if list(a.shape[:2][::-1])!=m['canvas']:errors.append({'code':'canvas_changed','clip':clip,'frame':i})
   if px!=f['pixel_sha256']:errors.append({'code':'frame_pixel_binding_changed','clip':clip,'frame':i})
   frames[(clip,i)]={'image':a,'pose':f['pose'],'path':str(path),'file_sha256':sha(path),'pixel_sha256':px,'duration_ticks':f['duration_ticks'],'source_tick':f['tick']}
  for i in range(len(c['frames'])-1):pairs.append((clip,i,clip,i+1,'adjacent'))
  if c['loop']:pairs.append((clip,len(c['frames'])-1,clip,0,'loop_wrap'))
  elif c.get('base_clip',clip.split('/')[0]) in ['slash','thrust','shoot','cast','hurt']:pairs.append((clip,len(c['frames'])-1,clip,0,'deliberate_replay_reset'))
 views={clip.split('/')[1]for clip in m['clips']}
 for view in sorted(views):
  for x,y in [('knockdown','recover'),('recover','idle'),('idle','slash'),('slash','idle'),('idle','thrust'),('thrust','idle'),('idle','shoot'),('shoot','idle'),('idle','cast'),('cast','idle'),('idle','hurt'),('hurt','idle')]:
   if x+'/'+view in m['clips']and y+'/'+view in m['clips']:pairs.append((x+'/'+view,len(m['clips'][x+'/'+view]['frames'])-1,y+'/'+view,0,'state_transition'))
 state_contract=load_contract(args.state_contract,m)if args.state_contract else None
 transition_metadata={}
 if state_contract:
  for row in state_contract['transitions']:
   pair=pair_tuple(row);pairs.append(pair);transition_metadata[pair]=row
 result=[];images={}
 for j,(ca,ia,cb,ib,kind) in enumerate(pairs):
  a=frames[(ca,ia)];b=frames[(cb,ib)];mtr=metric(a['image'],b['image'],a['pose'],b['pose'],palette);record={'id':j,'before_clip':ca,'before_frame':ia,'after_clip':cb,'after_frame':ib,'kind':kind,'metrics':mtr,'before_phase':a['pose']['phase'],'after_phase':b['pose']['phase'],'before_motion_contract':motion_contract(a['pose']),'after_motion_contract':motion_contract(b['pose']),'before_pixel_sha256':a['pixel_sha256'],'after_pixel_sha256':b['pixel_sha256'],'before_file_sha256':a['file_sha256'],'after_file_sha256':b['file_sha256']};
  if (ca,ia,cb,ib,kind)in transition_metadata:record['supported_state_contract']=transition_metadata[(ca,ia,cb,ib,kind)]
  result.append(record);images[j]=(a['image'],b['image'])
 # Stable globalcrop for DISPLAY only; metrics use whole192canvas. Fail if any visiblepixel cropped.
 crop=(0,0,192,192)
 for (clip,i),f in frames.items():
  outside=f['image'][:,:,3].copy();outside[crop[1]:crop[3],crop[0]:crop[2]]=0
  if outside.any():errors.append({'code':'display_crop_hides_source','clip':clip,'frame':i})
 sheet_rows=[];cw=392;ch=214;per=32
 for start in range(0,len(result),per):
  sheets={k:Image.new('RGBA',(cw*4,ch*8),(29,34,42,255))for k in ['pairs','overlay','difference']};draws={k:ImageDraw.Draw(v)for k,v in sheets.items()};ids=[]
  for k,row in enumerate(result[start:start+per]):
   j=row['id'];ids.append(j);a,b=images[j];x=k%4*cw;y=k//4*ch;ai=Image.fromarray(a);bi=Image.fromarray(b)
   sheets['pairs'].alpha_composite(ai.crop(crop),(x,y));sheets['pairs'].alpha_composite(bi.crop(crop),(x+196,y))
   aa=ai.copy();bb=bi.copy();aa.putalpha(aa.getchannel('A').point(lambda n:n//2));bb.putalpha(bb.getchannel('A').point(lambda n:n//2));over=Image.new('RGBA',(192,192));over.alpha_composite(aa);over.alpha_composite(bb);sheets['overlay'].alpha_composite(over.crop(crop),(x,y))
   diff=np.zeros_like(a);opa=a[:,:,3]>0;opb=b[:,:,3]>0;changed=np.any(a!=b,axis=2)&(opa|opb);diff[changed]=[240,210,30,255];diff[opb&~opa]=[60,240,150,255];diff[opa&~opb]=[245,70,160,255];sheets['difference'].alpha_composite(Image.fromarray(diff).crop(crop),(x,y))
   label=f'{j} {row["before_clip"]} {row["before_frame"]}>{row["after_frame"]} {row["kind"][:4]} Δ{row["metrics"]["visible_changed_pixels"]}'
   for kind in sheets:draws[kind].text((x+2,y+193),label,fill='white')
  paths={}
  for kind,im in sheets.items():path=out/f'{kind}-{start//per:03d}.png';im.save(path);paths[kind]={'path':str(path),'sha256':sha(path)}
  sheet_rows.append({'sheet':start//per,'pair_ids':ids,'files':paths})
 report={'schema':'complete-adjacent-sprite-evidence/v1','input_manifest':str(args.manifest.resolve()),'manifest_sha256':sha(args.manifest),'design_sha256':sha(args.design),'source_bindings':m['source_bindings'],'state_contract':state_contract,'default_boundary_scope':'Nominal clip endpoint comparisons; not evidence that a controller supports these state transitions. Explicit supported states require a bound state_contract.','frame_count':len(frames),'clip_count':len(m['clips']),'pairs':result,'sheets':sheet_rows,'binding_errors':errors,'binding_passed':not errors,'display_crop_global':list(crop),'source_camera':'No perframe centering/scaling;192canvas metrics, onefixeddisplaycrop.','material_scope':'Color-family masks acrosswholecomposite, not anatomical segmentation or trackedUV texture. Sharedcolors/occlusion can legitimately change areas.','approval':False,'limits':['Every sourceadjacency covered; pixel/landmark/material flags are reviewrequests, not aesthetic scores.','Declared grip equals authoredhandtarget; actual rasterattachment requires visualreview.','Worldroot motion, collisions/projectiles/effects and unsupportedviews are not validated by bodyPNG consistency.']}
 (out/'pairs.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'frames':len(frames),'pairs':len(result),'sheets':len(sheet_rows),'binding_errors':errors,'flagged_pairs':sum(bool(r['metrics']['flags'])for r in result)}))
if __name__=='__main__':main()
