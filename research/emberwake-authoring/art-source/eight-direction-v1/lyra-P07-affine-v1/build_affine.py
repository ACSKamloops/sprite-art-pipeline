"""One prescribed positive-affine Lyra07 P visible-paint test. No model/editor."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
G=Path('/home/astra/artifacts/emberwake-lyra-06-neighbor-guide-v1')
C=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/lyra-stance-spring-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def save(p,a):Image.fromarray(a.astype('uint8')).save(R/p)
def js(p,a):(R/p).write_text(json.dumps(a,indent=2)+'\n')
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype('uint8')
for folder in ['inputs/current','inputs/components','inputs/witnesses','layers','maps','masks','proof','raw']:(R/folder).mkdir(parents=True,exist_ok=True)
records=[]
def cp(p,local):
 dest=R/local
 if dest.exists():assert sha(p)==sha(dest)
 else:shutil.copy2(p,dest)
 records.append({'source':str(p),'local':local,'sha256':sha(dest)})
for i in (0,6,7):
 cp(G/f'inputs/current/{i:02}.png',f'inputs/current/{i:02}.png')
 assert sha(C/f'editor-render/{i:02}.png')==sha(R/f'inputs/current/{i:02}.png')
for layer in ['body','fixed_lower','cloth_a','cloth_b','undercoat']:
 cp(G/f'components/07-{layer}.png',f'inputs/components/07-{layer}.png')
for name in ['07-P-retained-paint-witness.png','07-Q-visible-boot-literal.png','07-upper-Q-protected.png']:
 cp(G/'masks'/name,'inputs/witnesses/'+name)
cp(G/'GUIDE.json','inputs/witnesses/neighbor-GUIDE.json')
js('INPUTS.json',records)
a=arr(R/'inputs/current/07.png');body=arr(R/'inputs/components/07-body.png');q=np.array(Image.open(R/'inputs/witnesses/07-Q-visible-boot-literal.png'))>0
protected=(body[:,:,3]>0)|q
# Literal inclusive native row spans inspected against actual current07 grid.
# The proximal rows own mixed charcoal cuff/outline as well as brown shaft;
# distal rows preserve the complete visible ankle/heel/toe/partial-alpha edge.
rows={84:[[66,78]],85:[[66,78]],86:[[65,79]],87:[[65,79]],88:[[63,78]],
 89:[[63,76]],90:[[63,78]],91:[[63,78]],92:[[63,79]],93:[[63,80]],94:[[63,81]],
 95:[[64,84]],96:[[65,84]],97:[[65,84]],98:[[65,85]],99:[[66,85]],100:[[66,85]],
 101:[[66,85]],102:[[66,84]],103:[[66,84]],104:[[66,83]],105:[[67,81]],106:[[67,75]],107:[[68,74]]}
cuffrows={84:[[66,72],[76,78]],85:[[66,71],[77,78]],86:[[65,69],[77,79]],87:[[65,67],[77,79]],88:[[63,64],[78,78]]}
owner=np.zeros((128,128),bool);cuff=np.zeros_like(owner)
for target,spans in [(owner,rows),(cuff,cuffrows)]:
 for y,runs in spans.items():
  for x0,x1 in runs:target[y,x0:x1+1]=True
assert not np.any(owner&protected),'Source owner must exclude actual upper and other Q.'
assert np.all(a[owner,3]>0),'Literal rows own actual positive source paint only.'
assert np.all(cuff<=owner)
p=np.zeros_like(a);p[owner]=a[owner]
save('layers/P07-source-visible.png',p);save('masks/P07-literal-source-owner.png',owner*255);save('masks/P07-charcoal-cuff-owner.png',cuff*255);save('masks/upper-Q-protected.png',protected*255)
S=np.array([[69.,87.,1.],[67.,104.,1.],[85.,101.,1.]])
T=np.array([[72.,88.5],[68.5,103.5],[81.5,100.5]])
coef=np.linalg.solve(S,T);M=np.eye(3);M[:2,:]=coef.T;inv=np.linalg.inv(M);det=float(np.linalg.det(M[:2,:2]));assert det>0
assert np.allclose((S@coef),T,atol=1e-12)
yy,xx=np.mgrid[:128,:128];grid=np.stack([xx,yy,np.ones_like(xx)],axis=2);uv=grid@inv.T
sx=np.floor(uv[:,:,0]+.5).astype('int16');sy=np.floor(uv[:,:,1]+.5).astype('int16')
valid=(sx>=0)&(sx<128)&(sy>=0)&(sy<128);scx=np.clip(sx,0,127);scy=np.clip(sy,0,127);valid&=owner[scy,scx]
part=np.zeros_like(a);part[valid]=a[sy[valid],sx[valid]];mp=np.full((128,128,2),-1,np.int16);mp[valid,0]=sx[valid];mp[valid,1]=sy[valid]
np.savez_compressed(R/'maps/P07-positive-affine.npz',source_xy=mp,source_float_xy=uv[:,:,:2],owner=valid,source_owner=owner,source_RGBA=a,matrix=M,inverse=inv)
save('raw/P07-affine-layer.png',part);save('masks/P07-affine-target-owner.png',valid*255)
under=a.copy();under[owner]=0;save('layers/07-after-oldP-erasure.png',under)
raw=over(under,part);save('raw/07-affine-unprotected.png',raw)
blocked=valid&protected;final=raw.copy();final[protected]=a[protected]
save('masks/affine-blocked-by-upper-Q.png',blocked*255);save('raw/07-affine-protected.png',final)
assert np.array_equal(final[protected],a[protected]);assert np.array_equal(final[~(owner|valid|protected)],a[~(owner|valid|protected)])
assert np.array_equal(part[valid],a[mp[valid,1],mp[valid,0]])
oldw=np.array(Image.open(R/'inputs/witnesses/07-P-retained-paint-witness.png'))>0
sourcew=[{'source_xy':[int(x),int(y)],'RGBA':a[y,x].tolist(),'material_assignment':'charcoal cuff/terminal outline (authored boundary, not pure leather)'if cuff[y,x]else'brown boot/calf/sole and partial-alpha contour','actual_components':[layer for layer in ['body','fixed_lower','cloth_a','cloth_b','undercoat']if arr(R/f'inputs/components/07-{layer}.png')[y,x,3]>0]}for y,x in np.argwhere(owner)]
recipe={'status':'RAW one-prescribed-affine prototype; no quality acceptance or editor package',
 'model_calls':0,'source':'inputs/current/07.png','source_sha256':sha(R/'inputs/current/07.png'),
 'actual_source_rows':rows,'declared_charcoal_cuff_rows':cuffrows,'source_positive_samples':int(owner.sum()),'declared_charcoal_cuff_samples':int(cuff.sum()),
 'retained342_witness_used_as_automatic_owner':False,'witness_included':int((owner&oldw).sum()),'additional_actual_paint_in_literal_owner':int((owner&~oldw).sum()),'witness_not_selected':int((oldw&~owner).sum()),
 'source_landmarks':{'cuff':[69,87],'heel':[67,104],'forefoot':[85,101]},'authored_target_landmarks':{'cuff':[72,88.5],'heel':[68.5,103.5],'forefoot':[81.5,100.5]},
 'matrix_source_to_target':M.tolist(),'inverse':inv.tolist(),'determinant':det,
 'sampling':'integer pixel centers; inverse affine; nearest floor(source+.5); accept literal source owner; exact sourceRGBA copy; no channel filtering or alpha cleanup',
 'wholeboot_geometry_invariance_claim':False,'authored_projection':'One positive affine foreshortening/reorientation of complete visible P calf/shaft/foot paint, with a declared small charcoal cuff region. It is a projected-paint hypothesis, not recovered anatomy or a rigid boot.',
 'old_P_removal':'Only actual positive paint in literal source owner is erased to transparent, then the affine part is source-over composited. No concealed background anatomy supplied.',
 'protected_upper_Q_samples':int(protected.sum()),'target_samples':int(valid.sum()),'target_samples_blocked_by_protected':int(blocked.sum()),
 'natural_underlap_samples':int((valid&~owner&(under[:,:,3]>0)&~protected).sum()),'current_original_RGBA_outside_source_target_protected_exact':True,
 'upper_Q_RGBA_exact':True,'changed_RGBA_samples':int(np.any(final!=a,axis=2).sum()),'raw_candidate_sha256':sha(R/'raw/07-affine-protected.png'),
 'timing':{'holds_unchanged':[9,160],'cycle_unchanged':[9,20]},'registration':'fixed128 stage; no fitting/recentering','hidden_anatomy_claim':False,
 'new_authored_joint_paint':0,'source_witnesses':sourcew}
js('AFFINE-RECIPE.json',recipe)
overlaps=[]
for y,x in np.argwhere(valid&~owner&(under[:,:,3]>0)):
 overlaps.append({'destination':[int(x),int(y)],'base_RGBA':a[y,x].tolist(),'base_component_owners':[layer for layer in ['body','fixed_lower','cloth_a','cloth_b','undercoat']if arr(R/f'inputs/components/07-{layer}.png')[y,x,3]>0],
  'source_xy':mp[y,x].tolist(),'source_RGBA':part[y,x].tolist(),'protected':bool(protected[y,x]),'composited_RGBA':final[y,x].tolist()})
js('SOURCE-UNDERLAP.json',overlaps)
print(json.dumps({k:recipe[k]for k in ['source_positive_samples','declared_charcoal_cuff_samples','witness_included','additional_actual_paint_in_literal_owner','witness_not_selected','matrix_source_to_target','determinant','target_samples','target_samples_blocked_by_protected','natural_underlap_samples','changed_RGBA_samples','raw_candidate_sha256']},indent=2))
