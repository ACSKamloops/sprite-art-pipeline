from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def a(i):return np.array(Image.open(P/'inputs/authority'/f'{i:02}.png').convert('RGBA'))
def poly(pts):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
base=a(4);stable=np.array(Image.open(P/'inputs/ownership/04-stable-upper-hem-owner.png'))>0;glove=np.array(Image.open(P/'inputs/ownership/04-opaque-gloves-protected.png'))>0
front_keep=np.zeros((128,128),bool)
for y in range(76,88):front_keep[y,50:68]=True
for y,x0,x1 in [(88,52,67),(89,51,67),(90,51,67),(91,52,67),(92,52,66),(93,53,65),(94,55,65),(95,58,63),(96,58,63)]:front_keep[y,x0:x1+1]=True
rear_keep=poly([(69,78),(80,78),(83,83),(83,87),(80,90),(73,90),(69,86),(67,82)])
# Complete transparent old-boot ownership, separate from the retained complete painted proximal trousers.
front_old=poly([(44,86),(53,86),(61,89),(69,94),(71,102),(72,119),(43,119)])
rear_old=poly([(61,82),(85,82),(89,90),(87,105),(65,106),(61,95)])
erase=(front_old|rear_old)&~front_keep&~rear_keep&~stable&~glove
out=base.copy();out[erase]=0
sid=np.full((128,128),4,np.int8);xy=np.stack(np.meshgrid(np.arange(128),np.arange(128)),axis=-1).astype(np.int16);layer=np.zeros((128,128),np.int8);sid[erase]=-1;xy[erase]=-1;layer[erase]=1
cfgs=[{'name':'rear screen-right whole boot','source_phase':6,'source_mask':'06-boot1.png','translation':[-1,-1],'toe_x_source_target':[83,82],'sole_y_source_target':[102,101],'source_sole_anchor':[75,102],'target_sole_anchor':[74,101],'layer':2},{'name':'front screen-left whole boot','source_phase':0,'source_mask':'00-boot1.png','translation':[-18,4],'toe_x_source_target':[86,68],'sole_y_source_target':[111,115],'source_sole_anchor':[76,111],'target_sole_anchor':[58,115],'layer':4}]
boot_masks=[]
def boot(cfg):
 donor=a(cfg['source_phase']);mask=np.array(Image.open(P/'inputs/donor-masks'/cfg['source_mask']))>0;dx,dy=cfg['translation'];paint=mask&(donor[...,3]>0);target=np.zeros((128,128),bool)
 sx,sy=cfg['source_sole_anchor'];tx,ty=cfg['target_sole_anchor'];assert donor[sy,sx,3]>16 and base[ty,tx,3]>16 and [sx+dx,sy+dy]==[tx,ty]
 for y,x in np.argwhere(paint):
  xx,yy=x+dx,y+dy;assert 0<=xx<128 and 0<=yy<128;out[yy,xx]=donor[y,x];sid[yy,xx]=cfg['source_phase'];xy[yy,xx]=[x,y];layer[yy,xx]=cfg['layer'];target[yy,xx]=True
 ys,xs=np.where(target);cfg['source_visible_paint_pixels']=int(paint.sum());cfg['target_bbox']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];cfg['whole_boot_rigid_RGBA_copy']=True;cfg['reflection']=False;cfg['scale']=[1,1];boot_masks.append((cfg,target))
boot(cfgs[0])
# Actual generated foreground thigh occludes the rear boot's hidden inner cuff; no hidden paint invented.
restore=front_keep&(base[...,3]>0);out[restore]=base[restore];sid[restore]=4;ys,xs=np.where(restore);xy[ys,xs]=np.stack([xs,ys],axis=-1);layer[restore]=3
boot(cfgs[1])
out[stable|glove]=base[stable|glove];sid[stable|glove]=4;ys,xs=np.where(stable|glove);xy[ys,xs]=np.stack([xs,ys],axis=-1);layer[stable|glove]=5
# No cloth underpaint has been authored yet: this literal layer trial shows any real gap first.
for cfg,m in boot_masks:
 donor=a(cfg['source_phase']);dx,dy=cfg['translation'];occluded=[]
 for y,x in np.argwhere(m):
  if not np.array_equal(out[y,x],donor[y-dy,x-dx]):occluded.append([int(x),int(y)])
 cfg['occluded_by_foreground_thigh_or_boot']=occluded;cfg['exposed_rgba_source_exact']=True
 Image.fromarray((m*255).astype('uint8')).save(P/'masks'/f"{cfg['layer']}-whole-boot-target.png")
