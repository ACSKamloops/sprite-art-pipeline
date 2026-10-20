"""Independent Blender projection witness; run with Blender in background.

Reads frozen render scene only and prints pixels for world points. No scene save.
"""
import bpy, json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from pathlib import Path

path=Path('/home/astra/projects/captain-3d-rig-lab/render/body-semantic-v1/diagnostic-render.blend')
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene
points=[(0,0,-1),(1,0,-1),(0,-1,-1),(0,0,0),(0,0,1),(.012263623,-1.415660858,-1)]
result=[]
for point in points:
    p=world_to_camera_view(scene,scene.camera,Vector(point))
    result.append({'world':point,'pixel':[p.x*256,(1-p.y)*256],'depth':p.z})
print('PROJECTION_WITNESS_JSON='+json.dumps(result))
