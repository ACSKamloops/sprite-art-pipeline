from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
P=Path(__file__).resolve().parents[1]
for n in ['preview/control-frames','preview/frames']:(P/n).mkdir(parents=True,exist_ok=True)
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n).convert('L'))>0
def save(arr,n):Image.fromarray(arr).save(P/n)
raw=a('generation/raw.png');r=raw.copy();cc,n=label(r[...,3]>16,np.ones((3,3)));counts=np.bincount(cc.ravel());counts[0]=0;keep=binary_dilation(cc==int(counts.argmax()),iterations=1)&(r[...,3]>0);r[~keep]=0;save(keep.astype('uint8')*255,'masks/raw-actor-owner.png');save(r,'generation/raw-main-actor.png')
g=np.array(Image.fromarray(r).resize((128,128),Image.Resampling.NEAREST));g[g[...,3]==0]=0;save(g,'generation/registered03.png')
base=a('inputs/A/03.png');repair=m('inputs/masks/03-lower-repair-owner.png');torso=m('inputs/masks/03-stable-upper-hem-owner.png');arm=m('inputs/masks/03-complete-arm-owner.png');opaque=m('inputs/masks/03-opaque-gloves-protected.png');negative=arm&~opaque;Y,X=np.indices((128,128));rf,gf,bf=[g[...,k].astype(float) for k in range(3)];cream=(g[...,3]>0)&(rf>70)&(gf>.70*rf)&(bf>.63*gf);behind=negative&repair&cream&(Y>=80)&(X>=47)&(X<=84)
out=base.copy();out[repair]=0;out[repair]=g[repair];out[negative&repair]=0;out[behind]=g[behind];out[opaque]=base[opaque];out[torso]=base[torso];out[out[...,3]==0]=0
assert np.array_equal(out[~repair],base[~repair]);assert np.array_equal(out[torso],base[torso]);assert np.array_equal(out[opaque],base[opaque])
for i in range(8):
 src=P/'inputs/A'/f'{i:02}.png'
 if i==4:src=P/'inputs/new04.png'
 if i==7:src=P/'inputs/new07.png'
 shutil.copy2(src,P/'preview/control-frames'/f'{i:02}.png')
 if i==3:Image.fromarray(out).save(P/'preview/frames/03.png')
 else:shutil.copy2(src,P/'preview/frames'/f'{i:02}.png')
for mask,name in [(repair,'03-lower-repair-owner'),(torso,'03-stable-upper-hem-owner'),(arm,'03-complete-old-arm-owner'),(opaque,'03-opaque-gloves-protected'),(negative,'03-negative-arm-owner'),(behind,'03-body-behind-glove'),(np.any(out!=base,axis=2),'03-actual-change')]:save(mask.astype('uint8')*255,f'masks/{name}.png')
gen=(repair&~arm)|behind;coord=np.floor((np.arange(128)+.5)*raw.shape[0]/128).astype(int);xy=np.full((128,128,2),-1,np.int16)
for y,x in np.argwhere(gen):xy[y,x]=[coord[x],coord[y]];assert np.array_equal(out[y,x],g[y,x])
np.savez_compressed(P/'maps/03-raw-source.npz',raw_source_xy=xy,generated_owner=gen)
def sheet(ids,size,prefix):
 can=Image.new('RGBA',(len(ids)*size,2*(size+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,bank in enumerate(['preview/control-frames','preview/frames']):
  for k,i in enumerate(ids):
   im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.alpha_composite(im,(k*size,row*(size+18)+18));d.text((k*size+3,row*(size+18)+2),f'{"control" if row==0 else "new03"} {i:02}',fill='white')
 can.save(P/f'proof/{prefix}.png');return can
for ids,prefix in [(list(range(8)),'full8'),([2,3,4,5],'02-03-04-05')]:
 im=sheet(ids,128,prefix+'-native');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/f'proof/{prefix}-3x.png');sheet(ids,84,prefix+'-game')
can=Image.new('RGBA',(384,146),(29,34,43,255));d=ImageDraw.Draw(can)
for i,(name,path) in enumerate([('original03','inputs/A/03.png'),('approved guide','generation/complete-painted-guide03.png'),('actual new03','preview/frames/03.png')]):can.alpha_composite(Image.open(P/path).convert('RGBA'),(i*128,18));d.text((i*128+3,2),name,fill='white')
can.save(P/'proof/original-guide-actual03-native.png');can.resize((1536,584),Image.Resampling.NEAREST).save(P/'proof/original-guide-actual03-4x.png')
for prefix,ids in [('paired',list(range(8))),('focused',[2,3,4,5])]:
 for size,scale in [(128,'native'),(84,'game')]:
  folder=P/f'proof/{prefix}-{scale}-ticks';folder.mkdir(exist_ok=True);reps=8
  for tick in range(len(ids)*9*reps):
   i=ids[(tick//9)%len(ids)];can=Image.new('RGB',(2*size+32,size+36),(29,34,43));d=ImageDraw.Draw(can)
   for col,bank in enumerate(['preview/control-frames','preview/frames']):
    im=Image.open(P/bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*(size+16)+8,24),im);d.text((col*(size+16)+8,5),f'{"control" if col==0 else "new03"} {i:02}',fill='white')
   can.save(folder/f'{tick:04}.png')
  subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','160','-i',str(folder/'%04d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/f'proof/{prefix}-{scale}.mp4')],check=True)
