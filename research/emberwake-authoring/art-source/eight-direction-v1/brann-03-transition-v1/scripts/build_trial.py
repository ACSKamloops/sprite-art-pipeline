"""One bounded BrannSE03 Qboot pitch/cuff transition from actual visible00/04surface."""
from pathlib import Path
import os,json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1];os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
def a(n):return np.array(Image.open(P/n).convert('RGBA'))
def m(n):return np.array(Image.open(P/n))>0
def sm(mask,n):Image.fromarray((mask*255).astype(np.uint8)).save(P/n)
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
base=a('inputs/control/03.png');source=a('inputs/control/00.png');upper=m('inputs/owners/03-upper.png');own=m('inputs/owners/00-complete-visible-front-boot.png')
body=a('inputs/03-after-erasure.png');cloth=a('inputs/03-authored-trousers.png');Pboot=a('inputs/03-right-retreating-placed.png');oldQ=a('inputs/03-left-passing-pitched-placed.png')
under=over(over(body,cloth),Pboot);old=over(under,oldQ);old[upper]=base[upper];assert np.array_equal(old,base),'Retained source layers must reconstruct frozen03exactly'
rows=[91,96,101,106,112,118];cols=[58,65,72,80,88,97];src=np.array([[x,y] for y in rows for x in cols],float)
# Controls are authored projected motion: source00cuff/calf/ankle/heel/toe to03passing, not recovered anatomy.
# Position along00sourceboot is preserved laterally; rows change width/lean/pitch separately.
xrows=[[52,56,61,67,73,79],[50,55,60,66,72,78],[49,54,59,65,71,77],[50,55,60,66,72,78],[51,56,61,67,73,79],[52,57,62,68,74,80]]
yrows=[[89,89,90,90,91,91],[93,93,94,94,94,95],[97,97,98,98,98,99],[101,101,102,102,102,103],[106,106,107,107,107,108],[110,110,111,111,111,112]]
dst=np.array([[xrows[j][i],yrows[j][i]] for j in range(len(rows)) for i in range(len(cols))],float);tris=[]
for j in range(len(rows)-1):
 for i in range(len(cols)-1):
  k=j*len(cols)+i;tris.extend([[k,k+len(cols),k+1],[k+1,k+len(cols),k+len(cols)+1]])
paint=np.zeros_like(base);xy=np.full((128,128,2),-1,np.int16);accepted=np.zeros((128,128),bool);triangle=np.full((128,128),-1,np.int16);dets=[]
for ordinal,t in enumerate(tris):
 s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;dets.append([float(ds),float(dd)]);inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
 for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
  for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
   bary=inv@np.array([x,y,1.])
   if bary.min()<-1e-8:continue
   sx,sy=np.floor(bary@s+.5).astype(int)
   if 0<=sx<128 and 0<=sy<128 and own[sy,sx]:paint[y,x]=source[sy,sx];xy[y,x]=[sx,sy];accepted[y,x]=True;triangle[y,x]=ordinal
out=over(under,paint);out[upper]=base[upper];assert np.array_equal(out[upper],base[upper]);assert np.array_equal(out[:86],base[:86]);Image.fromarray(out).save(P/'frames/03.png');Image.fromarray(under).save(P/'layers/03-after-oldQ-erasure.png');Image.fromarray(paint).save(P/'layers/03-newQ-projected-boot.png');sm(accepted,'masks/newQ-target-owner.png');sm(upper,'masks/03-upper-protected.png');sm(np.any(out!=base,axis=-1),'masks/03-actual-change.png');sm((oldQ[...,3]>0)|(paint[...,3]>0),'masks/03-old-new-Q-lower-owner.png');sm((paint[...,3]>0)&(Pboot[...,3]>0)&~upper,'masks/newQ-over-P-occlusion.png')
np.savez_compressed(P/'maps/03-newQ-source00.npz',source_xy=xy,owner=accepted,triangle=triangle)
controls={'status':'Unselected03only lower Qpitch/cuff trial; preview before packaging','roles':{'P':'00screen-rightforward;02 extended then03screen-rightretreating part unchanged frombase','Q':'02screen-lefttucked,03screen-leftpassing,04screen-leftfront support'},'source_phase':0,'source_role':'same actual complete visible boot surface already used for04Q; source00screen-right boot','source_owner':'inputs/owners/00-complete-visible-front-boot.png','source_vertices':src.tolist(),'target_vertices':dst.tolist(),'triangles':tris,'determinants':dets,'layer_order':['actual03afterleg erasure','existing03authored charcoal trousers','existingP02retreating placed part','newQ00projected cuff/boot','exact03upper restore'],'alpha_composition':'Integer source-over matches frozenbase producer, followed by exact upperRGBA restore. Source part samples have exact00RGBA; partial-alpha composite RGBA is explicitly derived, not claimed source-perfect.','new_authored_paint':0,'new_hidden_anatomy_claim':False,'projection':'Local cuff/calf/ankle/heel/toe rows and columns; nonrigid changing pitch, no reflection or bodyfit.','boot_source_material':'00screen-rightboot reused with declared projection;04 remains exact same source surface in its original projected placement.'}
(P/'RECIPE.json').write_text(json.dumps(controls,indent=2)+'\n')
sha=lambda n:hashlib.sha256((P/n).read_bytes()).hexdigest();same=[]
for i in [0,1,2,4,5,6,7]:assert (P/'frames'/f'{i:02}.png').read_bytes()==(P/'inputs/control'/f'{i:02}.png').read_bytes();same.append(i)
for y,x in np.argwhere(accepted):sx,sy=xy[y,x];assert np.array_equal(paint[y,x],source[sy,sx])
receipt={'frame03_sha256':sha('frames/03.png'),'only03_lower_changes':True,'other7_PNG_exact':same,'actual03upper_RGBA_exact':True,'actualP_placed_layer_unchanged':True,'source_part_pixels':int(own.sum()),'projected_Q_pixels':int((paint[...,3]>0).sum()),'changed03_RGBA_pixels':int(np.any(out!=base,axis=-1).sum()),'new00_source_RGBA_witnesses_exact':True,'frozen03_source_layer_reconstruction_before_edit_exact':True,'new_authored_pixels':0,'model_calls':0,'cycle_seconds':[9,20],'all8_holds':[9,160],'limits':'Qis deliberately projected to a less sole-facing plane, not physically calibrated. Actual02→03→04 chronology must be judged; no improvement/score claim from reconstruction.'}
(P/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
