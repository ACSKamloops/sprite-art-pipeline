"""Actual packed reload and separate standalone library append render checks."""
import bpy, json, hashlib, sys
from pathlib import Path
from mathutils import Matrix, Vector
from collections import Counter

P = Path(__file__).resolve().parent
OUT = P/'artifacts/fixed-row-uv-v2'
mode = 'append' if '--append' in sys.argv else 'reopen'
restore_components = '--restore-transform' in sys.argv
prefix = 'transform-'+mode if restore_components else mode
receipt = json.loads((OUT/'receipt.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(OUT/'shield-diagnostic.blend'))
scene = bpy.context.scene
owned = [o for o in scene.objects if o.name=='ShieldRoot' or o.parent and o.parent.name=='ShieldRoot']
if mode == 'append':
    for o in owned:
        bpy.data.objects.remove(o,do_unlink=True)
    with bpy.data.libraries.load(str(OUT/'ShieldRoot-module.blend'),link=False) as (src,dst):
        dst.objects=src.objects
    for o in dst.objects:
        if o:
            scene.collection.objects.link(o)
    owned=[o for o in dst.objects if o]
assert bpy.data.objects['LEFT_Hand_Attachment'].parent.name=='ShieldRoot'
assert all(not o.hide_render for o in owned if o.type=='MESH')
edges=Counter()
panel=bpy.data.objects['ShieldClosedCurvedPanel']
for polygon in panel.data.polygons:
    vs=list(polygon.vertices)
    for i,a in enumerate(vs):edges[tuple(sorted((a,vs[(i+1)%len(vs)])))]+=1
assert all(n==2 for n in edges.values())
camera=scene.camera
results=[]
for item in receipt['frames']:
    scene.render.resolution_x=scene.render.resolution_y=item['resolution']
    camera.matrix_world=Matrix(item['camera_matrix'])
    label=item['file'].split('-')[1]
    angle={'front':0,'threequarter':-3.141592653589793/4,'side':-3.141592653589793/2,'back':3.141592653589793}[label]
    rotation=Matrix.Rotation(angle,4,'Z')
    if restore_components:
        camera.location=rotation@Vector((0,-3,.45))
        camera.scale=(1,1,1)
        camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler()
    for name,position in [('Key',(-2,-3,3)),('Fill',(3,-2,1)),('Rim',(0,3,2))]:
        obj=bpy.data.objects[name];obj.location=rotation@Vector(position);obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
    path=OUT/(prefix+'-'+item['file']);scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    results.append({'reference':item['file'],'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT/(prefix+'-receipt.json')).write_text(json.dumps({'mode':mode,'restored_camera_components':restore_components,'module_sha256':hashlib.sha256((OUT/'ShieldRoot-module.blend').read_bytes()).hexdigest(),'actual_renders':results,'closed_panel_edge_incidence_2':True,'attachments':[o.name for o in owned if 'Attachment' in o.name],'packed_images':[{'name':im.name,'packed':bool(im.packed_file)}for im in bpy.data.images if im.name not in ['Render Result','Viewer Node']],'scope':'Static module exchange only; not carried motion, physical hand or art approval'},indent=2)+'\n')
