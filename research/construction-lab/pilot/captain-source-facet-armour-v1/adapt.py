from pathlib import Path
p=Path(__file__).resolve().parent;s=(p.parent/'captain-greave-hidden-material-v1/build.py').read_text()
start=s.index('def texture(');end=s.index('\ndef main():',start)
s=s[:start]+'''def texture(src,mask,kind=None):
 if kind in ['shin','cap']:
  result=src.copy();result[:,:,3]=np.where(mask,src[:,:,3],0);result[result[:,:,3]==0]=0;return result
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);return src[idx[0],idx[1]].copy()

def facets(mask, source, leg, cam, kind):
 axis,t,norm=basis(leg,kind=='cap');M=core.bone_matrix(source['knee'],source['ankle'],np.array(leg['world']['knee']),np.array(leg['world']['ankle']),cam,np.array([-.8,-.6,0]));inv=np.linalg.inv(np.column_stack([cam@t,cam@axis]))
 ys,xs=np.nonzero(mask);u0,u1=int(xs.min())-2,int(xs.max())+3;v0,v1=int(ys.min())-2,int(ys.max())+3
 verts=[];tri=[];columns=list(range(u0,u1+1,2));rows=list(range(v0,v1+1,2));center=(u0+u1)/2;radius=max(1,(u1-u0)/2)
 for v in rows:
  for u in columns:
   transverse=(u-center)/radius;depth=(6.5 if kind=='cap' else 3.0)+(2.0 if kind=='cap' else 2.5)*max(0,1-transverse*transverse)
   target=M@(np.array([u,v])-source['knee']);yz=inv@(target-(cam@norm)*depth);verts.append([[u,v],[depth,float(yz[0]),float(yz[1])]])
 for iy in range(len(rows)-1):
  for ix in range(len(columns)-1):
   j=iy*len(columns)+ix;tri.extend([[j,j+1,j+len(columns)],[j+1,j+1+len(columns),j+len(columns)]])
 return verts,tri
''' + s[end:]
old="local,tr=geometry(kind,original,n);axis,t,norm=basis(leg,kind=='cap');B=np.column_stack([norm,t,axis]);uvs=[(np.array(source['knee'])+inv@(cam@(B@np.array(v)))).tolist()for v in local];surfaces[n+'_'+kind]=[[uv,v]for uv,v in zip(uvs,local)];tris[n+'_'+kind]=tr"
assert old in s;s=s.replace(old,"surfaces[n+'_'+kind],tris[n+'_'+kind]=facets(ownership[n][kind],source,leg,cam,kind)")
start=s.index(';material=None');end=s.index('   bv,bt=boot.surface(n)',start)
s=s[:start]+"\n    im,world,xy,depthbuf=raster.render(surfaces[n+'_'+kind],tris[n+'_'+kind],texts[n+'_'+kind],fake,cam,root,return_depth=True);layers[n+'_'+kind]=im;local_depths[kind]=depthbuf;rr['meshes'][n+'_'+kind]={'vertices_world':world.tolist(),'vertices_pixels':xy.tolist()};zmin=min(zmin,float(world[:,2].min()))\n   layer_depths[n]=local_depths\n"+s[end:]
s=s.replace("   for kind in ['shin','cap']:\n    axis", "   local_depths={}\n   for kind in ['shin','cap']:\n    axis")
s=s.replace("root=np.array(f['physical_root_pixels']);layers={};", "root=np.array(f['physical_root_pixels']);layers={};layer_depths={};")
s=s.replace("  pelvis=np.array(f['upper_pixels']['pelvis'])", "  for nn in ['far','near']:\n   shell=np.array(layers[nn+'_shin']);cap=np.array(layers[nn+'_cap']);select=(cap[:,:,3]>0)&((shell[:,:,3]==0)|(layer_depths[nn]['cap']>=layer_depths[nn]['shin']));shell[select]=cap[select];layers[nn+'_shin']=Image.fromarray(shell);layers[nn+'_cap']=Image.new('RGBA',(256,256))\n  pelvis=np.array(f['upper_pixels']['pelvis'])")
s=s.replace("'hidden_material':", "'surface_comparator':'Source alpha-preserving curved front facets, depth authored; cap/shaft actual per-pixel depth merge; no closed back claimed','hidden_material':")
(p/'build.py').write_text(s)
f=p/'source/boot-rasterizer.py';s=f.read_text().replace('unknown_material=None):','unknown_material=None,return_depth=False):').replace('return Image.fromarray(rgba),world,xy','return (Image.fromarray(rgba),world,xy,depth) if return_depth else (Image.fromarray(rgba),world,xy)');f.write_text(s)
f=p/'check.py';s=f.read_text().replace("out=P/'artifacts/shaded-long110'","out=P/'artifacts/front-facets-long110'");f.write_text(s)
