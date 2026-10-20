import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;c=s.camera;size=256;s.render.resolution_x=size;s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.device='CPU'
a=next(o for o in s.objects if o.type=='ARMATURE' and 'lshin' in o.pose.bones)
allrec=[]
for f in [93,103,113,117]:
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rec={'source':f,'joints':{},'rays':[]};cache={}
 for side in ['l','r']:
  for joint,bone,part in [('hip',side+'thigh','head'),('knee',side+'shin','head'),('ankle',side+'foot','head')]:
   world=a.matrix_world@getattr(a.pose.bones[bone],part);v=world_to_camera_view(s,c,world);rec['joints'][side+'_'+joint]={'bone':bone,'endpoint':part,'world':list(world),'pixel':[v.x*size,(1-v.y)*size],'camera_depth':v.z}
  px,py=rec['joints'][side+'_knee']['pixel']
  for y in range(round(py)-4,round(py)+5):
   for x in range(round(px)-4,round(px)+5):
    mat=c.matrix_world;origin=mat.translation+mat.col[0].xyz*((x+.5)/size-.5)*c.data.ortho_scale+mat.col[1].xyz*(.5-(y+.5)/size)*c.data.ortho_scale;d=-mat.col[2].xyz
    hit,p,n,idx,obj,mw=s.ray_cast(dg,origin,d)
    if not hit:continue
    if obj.name not in cache:
     ev=obj.evaluated_get(dg);mesh=ev.to_mesh();cache[obj.name]=(ev,mesh)
    ev,mesh=cache[obj.name];poly=mesh.polygons[idx];groups={g.index:g.name for g in obj.vertex_groups};weights={}
    topology=len(mesh.vertices)==len(obj.data.vertices) and len(mesh.polygons)==len(obj.data.polygons)
    if topology:
     for vi in poly.vertices:
      for g in obj.data.vertices[vi].groups:weights[groups[g.group]]=weights.get(groups[g.group],0)+g.weight/len(poly.vertices)
    rec['rays'].append({'target':side+'_knee','pixel':[x,y],'object':obj.name,'polygon':idx,'world_hit':list(p),'source_index_counts_agree':topology,'source_vertex_ids':list(poly.vertices),'average_source_face_weights':weights,'parent_bone':obj.parent_bone})
 if f==117:
  s.render.filepath=str(out/'source-117.png');bpy.ops.render.render(write_still=True)
 allrec.append(rec)
 for ev,mesh in cache.values():ev.to_mesh_clear()
(out/'joints-and-rays.json').write_text(json.dumps({'camera_world':[list(r) for r in c.matrix_world],'ortho':c.data.ortho_scale,'resolution':size,'armature':a.name,'records':allrec},indent=2))
