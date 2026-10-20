"""Fixed manually bound source UV surface; rigid 3D feet, nearest painted texture."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
# UV [u,v] => fixed foot coordinates [forward, transverse, height].
# Sole corners define a quadrilateral, not the earlier unreliable heel/toe pixel pair.
BIND=json.loads((P/'binding.json').read_text())['surfaces']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def render(surface,triangles,texture,leg,cam,root):
 ft=leg['foot'];basis=np.column_stack([ft['orientation_world'][n] for n in ['forward','transverse','up']]);origin=np.array(ft['origin_world']); uv=np.array([v[0] for v in surface],float);local=np.array([v[1] for v in surface],float)
 world=local@basis.T+origin;xy=world@cam.T+np.array([130,239])-root;dep=world@np.array([0,math.cos(math.radians(18)),math.sin(math.radians(18))])
 rgba=np.zeros((256,256,4),np.uint8);depth=np.full((256,256),-np.inf);cov=np.zeros((256,256),bool)
 for inds in triangles:
  dst=xy[inds];src=uv[inds];det=np.linalg.det(np.column_stack([dst[1]-dst[0],dst[2]-dst[0]]))
  if abs(det)<1e-9:continue
  inv=np.linalg.inv(np.column_stack([dst[1]-dst[0],dst[2]-dst[0]]));x0=max(0,int(np.floor(dst[:,0].min())));x1=min(255,int(np.ceil(dst[:,0].max())));y0=max(0,int(np.floor(dst[:,1].min())));y1=min(255,int(np.ceil(dst[:,1].max())))
  if x1<x0 or y1<y0:continue
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];coords=np.stack([xx+.5,yy+.5],axis=-1);b=(coords-dst[0])@inv.T;weights=np.stack([1-b[...,0]-b[...,1],b[...,0],b[...,1]],axis=-1);inside=(weights>=-1e-9).all(axis=-1)
  sample=weights@src;ui=np.clip(np.floor(sample[...,0]).astype(int),0,127);vi=np.clip(np.floor(sample[...,1]).astype(int),0,127);colors=texture[vi,ui];z=weights@dep[inds]
  select=inside&(colors[...,3]>0)&(z>=depth[y0:y1+1,x0:x1+1]-1e-9);rgba[y0:y1+1,x0:x1+1][select]=colors[select];depth[y0:y1+1,x0:x1+1][select]=z[select];cov[y0:y1+1,x0:x1+1]|=select
 return Image.fromarray(rgba),world,xy

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output);assert not out.exists(),'Preserve previous outputs';out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir()
 source=P/'source/leg-master-128.png';texture=np.array(Image.open(source).convert('RGBA'));packet=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);meshes={n:Delaunay(np.array([v[0] for v in vs])).simplices.tolist() for n,vs in BIND.items()};records=[];images=[];minz=1e9;palette={tuple(c)for c in texture.reshape(-1,4) if c[3]};badcolors=0
 for f in packet['frames']:
  combined=Image.new('RGBA',(256,256));root=np.array(f['physical_root_pixels']);rr={'index':f['index'],'phase':f['phase'],'duration_ms':f['duration_ms'],'physical_root':list(root),'feet':{}}
  for n in ['far','near']:
   im,world,xy=render(BIND[n],meshes[n],texture,f['legs'][n],cam,root);minz=min(minz,float(world[:,2].min()));path=out/'layers'/f"{f['index']:03}-{n}.png";im.save(path);combined.alpha_composite(im)
   badcolors+=sum(tuple(c)not in palette for c in np.array(im).reshape(-1,4) if c[3]);rr['feet'][n]={'file':str(path.relative_to(out)),'sha256':sha(path),'bbox':im.getbbox(),'vertices_world':world.tolist(),'vertices_pixels':xy.tolist(),'role':f['legs'][n]['foot']['role'],'contact_episode':f['legs'][n]['foot']['episode'],'source_uv_mesh':n}
  path=out/'frames'/f"{f['index']:03}.png";combined.save(path);rr.update({'file':str(path.relative_to(out)),'sha256':sha(path)});records.append(rr);images.append(combined)
 sheet=Image.new('RGBA',(1024,560),(38,43,50,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(0,72,9)):
  sheet.alpha_composite(images[i],((j%4)*256,(j//4)*280));d.text(((j%4)*256+10,(j//4)*280+10),f"frame {i} / mesh volume trial",fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png')
 crop=sheet.crop((0,190,1024,256));crop.resize((2048,132),Image.Resampling.NEAREST).save(out/'first-half-boots-2x.png')
 images[0].save(out/'loop.gif',save_all=True,append_images=images[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72)) for i in range(72)],loop=0,disposal=2)
 data={'schema':'captain.boot_uv_surface.v1','state':'UNAPPROVED_AUTHORED_BINDING','source_sha256':sha(source),'poses_sha256':sha(P/'source/poses.json'),'builder_sha256':sha(Path(__file__)),'binding_sha256':sha(P/'binding.json'),'binding':BIND,'triangles':meshes,'records':records,'qa':{'min_vertex_world_z':minz,'new_opaque_RGBA_colors':badcolors,'alpha_values':sorted(set(np.array(images[0])[:,:,3].reshape(-1).tolist()))},'limitations':['Painted visible surface mesh, not recovered closed3D armor','Rear/bottom textures unknown; visible source surfaces may overlap at depth extremes','Source landmarks manually authored once; not imported unreliable3anchor registration','No pixel contact or art acceptance from vertex/anchor equations']}
 (out/'manifest.json').write_text(json.dumps(data,indent=2));print(json.dumps({'out':str(out),'min_world_z':minz,'new_colors':badcolors}))
if __name__=='__main__':main()
