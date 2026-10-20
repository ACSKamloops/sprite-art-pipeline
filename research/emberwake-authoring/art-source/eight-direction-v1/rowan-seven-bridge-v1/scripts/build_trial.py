from pathlib import Path
import json,hashlib,shutil,subprocess
from fractions import Fraction
import numpy as np
from scipy.ndimage import label,binary_dilation
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
for n in ['masks','maps','proof/paired-native-frames','proof/paired-game-frames','proof/triplet-native-frames','proof/triplet-game-frames']:(P/n).mkdir(parents=True,exist_ok=True)
def load(n):return np.array(Image.open(P/n).convert('RGBA'))
def mask(n):return np.array(Image.open(P/n).convert('L'))>0
def save(a,n):Image.fromarray(a).save(P/n)
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
raw=load('generation/raw.png');r=raw.copy();labs,n=label(r[...,3]>16,np.ones((3,3)));counts=np.bincount(labs.ravel());counts[0]=0;body=labs==int(counts.argmax());keep=binary_dilation(body,iterations=1)&(r[...,3]>0)
# Measured non-main components are minute alpha noise, not accessories. Raw remains intact.
r[~keep]=0;save(keep.astype('uint8')*255,'masks/raw-actor-owner.png');save(r,'generation/raw-main-actor.png')
g=np.array(Image.fromarray(r).resize((128,128),Image.Resampling.NEAREST));g[g[...,3]==0]=0;save(g,'generation/registered07.png')
base=load('inputs/A/07.png');repair=mask('guide/07-lower-repair-owner.png');torso=mask('guide/07-stable-upper-hem-owner.png');arm=mask('guide/07-complete-arm-owner.png');opaque=mask('guide/07-opaque-gloves-protected.png');negative=arm&~opaque
Y,X=np.indices((128,128));rf=g[...,0].astype(float);gf=g[...,1].astype(float);bf=g[...,2].astype(float)
cream=(g[...,3]>0)&(rf>70)&(gf>0.70*rf)&(bf>0.63*gf)
behind=negative&repair&cream&(Y>=80)&(X>=47)&(X<=84)
# Clear obsolete lower pixels first and paint the entire replacement lower area, including alpha0 erasure.
out=base.copy();out[repair]=0;out[repair]=g[repair]
# Complete arm erase owner removes candidate-arm remains. Opaque original gloves overlay last.
# Real new trouser body underpaint is retained where the old transparent arm owner intersects it.
out[negative&repair]=0;out[behind]=g[behind];out[opaque]=base[opaque];out[torso]=base[torso]
out[out[...,3]==0]=0
assert np.array_equal(out[~repair],base[~repair]);assert np.array_equal(out[torso],base[torso]);assert np.array_equal(out[opaque],base[opaque])
for i in range(8):
 if i==7:save(out,'trial/07.png')
 else:shutil.copy2(P/'inputs/A'/f'{i:02}.png',P/'trial'/f'{i:02}.png')
