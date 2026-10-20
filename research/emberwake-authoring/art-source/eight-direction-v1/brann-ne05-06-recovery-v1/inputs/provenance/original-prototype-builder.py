"""One authorized05 Q-donor prototype; frozen06/other6 remain unchanged."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/brann-full-lower-v1');B=R/'portable-donor07-v1';T=R/'prototype05-donor07-v1'
for n in ['inputs/control','inputs/provenance','frames','parts','masks','maps','proof']:(T/n).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def poly(points):
 m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
for i in range(8):shutil.copy2(B/'frames'/f'{i:02}.png',T/'inputs/control'/f'{i:02}.png')
for name in ['05.json','05.npz','05-allowed.png','05-body.png','05-branch-0-source-mask.png','05-branch-1-source-mask.png']:shutil.copy2(C/'ne/maps'/name,T/'inputs/provenance'/name)
shutil.copy2(C/'registered/ne/00.png',T/'inputs/provenance/registered00.png');shutil.copy2(C/'manual-loops-v3/masks/ne-05-accessory-visible.png',T/'inputs/provenance/visible-sash05.png');shutil.copy2(B/'masks/source07-complete-visible-boot-owner.png',T/'inputs/provenance/source07-boot-owner.png')
original=json.loads((C/'ne/project.json').read_text());cel=original['cels']['paint5'];under=np.array([original['palette'][k]for k in cel['pixels']],dtype='uint8').reshape(128,128,4);png(T/'inputs/provenance/original05-underpaint.png',under);save(T/'inputs/provenance/ORIGINAL-UNDERPAINT-ORIGIN.json',{'readonly_project':str(C/'ne/project.json'),'project_file_sha256':sha(C/'ne/project.json'),'cel':'paint5','RGBA_sha256':hashlib.sha256(under.tobytes()).hexdigest(),'palette_RGBA_used':sorted({tuple(int(v)for v in c)for c in under.reshape(-1,4)})})
src=arr(T/'inputs/control/05.png');donor=arr(T/'inputs/control/07.png');reg=arr(T/'inputs/provenance/registered00.png');allowed=np.array(Image.open(T/'inputs/provenance/05-allowed.png').convert('L'))>0;sash=np.array(Image.open(T/'inputs/provenance/visible-sash05.png').convert('L'))>0;protected=~allowed|sash;yy,xx=np.mgrid[:128,:128]
oldmap=np.load(T/'inputs/provenance/05.npz');Pvisible=(oldmap['owner']==0)&(src[:,:,3]>0)
def inv_shift(sm,dx,dy,plateau):
 ty=yy+3;a=1+dy/(plateau-80);sy=np.where(ty<80,ty,np.where(ty<plateau+dy,(ty+dy*80/(plateau-80))/a,ty-dy));t=np.clip((sy-80)/(plateau-80),0,1);sx=np.floor(xx-dx*t+.5).astype('int16');sy=np.floor(sy+.5).astype('int16');good=(sx>=0)&(sx<128)&(sy>=0)&(sy<128);own=np.zeros((128,128),bool);own[good]=sm[sy[good],sx[good]];return own&allowed,np.stack([sx,sy],-1)
p_source=np.array(Image.open(T/'inputs/provenance/05-branch-0-source-mask.png').convert('L'))>0;q_source=np.array(Image.open(T/'inputs/provenance/05-branch-1-source-mask.png').convert('L'))>0
Pown,Pmap=inv_shift(p_source,8,-2,93);Qoldown,Qmap=inv_shift(q_source,-3,3,93);P=np.zeros_like(src)
for y,x in np.argwhere(Pown):sx,sy=Pmap[y,x];P[y,x]=reg[sy,sx]
# Exact old branch0 map is retained, including its whole original boot plateau.
assert np.array_equal(Pmap[Pvisible],oldmap['source_xy'][Pvisible]);assert np.array_equal(P[Pvisible],reg[oldmap['source_xy'][:,:,1][Pvisible],oldmap['source_xy'][:,:,0][Pvisible]])
png(T/'parts/complete-P-source-layer-UNCHANGED.png',P)
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
Pcomposite=over(P,under);assert np.array_equal(Pcomposite[Pvisible],src[Pvisible])
# Old Q owns its COMPLETE inverse target, including transparent source places.
# Clear it, then reveal the existing full P source layer at the original map.
# The original underpaint is retained behind P, never as an exposed old-Q tail.
remove=Qoldown&~protected;out=src.copy();out[remove]=0
reveal=remove&(P[:,:,3]>0);out[reveal]=Pcomposite[reveal]
# Keep actual original P-cloth underpaint where the old Q owner crosses that
# existing P polygon. It is retained source art, not a newly flat drawn patch.
pcloth=poly([(50,76),(65,76),(62,90),(50,92)])&allowed
under_reveal=remove&pcloth&(out[:,:,3]==0);out[under_reveal]=under[under_reveal]
base_after=out.copy();png(T/'parts/05-after-complete-oldQ-removal-P-reveal.png',out)
# Bounded shaded gray source07 proximal underlay; not recovered hidden anatomy.
sp=np.array([[69,83],[76,83],[77,86],[73,88],[69,87],[73,85]],float);tp=np.array([[62,81],[74,81],[76,84],[70,90],[62,89],[69,85]],float);tris=[[5,0,1],[5,1,2],[5,2,3],[5,3,4],[5,4,0]];cloth=np.zeros_like(src);clothmap=np.full((128,128,2),-1,dtype='int16');cmask=np.zeros((128,128),bool)
for tri in tris:
 s=sp[tri];t=tp[tri];inv=np.linalg.inv(np.vstack((t.T,np.ones(3))))
 for y in range(int(t[:,1].min()),int(t[:,1].max())+1):
  for x in range(int(t[:,0].min()),int(t[:,0].max())+1):
   w=inv@np.array([x,y,1])
   if w.min()<-1e-8 or protected[y,x]or Pvisible[y,x]:continue
   sx,sy=np.floor(w@s+.5).astype(int);cloth[y,x]=donor[sy,sx];clothmap[y,x]=[sx,sy];cmask[y,x]=True
out[cmask]=cloth[cmask];preboot=out.copy();png(T/'parts/05-before-Q-source-over.png',preboot);png(T/'parts/source07-projected-gray-underlay.png',cloth)
# The exact same complete07 boot owner as the retained06. One[-7,0]
# translation, no reflection/scaling/clipping; Q is allowed in foreground.
sm=np.array(Image.open(T/'inputs/provenance/source07-boot-owner.png').convert('L'))>0;boot=np.zeros_like(src);bm=np.full((128,128,2),-1,dtype='int16');bown=np.zeros((128,128),bool)
for sy,sx in np.argwhere(sm):
 tx,ty=int(sx)-7,int(sy)
 if not(0<=tx<128 and 0<=ty<128):raise AssertionError('Clipped full boot owner')
 boot[ty,tx]=donor[sy,sx];bm[ty,tx]=[sx,sy];bown[ty,tx]=True
assert not np.any(bown&protected&(boot[:,:,3]>0));active=bown&(boot[:,:,3]>0);out[active]=over(boot,out)[active];out[protected]=src[protected];out[out[:,:,3]==0]=0
occludes=active&Pvisible;assert occludes.sum()==9
# Existing P is preserved as a full retained source layer; visible P outside
# actual Q foreground occlusion remains exact. No shoe is trimmed for it.
assert np.array_equal(out[Pvisible&~occludes],src[Pvisible&~occludes])
actual_owner=remove|cmask|active|reveal|under_reveal;assert np.array_equal(out[~actual_owner],src[~actual_owner]);assert np.array_equal(out[protected],src[protected])
for i in range(8):
 if i==5:png(T/'frames/05.png',out)
 else:shutil.copy2(T/'inputs/control'/f'{i:02}.png',T/'frames'/f'{i:02}.png')
for n,m in [('old-Q-complete-removal-owner',remove),('P-complete-layer-owner',Pown),('P-current-visible-owner',Pvisible),('P-source-revealed-after-oldQ-removal',reveal),('Q-new-complete-target-owner',bown),('Q-source07-complete-owner',sm),('Q-over-current-visible-P-nine',occludes),('Q-over-complete-P-layer',active&(P[:,:,3]>0)),('shaded-proximal-cloth-owner',cmask),('upper-sash-protected',protected),('actual-change',np.any(out!=src,axis=2))]:png(T/'masks'/f'{n}.png',m.astype('uint8')*255)
png(T/'parts/source07-boot-translated-minus7-0.png',boot)
np.savez_compressed(T/'maps/05.npz',complete_P_source_xy=Pmap,old_Q_source_xy=Qmap,cloth_source_xy=clothmap,new_Q_source_xy=bm)
witness=[]
for y,x in np.argwhere(occludes):
 sx,sy=map(int,bm[y,x]);px,py=map(int,Pmap[y,x]);witness.append({'target':[int(x),int(y)],'source07_Q_xy':[sx,sy],'source07_Q_RGBA':donor[sy,sx].tolist(),'original05_visible_P_RGBA':src[y,x].tolist(),'retained_P_layer_registered00_xy':[px,py],'retained_P_layer_RGBA':P[y,x].tolist(),'source_over_under_RGBA':preboot[y,x].tolist(),'final_RGBA':out[y,x].tolist()})
save(T/'maps/NINE-P-OCCLUSION-WITNESSES.json',witness)
# Literal source samples for every projected cloth and complete boot texel.
records=[]
for role,mask,mp in [('new-gray-cloth',cmask,clothmap),('complete07-Q-boot',bown,bm)]:
 for y,x in np.argwhere(mask):
  sx,sy=map(int,mp[y,x]);records.append({'role':role,'target':[int(x),int(y)],'source07_xy':[sx,sy],'source07_RGBA':donor[sy,sx].tolist(),'before_Q_RGBA':preboot[y,x].tolist(),'final_RGBA':out[y,x].tolist()})
save(T/'maps/ALL-Q-SOURCE-WITNESSES.json',records)
recipe={'status':'one authorized05 prototype; parent inspection pending, no editor or score','new05_sha256':sha(T/'frames/05.png'),'source05_sha256':sha(T/'inputs/control/05.png'),'unchanged06_sha256':sha(T/'frames/06.png'),'all_other7_PNG_bytes_exact':all((T/'frames'/f'{i:02}.png').read_bytes()==(T/'inputs/control'/f'{i:02}.png').read_bytes()for i in range(8)if i!=5),'actual_changed_RGBA_pixels':int(np.any(out!=src,axis=2).sum()),'upper_and_sash_RGBA_exact':True,'P_complete_layer_registered00_projection':{'dx':8,'dy':-2,'plateau_source_y':93,'hip_y':80,'common_lower_translation':[0,-3],'source_mask':'inputs/provenance/05-branch-0-source-mask.png','complete_layer':'parts/complete-P-source-layer-UNCHANGED.png','no_P_repositioning_or_deformation_added':True},'old_Q_complete_removal_owner':'masks/old-Q-complete-removal-owner.png','old_Q_negative_places_removed':int((remove&(src[:,:,3]==0)).sum()),'P_layer_revealed_after_Q_removal_pixels':int(reveal.sum()),'Q_complete_source07_boot_translation':[-7,0],'complete_boot_nonzero_texels':int((sm&(donor[:,:,3]>0)).sum()),'Q_scaling_reflection_or_boot_clipping':False,'actual_visible_P_occlusion_pixels':9,'visible_P_occlusion_witnesses':'maps/NINE-P-OCCLUSION-WITNESSES.json','complete_P_layer_under_Q_nonzero_pixels':int((active&(P[:,:,3]>0)).sum()),'P_visible_RGBA_exact_outside_9_Q_occlusions':True,'cloth_source_controls':sp.tolist(),'cloth_target_controls':tp.tolist(),'cloth_triangles':tris,'cloth_source':'inputs/control/07.png actual visible charcoal trouser texels','cloth_new_coverage':'declared bounded projected underpaint, not recovered hidden anatomy','source_map':'maps/05.npz','all_source07_witnesses':'maps/ALL-Q-SOURCE-WITNESSES.json','unchanged_timing':{'hold':[9,160],'cycle':[9,20]},'limits':['Source00 P/Q semantic masks are inherited paint ownership; projected layers do not prove hidden limb anatomy.','Previously occluded P paint is actual registered00 source-part paint at its unchanged existing map, not original05 hidden anatomy recovery.','The old Q owner includes transparent negative places; no old shoe pixels are left protected simply by source-row math.','All six ambiguous frozen06 tail witnesses are unchanged.','Review04→05 as well as05→06 and06→07; new earlier boot plane can worsen the entry.'],'model_calls':0,'canonical_writes':0}
save(T/'RECIPE.json',recipe)
# Context: currentcontrol has already-retained06. Only05 differs in the trial.
forest=Image.open(R/'inputs/forest-ground-crop.png').convert('RGBA');backs=[('light',(232,231,218,255)),('dark',(24,27,25,255)),('forest',None)]
for size in [128,256,84]:
 h=size+20;canvas=Image.new('RGB',(4*size,6*h),(232,231,218));d=ImageDraw.Draw(canvas)
 for bi,(label,bg)in enumerate(backs):
  for vi,(vn,folder)in enumerate([('control',T/'inputs/control'),('trial',T/'frames')]):
   row=bi*2+vi
   for j,i in enumerate([4,5,6,7]):
    z=forest.copy()if bg is None else Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(folder/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST if size>=128 else Image.Resampling.LANCZOS);canvas.paste(z.convert('RGB'),(j*size,row*h+20));d.text((j*size+2,row*h+3),f'{vn}{i:02} {label}',fill='black')
 canvas.save(T/'proof'/f'04-05-06-07-before-after-{size}.png')
# Enlarged lower actual04/old05/new05/frozen06/frozen07 on the same light.
box=(43,77,90,113);scale=7;w=(box[2]-box[0])*scale;canvas=Image.new('RGB',(5*w,(box[3]-box[1])*scale+24),(232,231,218));d=ImageDraw.Draw(canvas)
for j,(label,path)in enumerate([('04 exact',T/'frames/04.png'),('old05',T/'inputs/control/05.png'),('new05',T/'frames/05.png'),('06 exact',T/'frames/06.png'),('07 exact',T/'frames/07.png')]):
 z=Image.new('RGBA',(128,128),(232,231,218,255));z.alpha_composite(Image.open(path).convert('RGBA'));canvas.paste(z.crop(box).resize((w,(box[3]-box[1])*scale),Image.Resampling.NEAREST).convert('RGB'),(j*w,24));d.text((j*w+4,3),label,fill='black')
canvas.save(T/'proof/lower04-old05-new05-06-07-7x.png')
# All8forest beforeafter and all requested adjacentpairs on three contrasts.
for size in [128,84]:
 h=size+20;canvas=Image.new('RGB',(8*size,2*h),(232,231,218));d=ImageDraw.Draw(canvas)
 for row,folder in enumerate([T/'inputs/control',T/'frames']):
  for i in range(8):
   z=forest.copy();z.alpha_composite(Image.open(folder/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST if size==128 else Image.Resampling.LANCZOS);canvas.paste(z.convert('RGB'),(i*size,row*h+20));d.text((i*size+2,row*h+3),f'{"old"if row==0 else"trial"}{i:02}',fill='black')
 canvas.save(T/'proof'/f'full8-before-after-{size}.png')
 canvas=Image.new('RGB',(4*size,9*h),(232,231,218));d=ImageDraw.Draw(canvas)
 for bi,(label,bg)in enumerate(backs):
  for pi,(lo,hi)in enumerate([(4,5),(5,6),(6,7)]):
   row=bi*3+pi
   for ci,(vn,folder,k)in enumerate([('old',T/'inputs/control',lo),('old',T/'inputs/control',hi),('trial',T/'frames',lo),('trial',T/'frames',hi)]):
    z=forest.copy()if bg is None else Image.new('RGBA',(128,128),bg);z.alpha_composite(Image.open(folder/f'{k:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST if size==128 else Image.Resampling.LANCZOS);canvas.paste(z.convert('RGB'),(ci*size,row*h+20));d.text((ci*size+2,row*h+3),f'{vn}{k:02} {label}',fill='black')
 canvas.save(T/'proof'/f'all-three-pairs-contrast-{size}.png')
print(json.dumps({k:recipe[k]for k in ['new05_sha256','unchanged06_sha256','actual_changed_RGBA_pixels','actual_visible_P_occlusion_pixels','complete_P_layer_under_Q_nonzero_pixels','P_layer_revealed_after_Q_removal_pixels','all_other7_PNG_bytes_exact']},indent=2))
