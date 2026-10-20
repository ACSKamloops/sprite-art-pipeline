from pathlib import Path
import shutil,json,hashlib,subprocess
import numpy as np
from scipy.ndimage import label,binary_dilation
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];O=P/'final-torso-protected-v1';O.mkdir(exist_ok=True)
for n in ['trial','masks','maps','paired-native-frames','paired-game-frames','triplet-native-frames','triplet-game-frames']:(O/n).mkdir(exist_ok=True)
def arr(n):return np.array(Image.open(P/n).convert('RGBA'))
def save(a,n):Image.fromarray(a).save(O/n)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
raw=Image.open(P/'generation/raw.png').convert('RGBA');r=np.array(raw)
cc,n=label(r[...,3]>16,np.ones((3,3)));ct=np.bincount(cc.ravel());ct[0]=0;keep=binary_dilation(cc==int(ct.argmax()),iterations=1)&(r[...,3]>0)
r[~keep]=0;Image.fromarray(r).save(O/'registered-mainbody-raw.png')
g=np.array(Image.fromarray(r).resize((128,128),Image.Resampling.NEAREST));save(g,'registered-generated05.png')
base=arr('inputs/A/05.png');repair=np.array(Image.open(P/'audit/05-waist-lower-owner.png'))>0
arm=np.array(Image.open(P/'audit/05-complete-gloves-owner.png'))>0
conf=json.loads((P/'scripts/torso-contour.json').read_text());torso=np.zeros((128,128),bool);torso[:conf['all_stage_rows_through']+1]=True
for x,y in conf['additional_column_last_protected_y'].items():torso[:int(y)+1,int(x)]=True
repair &= ~torso
# Complete visible approved gloves are immutable. Their alpha0 erase owner is applied separately;
# cream body paint can occupy only the literal authorized behind-arm waist intersection.
arm_opaque=arm&(base[...,3]>0)
arm_negative=arm&~arm_opaque
Y,X=np.indices((128,128));rf=g[...,0].astype(float);gf=g[...,1].astype(float);bf=g[...,2].astype(float)
cream=(g[...,3]>0)&(rf>70)&(gf>0.70*rf)&(bf>0.63*gf)
behind=arm_negative&repair&cream&(Y>=80)&(X>=47)&(X<=84)
out=base.copy();out[repair]=g[repair]
out[arm_negative&repair]=0
out[behind]=g[behind]
out[arm_opaque]=base[arm_opaque]
# Outside literal lower repair, all old RGBA remains exact. All opaque glove pixels exact.
assert np.array_equal(out[~repair],base[~repair]);assert np.array_equal(out[arm_opaque],base[arm_opaque])
assert not np.any(out[...,3][arm_negative&repair&~behind])
changed=np.any(out!=base,axis=2)
for i in range(8):
 dst=O/'trial'/f'{i:02}.png'
 if i==5:Image.fromarray(out).save(dst)
 else:shutil.copy2(P/'inputs/A'/f'{i:02}.png',dst)
