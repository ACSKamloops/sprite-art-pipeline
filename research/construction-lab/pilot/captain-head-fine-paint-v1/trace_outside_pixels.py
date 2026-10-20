"""Identify direct surface owners of changed pixels outside the head ROI."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.geometry import barycentric_transform

HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-wide-accommodation-v1/full-captain-wide-cape-camera12-packed.blend')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;camera=scene.camera
requests=json.loads((HERE/'outside-head-ray-requests.json').read_text());rows=[]
for frame in (1,33,103):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();cache={}
    for request in requests:
        if request['frame']!=frame:continue
        x,y=request['pixel'];matrix=camera.matrix_world
        origin=matrix.translation+matrix.col[0].xyz*((x+.5)/384-.5)*camera.data.ortho_scale+matrix.col[1].xyz*(.5-(y+.5)/384)*camera.data.ortho_scale
        hit,position,normal,index,obj,world=scene.ray_cast(deps,origin,-matrix.col[2].xyz)
        row=dict(request,ray_hit=bool(hit))
        if hit:
            row.update(object=obj.name,polygon=index)
            if obj.type=='MESH':
                if obj.name not in cache:
                    evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();triangles={}
                    for triangle in mesh.loop_triangles:triangles.setdefault(triangle.polygon_index,[]).append(triangle)
                    cache[obj.name]=(evaluated,mesh,triangles)
                evaluated,mesh,triangles=cache[obj.name];polygon=mesh.polygons[index]
                groups={group.index:group.name for group in obj.vertex_groups}
                weights={vertex:[(groups[group.group],group.weight)for group in obj.data.vertices[vertex].groups]for vertex in polygon.vertices}
                row['vertex_owners']=weights
                row['pure_head_surface']=all(any(name=='head'and weight>.999999 for name,weight in owner)for owner in weights.values())
                if mesh.uv_layers.active:
                    local=evaluated.matrix_world.inverted()@position
                    for triangle in triangles[index]:
                        a,b,c=[mesh.vertices[v].co for v in triangle.vertices]
                        bary=barycentric_transform(local,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
                        if min(bary)<-1e-4:continue
                        uv=sum((mesh.uv_layers.active.data[loop].uv*weight for loop,weight in zip(triangle.loops,bary)),Vector((0,0)))
                        row['UV']=list(uv)
                        row['material']=mesh.materials[polygon.material_index].name
                        break
        rows.append(row)
    for evaluated,mesh,triangles in cache.values():evaluated.to_mesh_clear()
(HERE/'outside-head-ray-owners.json').write_text(json.dumps({'state':'DIRECT_SURFACE_WITNESS_NOT_FULL_GI_ATTRIBUTION','source_SHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'rows':rows,'limits':['Geometric pixel centre; antialiasing covers nearby surfaces','Indirect lighting can alter unedited surfaces; directUV sample requires independent image check']},indent=2)+'\n')
print('OUTSIDE_RAY_OWNERS',len(rows))
