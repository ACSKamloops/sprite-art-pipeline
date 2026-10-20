"""SingleBrannSE07lower return trial from actualvisible00P and unchanged07Q paint."""
from pathlib import Path
import os,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def sm(m,n):Image.fromarray((m*255).astype(np.uint8)).save(P/n)
def poly(points):
 im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*(255-sa[use])*da[use]+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype(np.uint8)
base=a('inputs/control/07.png');source=a('inputs/control/00.png');yy,xx=np.indices((128,128));upper=yy<=85
for layer in ['sleeve','far','near','fixed']:upper|=a(f'inputs/source-layers/07-{layer}.png')[...,3]>0
# Literalvisible side ownership at the crotch is an authored surface split, not anatomical recovery.
p_points=[(63,85),(81,85),(83,94),(92,99),(95,108),(95,118),(59,118),(60,96),(63,90)]
q_points=[(46,85),(64,85),(68,88),(68,92),(65,96),(67,101),(66,110),(46,110),(44,91)]
powner=poly(p_points)&(source[...,3]>0);qowner=poly(q_points)&(base[...,3]>0)&~upper
for n,m in [('07-upper-protected',upper),('00-P-complete-visible-leg',powner),('07-Q-visible-preserved',qowner)]:sm(m,'masks/'+n+'.png')
qpart=np.zeros_like(base);qpart[qowner]=base[qowner];Image.fromarray(qpart).save(P/'layers/07-Q-preserved.png')
rows=[85,90,95,100,106,112,118];cols=[60,66,72,80,88,96]
xr=[[63,68,75,83,90,97],[62,68,75,82,89,96],[62,68,74,81,88,95],[62,68,74,80,87,94],[63,69,75,81,87,93],[64,69,75,81,86,92],[65,70,76,82,87,92]]
yr=[85,89,93,97,103,109,115]
src=np.array([[x,y] for y in rows for x in cols],float);dst=np.array([[xr[j][i],yr[j]] for j in range(len(rows)) for i in range(len(cols))],float);tri=[]
for j in range(len(rows)-1):
 for i in range(len(cols)-1):
  k=j*len(cols)+i;tri.extend([[k,k+len(cols),k+1],[k+1,k+len(cols),k+len(cols)+1]])
part=np.zeros_like(base);xy=np.full((128,128,2),-1,np.int16);accepted=np.zeros((128,128),bool);triangle=np.full((128,128),-1,np.int16);dets=[]
for ordinal,t in enumerate(tri):
 s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;dets.append([float(ds),float(dd)]);inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
 for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
  for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
   bary=inv@np.array([x,y,1.])
   if bary.min()<-1e-8:continue
   sx,sy=np.floor(bary@s+.5).astype(int)
   if 0<=sx<128 and 0<=sy<128 and powner[sy,sx]:part[y,x]=source[sy,sx];xy[y,x]=[sx,sy];accepted[y,x]=True;triangle[y,x]=ordinal
body=base.copy();body[~upper]=0;out=over(over(body,qpart),part);out[upper]=base[upper]
assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[:86],base[:86]);Image.fromarray(out).save(P/'frames/07.png');Image.fromarray(part).save(P/'layers/07-newP-projected-leg.png');Image.fromarray(body).save(P/'layers/07-after-lower-erasure.png');sm(accepted,'masks/07-newP-target-owner.png');sm(np.any(out!=base,axis=-1),'masks/07-actual-change.png');sm((qpart[...,3]>0)&(part[...,3]>0)&~upper,'masks/07-P-over-Q-occlusion.png');np.savez_compressed(P/'maps/07-newP-source00.npz',source_xy=xy,owner=accepted,triangle=triangle)
for y,x in np.argwhere(accepted):sx,sy=xy[y,x];assert np.array_equal(part[y,x],source[sy,sx])
other=[]
for i in range(7):assert (P/'frames'/f'{i:02}.png').read_bytes()==(P/'inputs/control'/f'{i:02}.png').read_bytes();other.append(i)
sha=lambda n:hashlib.sha256((P/n).read_bytes()).hexdigest()
recipe={'status':'Unselected one07lower return candidate; source-art projection, no inferred hidden anatomy or contact','roles':{'P':'00screen-rightforward;06tuckedbehind;07screen-rightreturn;00front. Puses actual00wholevisible trouser/cuff/boot surface, explicitly projected to shorter return.','Q':'06screen-leftsupport;07bentbackscreen-left surface preserved fromactual07;00tuckedleft. Distinct bentboot projection retained.'},'source_P_phase':0,'source_P_owner_polygon':p_points,'source_P_owner':'masks/00-P-complete-visible-leg.png','source_Q_phase':7,'source_Q_owner_polygon':q_points,'source_Q_owner':'masks/07-Q-visible-preserved.png','source_vertices':src.tolist(),'target_vertices':dst.tolist(),'triangles':tri,'determinants':dets,'band_roles':['fixedhip','knee','cufftop','cufflower','ankle','heel_toe','sole'],'layer_order':['actual07upper with oldlower transparent','actual07Qvisible surface','projected actual00Pcompleteleg','exactactual07upper restore'],'composition':'Integer source-over for declared overlapping surfaces; raw sampledPsourceRGBA exact. Partial-alpha compositeRGBA derived, notdirect sourcecopy claim.','new_authored_paint':0,'wholebodyfit_reflection':False,'00through06_PNG_exact':True,'03_seam':'Unchanged; no seamfix before07preview.'}
(P/'RECIPE.json').write_text(json.dumps(recipe,indent=2)+'\n')
receipt={'new07_sha256':sha('frames/07.png'),'model_calls':0,'other7_PNG_bytes_exact':other,'actual07upper_RGBA_exact':True,'00through06_includingnew03_unchanged':True,'changed07_RGBA_coords':int(np.any(out!=base,axis=-1).sum()),'source_P_visible_pixels':int(powner.sum()),'projected_P_pixels':int((part[...,3]>0).sum()),'Q_preserved_source_pixels':int(qowner.sum()),'Q_occluded_by_P_pixels':int(((qpart[...,3]>0)&(part[...,3]>0)&~upper).sum()),'new_authored_pixels':0,'sourceRGBA_witnesses_exact':True,'hold':[9,160],'cycle':[9,20],'limits':'Projectedshorterreturn hypothesis; no anatomicalrecovery, contact or quality score. Need actual06→07→00inspection beforepackaging.'}
(P/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
