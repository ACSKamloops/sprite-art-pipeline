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
previous_build=sys.modules.get('build');raster=load('boot_rasterizer',P/'source/boot-rasterizer.py');sys.modules['build']=raster;boot=load('frozen_boot_proxy',P/'source/boot-proxy.py')
if previous_build is not None:sys.modules['build']=previous_build
else:sys.modules.pop('build',None)
CFG=core.CFG

def basis(leg,cap=False):
 w=leg['world'];axis=core.unit(np.array(w['ankle'])-w['knee'])
 if cap:axis=core.unit(axis+core.unit(np.array(w['knee'])-w['hip']))
 t=np.array([-.8,-.6,0]);t=core.unit(t-axis*np.dot(t,axis));n=core.unit(np.cross(axis,t))
 if np.dot(n,[0,math.cos(math.radians(18)),math.sin(math.radians(18))])<0:n=-n
 return axis,t,n

def geometry(kind,original=False,leg_name=None):
 verts=[];tri=[];sides=16
 if kind=='thigh':rings=[(0,8,5),(24,8,5),(34,7,5),(44,7,5)]
 elif kind=='shin':rings=[(0,11,7),(12,12,7),(28,11,6),(40,9,5),(48,8,5)] if original else [(0,14,8),(12,14,8),(28,12,7),(40,10,6),(48,9,5)]
 else:rings=[((13 if original else 16)*math.sin(p),(11 if original else 16)*math.cos(p),(5 if original else 6)*math.cos(p))for p in np.linspace(-math.pi/2,math.pi/2,9)]
 if kind=='shin' and leg_name is not None:
  rings=json.loads((P/'calibration.json').read_text())['legs'][leg_name]['rings']
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

def texture(src,mask,kind=None):
 if kind in ['shin','cap','shin_ornament']:
  result=src.copy();result[:,:,3]=np.where(mask,src[:,:,3],0);result[result[:,:,3]==0]=0;return result
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);return src[idx[0],idx[1]].copy()

