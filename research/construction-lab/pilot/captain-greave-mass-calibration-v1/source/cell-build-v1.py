"""One fixed-volume greave/cap comparator; source-owned UV, not recovered armor."""
import argparse,json,math,hashlib,importlib.util,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageChops
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
upper=load('construct',P/'source/upper/construct.py');core=load('legacy_planes',P/'source/root-render-volume.py');core.P=P;core.construct=upper
raster=load('build',P/'source/boot-rasterizer.py');boot=load('frozen_boot_proxy',P/'source/boot-proxy.py')
CFG=core.CFG

def basis(leg,cap=False):
 w=leg['world'];axis=core.unit(np.array(w['ankle'])-w['knee'])
 if cap:axis=core.unit(axis+core.unit(np.array(w['knee'])-w['hip']))
 t=np.array([-.8,-.6,0]);t=core.unit(t-axis*np.dot(t,axis));n=core.unit(np.cross(axis,t))
 if np.dot(n,[0,math.cos(math.radians(18)),math.sin(math.radians(18))])<0:n=-n
 return axis,t,n

def geometry(kind):
 verts=[];tri=[];sides=16
 if kind=='shin':rings=[(0,14,8),(12,14,8),(28,12,7),(40,10,6),(48,9,5)]
 else:rings=[(16*math.sin(p),16*math.cos(p),6*math.cos(p))for p in np.linspace(-math.pi/2,math.pi/2,9)]
 for longitudinal,radius,depth in rings:
  for j in range(sides):
   angle=2*math.pi*j/sides;verts.append([depth*math.cos(angle),radius*math.sin(angle),longitudinal])
 for k in range(len(rings)-1):
  for j in range(sides):
   a=k*sides+j;c=k*sides+(j+1)%sides;tri.extend([[a,c,a+sides],[c,c+sides,a+sides]])
 for k in [0,len(rings)-1]:
  for j in range(1,sides-1):tri.append([k*sides,k*sides+j,k*sides+j+1])
 return verts,tri

def masks(src):
 yy,xx=np.mgrid[:128,:128];base=src[:,:,3]>0;legsplit=Image.new('L',(128,128));ImageDraw.Draw(legsplit).polygon([(0,0),(62,0),(64,40),(68,128),(0,128)],fill=255);split=np.array(legsplit)>0;ans={}
 for n in ['far','near']:
  own=base&(split if n=='far'else~split);cap=Image.new('L',(128,128));d=ImageDraw.Draw(cap)
  if n=='far':d.ellipse((27,27,59,64),fill=255)
  else:d.ellipse((74,37,103,59),fill=255)
  cap=np.array(cap)>0;cut=27 if n=='far' else 37
  ans[n]={'cap':own&cap,'shin':own&(yy>=cut)&(yy<=93)&~cap,'thigh':own&(yy<cut)&~cap,'boot':own&(yy>= (93 if n=='far' else 94))}
 return ans

