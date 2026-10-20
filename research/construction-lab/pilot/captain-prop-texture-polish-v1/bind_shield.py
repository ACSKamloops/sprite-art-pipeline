"""Fixed once-only UV registration onto real curved shield; no pose painting.

Generated pixels stay unchanged. The opaque row bounds define an explicit
nonuniform horizontal UV registration, rather than importing background glow.
This proposes new authored frontal paint and does not certify source fidelity.
"""
import bpy, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector, Matrix

P = Path(__file__).resolve().parent
SOURCE = Path('/home/astra/projects/captain-3d-generation-lab/modular-captain-equipment-v1/artifacts/trial-v2/ShieldRoot-module.blend')
cropped_tips = '--crop-tips' in sys.argv
OUT = P / ('artifacts/fixed-row-uv-v2' if cropped_tips else 'artifacts/fixed-row-uv-v1')
if OUT.exists():
    raise FileExistsError('Keep earlier candidates immutable')
OUT.mkdir(parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
    dst.objects = src.objects
for obj in dst.objects:
    if obj:
        scene.collection.objects.link(obj)
owned = [o for o in scene.objects]
body = bpy.data.objects['ShieldClosedCurvedPanel']
positions = [tuple(v.co) for v in body.data.vertices]
old_uv = [tuple(v.uv) for v in body.data.uv_layers.active.data]
registration = json.loads((P / 'source/uv-row-registration.json').read_text())
rows = {r[0]: r[1:] for r in registration['rows']}
first, last = min(rows), max(rows)
if cropped_tips:
    # One declared fixed crop avoids expanding a tiny decorative source tip
    # across the entire width of a shield with a broad physical top edge.
    max_span = max(hi-lo for lo,hi in rows.values())
    usable = [y for y,(lo,hi) in rows.items() if hi-lo >= .25*max_span]
    first, last = min(usable), max(usable)
width, height = registration['size']
uv = body.data.uv_layers.new(name='AuthoredShieldRowUV')
for polygon in body.data.polygons:
    for loop_idx in polygon.loop_indices:
        u, v = old_uv[loop_idx]
        y = round(last + (first-last)*v)
        lo, hi = rows[y]
        # Inset just one texel where possible to avoid the glow boundary.
        inset = min(1, (hi-lo)/4)
        x = lo+inset + u*(hi-lo-2*inset)
        uv.data[loop_idx].uv = ((x+.5)/width, 1-(y+.5)/height)
material = body.data.materials[0].copy()
material.name = 'AuthoredGoldBlackShieldFixedUV'
body.data.materials[0] = material
nodes = material.node_tree.nodes
links = material.node_tree.links
texture = next(n for n in nodes if n.type == 'TEX_IMAGE')
texture.image = bpy.data.images.load(str(P / 'source/alpha-edit-v2.png'))
texture.image.pack()
texture.interpolation = 'Closest'
uvnode = nodes.new('ShaderNodeUVMap')
uvnode.uv_map = uv.name
links.new(uvnode.outputs['UV'], texture.inputs['Vector'])
principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
# The closed shield surface is opaque; source alpha is only a UV-registration
# guide. Do not render a translucent physical shield or import outside haze.
links.new(texture.outputs['Color'], principled.inputs['Base Color'])
principled.inputs['Metallic'].default_value = .2
principled.inputs['Roughness'].default_value = .6
assert positions == [tuple(v.co) for v in body.data.vertices]
assert old_uv == [tuple(v.uv) for v in body.data.uv_layers[0].data]
for image in bpy.data.images:
    if image.name not in ['Render Result', 'Viewer Node']:
        image.pack()
bpy.data.libraries.write(str(OUT / 'ShieldRoot-module.blend'), set(owned), fake_user=True)
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.threads_mode = 'FIXED'
scene.render.threads = 4
scene.render.film_transparent = True
scene.view_settings.view_transform = 'Standard'
scene.world = bpy.data.worlds.new('StudioWorld')
scene.world.color = (.15,.15,.15)
camera_data = bpy.data.cameras.new('Camera')
camera = bpy.data.objects.new('Camera',camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 1.6
lights = []
for name, position, energy in [('Key',(-2,-3,3),450),('Fill',(3,-2,1),280),('Rim',(0,3,2),350)]:
    data = bpy.data.lights.new(name,'AREA')
    data.energy = energy
    data.size = 4
    obj = bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    lights.append((obj,Vector(position)))
frames = []
for resolution in [256,384]:
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    for label, angle in [('front',0),('threequarter',-math.pi/4),('side',-math.pi/2),('back',math.pi)]:
        rotation = Matrix.Rotation(angle,4,'Z')
        camera.location = rotation @ Vector((0,-3,.45))
        camera.rotation_euler = (-camera.location).to_track_quat('-Z','Y').to_euler()
        for light, position in lights:
            light.location = rotation @ position
            light.rotation_euler = (-light.location).to_track_quat('-Z','Y').to_euler()
        path = OUT / f'shield-{label}-native{resolution}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        frames.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resolution':resolution,'camera_matrix':[list(r)for r in camera.matrix_world]})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'shield-diagnostic.blend'))
(OUT / 'receipt.json').write_text(json.dumps({'state':'UNAPPROVED_SOURCE_CONDITIONED_FIXED_UV_PROPOSAL','input_module_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256((P/'source/alpha-edit-v2.png').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'registration':{'first_row':first,'last_row':last,'alpha_threshold':248,'crop_tiny_tips_min_width_fraction':.25 if cropped_tips else None,'per_row_horizontal_warp':True,'same_for_every_pose_and_view':True},'original_positions_and_original_UV_unchanged':True,'new_UV_layer':uv.name,'attachment':list(bpy.data.objects['LEFT_Hand_Attachment'].location),'frames':frames,'limits':['Authored frontal motif not exact original pixel recovery','Existing shield outline/volume retained; texture shape is warped to that surface','Camera-relative studio lights diagnose materials only','Packed module append and equipped motion require separate checks']},indent=2)+'\n')
