"""Render the smaller socket trial; retain all previous rejected candidates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_candidates import SOURCE, EXPECTED, mesh_fingerprint, evaluated_pose_fingerprint

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--resolution',type=int,choices=(256,384),required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
out=HERE/'compact-renders'/f'native{args.resolution}'
out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
geometry=mesh_fingerprint();poses=evaluated_pose_fingerprint()
texture=HERE/'compact-candidate/compact-steel-socket.png'
image=bpy.data.images.load(str(texture),check_existing=False);image.colorspace_settings.name='sRGB';image.pack()
bindings=[]
for material in bpy.data.materials:
    if not material.use_nodes:continue
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.name.startswith('Material_0-side-polish-UV'):
            bindings.append(material.name);node.image=image
assert len(bindings)==3
assert geometry==mesh_fingerprint() and poses==evaluated_pose_fingerprint()
scene.render.resolution_x=scene.render.resolution_y=args.resolution;scene.render.resolution_percentage=100
scene.render.threads_mode='FIXED';scene.render.threads=6
for frame in (1,33,103):
    scene.frame_set(frame);scene.render.filepath=str(out/f'compact-source{frame:03}.png');bpy.ops.render.render(write_still=True)
if args.resolution==384:
    scene.frame_set(33);scene.render.filepath=str(out/'compact-source033.png');packed=out/'compact-steel-socket.blend';bpy.ops.wm.save_as_mainfile(filepath=str(packed));bpy.ops.wm.open_mainfile(filepath=str(packed));bpy.context.scene.render.filepath=str(out/'compact-reopened-source033.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
(out/'receipt.json').write_text(json.dumps({'state':'BOUNDED_COMPACT_SOCKET_NOT_ART_APPROVAL','source_SHA256':EXPECTED,'texture_SHA256':hashlib.sha256(texture.read_bytes()).hexdigest(),'script_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'geometry_UV_weights_shapes_SHA256':geometry,'all521_pose_object_shape_values_SHA256':poses,'protected_signatures_exact':True,'image_bindings':bindings,'source_frames':[1,33,103],'native_resolution':args.resolution},indent=2)+'\n')