changed=np.any(out!=base,axis=2)
for m,name in [(repair,'07-lower-repair-owner'),(torso,'07-stable-upper-hem-owner'),(arm,'07-complete-old-part-arm-owner'),(opaque,'07-opaque-gloves-protected'),(negative,'07-negative-arm-owner'),(behind,'07-generated-body-behind-glove'),(changed,'07-actual-change')]:save(m.astype('uint8')*255,f'masks/{name}.png')
gen=repair&~arm;gen|=behind;coord=np.floor((np.arange(128)+.5)*raw.shape[0]/128).astype(int);xy=np.full((128,128,2),-1,np.int16)
for y,x in np.argwhere(gen):xy[y,x]=[coord[x],coord[y]];assert np.array_equal(out[y,x],r[coord[y],coord[x]])
np.savez_compressed(P/'maps/07-raw-source.npz',raw_source_xy=xy,generated_owner=gen)
# Equal-size source and candidate rows; every unchanged stage remains byte-identical.
def sheet(ids,size,prefix):
 can=Image.new('RGBA',(len(ids)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['inputs/A','trial']):
  for k,i in enumerate(ids):
   im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.alpha_composite(im,(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"source" if row==0 else "trial"} {i:02}',fill='white')
 can.save(P/f'proof/{prefix}.png');return can
for ids,prefix in [(list(range(8)),'full8'),([6,7,0],'06-07-00')]:
 im=sheet(ids,128,prefix+'-native');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/f'proof/{prefix}-3x.png');sheet(ids,84,prefix+'-game')
# Every stage holds for exactly9 frames at160Hz;8 stage cycle is72/160=9/20s.
for prefix,ids in [('paired',list(range(8))),('triplet',[6,7,0])]:
 for size,scale in [(128,'native'),(84,'game')]:
  folder=P/f'proof/{prefix}-{scale}-frames';reps=8 if prefix=='paired' else 12
  for tick in range(len(ids)*9*reps):
   i=ids[(tick//9)%len(ids)];can=Image.new('RGB',(2*size+32,size+36),(29,34,43));d=ImageDraw.Draw(can)
   for col,bank in enumerate(['inputs/A','trial']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*(size+16)+8,24),im);d.text((col*(size+16)+8,5),f'{"source" if col==0 else "trial"} {i:02}',fill='white')
   can.save(folder/f'{tick:04}.png')
  subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','160','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/f'proof/{prefix}-{scale}.mp4')],check=True)
receipt={'status':'UNSELECTED07-only semantic cleanup trial; awaiting parent art inspection before packaging','built_in_calls_used':1,'additional_calls_allowed':0,'stage':[128,128],'pivot':[64,112],'single_whole_stage_registration':{'raw_dimensions':list(Image.fromarray(raw).size),'resize_to':[128,128],'scale':[128,raw.shape[0]],'translation':[0,0],'method':'nearest','per_pose_fit':False},'raw_actor_owner':{'threshold':16,'connectivity':8,'main_alpha_pixels':int(body.sum()),'one_raw_pixel_fringe_dilation':True,'kept_alpha_pixels':int(keep.sum()),'removed_alpha_noise_pixels':int(((raw[...,3]>0)&~keep).sum()),'original_raw_preserved':True},'upper_ownership':{'all_RGBA_outside_lower_owner_exact':True,'stable_upper_blue_gold_hem_exact':True,'all_original_opaque_gloves_exact':True,'full_old_arm_erase_owner':True,'generated_body_behind_transparent_glove_owner_pixels':int(behind.sum()),'behind_coordinates':[[int(x),int(y)] for y,x in np.argwhere(behind)]},'changed07_pixels':int(changed.sum()),'original07_bbox':list(Image.fromarray(base).getbbox()),'registered07_bbox':list(Image.fromarray(g).getbbox()),'trial07_bbox':list(Image.fromarray(out).getbbox()),'trial07_sha256':sha('trial/07.png'),'hold':[9,160],'cycle':[9,20],'game_proxy':[84,128],'other_seven_byte_exact':[{'phase':i,'exact':sha(f'trial/{i:02}.png')==sha(f'inputs/A/{i:02}.png')} for i in range(8) if i!=7]}
(P/'TRIAL-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(P/'TIMING.json').write_text(json.dumps({'stage':[128,128],'pivot':[64,112],'frames':[f'trial/{i:02}.png' for i in range(8)],'holds':[[9,160]]*8,'total_cycle':[9,20],'native_height':128,'game_proxy_height':84},indent=2)+'\n')
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rowan07 bridge trial</title><style>body{background:#1d222b;color:white;font:16px sans-serif}video,img{image-rendering:pixelated}video{margin-right:16px}</style><h1>Unselected Rowan SE07 bridge trial</h1><p>Source left, trial right. Only07 changes. Each phase holds9/160s, cycle9/20s. Native128 and game proxy84px. No runtime or art approval claimed.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" autoplay loop muted controls></video>' for n in ['paired-native','paired-game','triplet-native','triplet-game'])+'<p>All8 source top, trial bottom</p><img src="full8-native.png"><p>06→07→00 source top, trial bottom</p><img src="06-07-00-native.png">')
print(json.dumps(receipt,indent=2))
