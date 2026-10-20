from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def a(i):return np.array(Image.open(P/'inputs/authority'/f'{i:02}.png').convert('RGBA'))
def m(n):return np.array(Image.open(P/n))>0
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
base=a(3);Y,X=np.indices((128,128));torso=m('inputs/ownership/03-stable-upper-hem-owner.png');arms=m('inputs/ownership/03-complete-arm-owner.png');boots=m('inputs/ownership/03-screen-left-descending-whole-boot-target.png')|m('inputs/ownership/03-screen-right-retreating-whole-boot-target.png');protected=torso|arms|boots
# Source04actual retained rounded front thigh, bounded to cream pants and its actual cloth edge.
front_source=np.zeros((128,128),bool)
for y in range(82,88):front_source[y,51:67]=True
for y,x0,x1 in [(88,52,67),(89,51,67),(90,51,67),(91,52,67),(92,51,66),(93,50,65),(94,51,65)]:front_source[y,x0:x1+1]=True
front_source &= a(4)[...,3]>0
# Actual00rounded cream thigh, with garment/boot paint outside its literal source owner excluded.
rear_source=poly([(67,82),(76,82),(80,84),(81,87),(79,90),(70,91),(66,88),(65,85)])&(Y>=82)&(Y<=89)&(a(0)[...,3]>0)
fore_owner=poly([(48,80),(64,80),(68,85),(67,93),(48,93),(45,87)])&(Y<93)
rear_owner=poly([(64,79),(82,79),(84,85),(82,88),(65,88)])&(Y<88)
owner=(fore_owner|rear_owner)&~protected
out=base.copy();out[owner]=0;sid=np.full((128,128),3,np.int8);xy=np.stack(np.meshgrid(np.arange(128),np.arange(128)),axis=-1).astype(np.int16);layer=np.zeros((128,128),np.int8);sid[owner]=-1;xy[owner]=-1;layer[owner]=1
configs=[('rear rounded00thigh',0,rear_source,-2,-2,2),('descending rounded04thigh',4,front_source,-2,-1,3)]
receipts=[]
for name,sp,source,dx,dy,lid in configs:
 donor=a(sp);target=np.zeros((128,128),bool)
 for y,x in np.argwhere(source):
  tx,ty=x+dx,y+dy
  if 0<=tx<128 and 0<=ty<128 and owner[ty,tx]:out[ty,tx]=donor[y,x];sid[ty,tx]=sp;xy[ty,tx]=[x,y];layer[ty,tx]=lid;target[ty,tx]=True
 Image.fromarray((source*255).astype('uint8')).save(P/'inputs/donor-owners'/f'{lid}-source.png');Image.fromarray((target*255).astype('uint8')).save(P/'masks'/f'{lid}-target.png');receipts.append({'part':name,'source_phase':sp,'native_translation':[dx,dy],'source_paint_pixels':int(source.sum()),'target_pixels':int(target.sum()),'deformation':False,'scaling':False})
out[protected]=base[protected];sid[protected]=3;ys,xs=np.where(protected);xy[ys,xs]=np.stack([xs,ys],axis=-1);layer[protected]=4
assert np.array_equal(out[protected],base[protected]);assert np.array_equal(out[~owner],base[~owner])
for i in range(8):
 if i==3:Image.fromarray(out).save(P/'candidate'/f'{i:02}.png')
 else:shutil.copy2(P/'inputs/authority'/f'{i:02}.png',P/'candidate'/f'{i:02}.png')
for mask,name in [(owner,'03-proximal-trouser-owner'),(protected,'03-upper-arms-complete-boots-protected'),(boots,'03-whole-boots-protected'),(np.any(out!=base,axis=2),'03-actual-change')]:Image.fromarray((mask*255).astype('uint8')).save(P/'masks'/f'{name}.png')
np.savez_compressed(P/'maps/03-source-map.npz',source_phase=sid,source_xy=xy,layer_id=layer)
# Literal source map replay and original boot/upper alpha remain exact.
replay=np.zeros_like(base)
for y,x in np.argwhere(sid>=0):sp=int(sid[y,x]);sx,sy=xy[y,x];replay[y,x]=a(sp)[sy,sx]
assert np.array_equal(replay,out)
for sz,scale in [(128,'native'),(84,'game')]:
 for ids,name in [([2,3,4,5],'02-03-04-05'),(list(range(8)),'full8')]:
  can=Image.new('RGBA',(len(ids)*sz,2*(sz+18)),(29,34,43,255));d=ImageDraw.Draw(can)
  for row,trial in enumerate([False,True]):
   for k,i in enumerate(ids):
    im=Image.fromarray(out if trial and i==3 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.alpha_composite(im,(k*sz,row*(sz+18)+18));d.text((k*sz+3,row*(sz+18)+2),f'{"pants" if trial else "base"} {i:02}',fill='white')
  can.save(P/'proof'/f'{name}-{scale}.png')
  if sz==128 and name!='full8':can.resize((can.width*4,can.height*4),Image.Resampling.NEAREST).save(P/'proof'/f'{name}-4x.png')
 frames=[];size=(sz*2+32,sz+36)
 for i in range(8):
  can=Image.new('RGB',size,(29,34,43));d=ImageDraw.Draw(can)
  for j,trial in enumerate([False,True]):
   im=Image.fromarray(out if trial and i==3 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.paste(im,(j*(sz+16)+8,24),im);d.text((j*(sz+16)+8,5),f'{"pants" if trial else "base"} {i:02}',fill='white')
  frames.append(can)
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','160','-i','-','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'proof'/f'paired-{scale}.mp4')],stdin=subprocess.PIPE)
 for _ in range(8):
  for im in frames:
   for __ in range(9):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
(P/'CONSTRUCTION.json').write_text(json.dumps({'status':'UNSELECTED bounded03proximal trousers preview','generation_calls':0,'source_part_transfers':receipts,'original03wholeboots_transforms_unchanged':{'left_source02':[3,7],'right_source02':[-2,-6]},'both_original_boots_RGBA_and_alpha_exact':True,'original03upper_hem_complete_arm_ownership_RGBA_exact':True,'other7PNG_byte_exact':True,'new_authored_pixels':0,'phase04source_note':'Retained actual generated04proximal pants from hybrid; includes its prior12source-palette cuff-connection pixels where visible. No new03hidden anatomy authored.','source_map_replay_RGBA_exact':True,'hold':[9,160],'cycle':[9,20],'candidate03_sha256':hashlib.sha256((P/'candidate/03.png').read_bytes()).hexdigest()},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>03rounded proximal trousers trial — unselected</h1><p>Whole original03boots and original upper/hem/complete arm ownership exact. Only03pants changed. No generation or new flat-colour fill.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['02-03-04-05-native','02-03-04-05-game','full8-native','full8-game'])+''.join(f'<video controls loop autoplay muted src="paired-{s}.mp4"></video>' for s in ['native','game']))
print(json.dumps(receipts));print('changed',int(np.any(out!=base,axis=2).sum()))
