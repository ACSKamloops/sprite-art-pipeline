"""Independent Blender camera projection for frozen integrated256/384 scenes."""
import bpy, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-source-hinge-v4')
OUT=Path('/home/astra/artifacts/captain-integrated-projection-v4')
OUT.mkdir(exist_ok=False)
rows=[]
for size in [256,384]:
    scene_file=ROOT/f'native{size}/full-captain-diagnostic.blend'
    bpy.ops.wm.open_mainfile(filepath=str(scene_file));scene=bpy.context.scene
    assert scene.render.resolution_x==size and scene.render.resolution_y==size
    points=[]
    for point in [(0,0,-1),(.25,0,-1),(0,.25,-1),(0,0,0),(1,-2,-1),(-1,.5,.7)]:
        p=world_to_camera_view(scene,scene.camera,Vector(point))
        points.append({'world':point,'actual_blender_pixel':[float(p.x*size),float((1-p.y)*size)]})
    rows.append({'resolution':size,'scene_sha256':hashlib.sha256(scene_file.read_bytes()).hexdigest(),'camera_matrix':[list(r)for r in scene.camera.matrix_world],'points':points})
(OUT/'witness.json').write_text(json.dumps({'method':'bpy_extras.object_utils.world_to_camera_view','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'witnesses':rows},indent=2)+'\n')
