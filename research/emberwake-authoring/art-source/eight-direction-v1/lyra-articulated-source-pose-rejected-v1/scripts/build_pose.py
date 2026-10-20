"""One source-part Lyra06 articulation hypothesis. No model or whole-cloth mesh.
Actual visible04 thigh/shaft separately transformed. Distal136 remains exact.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def png(p,z):Image.fromarray(z.astype('uint8')).save(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,z):p.write_text(json.dumps(z,indent=2)+'\n')
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
def segment_affine(s0,s1,t0,t1,widthscale=1.):
 s0=np.array(s0,float);s1=np.array(s1,float);t0=np.array(t0,float);t1=np.array(t1,float);v=s1-s0;w=t1-t0;sl=np.linalg.norm(v);tl=np.linalg.norm(w);v/=sl;w/=tl;sn=np.array([-v[1],v[0]]);tn=np.array([-w[1],w[0]]);A=np.outer(w,v)*(tl/sl)+np.outer(tn,sn)*widthscale;b=t0-A@s0;return A,b
src=a(R/'inputs/source04.png');cur=a(R/'inputs/current06.png');bodyowner=m(R/'inputs/guide/protected-current06-upper-owner.png');oldq=m(R/'inputs/current06-old-Q-owner.png');otherowner=(cur[:,:,3]>0)&~oldq&~bodyowner;distalowner=m(R/'inputs/guide/protected-distal-target-owner.png');distal=a(R/'inputs/guide/06-protected-distal-source-paint.png')
retained=cur.copy();retained[oldq]=0;body=np.zeros_like(cur);body[bodyowner]=cur[bodyowner];other=np.zeros_like(cur);other[otherowner]=cur[otherowner];retained[bodyowner]=0
specs=[('thigh',[58,85],[57,96],[58,83],[52,92],'04-thigh-knee-charcoal-owner.png'),('shaft',[57,96],[55,105],[52,92],[43,93],'04-shaft-calf-leather-owner.png')];parts={};maps={};records=[]
for name,s0,s1,t0,t1,fn in specs:
 owner=m(R/'inputs/guide'/fn);widthscale=.5 if name=='shaft' else 1.;A,b=segment_affine(s0,s1,t0,t1,widthscale);inv=np.linalg.inv(A);layer=np.zeros_like(src);sm=np.full((128,128,2),-1,dtype='int16');owned=np.zeros((128,128),bool)
 for y in range(128):
  for x in range(128):
   p=inv@(np.array([x,y])-b);sx,sy=np.floor(p+.5).astype(int)
   if 0<=sx<128 and 0<=sy<128 and owner[sy,sx]:layer[y,x]=src[sy,sx];sm[y,x]=[sx,sy];owned[y,x]=True
 parts[name]=layer;maps[name]=sm;png(R/'layers'/f'{name}-mapped-raw.png',layer);png(R/'masks'/f'{name}-mapped-owner.png',owned.astype('uint8')*255);np.savez_compressed(R/'maps'/f'{name}.npz',source_xy=sm,affine=A,offset=b)
 rawsrc=np.zeros_like(src);rawsrc[owner]=src[owner];png(R/'layers'/f'{name}-source04.png',rawsrc)
 records.append({'part':name,'source_controls':[s0,s1],'target_controls':[t0,t1],'source_owner':f'inputs/guide/{fn}','source_visible_owned_pixels':int(owner.sum()),'affine_matrix':A.tolist(),'offset':b.tolist(),'determinant':float(np.linalg.det(A)),'authored_cross_section_projection':widthscale,'target_owned_samples':int(owned.sum()),'source_index_rule':'integer target centers; inverse matrix; nearest floor(source+.5); accept only literal source owner; copy source RGBA exactly','mapped_source_witnesses':[{'target':[int(x),int(y)],'source04':sm[y,x].tolist(),'RGBA':layer[y,x].tolist()}for y,x in np.argwhere(owned)]})
# Declared depth: other leg retained, shaft, distal, thigh, current wholeupper.
# Actual positive current other-leg texels are protected in final composition
# by making that retained leg foreground where it overlaps proposed sourcepart.
# Every such overlap is recorded; no implied unseen anatomy/automatic fill.
raw=over(parts['thigh'],over(distal,over(parts['shaft'],retained)));raw=over(body,raw);distal_overlap=(parts['thigh'][:,:,3]>0)&distalowner
# Protected distal has final depth at its literal foot boundary. This is an
# explicit authored cut between calf and shoe, not a claim that an ankle exists.
raw[distalowner]=distal[distalowner]
raw[otherowner]=cur[otherowner];raw[bodyowner]=cur[bodyowner];raw[raw[:,:,3]==0]=0
png(R/'layers/retained-current06-other-and-residual.png',retained);png(R/'layers/current06-upper.png',body);png(R/'layers/current06-other-visible-leg.png',other);png(R/'layers/protected-distal136.png',distal);png(R/'raw-pose.png',raw)
# Explicit part visibility/contour decisions after actual material inspection.
# Raw affine parts and raw-pose remain immutable outputs of the sampler.
visible={name:z.copy()for name,z in parts.items()};visrec=[]
for q in json.loads((R/'PART-VISIBILITY.json').read_text()):
 name=q['part'];x,y=q['target'];sx,sy=maps[name][y,x];assert sx>=0 and parts[name][y,x,3]>0;assert not(bodyowner[y,x]or otherowner[y,x]or distalowner[y,x]);visible[name][y,x]=0;visrec.append(q|{'source04':[int(sx),int(sy)],'source_RGBA':parts[name][y,x].tolist()})
for name,z in visible.items():png(R/'layers'/f'{name}-visible-after-contour.png',z)
posed=over(visible['thigh'],over(distal,over(visible['shaft'],retained)));posed=over(body,posed);posed[distalowner]=distal[distalowner];posed[otherowner]=cur[otherowner];posed[bodyowner]=cur[bodyowner];posed[posed[:,:,3]==0]=0;png(R/'visible-part-pose.png',posed)
# Joint paint, explicitly declared only at inspected source attachment.

patchfile=R/'JOINT-PATCHES.json';patches=json.loads(patchfile.read_text())if patchfile.exists()else[];joint=np.zeros_like(src);jm=np.full((128,128,2),-1,dtype='int16');patchrec=[]
for p in patches:
 x,y=p['target'];sx,sy=p['source04'];assert not(bodyowner[y,x]or otherowner[y,x]or distalowner[y,x]);joint[y,x]=src[sy,sx];jm[y,x]=[sx,sy];patchrec.append(p|{'donor_RGBA':src[sy,sx].tolist(),'before_RGBA':posed[y,x].tolist()})
# Explicit local joint strokes compose on source parts, behind all protected
# upper/other-leg/distal paint. No blanket guide-region completion.
out=over(joint,posed);out[distalowner]=distal[distalowner];out[otherowner]=cur[otherowner];out[bodyowner]=cur[bodyowner];out[out[:,:,3]==0]=0
assert np.array_equal(out[bodyowner],cur[bodyowner]);assert np.array_equal(out[otherowner],cur[otherowner]);assert np.array_equal(out[distalowner],distal[distalowner]);assert int(distalowner.sum())==136
png(R/'layers/explicit-joint-paint.png',joint);np.savez_compressed(R/'maps/joint-paint.npz',source_xy=jm);png(R/'candidate06.png',out);changed=np.any(out!=cur,axis=2);png(R/'masks/changed-from-current06.png',changed.astype('uint8')*255)
compositeparts=(parts['thigh'][:,:,3]>0)|(parts['shaft'][:,:,3]>0);save(R/'RECIPE.json',{'status':'one authored articulated source pose; unselected; raw construction retained','source04_png_sha256':sha(R/'inputs/source04.png'),'current06_png_sha256':sha(R/'inputs/current06.png'),'guide_controls_authored_not_measured':{'H':[58,83],'K':[52,92],'A':[43,93]},'parts':records,'protected_distal_samples':136,'distal_translation':[-12,-12],'whole_boot_invariance':False,'raw_distal_thigh_overlap_coordinates':[[int(x),int(y)]for y,x in np.argwhere(distal_overlap)],'protected_otherleg_overlap_coordinates':[[int(x),int(y)]for y,x in np.argwhere(compositeparts&otherowner)],'upper_actual_part_occlusion_coordinates':[[int(x),int(y)]for y,x in np.argwhere(compositeparts&bodyowner)],'declared_depth':'retained current residual; shaft; protected distal; thigh; explicit local joint strokes; protected current other visible leg where overlapping; complete current upper. Distal136 final visible at its literal owner boundary.','part_visibility_contour_erasures':visrec,'visible_part_samples':{n:int((z[:,:,3]>0).sum())for n,z in visible.items()},'joint_paint':patchrec,'authored_joint_pixels':len(patchrec),'changed_pixels':[{'xy':[int(x),int(y)],'before':cur[y,x].tolist(),'after':out[y,x].tolist()}for y,x in np.argwhere(changed)],'candidate_png_sha256':sha(R/'candidate06.png'),'upper_and_otherleg_RGBA_exact':True,'distal136_RGBA_exact':True,'source_only':True,'unknowns':'Visible U-shaped source leather has no complete hidden calf/ankle. H/K/A are a projected pose hypothesis. No anatomical/contact calibration.','model_calls':0,'fullbank':False,'editor':False})
# Actual source/current/part-only/proposal art on three grounds, normal pixels.
for size in[128,256,84]:
 for ground,col in [('light',(231,227,214,255)),('dark',(34,37,43,255)),('game',(39,57,47,255))]:
  board=Image.new('RGB',(4*size,size+24),col[:3]);d=ImageDraw.Draw(board)
  for j,(label,z)in enumerate([('source04',src),('current06',cur),('raw parts',raw),('joint proposal',out)]):
   bg=Image.new('RGBA',(128,128),col);bg.alpha_composite(Image.fromarray(z));board.paste(bg.resize((size,size),Image.Resampling.NEAREST).convert('RGB'),(j*size,24));d.text((j*size+2,4),label,fill='white'if ground!='light'else'black')
  board.save(R/'proof'/f'comparison-{size}-{ground}.png')
box=(33,76,69,106);board=Image.new('RGB',(4*360,324),(231,227,214));d=ImageDraw.Draw(board)
for j,(label,z)in enumerate([('raw shaft',parts['shaft']),('raw thigh',parts['thigh']),('raw composite',raw),('proposal',out)]):
 bg=Image.new('RGBA',(128,128),(231,227,214,255));bg.alpha_composite(Image.fromarray(z));board.paste(bg.crop(box).resize((360,300),Image.Resampling.NEAREST).convert('RGB'),(j*360,24));d.text((j*360+2,3),label,fill='black')
board.save(R/'proof/joints-and-raw-parts-10x.png')
print(json.dumps({'candidate':str(R/'candidate06.png'),'target_part_samples':{r['part']:r['target_owned_samples']for r in records},'authored_joint_pixels':len(patchrec),'protected_upper_otherleg_and136_distal_exact':True,'otherleg_overlaps':int((compositeparts&otherowner).sum()),'distal_thigh_overlaps':int(distal_overlap.sum())},indent=2))
