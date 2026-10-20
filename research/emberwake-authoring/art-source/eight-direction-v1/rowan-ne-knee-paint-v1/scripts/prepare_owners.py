from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];Y,X=np.indices((128,128))
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def polygon(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0

def shift(a,dx,dy):
 out=np.zeros_like(a);ys,xs=np.where(a)
 for y,x in zip(ys,xs):
  if 0<=x+dx<128 and 0<=y+dy<128:out[y+dy,x+dx]=True
 return out
# Literal inclusive native row owners, authored from the visible cream surfaces.
# They follow each existing projection; no anatomical recovery or pose refit.
runs={
3:{'screen-right descending trouser':[(82,69,78),(83,68,78),(84,68,78),(85,68,77),(86,67,77),(87,67,76),(88,67,76),(89,66,75),(90,65,74),(91,66,73)],'mostly occluded screen-left trouser neck':[(82,62,65),(83,63,66),(84,64,67)]},
4:{'diagonal front cream knee':[(82,66,75),(83,65,74),(84,65,74),(85,65,74),(86,65,74),(87,64,73),(88,64,73),(89,66,73),(90,68,72),(91,70,72)],'short partly occluded rear cream knee':[(82,55,61),(83,55,62),(84,55,63),(85,56,63),(86,56,62),(87,57,62),(88,58,62)]},
5:{'screen-left/front short cream cap':[(82,50,58),(83,51,59),(84,51,59),(85,52,60),(86,52,59),(87,53,58),(88,54,57)],'crossing screen-right cream cap':[(82,63,68),(83,63,68),(84,64,68),(85,63,67),(86,62,66),(87,63,65),(88,63,65)]},
6:{'screen-left extended cream trouser':[(82,46,57),(83,45,56),(84,44,57),(85,44,57),(86,44,57),(87,44,56),(88,44,56),(89,44,56),(90,44,55),(91,44,55),(92,44,55),(93,44,54)],'screen-right raised boot cream cap':[(82,67,71),(83,67,71)]}}
bootpolys={
3:[[(50,81),(58,81),(63,84),(65,90),(62,96),(59,99),(55,98),(51,93),(49,87)],[(64,92),(77,92),(79,99),(82,103),(82,110),(76,113),(64,113),(63,106),(63,98)]],
4:[[(60,89),(66,89),(68,94),(66,97),(70,102),(70,109),(65,113),(56,110),(53,105),(55,99),(58,94)],[(70,92),(75,92),(76,98),(72,102),(67,99)]],
5:[[(53,89),(61,89),(64,92),(66,99),(66,105),(62,109),(53,109),(50,105),(50,95)],[(69,83),(75,83),(77,90),(75,97),(70,102),(64,101),(62,95),(64,89)]],
6:[[(43,94),(57,94),(58,100),(57,105),(59,110),(59,116),(43,116),(42,111),(43,103)],[(72,81),(78,81),(78,86),(80,92),(78,98),(68,99),(65,95),(64,89),(66,85),(69,84),(72,84)]]}
# These are observed painted attachment/cuff/boot witnesses, not inferred joints.
landmarks={
3:{'cream_attachment_right':[73,83],'cream_knee_plane_right':[72,87],'cuff_right':[70,92],'boot_toe_right':[79,107],'rear_cuff_left':[57,84],'rear_boot_lower_paint':[58,96]},
4:{'cream_attachment_front':[69,83],'cream_knee_plane_front':[69,87],'cuff_front':[65,91],'boot_toe_front':[65,108],'rear_cream_plane':[60,85],'rear_cuff':[61,89]},
5:{'cream_attachment_left':[55,83],'cream_knee_plane_left':[57,86],'cuff_left':[58,89],'boot_toe_left':[59,105],'crossing_cream_plane':[66,84],'crossing_cuff':[66,88]},
6:{'cream_attachment_left':[52,83],'cream_knee_plane_left':[51,88],'cuff_left':[51,94],'boot_lowest_sole_left':[46,113],'raised_cream_cap':[69,82],'raised_cuff':[72,84],'raised_boot_low_point':[70,97]}}
# Explicit1–2 native-pixel contour envelopes; no blind dilation.03 expands
# its free/right cream edge;04 expands its free/right knee and short-left cap.
# These include missing cloth alpha, with complete boot/upper owners subtracted.
envelope_rows={
3:[(83,79,79),(84,79,80),(85,78,79),(86,78,79),(87,77,78),(88,77,78),(89,76,77),(90,75,76),(91,74,75)],
4:[(82,76,76),(83,76,76),(84,75,76),(85,75,76),(86,75,75),(87,74,75),(88,74,74),(89,74,74),(90,73,73),(91,73,73),(83,54,54),(84,53,54),(85,54,54),(86,55,55),(87,56,56),(88,56,57)]}
records=[];grid_allowed=Image.new('L',(256,256));grid_protected=Image.new('L',(256,256));overlays=[]
for k,i in enumerate([3,4,5,6]):
 a=arr(P/f'inputs/source-frames/{i:02}.png');z=np.load(P/f'inputs/source-maps/{i:02}-source.npz',allow_pickle=False);upper=np.isin(z['layer_id'],[0,4,5,6]);bob=[0,1,1,0,0,1,1,0][i];swing=[0,-1,-2,-1,0,1,2,1][i]
 arms=shift(mask(P/'inputs/source-masks/left-arm-owner.png'),swing,bob)|shift(mask(P/'inputs/source-masks/right-arm-owner.png'),-swing,bob)
 upper|=arms|(Y<=80)
 # Exact painted gold rim points which the old foreground-knee owner reasserted.
 hem_extra=[(63,82),(64,82)]if i==3 else[]
 for x,y in hem_extra:upper[y,x]=True
 boot=mask(P/f'inputs/source-masks/{i:02}-complete-boot.png')
 for pts in bootpolys[i]:boot|=polygon(pts)
 raw=np.zeros((128,128),bool);parts=[]
 for role,rows in runs[i].items():
  part=np.zeros((128,128),bool)
  for y,x0,x1 in rows:part[y,x0:x1+1]=True
  part&=~(upper|boot);raw|=part;parts.append({'role':role,'inclusive_native_rows':rows,'allowed_pixels_after_protection':int(part.sum())})
 base_allowed=raw.copy();envelope=np.zeros((128,128),bool)
 for y,x0,x1 in envelope_rows.get(i,[]):envelope[y,x0:x1+1]=True
 envelope&=~(upper|boot);added=envelope&~base_allowed;allowed=base_allowed|envelope;protected=~allowed
 # Bound every newly permitted pixel to at most2native pixels from the old
 # explicitly traced cream owner. This is an audit, not automatic expansion.
 oldcoords=np.argwhere(base_allowed)
 for y,x in np.argwhere(added):assert np.min(np.max(np.abs(oldcoords-[y,x]),axis=1))<=2
 Image.fromarray(added.astype('uint8')*255).save(P/f'owners/{i:02}-authored-cloth-envelope-additions.png')
 # Every original boot region, upper owner and all outside negative space stays protected.
 assert not np.any(allowed&(upper|boot));Image.fromarray(allowed.astype('uint8')*255).save(P/f'owners/{i:02}-allowed-trouser-knee-cuff.png');Image.fromarray(protected.astype('uint8')*255).save(P/f'owners/{i:02}-protected-complete.png');Image.fromarray(upper.astype('uint8')*255).save(P/f'owners/{i:02}-upper-hem-gloves.png');Image.fromarray(boot.astype('uint8')*255).save(P/f'owners/{i:02}-complete-boot-protected-region.png')
 grid_allowed.paste(Image.fromarray(allowed.astype('uint8')*255),((k%2)*128,(k//2)*128));grid_protected.paste(Image.fromarray(protected.astype('uint8')*255),((k%2)*128,(k//2)*128))
 # Alpha overlay is explanatory proof only, never the edit target.
 b=Image.fromarray(a);ol=Image.new('RGBA',(128,128));v=np.zeros_like(a);v[allowed]=[255,0,190,135];ol=Image.fromarray(v);b=Image.alpha_composite(b,ol);overlays.append(b)
 validmarks={}
 for name,point in landmarks[i].items():
  x,y=point;validmarks[name]={'native_xy':point,'original_RGBA':a[y,x].tolist(),'observed_positive_alpha':bool(a[y,x,3]>0),'role':'paint witness / authored attachment cue; not measured anatomical joint'}
 ys,xs=np.where(allowed);records.append({'phase':i,'cell':{'column':k%2,'row':k//2,'native_origin':[(k%2)*128,(k//2)*128],'edit4x_origin':[(k%2)*512,(k//2)*512]},'source_PNG_sha256':hashlib.sha256((P/f'inputs/source-frames/{i:02}.png').read_bytes()).hexdigest(),'allowed_pixels':int(allowed.sum()),'initial_positive_only_owner_pixels':int(base_allowed.sum()),'explicit_envelope_inclusive_rows':envelope_rows.get(i,[]),'authored_envelope_added_pixels':int(added.sum()),'authored_envelope_added_transparent_pixels':int((added&(a[...,3]==0)).sum()),'maximum_new_envelope_distance_native_pixels':2 if added.any() else 0,'allowed_bounds_inclusive':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'existing_transparent_pixels_inside_authored_cloth_owner':int(((a[...,3]==0)&allowed).sum()),'all_other_negative_space_protected':True,'complete_boot_protection_polygons':bootpolys[i],'upper_manual_gold_rim_points':hem_extra,'parts':parts,'landmarks':validmarks})
for name,im in [('allowed-grid',grid_allowed),('protected-grid',grid_protected)]:im.save(P/f'owners/{name}-native.png');im.resize((1024,1024),Image.Resampling.NEAREST).save(P/f'owners/{name}-4x.png')
# Human proofs keep native coordinate registration and full actor paint visible.
for size,label in [(128,'native'),(256,'2x'),(84,'game')]:
 can=Image.new('RGBA',(4*size,2*(size+22)),(235,230,215,255));d=ImageDraw.Draw(can)
 for col,i in enumerate([3,4,5,6]):
  for row,im in enumerate([Image.open(P/f'inputs/source-frames/{i:02}.png').convert('RGBA'),overlays[col]]):
   can.alpha_composite(im.resize((size,size),Image.Resampling.NEAREST),(col*size,row*(size+22)+22));d.text((col*size+3,row*(size+22)+3),f'{i:02} '+('actual target'if row==0 else'magenta = allowed'),fill='black')
 can.save(P/f'proof/targets-and-owners-{label}.png')
# Landmarks are annotated on complete target copies, not skeletal substitutes.
can=Image.new('RGBA',(4*512,560),(235,230,215,255));d=ImageDraw.Draw(can)
for col,rec in enumerate(records):
 i=rec['phase'];can.alpha_composite(Image.open(P/f'inputs/source-frames/{i:02}.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST),(col*512,28));d.text((col*512+4,5),f'{i:02} native128; crosses in fixed stage',fill='black')
 for n,(name,w)in enumerate(rec['landmarks'].items(),1):
  x,y=w['native_xy'];xx=col*512+x*4+2;yy=y*4+30;d.line((xx-4,yy,xx+4,yy),fill=(20,255,240,255),width=1);d.line((xx,yy-4,xx,yy+4),fill=(20,255,240,255),width=1);d.text((xx+5,yy-6),str(n),fill=(20,255,240,255))
can.save(P/'proof/native-landmarks-4x.png')
(P/'OWNERSHIP.json').write_text(json.dumps({'status':'PREPARATION ONLY; no model call','coordinate_convention':'Native128 pixel centers; row ranges inclusive; grid03/04 on top05/06 below; no per-pose fit','native_stage':[128,128],'native_grid':[256,256],'edit_target':[1024,1024],'whole_grid_upscale':[4,1],'pivot_per_cell':[64,112],'protected_rule':'Complement of explicit allowed cream owners; preserves original RGBA including all outside negative space. Complete boot regions and full visible upper/hem/gloves subtract from cloth owners.','scope':'Connected rounded cream trousers only; no pose/foot/boot material or toe reflection change','frames':records},indent=2)+'\n')
print(json.dumps([{'phase':r['phase'],'allowed':r['allowed_pixels'],'bounds':r['allowed_bounds_inclusive'],'transparent_inside_owner':r['existing_transparent_pixels_inside_authored_cloth_owner'],'all_landmark_alpha_positive':all(w['observed_positive_alpha']for w in r['landmarks'].values())}for r in records]))
