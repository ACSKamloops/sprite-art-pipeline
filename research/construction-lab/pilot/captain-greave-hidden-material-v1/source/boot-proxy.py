"""Closed authored 3D boot proxy. Visible UV projection + declared edge-extruded unknown sides."""
import json,math,argparse
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image,ImageDraw
import build as b
P=b.P
RINGS=[(-8,[(-7,0),(-8,6),(-6,12),(0,14),(6,12),(8,6),(7,0)]),(0,[(-7,0),(-8,9),(-6,24),(0,25.235093),(6,24),(8,9),(7,0)]),(10,[(-8,0),(-9,5),(-7,11),(0,13),(7,11),(9,5),(8,0)]),(20,[(-7,0),(-8,3),(-6,7),(0,8),(6,7),(8,3),(7,0)])]
def surface(n):
 vertices=[]
 for f,ring in RINGS:
  for t,z in ring:
   if n=='far':uv=[44+(-.6*f-.8*t)/.8,93+(.309016994*(.8*f-.6*t)+24-.951056516*z)/1.1]
   else:uv=[101-.2*f-.8*t,94+.06*f+.01*t+(24-.951056516*z)/1.2]
   vertices.append([uv,[f,t,z]])
 triangles=[]
 for k in range(3):
  for j in range(7):
   a=k*7+j;c=k*7+(j+1)%7;d=c+7;e=a+7;triangles.extend([[a,c,e],[c,d,e]])
 # End caps are fans of perimeter vertices. Their unobserved texture is declared.
 for k in [0,3]:
  for j in range(1,6):triangles.append([k*7,k*7+j,k*7+j+1])
 return vertices,triangles

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output);assert not out.exists();out.mkdir(parents=True);(out/'frames').mkdir();(out/'layers').mkdir();src=np.array(Image.open(P/'source/leg-master-128.png').convert('RGBA'));packet=json.loads((P/'source/poses.json').read_text());cam=np.array(packet['camera']['matrix_2x3']);tex={};surfs={};rows=[];ims=[];zmin=1e9
 yy,xx=np.mgrid[:128,:128]
 for n in ['far','near']:
  mask=(src[:,:,3]>0)&(yy>= (93 if n=='far' else 94))&((xx<69)if n=='far'else(xx>70));idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);tex[n]=src[idx[0],idx[1]].copy();Image.fromarray(tex[n]).save(out/f'{n}-edge-extended-UV.png');surfs[n]=surface(n)
 for f in packet['frames']:
  im=Image.new('RGBA',(256,256));r={'index':f['index'],'phase':f['phase'],'duration_ms':f['duration_ms'],'physical_root':f['physical_root_pixels'],'feet':{}}
  for n in ['far','near']:
   layer,world,xy=b.render(*surfs[n],tex[n],f['legs'][n],cam,np.array(f['physical_root_pixels']));zmin=min(zmin,float(world[:,2].min()));path=out/'layers'/f"{f['index']:03}-{n}.png";layer.save(path);im.alpha_composite(layer);r['feet'][n]={'file':str(path.relative_to(out)),'sha256':b.sha(path),'bbox':layer.getbbox(),'role':f['legs'][n]['foot']['role'],'vertices_world':world.tolist(),'vertices_pixels':xy.tolist()}
  path=out/'frames'/f"{f['index']:03}.png";im.save(path);r.update({'file':str(path.relative_to(out)),'sha256':b.sha(path)});rows.append(r);ims.append(im)
 sheet=Image.new('RGBA',(1024,560),(38,43,50,255));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(0,72,9)):
  sheet.alpha_composite(ims[i],((j%4)*256,(j//4)*280));d.text(((j%4)*256+8,(j//4)*280+10),f'frame{i} / closed volume proxy',fill='white')
 sheet.save(out/'eight-keys-native.png');sheet.resize((2048,1120),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png')
 ims[0].save(out/'loop.gif',save_all=True,append_images=ims[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72))for i in range(72)],loop=0,disposal=2)
 data={'schema':'captain.boot_closed_proxy.v1','state':'UNAPPROVED_PROXY','source_sha256':b.sha(P/'source/leg-master-128.png'),'poses_sha256':b.sha(P/'source/poses.json'),'proxy_builder_sha256':b.sha(Path(__file__)),'rasterizer_sha256':b.sha(P/'build.py'),'surfaces':{n:{'vertices_UV_local':v,'triangles':t}for n,(v,t)in surfs.items()},'records':rows,'qa':{'minimum_vertex_world_z':zmin},'unknown_surfaces':'Closed proxy shape is authored. Rear/underside textures are fixed nearest-source-edge extrusions, not recovered artwork or a new painted motif. Original source unchanged.'};(out/'manifest.json').write_text(json.dumps(data,indent=2));print(out)
if __name__=='__main__':main()
