"""Guide-only opposite contact04. No generation, no boot reflection/warp, explicit authored pants."""
from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def a(i):return np.array(Image.open(P/'inputs/authority'/f'{i:02}.png').convert('RGBA'))
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
base=a(4);source2=np.array(Image.open(P/'inputs/upper/source02.png').convert('RGBA'))
arm=np.zeros((128,128),bool);armpaint=np.zeros_like(base)
for n in ['left','right']:
 m=np.array(Image.open(P/'inputs/upper'/f'{n}-arm-owner.png'))>0;arm|=m;armpaint[m]=source2[m]
armopaque=arm&(armpaint[...,3]>0)
# Literal original04 upper and garment contour, excluding old pale thigh fragments.
contours={}
for x in range(48,83):
 stop=81
 for y in range(76,82):
  r,g,b,z=[int(v) for v in base[y,x]]
  if not z or (r>90 and g>r*.72 and b>g*.65):stop=y-1;break
 contours[str(x)]=stop
stable=np.zeros((128,128),bool);stable[:76]=True
for x,y in contours.items():stable[:y+1,int(x)]=True
owner=np.zeros((128,128),bool);owner[76:]=True;owner&=~stable
# Clear all old legs through transparency before new underpaint and opaque arms.
out=base.copy();out[owner]=0
source_id=np.full((128,128),-1,np.int8);xy=np.full((128,128,2),-1,np.int16);authored=np.zeros((128,128),bool);layer=np.zeros((128,128),np.int8)
# New cream volume is a stylized projected guide, not source-recovered anatomy.
# Every authored palette entry points to one actual visible source-paint sample.
samples=[(0,78,87),(6,51,82),(6,59,88),(0,75,90),(6,57,86),(0,75,84),(6,54,84),(0,75,87),(0,72,87)]
colors=[a(i)[y,x].tolist() for i,x,y in samples]
authored_log=[]
def fill(points,color_index,layer_id,label):
 m=poly(points)&owner
 if 6<=layer_id<=12:m &= front_shape
 c=colors[color_index]
 for y,x in np.argwhere(m):
  before=out[y,x].tolist();out[y,x]=c;source_id[y,x]=-2;xy[y,x]=[-1,-1];authored[y,x]=True;layer[y,x]=layer_id
  authored_log.append({'target':[int(x),int(y)],'before':before,'after':c,'palette_sample':{'phase':samples[color_index][0],'xy':list(samples[color_index][1:])},'part':label})
