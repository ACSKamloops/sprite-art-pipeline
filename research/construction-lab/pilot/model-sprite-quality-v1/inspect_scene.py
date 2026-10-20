import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent/'candidate-walk-rpg128-v4';s=bpy.context.scene;v=world_to_camera_view(s,s.camera,Vector((0,0,0)))
r={'canvas':[128,128],'projected_world_origin_pivot':[v.x*128,(1-v.y)*128],'pivot_scope':'Projection of fixed world origin at groundplaneZ0; not a perframe fitted sole or physicalcontact validation. Same orthographic scale/elevation for allfour directions.','camera':{'location':list(s.camera.location),'rotation_euler':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale},'meshes':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'UV_layers':list(o.data.uv_layers.keys()),'armature_modifiers':[m.object.name for m in o.modifiers if m.type=='ARMATURE'],'hidden_render':o.hide_render}for o in bpy.data.objects if o.type=='MESH'],'bones':len(bpy.data.objects['CharacterArmature'].data.bones),'texture_images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)}for i in bpy.data.images if i.type!='RENDER_RESULT']};(p/'scene-contract.json').write_text(json.dumps(r,indent=2)+'\n')