def facets(mask, source, leg, cam, kind):
 axis,t,norm=basis(leg,kind=='cap');M=core.bone_matrix(source['knee'],source['ankle'],np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array([-.8,-.6,0]));inv=np.linalg.inv(np.column_stack([cam@t,cam@axis]))
 ys,xs=np.nonzero(mask);u0,u1=int(xs.min())-2,int(xs.max())+3;v0,v1=int(ys.min())-2,int(ys.max())+3
 verts=[];tri=[];columns=list(range(u0,u1+1,2));rows=list(range(v0,v1+1,2));center=(u0+u1)/2;radius=max(1,(u1-u0)/2)
 for v in rows:
  for u in columns:
   transverse=(u-center)/radius;depth=1.0 if kind=='shin_ornament' else (6.5 if kind=='cap' else 3.0)+(2.0 if kind=='cap' else 2.5)*max(0,1-transverse*transverse)
   target=M@(np.array([u,v])-source['knee']);yz=inv@(target-(cam@norm)*depth);verts.append([[u,v],[depth,float(yz[0]),float(yz[1])]])
 for iy in range(len(rows)-1):
  for ix in range(len(columns)-1):
   j=iy*len(columns)+ix;tri.extend([[j,j+1,j+len(columns)],[j+1,j+1+len(columns),j+len(columns)]])
 return verts,tri

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--source-mode',choices=['cell','original'],default='original');ap.add_argument('--poses',default=str(P/'source/poses.json'));a=ap.parse_args();original=a.source_mode=='original';out=Path(a.output);assert not out.exists();out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir();(out/'parts').mkdir();(out/'integration-layers').mkdir()
 source_path=P/'source/upper/source/native-256.png' if original else P/'source/leg-master-128.png';src=np.array(Image.open(source_path).convert('RGBA'));pose_path=Path(a.poses);packet=json.loads(pose_path.read_text());calibration=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);cfg,up,receipt=upper.construct(out/'upper-parts');ownership=masks(src) if not original else {};
 if original:
  yy,xx=np.mgrid[:256,:256]
  for n in ['far','near']:
   own=np.array(Image.open(out/'upper-parts/source-owned'/f'{n}_leg.png'))[:,:,3]>0;cap=Image.new('L',(256,256));ImageDraw.Draw(cap).ellipse((97,153,120,181) if n=='far' else (142,154,165,180),fill=255);cm=np.array(cap)>0;cut=152 if n=='far' else 154;bc=205 if n=='far' else 209
   ownership[n]={'cap':own&cm,'shin':own&(yy>=cut)&(yy<=bc)&~cm,'thigh':own&(yy<cut)&~cm,'boot':own&(yy>bc)}
 if original:
  armor_polys={'far':[(101,174),(117,176),(119,189),(114,205),(99,210),(91,206),(96,188)],'near':[(145,179),(158,179),(165,191),(174,209),(163,214),(148,211),(143,192)]}
  for nn in ['far','near']:
   am=Image.new('L',(256,256));ImageDraw.Draw(am).polygon(armor_polys[nn],fill=255);armor=np.array(am)>0;full=ownership[nn]['shin'].copy();ownership[nn]['shin']=full&armor;ownership[nn]['shin_ornament']=full&~armor
 if original:
  source_cfg={n:{k:cfg['legs'][n][k] for k in ['hip','knee','ankle']} for n in ['far','near']}
 else:source_cfg=CFG
 texts={};surfaces={};tris={};parts={};bind=calibration['neutral_bind']
 for n in ['far','near']:
  for kind in ['thigh','shin','cap','boot','shin_ornament']:
   im=src.copy();im[:,:,3]=np.where(ownership[n][kind],src[:,:,3],0);im[im[:,:,3]==0]=0;parts[n+'_'+kind]=Image.fromarray(im);parts[n+'_'+kind].save(out/'parts'/f'{n}_{kind}-source.png');texts[n+'_'+kind]=texture(src,ownership[n][kind],kind);Image.fromarray(texts[n+'_'+kind]).save(out/'parts'/f'{n}_{kind}-extended-UV.png')
  source=source_cfg[n];leg=bind['legs'][n];M=core.bone_matrix(source['knee'],source['ankle'],np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array(packet['camera']['transverse']));inv=np.linalg.inv(M)
  for kind in ['shin','cap','shin_ornament']:
   surfaces[n+'_'+kind],tris[n+'_'+kind]=facets(ownership[n][kind],source,leg,cam,kind)
 order=['cape','backpack_halo','far_thigh','far_shin','far_cap','far_boot','near_thigh','near_shin','near_cap','near_boot','joint_backing','sword_upper_arm','sword_forearm','waist','chest','head','tabard','shield'];records=[];ims=[];zmin=1e9;newcolors=0;palette={tuple(c)for c in src.reshape(-1,4)if c[3]};closed={}
 for f in packet['frames']:
  root=np.array(f['physical_root_pixels']);layers={};layer_depths={};rr={'index':f['index'],'duration_ms':f['duration_ms'],'phase':f['phase'],'physical_root':list(root),'meshes':{}}
  for n,c in source_cfg.items():
   leg=f['legs'][n];w=leg['world'];pix={k:np.array(v)-root for k,v in leg['pixels'].items()};M=core.bone_matrix(c['hip'],c['knee'],np.array(w['hip']),np.array(w['knee']),cam,np.array(packet['camera']['transverse']));plate=core.warp(parts[n+'_thigh'],M,c['hip'],pix['hip'])
   ta=core.unit(np.array(w['knee'])-w['hip']);tt=np.array(packet['camera']['transverse']);tt=core.unit(tt-ta*np.dot(tt,ta));tn=core.unit(np.cross(ta,tt));tv,tr=geometry('thigh',original);tube_surface=[]
   for vv in tv:
    tube_surface.append([[0,0 if vv[2]<30 else 1],vv])
   colors={kk:np.array(Image.open(P/'source/upper/source/native-256.png').convert('RGBA'))[cfg['hidden_palette_sample_points'][kk][1],cfg['hidden_palette_sample_points'][kk][0]]for kk in ['dark_red','joint']};tube_texture=np.array([[colors['dark_red']],[colors['joint']]],np.uint8);fake_thigh={'foot':{'orientation_world':{'forward':tn,'transverse':tt,'up':ta},'origin_world':w['hip']}};tube,tw,tpx=raster.render(tube_surface,tr,tube_texture,fake_thigh,cam,root);tube.alpha_composite(plate);layers[n+'_thigh']=tube;rr['meshes'][n+'_thigh_underlap']={'vertices_world':tw.tolist(),'vertices_pixels':tpx.tolist(),'authorship':'fixed tapered femur tube, extends2worldunits past knee, source dark_red/joint palette'}
   local_depths={}
   for kind in ['shin','cap','shin_ornament']:
    axis,t,norm=basis(leg,kind=='cap');fake={'foot':{'orientation_world':{'forward':norm,'transverse':t,'up':axis},'origin_world':w['knee']}}
    im,world,xy,depthbuf=raster.render(surfaces[n+'_'+kind],tris[n+'_'+kind],texts[n+'_'+kind],fake,cam,root,return_depth=True);layers[n+'_'+kind]=im;local_depths[kind]=depthbuf;rr['meshes'][n+'_'+kind]={'vertices_world':world.tolist(),'vertices_pixels':xy.tolist()};zmin=min(zmin,float(world[:,2].min()))
   layer_depths[n]=local_depths
   bv,bt=boot.surface(n)
   if original:
    uv=[]
    for old,v in bv:
     ff,tt,zz=v
     uv.append([[102+(-.6*ff-.8*tt)/1.15,211+(.309016994*(.8*ff-.6*tt)+24-.951056516*zz)/1.2] if n=='far' else [159-.1*ff-.9*tt,215+.06*ff+.01*tt+(24-.951056516*zz)/1.1],v])
    bv=uv
   im,world,xy=raster.render(bv,bt,texts[n+'_boot'],leg,cam,root);layers[n+'_boot']=im
  for nn in ['far','near']:
   leg=f['legs'][nn];axis,t,norm=basis(leg);fake={'foot':{'orientation_world':{'forward':norm,'transverse':t,'up':axis},'origin_world':leg['world']['knee']}}
   cv=[];ct=[]
   for long,radius in [(38,5),(44,6),(50,5)]:
    for j in range(12):
     angle=2*math.pi*j/12;cv.append([[0,0],[4*math.cos(angle),radius*math.sin(angle),long]])
   for ring in range(2):
    for j in range(12):
     a0=ring*12+j;b0=ring*12+(j+1)%12;ct.extend([[a0,b0,a0+12],[b0,b0+12,a0+12]])
   color=src[cfg['hidden_palette_sample_points']['joint'][1],cfg['hidden_palette_sample_points']['joint'][0]];collar,_,_,cd=raster.render(cv,ct,np.array([[color]]),fake,cam,root,return_depth=True)
   shell=np.array(layers[nn+'_shin']);db=layer_depths[nn]['shin'].copy();under=np.array(collar);show=(under[:,:,3]>0)&(shell[:,:,3]==0);shell[show]=under[show];db[show]=cd[show]
   for piece in ['shin_ornament','cap']:
    cap=np.array(layers[nn+'_'+piece]);select=(cap[:,:,3]>0)&((shell[:,:,3]==0)|(layer_depths[nn][piece]>=db));shell[select]=cap[select];db[select]=layer_depths[nn][piece][select]
   layers[nn+'_shin']=Image.fromarray(shell);layers[nn+'_cap']=Image.new('RGBA',(256,256))
  pelvis=np.array(f['upper_pixels']['pelvis'])-root;chest=np.array(f['upper_pixels']['chest'])-root;rest=packet['neutral_bind']['upper_pixels'];chest+=np.array(cfg['chest_hinge'])-np.array(cfg['pelvis_rest'])-(np.array(rest['chest'])-rest['pelvis']);ang=math.radians(f['chest_counterrotation_degrees']);rotation=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
  for n in ['cape','tabard','waist']:layers[n]=core.warp(up[n],np.eye(2),cfg['pelvis_rest'],pelvis)
  for n in ['chest','head','shield','backpack_halo','sword_upper_arm','sword_forearm']:layers[n]=core.warp(up[n],np.eye(2)if n=='head'else rotation,cfg['chest_hinge'],chest)
  backing=Image.new('RGBA',(256,256));ImageDraw.Draw(backing).rectangle((121,100,147,133),fill=(45,18,22,255));layers['joint_backing']=core.warp(backing,np.eye(2),cfg['pelvis_rest'],pelvis);im=Image.new('RGBA',(256,256));rr['layers']={}
  for n in order:
   path=out/'layers'/f"{f['index']:03}-{n}.png";layers[n].save(path);rr['layers'][n]={'file':str(path.relative_to(out)),'sha256':sha(path)};im.alpha_composite(layers[n])
  rr['integration_layers']={}
  for nn in ['far','near']:
   combo=layers[nn+'_shin'].copy();combo.alpha_composite(layers[nn+'_cap'])
   for suffix,layer in [('shin',combo),('boot',layers[nn+'_boot']),('thigh',layers[nn+'_thigh'])]:
    ip=out/'integration-layers'/f"{f['index']:03}-{nn}_{suffix}.png";layer.save(ip);rr['integration_layers'][nn+'_'+suffix]={'file':str(ip.relative_to(out)),'sha256':sha(ip),'ownership':'shin includes separately articulated kneecap' if suffix=='shin' else suffix}
  path=out/'frames'/f"{f['index']:03}.png";im.save(path);rr.update({'file':str(path.relative_to(out)),'sha256':sha(path)});records.append(rr);ims.append(im)
 sheet=Image.new('RGBA',(1024,560),(38,43,50,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(0,72,9)):
  sheet.alpha_composite(ims[i],((j%4)*256,(j//4)*280));d.text(((j%4)*256+8,(j//4)*280+258),f'{i}: fixed shell/cap comparator',fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png');ims[0].save(out/'loop.gif',save_all=True,append_images=ims[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72))for i in range(72)],loop=0,disposal=2)
 data={'schema':'captain.greave_volume_trial.v1','state':'UNAPPROVED_COMPARATOR','source_sha256':sha(source_path),'source_mode':a.source_mode,'source_anchors':source_cfg,'poses_sha256':sha(pose_path),'fixed_UV_bind_poses_sha256':sha(P/'source/poses.json'),'builder_sha256':sha(Path(__file__)),'calibration_sha256':sha(P/'calibration.json'),'surfaces':{n:{'UV_local_vertices':v,'triangles':tris[n]}for n,v in surfaces.items()},'records':records,'layer_order':order,'min_shell_world_z':zmin,'authored_hidden_thigh':'fixed femur-owned tapered tube, radius7..8 depth5, length44 over bone42; source sampled dark_red/joint colors; source plate remains foreground','armour_ownership_polygons':armor_polys,'authored_ankle_collar':'Fixed shin-owned dark joint sleeve longitudinal38..50, radial5..6/depth4 behind source plate and boot; source sampled joint RGBA. Not extracted surface.','surface_comparator':'Source alpha-preserving curved front facets, depth authored; cap/shaft actual per-pixel depth merge; no closed back claimed','hidden_material':'No outside-owned UV fill; explicit source-alpha front facets only; flat separate ornament sheet depth1 and curved armor depth3..5.5/cap6.5..8.5 authored. Closed back unknown.', 'ownership':'Source armor and ornament masks partition inherited shaft exactly; source front alpha mapped to curved armor or flat ornament. Cap/shaft depth merge; explicit hidden femur tube and ankle collar. Unseen back unsupported. Upper/boots remain previous exact implementation.'};(out/'manifest.json').write_text(json.dumps(data,indent=2));print(out)
if __name__=='__main__':main()