# Rear screen-right thigh: connected rounded foreshortened volume, behind front leg/boots.
fill([(66,77),(72,76),(77,78),(81,80),(84,83),(84,86),(81,89),(75,89),(71,86),(67,83)],0,1,'new rear thigh silhouette')
fill([(68,78),(73,77),(78,79),(82,82),(83,85),(80,88),(75,87),(71,84)],2,2,'rear cloth shadow')
fill([(69,79),(74,78),(78,80),(81,82),(81,85),(78,87),(74,85),(71,83)],4,3,'rear rounded midtone')
fill([(70,79),(74,78),(78,80),(80,82),(79,85),(75,85),(72,83)],5,4,'rear cream light')
fill([(73,79),(76,80),(78,82),(77,84),(74,83),(72,81)],6,5,'rear cream highlight')
# Front screen-left thigh: broad rounded volume follows left hip toward forward left boot cuff.
front_shape=poly([(50,77),(57,76),(62,78),(65,82),(64,87),(60,91),(58,93),(49,94),(45,92),(44,90),(45,85),(47,80)])
fill([(50,77),(57,76),(62,78),(65,82),(64,87),(61,91),(61,96),(57,99),(49,98),(45,94),(44,90),(45,85),(47,80)],0,6,'new front thigh silhouette')
fill([(50,78),(57,77),(61,79),(63,82),(62,87),(59,91),(60,95),(56,97),(50,96),(47,93),(46,89),(47,84)],1,7,'front cloth shadow')
fill([(50,79),(56,78),(60,80),(62,83),(61,87),(58,91),(58,95),(53,96),(49,93),(47,89),(48,84)],4,8,'front rounded midtone')
fill([(51,79),(56,78),(60,81),(61,84),(59,88),(56,92),(56,94),(52,94),(49,91),(48,87),(49,83)],5,9,'front cream body')
fill([(52,80),(57,79),(60,82),(60,85),(58,88),(56,91),(52,91),(50,88),(50,84)],6,10,'front cream light')
fill([(53,81),(56,80),(58,82),(59,85),(57,88),(54,89),(51,87),(51,84)],7,11,'front highlight')
fill([(54,82),(56,82),(57,84),(56,86),(54,87),(52,85)],8,12,'front small highlight')
# Fixed declared native boot placements. Full2D alpha paint rigid; toes keep sourceSE direction.
placements=[{'name':'rear screen-right boot','source_phase':6,'source_mask':'06-boot1.png','translation':[4,-2],'layer':13}, {'name':'front screen-left supporting boot','source_phase':0,'source_mask':'00-boot1.png','translation':[-23,1],'layer':14}]
boot_visible=np.zeros((128,128),bool);boot_full=np.zeros((128,128),bool);boot_receipts=[]
for cfg in placements:
 donor=a(cfg['source_phase']);m=np.array(Image.open(P/'inputs/donor-masks'/cfg['source_mask']))>0;dx,dy=cfg['translation'];paint=m&(donor[...,3]>0);target=np.zeros((128,128),bool);sourcecoords=[]
 for y,x in np.argwhere(m):
  tx,ty=x+dx,y+dy
  if 0<=tx<128 and 0<=ty<128:boot_full[ty,tx]=1
 for y,x in np.argwhere(paint):
  tx,ty=x+dx,y+dy
  assert 0<=tx<128 and 0<=ty<128
  out[ty,tx]=donor[y,x];source_id[ty,tx]=cfg['source_phase'];xy[ty,tx]=[x,y];authored[ty,tx]=False;layer[ty,tx]=cfg['layer'];target[ty,tx]=1;sourcecoords.append([int(tx),int(ty),int(x),int(y)])
 boot_visible|=target
 ys,xs=np.where(target);cfg['target_paint_bbox']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];cfg['source_paint_pixels']=int(paint.sum());cfg['no_reflection_or_deformation']=True;boot_receipts.append(cfg)
 Image.fromarray((target*255).astype('uint8')).save(P/'guide'/f"{cfg['layer']}-boot-painted-owner.png")
# Original complete opaque forearms/gloves and fixed original blue/gold torso/hem are foreground.
out[stable]=base[stable];source_id[stable]=-1;xy[stable]=-1;authored[stable]=False;layer[stable]=0
out[armopaque]=armpaint[armopaque];source_id[armopaque]=-1;xy[armopaque]=-1;authored[armopaque]=False;layer[armopaque]=15
# For every donor boot pixel prove it remains exact, including full toes/heels. Any occlusion is declared.
for cfg in placements:
 m=np.array(Image.open(P/'guide'/f"{cfg['layer']}-boot-painted-owner.png"))>0;dx,dy=cfg['translation'];donor=a(cfg['source_phase']);occluded=[]
 for ty,tx in np.argwhere(m):
  if not np.array_equal(out[ty,tx],donor[ty-dy,tx-dx]):occluded.append([int(tx),int(ty)])
 cfg['occluded_source_paint_coordinates']=occluded;cfg['visible_complete_boot_RGBA_exact']=not occluded