def texture(src,mask):
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);return src[idx[0],idx[1]].copy()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output);assert not out.exists();out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir();(out/'parts').mkdir()
 src=np.array(Image.open(P/'source/leg-master-128.png').convert('RGBA'));packet=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);ownership=masks(src);cfg,up,receipt=upper.construct(out/'upper-parts');texts={};surfaces={};tris={};parts={};bind=packet['neutral_bind']
 for n in ['far','near']:
  for kind in ['thigh','shin','cap','boot']:
   im=src.copy();im[:,:,3]=np.where(ownership[n][kind],src[:,:,3],0);im[im[:,:,3]==0]=0;parts[n+'_'+kind]=Image.fromarray(im);parts[n+'_'+kind].save(out/'parts'/f'{n}_{kind}-source.png');texts[n+'_'+kind]=texture(src,ownership[n][kind]);Image.fromarray(texts[n+'_'+kind]).save(out/'parts'/f'{n}_{kind}-extended-UV.png')
  source=CFG[n];leg=bind['legs'][n];M=core.bone_matrix(source['knee'],source['ankle'],np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array(packet['camera']['transverse']));inv=np.linalg.inv(M)
  for kind in ['shin','cap']:
   local,tr=geometry(kind);axis,t,norm=basis(leg,kind=='cap');B=np.column_stack([norm,t,axis]);uvs=[(np.array(source['knee'])+inv@(cam@(B@np.array(v)))).tolist()for v in local];surfaces[n+'_'+kind]=[[uv,v]for uv,v in zip(uvs,local)];tris[n+'_'+kind]=tr
 order=['cape','backpack_halo','far_thigh','far_shin','far_cap','far_boot','near_thigh','near_shin','near_cap','near_boot','joint_backing','sword_upper_arm','sword_forearm','waist','chest','head','tabard','shield'];records=[];ims=[];zmin=1e9;newcolors=0;palette={tuple(c)for c in src.reshape(-1,4)if c[3]};closed={}
 for f in packet['frames']:
  root=np.array(f['physical_root_pixels']);layers={};rr={'index':f['index'],'duration_ms':f['duration_ms'],'phase':f['phase'],'physical_root':list(root),'meshes':{}}
  for n,c in CFG.items():
   leg=f['legs'][n];w=leg['world'];pix={k:np.array(v)-root for k,v in leg['pixels'].items()};M=core.bone_matrix(c['hip'],c['knee'],np.array(w['hip']),np.array(w['knee']),cam,np.array(packet['camera']['transverse']));layers[n+'_thigh']=core.warp(parts[n+'_thigh'],M,c['hip'],pix['hip'])
   for kind in ['shin','cap']:
    axis,t,norm=basis(leg,kind=='cap');fake={'foot':{'orientation_world':{'forward':norm,'transverse':t,'up':axis},'origin_world':w['knee']}};im,world,xy=raster.render(surfaces[n+'_'+kind],tris[n+'_'+kind],texts[n+'_'+kind],fake,cam,root);layers[n+'_'+kind]=im;rr['meshes'][n+'_'+kind]={'vertices_world':world.tolist(),'vertices_pixels':xy.tolist()};zmin=min(zmin,float(world[:,2].min()))
   im,world,xy=raster.render(*boot.surface(n),texts[n+'_boot'],leg,cam,root);layers[n+'_boot']=im
  pelvis=np.array(f['upper_pixels']['pelvis'])-root;chest=np.array(f['upper_pixels']['chest'])-root;rest=packet['neutral_bind']['upper_pixels'];chest+=np.array(cfg['chest_hinge'])-np.array(cfg['pelvis_rest'])-(np.array(rest['chest'])-rest['pelvis']);ang=math.radians(f['chest_counterrotation_degrees']);rotation=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
  for n in ['cape','tabard','waist']:layers[n]=core.warp(up[n],np.eye(2),cfg['pelvis_rest'],pelvis)
  for n in ['chest','head','shield','backpack_halo','sword_upper_arm','sword_forearm']:layers[n]=core.warp(up[n],np.eye(2)if n=='head'else rotation,cfg['chest_hinge'],chest)
  backing=Image.new('RGBA',(256,256));ImageDraw.Draw(backing).rectangle((121,100,147,133),fill=(45,18,22,255));layers['joint_backing']=core.warp(backing,np.eye(2),cfg['pelvis_rest'],pelvis);im=Image.new('RGBA',(256,256));rr['layers']={}
  for n in order:
   path=out/'layers'/f"{f['index']:03}-{n}.png";layers[n].save(path);rr['layers'][n]={'file':str(path.relative_to(out)),'sha256':sha(path)};im.alpha_composite(layers[n])
  path=out/'frames'/f"{f['index']:03}.png";im.save(path);rr.update({'file':str(path.relative_to(out)),'sha256':sha(path)});records.append(rr);ims.append(im)
 sheet=Image.new('RGBA',(1024,560),(38,43,50,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(0,72,9)):
  sheet.alpha_composite(ims[i],((j%4)*256,(j//4)*280));d.text(((j%4)*256+8,(j//4)*280+258),f'{i}: fixed shell/cap comparator',fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png');ims[0].save(out/'loop.gif',save_all=True,append_images=ims[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72))for i in range(72)],loop=0,disposal=2)
 data={'schema':'captain.greave_volume_trial.v1','state':'UNAPPROVED_COMPARATOR','source_sha256':sha(P/'source/leg-master-128.png'),'poses_sha256':sha(P/'source/poses.json'),'builder_sha256':sha(Path(__file__)),'surfaces':{n:{'UV_local_vertices':v,'triangles':tris[n]}for n,v in surfaces.items()},'records':records,'layer_order':order,'min_shell_world_z':zmin,'ownership':'Original source partitioned into separate cap/shaft/thigh regions; no old shin plane underneath closed replacement. Hidden surfaces fixed nearest-edge source-color extrusion. Upper remains exact source parts.'};(out/'manifest.json').write_text(json.dumps(data,indent=2));print(out)
if __name__=='__main__':main()