for a,n in [(repair,'05-lower-repair-owner'),(arm,'05-complete-old-part-arm-owner'),(arm_opaque,'05-opaque-gloves-protected'),(arm_negative,'05-negative-arm-owner'),(behind,'05-generated-body-behind-glove'),(changed,'05-actual-change'),(torso,'05-stable-torso-hem-owner')]:save(a.astype('uint8')*255,f'masks/{n}.png')
# Frozen raw map witnesses every selected generated pixel after the single full-stage transform.
coord=np.floor((np.arange(128)+0.5)*raw.width/128).astype(int);xy=np.full((128,128,2),-1,np.int16)
gen=(repair&~arm)&(g[...,3]>0) | behind
for y,x in np.argwhere(gen):xy[y,x]=[coord[x],coord[y]];assert np.array_equal(out[y,x],r[coord[y],coord[x]])
np.savez_compressed(O/'maps/05-raw-source.npz',raw_source_xy=xy,generated_visible=gen)
# Chronology rows: frozen control then fresh05 trial, all8 and focused04/05/06.
def sheet(ids,size,path):
 w=len(ids)*size;can=Image.new('RGBA',(w,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['inputs/A','final-torso-protected-v1/trial']):
  for k,i in enumerate(ids):
   im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.alpha_composite(im,(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"A" if row==0 else "trial"} {i:02}',fill='white')
 can.save(O/path)
 return can
for ids,prefix in [(list(range(8)),'full8'),([4,5,6],'04-05-06')]:
 im=sheet(ids,128,prefix+'-native.png');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(O/(prefix+'-3x.png'));sheet(ids,84,prefix+'-game.png')
# Normal-speed paired loops. Both panels always share exactly nine160Hz ticks per phase.
for prefix,ids in [('paired',list(range(8))),('triplet',[4,5,6])]:
 for sz,scale in [(128,'native'),(84,'game')]:
  dest=O/f'{prefix}-{scale}-frames'
  for k,i in enumerate(ids):
   can=Image.new('RGB',(sz*2+32,sz+36),(29,34,43));d=ImageDraw.Draw(can)
   for j,bank in enumerate(['inputs/A','final-torso-protected-v1/trial']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((sz,sz),Image.Resampling.NEAREST);can.paste(im,(j*(sz+16)+8,24),im);d.text((j*(sz+16)+8,5),f'{"A" if j==0 else "trial"} {i:02}',fill='white')
   can.save(dest/f'{k:02}.png')
  # 8 full loops or 12 triplet repetitions; each true frame hold is9/160sec.
  reps=8 if prefix=='paired' else 12;seq=dest/'sequence';seq.mkdir(exist_ok=True)
  for k in range(len(ids)*reps):shutil.copy2(dest/f'{k%len(ids):02}.png',seq/f'{k:03}.png')
  cmd=['ffmpeg','-y','-loglevel','error','-framerate','160/9','-i',str(seq/'%03d.png'),'-r','160','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(O/f'{prefix}-{scale}.mp4')]
  subprocess.run(cmd,check=True)
receipt={'status':'UNSELECTED bounded05 trial; only one new generation call','raw_actual_dimensions':list(raw.size),'single_registration':{'whole_stage_resize':[128,128],'scale':[128,raw.width],'method':'nearest','translation':[0,0],'per_pose_fit':False},'raw_mainbody_component':{'threshold':16,'connectivity':8,'edge_alpha_preservation':'one raw pixel dilation intersect alpha>0','kept_raw_alpha_pixels':int(keep.sum()),'removed_raw_alpha_pixels':int(((np.array(raw)[...,3]>0)&~keep).sum())},'upper_protection':{'all_RGBA_outside_lower_owner_exact':True,'all_opaque_glove_RGBA_exact':True,'full_old_arm_erase_owner_retained':True,'all_RGBA_in_frozen_A05_torso_hem_contour_exact':bool(np.array_equal(out[torso],base[torso])),'generated_behind_glove_pixels':int(behind.sum()),'generated_behind_glove_coordinates':[[int(x),int(y)] for y,x in np.argwhere(behind)],'authored_pixels':0,'body_underpaint_authority':'new generated lower paint, inside literal repair only; not recovered hidden source'},'changed05_pixels':int(changed.sum()),'original_A05_bbox':list(Image.fromarray(base).getbbox()),'registered_generated_bbox':list(Image.fromarray(g).getbbox()),'trial05_bbox':list(Image.fromarray(out).getbbox()),'hold':[9,160],'cycle':[9,20],'proxy':[84,128],'unchanged_other_seven':[{'phase':i,'byte_exact':sha(O/'trial'/f'{i:02}.png')==sha(P/'inputs/A'/f'{i:02}.png')} for i in range(8) if i!=5]}
(O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}video,img{image-rendering:pixelated}</style><h1>Rowan SE05 bridge trial — unselected</h1><p>Left A, right fresh05 trial. Same9/160s hold per frame.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" controls loop autoplay muted></video>' for n in ['paired-native','paired-game','triplet-native','triplet-game'])+'<p>Full8 native chronology</p><img src="full8-native.png"><p>04→05→06</p><img src="04-05-06-native.png">')
print(json.dumps(receipt,indent=2))