assert all(not x['occluded_source_paint_coordinates'] for x in placements)
assert np.array_equal(out[stable],base[stable]);assert np.array_equal(out[armopaque],armpaint[armopaque])
Image.fromarray(out).save(P/'guide/04.png')
for mask,name in [(owner,'04-new-lower-owner'),(stable,'04-stable-upper-hem-owner'),(arm,'04-complete-old-arm-erase-owner'),(armopaque,'04-opaque-glove-foreground-owner'),(boot_full,'04-full-boot-owner'),(boot_visible,'04-boot-visible-paint'),(authored,'04-authored-visible-pants'),(np.any(out!=base,axis=2),'04-actual-change')]:Image.fromarray((mask*255).astype('uint8')).save(P/'guide'/f'{name}.png')
np.savez_compressed(P/'guide/04-construction-map.npz',source_id=source_id,source_xy=xy,layer_id=layer,authored_visible=authored)
(P/'guide/AUTHORED-PAINT-JOURNAL.json').write_text(json.dumps({'meaning':'literal new guide-only cloth drawing from source palette, not recovered hidden anatomy','strokes':authored_log,'palette_samples':[{'rgba':color,'phase':i,'source_xy':[x,y]} for color,(i,x,y) in zip(colors,samples)]},indent=2)+'\n')
(P/'guide/CONSTRUCTION.json').write_text(json.dumps({'status':'GUIDE ONLY; no generation call; stylized projected gait hypothesis','stage':[128,128],'pivot':[64,112],'source_authority':'inputs/authority/00..07.png','role_chronology':'00 viewer-right boot forward;02 viewer-left swing;proposed04 viewer-left boot forward;06 viewer-right swing','boot_placements':boot_receipts,'upper_and_hem_contour':{'all_rows_through':75,'column_last_protected_y':contours},'old_lower_erased':True,'complete_old_arm_ownership':'cleared before new legs within lower owner; only opaque source02 glove paint composed above pants','new_visible_palette_drawn_pixels':int(authored.sum()),'new_hidden_anatomy_claim':False,'horizontal_reflection':False,'boot_warp':False,'source_00_rear_boot0':'rejected as partial visible donor;125paint pixels in11x15 bbox','old04_unchanged_in_frozen_inputs':True,'other_phase_edits':False},indent=2)+'\n')
# Fair fixed-time proof: only guide04 substitutes; all other poses unchanged snapshots.
for i in range(8):
 if i==4:Image.fromarray(out).save(P/'guide'/f'frame-{i:02}.png')
 else:shutil.copy2(P/'inputs/authority'/f'{i:02}.png',P/'guide'/f'frame-{i:02}.png')
def make_sheet(ids,sz,name):
 can=Image.new('RGBA',(len(ids)*sz,2*(sz+18)),(29,34,43,255));d=ImageDraw.Draw(can)
 for row,trial in enumerate([False,True]):
  for k,i in enumerate(ids):
   im=Image.fromarray(out) if trial and i==4 else Image.fromarray(a(i));im=im.resize((sz,sz),Image.Resampling.NEAREST);can.alpha_composite(im,(k*sz,row*(sz+18)+18));d.text((k*sz+3,row*(sz+18)+2),f'{"guide" if trial else "control"} {i:02}',fill='white')
 can.save(P/'proof'/name);return can
for sz,label in [(128,'native'),(84,'game')]:
 im=make_sheet([0,4],sz,f'contact00-vs04-{label}.png')
 if sz==128:im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(P/'proof/contact00-vs04-4x.png')
 im=make_sheet([2,3,4,5,6],sz,f'02-03-04-05-06-{label}.png')
 if sz==128:im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(P/'proof/02-03-04-05-06-3x.png')
 make_sheet(list(range(8)),sz,f'full8-{label}.png')
# Full8 paired loop is a hypothesis visualization, not revised03/05 bridges.
for sz,label in [(128,'native'),(84,'game')]:
 size=(sz*2+32,sz+36);frames=[]
 for i in range(8):
  can=Image.new('RGB',size,(29,34,43));d=ImageDraw.Draw(can)
  for j,trial in enumerate([False,True]):
   im=(Image.fromarray(out) if trial and i==4 else Image.fromarray(a(i))).resize((sz,sz),Image.Resampling.NEAREST);can.paste(im,(j*(sz+16)+8,24),im);d.text((j*(sz+16)+8,5),f'{"guide" if trial else "control"} {i:02}',fill='white')
  frames.append(can)
 proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','160','-i','-','-an','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'proof'/f'guide-loop-{label}.mp4')],stdin=subprocess.PIPE)
 for _ in range(8):
  for im in frames:
   for __ in range(9):proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
(P/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img,video{image-rendering:pixelated}</style><h1>GUIDE ONLY: Rowan SE opposite contact04</h1><p>No model call. Only04 replaced by a source-boot plus authored-pants projected gait hypothesis. Adjacent03/05 unchanged. All9/160s holds fixed.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['contact00-vs04-native','contact00-vs04-game','02-03-04-05-06-native','02-03-04-05-06-game'])+''.join(f'<p>{n}</p><video src="{n}.mp4" controls loop autoplay muted></video>' for n in ['guide-loop-native','guide-loop-game']))
print(json.dumps(boot_receipts,indent=2));print('visible new guide pants pixels',int(authored.sum()))
