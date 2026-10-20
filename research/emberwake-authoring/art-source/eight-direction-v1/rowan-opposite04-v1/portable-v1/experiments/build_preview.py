from pathlib import Path
import hashlib,json,shutil,subprocess
import numpy as np
from scipy.ndimage import label,binary_dilation
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];O=P/'preview'
for n in ['frames','masks','maps']:(O/n).mkdir(exist_ok=True)
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def a(i):return np.array(Image.open(P/'inputs/authority'/f'{i:02}.png').convert('RGBA'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
raw_im=Image.open(P/'generation/raw.png').convert('RGBA');raw=np.array(raw_im)
cc,n=label(raw[...,3]>16,np.ones((3,3)));ct=np.bincount(cc.ravel());ct[0]=0;keep=binary_dilation(cc==int(ct.argmax()),iterations=1)&(raw[...,3]>0)
r=raw.copy();r[~keep]=0;g=np.array(Image.fromarray(r).resize((128,128),Image.Resampling.NEAREST));Image.fromarray(g).save(O/'registered-generated04.png')
base=a(4);owner=np.array(Image.open(P/'inputs/guide/04-new-lower-owner.png'))>0;stable=np.array(Image.open(P/'inputs/guide/04-stable-upper-hem-owner.png'))>0
arm=np.array(Image.open(P/'inputs/guide/04-complete-old-arm-erase-owner.png'))>0;armopaque=np.array(Image.open(P/'inputs/guide/04-opaque-glove-foreground-owner.png'))>0;armnegative=arm&~armopaque
# Literal connected painted lower volume behind moved/overlapping gloves. Old complete arm
# ownership is an erase step BEFORE body composition, not a final hole-punch through trousers.
bodypoly=poly([(49,79),(61,78),(66,82),(67,89),(64,97),(53,99),(48,94),(47,86)])|poly([(68,79),(79,78),(84,82),(84,87),(80,91),(71,90),(67,85)])
behind=owner&armnegative&bodypoly&(g[...,3]>0)
out=base.copy();out[owner]=0;out[owner]=g[owner];out[owner&armnegative]=0;out[behind]=g[behind];out[armopaque]=base[armopaque];out[stable]=base[stable]
assert np.array_equal(out[~owner],base[~owner]);assert np.array_equal(out[stable],base[stable]);assert np.array_equal(out[armopaque],base[armopaque])
assert not np.any(out[...,3][owner&armnegative&~behind])
for i in range(8):
 if i==4:Image.fromarray(out).save(O/'frames'/f'{i:02}.png')
 else:shutil.copy2(P/'inputs/authority'/f'{i:02}.png',O/'frames'/f'{i:02}.png')
for mask,n in [(keep,'raw-mainbody-owner'),(owner,'04-lower-owner'),(stable,'04-stable-upper-hem-owner'),(arm,'04-complete-old-arm-erase-owner'),(armopaque,'04-opaque-gloves-protected'),(armnegative,'04-negative-arm-owner'),(bodypoly,'04-literal-painted-thigh-volume'),(behind,'04-generated-body-behind-arm'),(np.any(out!=base,axis=2),'04-actual-change')]:Image.fromarray((mask*255).astype('uint8')).save(O/'masks'/f'{n}.png')
selected=(owner&~armnegative&~armopaque | behind)&(g[...,3]>0);xy=np.full((128,128,2),-1,np.int16);coord=np.floor((np.arange(128)+.5)*raw_im.width/128).astype(int)
for y,x in np.argwhere(selected):xy[y,x]=[coord[x],coord[y]];assert np.array_equal(out[y,x],raw[coord[y],coord[x]])
np.savez_compressed(O/'maps/04-raw-source.npz',raw_source_xy=xy,generated_visible=selected)
def sheet(ids,sz,name):
 can=Image.new('RGBA',(len(ids)*sz,2*(sz+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,trial in enumerate([False,True]):
  for k,i in enumerate(ids):
   im=Image.fromarray(out if trial and i==4 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.alpha_composite(im,(k*sz,row*(sz+18)+18));d.text((k*sz+3,row*(sz+18)+2),f'{"new04" if trial else "control"} {i:02}',fill='white')
 can.save(O/name);return can
for sz,scale in [(128,'native'),(84,'game')]:
 for ids,name in [([0,4],'contact00-vs04'),([2,3,4,5,6],'02-03-04-05-06'),(list(range(8)),'full8')]:
  im=sheet(ids,sz,f'{name}-{scale}.png')
  if sz==128 and name!='full8':im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(O/f'{name}-3x.png')
 # Exact native/game normal clock proof;03/05/07 stay fixed.
 frames=[];size=(sz*2+32,sz+36)
 for i in range(8):
  can=Image.new('RGB',size,(29,34,43));d=ImageDraw.Draw(can)
  for j,trial in enumerate([False,True]):
   im=Image.fromarray(out if trial and i==4 else a(i)).resize((sz,sz),Image.Resampling.NEAREST);can.paste(im,(j*(sz+16)+8,24),im);d.text((j*(sz+16)+8,5),f'{"new04" if trial else "control"} {i:02}',fill='white')
  frames.append(can)
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','160','-i','-','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(O/f'paired-{scale}.mp4')],stdin=subprocess.PIPE)
 for _ in range(8):
  for im in frames:
   for __ in range(9):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
# Native side-by-side exact target, guide, returned registration, protected-upper composite.
can=Image.new('RGBA',(512,146),(29,34,43,255));d=ImageDraw.Draw(can)
for j,(title,im) in enumerate([('original04',Image.fromarray(base)),('guide04',Image.open(P/'inputs/guide/04.png')),('registered raw',Image.fromarray(g)),('protected04',Image.fromarray(out))]):can.alpha_composite(im,(j*128,18));d.text((j*128+3,2),title,fill='white')
can.save(O/'registration-composition-native.png');can.resize((2048,584),Image.Resampling.NEAREST).save(O/'registration-composition-4x.png')
# Connected image support is an ownership check, not physical gait validation.
body_cc,body_n=label(out[...,3]>16,np.ones((3,3)));body_sizes=np.bincount(body_cc.ravel());body_sizes[0]=0
receipt={'status':'PREVIEW ONLY; not selected or deployed','new04_calls_authorized':1,'new04_calls_used':1,'raw_actual_dimensions':list(raw_im.size),'single_whole_stage_registration':{'resize':[128,128],'scale':[128,raw_im.width],'translation':[0,0],'interpolation':'nearest','per_pose_fit':False},'original04_bbox':list(Image.fromarray(base).getbbox()),'guide04_bbox':list(Image.open(P/'inputs/guide/04.png').getbbox()),'registered_raw_bbox':list(Image.fromarray(g).getbbox()),'composite04_bbox':list(Image.fromarray(out).getbbox()),'source_guide_authored_visible_pants_pixels':276,'new_composite_authored_pixels':0,'whole_upper_hem_RGBA_exact':True,'complete_visible_glove_RGBA_exact':True,'complete_old_arm_ownership_erased_before_new_body':True,'new_generated_body_behind_negative_arm_pixels':int(behind.sum()),'new_generated_body_behind_negative_arm_xy':[[int(x),int(y)] for y,x in np.argwhere(behind)],'source_map':'maps/04-raw-source.npz','sole_drift_note':'Compare fixed-stage registration; returned painting placement is not fitted to guide. All visible role/stance differences retained for review.','hold':[9,160],'cycle':[9,20],'proxy':[84,128],'png_sha256':sha(O/'frames/04.png'),'other7_png_byte_identical':[{'phase':i,'exact':sha(O/'frames'/f'{i:02}.png')==sha(P/'inputs/authority'/f'{i:02}.png')} for i in range(8) if i!=4],'alpha_support_component_sizes':sorted([int(x) for x in body_sizes[1:] if x],reverse=True)}
(O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>Rowan SE04 generated opposite-contact trial</h1><p>Preview only. One call. Only04 differs; fixed05 and07 untouched. Nine160Hz ticks per pose.</p>'+''.join(f'<p>{name}</p><img src="{name}.png">' for name in ['contact00-vs04-native','contact00-vs04-game','02-03-04-05-06-native','02-03-04-05-06-game','registration-composition-native'])+''.join(f'<p>normal clock {scale}</p><video controls autoplay loop muted src="paired-{scale}.mp4"></video>' for scale in ['native','game']))
print(json.dumps(receipt,indent=2))
