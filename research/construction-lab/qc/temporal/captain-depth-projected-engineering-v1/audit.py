import json,hashlib,math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageChops
from scipy.ndimage import distance_transform_edt,label
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=Path('/home/astra/projects/sprite-construction-lab/pilot');P=R/'captain-depth-projected-art-v1';S=P/'artifacts/trial-v3-volume';B=R/'captain-boot-volume-binding-v1/artifacts/proxy-v2';POSE=P/'source/authored-poses-final.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
packet=json.loads(POSE.read_text());boot=json.loads((B/'manifest.json').read_text());binding=json.loads((S/'binding.json').read_text());spec=json.loads((S/'audition.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);screen=np.array(packet['camera']['screen_origin']);T=np.array(packet['camera']['transverse']);cfg=json.loads((R/'captain-upright-rig-v1/design.json').read_text())
assert len(packet['frames'])==len(boot['records'])==len(spec['frames'])==72
assert boot['source_sha256']==sha(P/'source/leg-master-128.png')==binding['source_leg_sha256']
assert boot['poses_sha256']==sha(POSE)==binding['pose_packet_sha256'];assert binding['boot_manifest_sha256']==sha(B/'manifest.json')
# Independent area-coordinate rasterizer; no producer render helper imported.
def raster(xy,world,uv,triangles,texture):
 out=np.zeros((256,256,4),np.uint8);zbuffer=np.full((256,256),-np.inf);depth=world@np.array([0,math.cos(math.radians(18)),math.sin(math.radians(18))]);material_uv=np.zeros((256,256,2))
 for tri in triangles:
  a,b,c=xy[tri];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-9:continue
  x0=max(0,math.floor(min(a[0],b[0],c[0])));x1=min(255,math.ceil(max(a[0],b[0],c[0])));y0=max(0,math.floor(min(a[1],b[1],c[1])));y1=min(255,math.ceil(max(a[1],b[1],c[1])))
  if x1<x0 or y1<y0:continue
  y,x=np.mgrid[y0:y1+1,x0:x1+1];x=x+.5;y=y+.5
  w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w=np.stack([w0,w1,1-w0-w1],-1);inside=(w>=-1e-9).all(-1);sample=w@uv[tri];colors=texture[np.clip(np.floor(sample[...,1]).astype(int),0,127),np.clip(np.floor(sample[...,0]).astype(int),0,127)];dep=w@depth[tri];sl=np.s_[y0:y1+1,x0:x1+1];select=inside&(colors[...,3]>0)&(dep>=zbuffer[sl]-1e-9);out[sl][select]=colors[select];zbuffer[sl][select]=dep[select];material_uv[sl][select]=sample[select]
 return out,material_uv
# Bind declared plane source from fixed output partitions, proving source pixels recombine.
source=Image.open(P/'source/leg-master-128.png').convert('RGBA');rest=Image.new('RGBA',source.size);parts={};anchors={'far':{'hip':[49,10],'knee':[44,43],'ankle':[44,90]},'near':{'hip':[82,10],'knee':[89,46],'ankle':[98,91]}}
for n in ['far','near']:
 for kind,joint in [('thigh','knee'),('shin','ankle'),('boot',None)]:
  f=S/'parts'/f'{n}_{kind}-visible.png';im=Image.open(f).convert('RGBA');rest.alpha_composite(im)
  if kind!='boot':
   h=Image.new('RGBA',im.size);k=anchors[n][joint];ImageDraw.Draw(h).rectangle((k[0]-5,k[1]-8,k[0]+5,k[1]+5),fill=(30,30,32,255));h.alpha_composite(im);parts[n+'_'+kind]=h
assert rest.tobytes()==source.tobytes(),'Visible source partitions must recompose original RGBA exactly'
assert Image.open(S/'upper-parts/source-rest.png').convert('RGBA').tobytes()==Image.open(R/'captain-upright-rig-v1'/cfg['source']).convert('RGBA').tobytes()
texture_checks={}
for n in ['far','near']:
 a=np.array(source);yy,xx=np.indices(a.shape[:2]);mask=(a[:,:,3]>0)&(yy>=(93 if n=='far'else 94))&((xx<69)if n=='far'else(xx>70));idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);texture=a[idx[0],idx[1]];actual=np.array(Image.open(B/f'{n}-edge-extended-UV.png'));assert np.array_equal(texture,actual);texture_checks[n]={'sha256':sha(B/f'{n}-edge-extended-UV.png'),'reconstructed_source_edge_extrusion_exact':True}
upper={n:Image.open(f).convert('RGBA')for f in (S/'upper-parts/complete').glob('*.png')for n in [f.stem]}
def affine(im,M,source_anchor,target):
 q=np.linalg.inv(M);offset=np.array(source_anchor)-q@target
 return im.transform((256,256),Image.Transform.AFFINE,tuple(q[0])+tuple([offset[0]])+tuple(q[1])+tuple([offset[1]]),Image.Resampling.NEAREST)
def near_distance(mask,p):
 ys,xs=np.nonzero(mask)
 return float(np.min(np.hypot(xs+.5-p[0],ys+.5-p[1]))) if len(xs)else 999.
records=[];bootdiff=[];full_diff=[];joint_flags=[];contacts=[];flat={};inputs=[]
for i,(f,br,sr) in enumerate(zip(packet['frames'],boot['records'],spec['frames'])):
 root=np.array(f['physical_root_pixels']);layers={};projection_error=0
 for n in ['far','near']:
  mesh=boot['surfaces'][n];ft=f['legs'][n]['foot'];basis=np.array([ft['orientation_world'][v]for v in ['forward','transverse','up']]).T;local=np.array([v[1]for v in mesh['vertices_UV_local']]);uv=np.array([v[0]for v in mesh['vertices_UV_local']]);world=local@basis.T+ft['origin_world'];xy=world@cam.T+screen-root;rr=br['feet'][n];projection_error=max(projection_error,float(np.max(np.abs(xy-np.array(rr['vertices_pixels'])))),float(np.max(np.abs(world-np.array(rr['vertices_world'])))))
  tex=np.array(Image.open(B/f'{n}-edge-extended-UV.png').convert('RGBA'));expected,uvmap=raster(xy,world,uv,mesh['triangles'],tex);actual=np.array(Image.open(B/rr['file']).convert('RGBA'));assert sha(B/rr['file'])==rr['sha256'];diff=int(np.any(expected!=actual,axis=-1).sum());coords=np.argwhere(np.any(expected!=actual,axis=-1));cases=[]
  for yy,xx in coords:
   q=uvmap[yy,xx];u,v=np.floor(q).astype(int);neighbors=tex[max(0,v-1):min(128,v+2),max(0,u-1):min(128,u+2)];cases.append({'xy':[int(xx),int(yy)],'alpha_changed':bool(expected[yy,xx,3]!=actual[yy,xx,3]),'uv':q.tolist(),'distance_to_integer_boundary':float(np.min(np.abs(q-np.round(q)))),'actual_color_in_neighbor_texel':bool(np.any(np.all(neighbors==actual[yy,xx],axis=-1)))})
  bootdiff.append({'frame':i,'leg':n,'changed_pixels':diff,'cases':cases});layers[n+'_boot']=Image.fromarray(actual)
  if ft['role']=='flat':flat.setdefault((n,ft.get('episode',0)),[]).append(world)
  # Actual opaque layer witness near the declared z=0 contact surface vertices.
  support=np.flatnonzero(np.abs(world[:,2])<1e-6);dist=[near_distance(actual[:,:,3]>0,xy[j])for j in support];contacts.append({'frame':i,'leg':n,'role':ft['role'],'contact_vertex_count':len(support),'max_contact_vertex_to_opaque_pixel_center_px':max(dist)if dist else None,'contact_role_declared':ft['contact']})
  leg=f['legs'][n];pix={k:np.array(v)-root for k,v in leg['pixels'].items()}
  for kind,a,b in [('thigh','hip','knee'),('shin','knee','ankle')]:
   s=np.array(anchors[n][a]);e=np.array(anchors[n][b]);L=(e-s)/np.linalg.norm(e-s);perp=np.array([L[1],-L[0]]);axis=np.array(leg['world'][b])-leg['world'][a];axis/=np.linalg.norm(axis);side=T-axis*np.dot(T,axis);side/=np.linalg.norm(side);side=-side if(cam@side)[0]<0 else side;M=np.outer(cam@side/.8,perp)+np.outer((pix[b]-pix[a])/np.linalg.norm(e-s),L);layers[n+'_'+kind]=affine(parts[n+'_'+kind],M,s,pix[a])
 pelvis=np.array(f['upper_pixels']['pelvis'])-root;chest=np.array(f['upper_pixels']['chest'])-root;bind=packet['neutral_bind']['upper_pixels'];chest+=np.array(cfg['chest_hinge'])-cfg['pelvis_rest']-(np.array(bind['chest'])-bind['pelvis']);r=math.radians(f['chest_counterrotation_degrees']);rotation=np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
 for n in ['cape','tabard','waist']:layers[n]=affine(upper[n],np.eye(2),cfg['pelvis_rest'],pelvis)
 for n in ['chest','head','shield','backpack_halo','sword_upper_arm','sword_forearm']:layers[n]=affine(upper[n],np.eye(2)if n=='head'else rotation,cfg['chest_hinge'],chest)
 backing=Image.new('RGBA',(256,256));ImageDraw.Draw(backing).rectangle((121,100,147,133),fill=(45,18,22,255));layers['joint_backing']=affine(backing,np.eye(2),cfg['pelvis_rest'],pelvis)
 order=['cape','backpack_halo','far_thigh','far_shin','far_boot','near_thigh','near_shin','near_boot','joint_backing','sword_upper_arm','sword_forearm','waist','chest','head','tabard','shield'];out=Image.new('RGBA',(256,256))
 for n in order:out.alpha_composite(layers[n])
 actualfull=Image.open(S/sr['file']).convert('RGBA');assert sha(S/sr['file'])==sr['sha256'];d=int(np.any(np.array(out)!=np.array(actualfull),axis=-1).sum());full_diff.append({'frame':i,'changed_pixels':d});uppercover=Image.new('RGBA',(256,256))
 for n in order[8:]:uppercover.alpha_composite(layers[n])
 for n in ['far','near']:
  for joint,aa,bb in [('knee','thigh','shin'),('ankle','shin','boot')]:
   point=np.array(f['legs'][n]['pixels'][joint])-root;a=np.array(layers[n+'_'+aa])[:,:,3]>0;b=np.array(layers[n+'_'+bb])[:,:,3]>0;da=near_distance(a,point);db=near_distance(b,point);x,y=np.floor(point).astype(int);occluded=bool(np.array(uppercover)[np.clip(y,0,255),np.clip(x,0,255),3]>0);joint_flags.append({'frame':i,'leg':n,'joint':joint,'source_point':point.tolist(),'distance_to_first_mask_px':da,'distance_to_second_mask_px':db,'joint_anchor_upper_occluded':occluded,'mask_overlap_pixels_within_8px':int(np.sum(a&b&((np.indices(a.shape)[1]+.5-point[0])**2+(np.indices(a.shape)[0]+.5-point[1])**2<64))),'flag_2px_neighborhood':max(da,db)>2})
 if i in [0,9,18,27,36,45,54,63]:
  own=O/'layers';own.mkdir(exist_ok=True)
  for n in order:layers[n].save(own/f'{i:03}-{n}.png')
 records.append({'frame':i,'projection_metadata_max_error':projection_error})
# Deliberate actual material shift: expected raster and shifted real layer must disagree.
a=np.array(Image.open(B/'layers/000-far.png'));shift=np.zeros_like(a);shift[10:]=a[:-10];negative_pixel_count=int(np.any(a!=shift,axis=-1).sum());assert negative_pixel_count>0
def require_pose_hash(expected,observed):
 if expected!=observed:raise ValueError('pose hash binding mismatch')
require_pose_hash(sha(POSE),boot['poses_sha256'])
try:require_pose_hash('0'*64,boot['poses_sha256']);mismatch_guard=False
except ValueError:mismatch_guard=True
assert mismatch_guard
report={'schema':'captain.independent_depth_engineering.v1','art_approval':False,'inputs':{'pose_sha256':sha(POSE),'boot_manifest_sha256':sha(B/'manifest.json'),'sprite_binding_sha256':sha(S/'binding.json'),'sprite_audition_sha256':sha(S/'audition.json'),'renderer_sha256':sha(P/'render-volume.py'),'leg_source_sha256':sha(P/'source/leg-master-128.png'),'upper_design_sha256':sha(R/'captain-upright-rig-v1/design.json')},'texture_binding_checks':texture_checks,'frames':len(records),'projection_records':records,'boot_raster_comparisons':bootdiff,'full_sprite_comparisons':full_diff,'contact_witnesses':contacts,'joint_neighborhoods':joint_flags,'flat_world_vertex_max_change':{str(k):max(float(np.max(np.abs(v[0]-x)))for x in v)for k,v in flat.items()},'negative_cases':{'boot_shift_y_10_changed_pixels':negative_pixel_count,'shift_rejected_by_exact_raster_comparison':not np.array_equal(a,shift),'mismatched_pose_hash_rejected':mismatch_guard},'limits':['Support vertex-to-raster witness is not a heel/toe force or complete material plant proof.','2px joint-anchor mask neighborhood is diagnostic; underlaps/source registration are authored assumptions.','Upper occlusion at anchor is recorded separately; no automatic gap or art verdict.','No reconstructed full3D armor or unseen source geometry claim.']}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print({'boot_diff':sum(x['changed_pixels']for x in bootdiff),'sprite_diff':sum(x['changed_pixels']for x in full_diff),'joint_flags':sum(x['flag_2px_neighborhood']for x in joint_flags),'contact_max':max(x['max_contact_vertex_to_opaque_pixel_center_px']or 0 for x in contacts),'negative_shift':negative_pixel_count})