measure={}
for label,path in [('source02','inputs/A/02.png'),('guide03','generation/complete-painted-guide03.png'),('new03','preview/frames/03.png'),('new04','inputs/new04.png')]:
 image=a(path);mask=image[...,3]>128;measure[label]={}
 for side,region in [('screen-left',(X<65)&(Y>=90)),('screen-right',(X>=65)&(Y>=90))]:
  yy,xx=np.where(mask&region);measure[label][side]={'lower_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]}
receipt={'status':'UNSELECTED actual03 cleanup preview; parent review before packaging','provider':'built-in OpenAI ImageGen','generation_calls':1,'further_calls_allowed':0,'raw_dimensions':list(Image.fromarray(raw).size),'single_whole_stage_registration':{'resize_to':[128,128],'scale':[128,raw.shape[0]],'translation':[0,0],'method':'nearest','per_pose_fit':False},'raw_actor_owner':{'threshold':16,'connectivity':8,'one_raw_pixel_fringe_dilation':True,'retained_alpha_pixels':int(keep.sum()),'removed_noise_alpha_pixels':int(((raw[...,3]>0)&~keep).sum())},'stable_upper_blue_gold_hem_RGBA_exact':True,'original03_complete_visible_gloves_RGBA_exact':True,'outside_lower_repair_RGBA_exact':True,'body_behind_transparent_glove_pixels':int(behind.sum()),'candidate03_sha256':hashlib.sha256((P/'preview/frames/03.png').read_bytes()).hexdigest(),'other7_control_PNG_bytes_exact':all((P/'preview/frames'/f'{i:02}.png').read_bytes()==(P/'preview/control-frames'/f'{i:02}.png').read_bytes() for i in range(8) if i!=3),'hold':[9,160],'cycle':[9,20],'fullcycle_overrides':[3,4,7],'projected_lower_measurements':measure,'guide_conformance_note':'Actual generation descends the screen-left boot farther than guide; inspect possible premature new04 contact before accepting. No corrective per-pose transform applied.'}
(P/'PREVIEW-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Actual03 cleanup trial</title><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>One-call03 cleanup: actual unselected trial</h1><p>Original03 control left, actualnew03 right. Both banks contain new04 and exactnew07. Each stage9/160s.</p>'+''.join(f'<p>{n}</p><video src="{n}.mp4" autoplay loop muted controls></video>' for n in ['paired-native','paired-game','focused-native','focused-game'])+'<p>02→03→new04→05</p><img src="02-03-04-05-native.png"><p>Full8</p><img src="full8-native.png"><p>Original,guide,actual03</p><img src="original-guide-actual03-native.png">')