assert np.array_equal(out[stable|glove],base[stable|glove])
actual=np.any(out!=base,axis=2);allowed=erase|front_keep|rear_keep
for _,m in boot_masks:allowed|=m
assert np.array_equal(out[~allowed],base[~allowed])
for y,x in np.argwhere(out[...,3]>0):
 source=int(sid[y,x]);sx,sy=xy[y,x];assert source>=0 and np.array_equal(out[y,x],a(source)[sy,sx])
for i in range(8):
 if i==4:Image.fromarray(out).save(P/'candidate'/f'{i:02}.png')
 else:shutil.copy2(P/'inputs/authority'/f'{i:02}.png',P/'candidate'/f'{i:02}.png')
for m,n in [(erase,'04-old-generated-boots-erased'),(front_keep,'04-generated-front-pants-preserved'),(rear_keep,'04-generated-rear-pants-preserved'),(allowed,'04-whole-hybrid-owner'),(actual,'04-actual-change')]:Image.fromarray((m*255).astype('uint8')).save(P/'masks'/f'{n}.png')
np.savez_compressed(P/'maps/04-source-map.npz',source_phase=sid,source_xy=xy,layer_id=layer)
(P/'CONSTRUCTION.json').write_text(json.dumps({'status':'UNSELECTED source-boot hybrid preview','source04':'inputs/authority/04.png','model_calls':0,'base04_proximal_generated_pants':'retained, except actual front/rear complete boot occlusion','boot_placements':cfgs,'literal_layers':['fixed generated04 complete pose','complete old boot transparency erase','rear complete06boot','actual generated04 front pants foreground','front complete00boot','actual fixed original04 torso/hem/gloves'],'authored_connection_pixels':0,'bounds_anchor_note':'Exact integer translations preserve existing04rightmost toeX and lowest soleY for each boot. Source sole anchor maps to an actual existing04sole pixel. No scaling, reflection, silhouette fit or stance change. Source sole contour differs as complete source paint is restored.','other7_unchanged':True,'hold':[9,160],'cycle':[9,20]},indent=2)+'\n')
# Fair chronology and contact comparisons, native and84proxy.
def sheet(ids,sz,name):
 can=Image.new('RGBA',(len(ids)*sz,2*(sz+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,trial in enumerate([False,True]):
  for k,i in enumerate(ids):
   im=Image.fromarray(out if trial and i==4 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.alpha_composite(im,(k*sz,row*(sz+18)+18));d.text((k*sz+3,row*(sz+18)+2),f'{"hybrid" if trial else "as-is"} {i:02}',fill='white')
 can.save(P/'proof'/name);return can
for sz,scale in [(128,'native'),(84,'game')]:
 for ids,name in [([3,4,5],'03-04-05'),([0,4],'00-vs04'),(list(range(8)),'full8')]:
  can=sheet(ids,sz,f'{name}-{scale}.png')
  if sz==128 and name!='full8':can.resize((can.width*4,can.height*4),Image.Resampling.NEAREST).save(P/'proof'/f'{name}-4x.png')
 frames=[];size=(sz*2+32,sz+36)
 for i in range(8):
  can=Image.new('RGB',size,(29,34,43));d=ImageDraw.Draw(can)
  for j,trial in enumerate([False,True]):
   im=Image.fromarray(out if trial and i==4 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.paste(im,(j*(sz+16)+8,24),im);d.text((j*(sz+16)+8,5),f'{"hybrid" if trial else "as-is"} {i:02}',fill='white')
  frames.append(can)
 proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','160','-i','-','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'proof'/f'paired-{scale}.mp4')],stdin=subprocess.PIPE)
 for _ in range(8):
  for im in frames:
   for __ in range(9):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>Source boot hybrid04 — preview only</h1><p>Original00/06complete boots anchored at generated04toe/sole extents. Generated proximal pants/upper retained. No generation, reflection, scaling or new stance. No authored cuff join yet.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['03-04-05-native','03-04-05-game','00-vs04-native','00-vs04-game','full8-native'])+''.join(f'<video controls autoplay muted loop src="paired-{s}.mp4"></video>' for s in ['native','game']))
print(json.dumps(cfgs,indent=2));print('changed',int(actual.sum()))
