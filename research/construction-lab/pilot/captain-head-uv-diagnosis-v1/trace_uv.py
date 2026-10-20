import bpy,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;cam=s.camera;size=384;img=bpy.data.images['Material_0-side-polish-UV.png'];pixels=np.empty(2048*2048*4,dtype=np.float32);img.pixels.foreach_get(pixels);np.save(out/'packed-texture-linear-float.npy',pixels.reshape(2048,2048,4))
uvtris=[];headflags=[];owners=[];meshes=[]
for o in s.objects:
 if o.type!='MESH' or not any(m and m.use_nodes and any(n.type=='TEX_IMAGE' and n.image==img for n in m.node_tree.nodes) for m in o.data.materials): continue
 m=o.data;m.calc_loop_triangles();groups={g.index:g.name for g in o.vertex_groups};owned={v.index:[(groups[g.group],g.weight)for g in v.groups]for v in m.vertices};uv=m.uv_layers.active.data
 for t in m.loop_triangles:
  # Only faces actually using this image, not constant cap/joint slots.
  mat=m.materials[m.polygons[t.polygon_index].material_index]
  if not mat or not mat.use_nodes or not any(n.type=='TEX_IMAGE' and n.image==img for n in mat.node_tree.nodes):continue
  hs=all(any(n=='head' and w>.999999 for n,w in owned[v]) and sum(w for n,w in owned[v] if n!='head')<1e-6 for v in t.vertices)
  uvtris.append([list(uv[l].uv)for l in t.loops]);headflags.append(hs);owners.append([o.name,t.polygon_index,list(t.vertices)])
 meshes.append({'object':o.name,'vertices':len(m.vertices),'faces':len(m.polygons)})
np.savez_compressed(out/'source-uv-triangles.npz',uv=np.array(uvtris),head=np.array(headflags));(out/'source-triangle-owners.json').write_text(json.dumps(owners))
records=[];named=[]
manual={1:{'hair':(185,82),'forehead':(185,90),'cyber_eye':(193,96),'temple_plate':(203,102),'cheek':(186,107)},33:{'hair':(184,89),'forehead':(183,97),'cyber_eye':(191,103),'temple_plate':(203,110),'cheek':(183,114)},103:{'hair':(185,85),'forehead':(185,93),'cyber_eye':(193,100),'temple_plate':(203,105),'cheek':(186,110)}}
for f in [1,33,103]:
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache={}
 for y in range(76,124):
  for x in range(168,212):
   mat=cam.matrix_world;origin=mat.translation+mat.col[0].xyz*((x+.5)/size-.5)*cam.data.ortho_scale+mat.col[1].xyz*(.5-(y+.5)/size)*cam.data.ortho_scale;direction=-mat.col[2].xyz
   hit,pos,norm,idx,obj,world=s.ray_cast(dg,origin,direction)
   if not hit or obj.name!='CaptainArticulatedBody':continue
   if obj.name not in cache:
    ev=obj.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();tri={}
    for t in m.loop_triangles:tri.setdefault(t.polygon_index,[]).append(t)
    cache[obj.name]=(ev,m,tri)
   ev,m,tri=cache[obj.name];p=m.polygons[idx];gmap={g.index:g.name for g in obj.vertex_groups};vw={v:[(gmap[g.group],g.weight)for g in obj.data.vertices[v].groups]for v in p.vertices};hs=all(any(n=='head' and w>.999999 for n,w in ws) for ws in vw.values())
   if not hs:continue
   local=ev.matrix_world.inverted()@pos;uv=m.uv_layers.active.data;best=None
   for t in tri[idx]:
    a,b,c=[m.vertices[i].co for i in t.vertices];u=barycentric_transform(local,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
    if min(u)>=-1e-4:best=(t,u);break
   if best is None:continue
   t,w=best;v=sum((uv[l].uv*ww for l,ww in zip(t.loops,w)),Vector((0,0)));rec={'source_frame':f,'pixel_xy':[x,y],'object':obj.name,'evaluated_polygon':idx,'source_polygon':idx,'topology_counts_agree':len(m.vertices)==len(obj.data.vertices) and len(m.polygons)==len(obj.data.polygons),'source_vertex_ids':list(p.vertices),'source_vertex_weights':vw,'material':m.materials[p.material_index].name,'uv':list(v),'texture_xy_top_origin':[int(v.x*2048),int((1-v.y)*2048)],'world_hit':list(pos)};records.append(rec)
   for label,xy in manual[f].items():
    if (x,y)==xy:named.append({'feature_label_visual_proposal':label,**rec})
 for ev,m,tri in cache.values():ev.to_mesh_clear()
(out/'visible-head-pixel-map.json').write_text(json.dumps(records,indent=2));(out/'named-feature-rays.json').write_text(json.dumps(named,indent=2));(out/'trace-summary.json').write_text(json.dumps({'head_source_triangles':sum(headflags),'nonhead_image_triangles':len(headflags)-sum(headflags),'meshes':meshes,'visible_head_pixels':len(records),'named_feature_hits':len(named),'mapping_limit':'Geometric pixel-centre primary ray; Cycles antialiasing/light shading can mix neighboring samples. Source/evaluated polygon index used only with counts agreement; no topology-generating body modifier expected.'},indent=2));print(len(records),len(named))
