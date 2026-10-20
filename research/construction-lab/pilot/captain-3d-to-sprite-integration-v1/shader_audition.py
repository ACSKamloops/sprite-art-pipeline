"""Three controlled model-shader choices, actual384px source-pose renders.

Reads frozen fullCaptain scene. Separate diagnostics only; no sprite approval.
"""
import bpy, hashlib, json
from pathlib import Path

SOURCE=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-integration-v3/full-captain-diagnostic.blend')
OUT=Path('/home/astra/artifacts/captain-body-shader-audition-v1')
if OUT.exists():raise FileExistsError('Preserve prior shader experiments')
OUT.mkdir(parents=True);rows=[];source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
for mode in ['lit_source','paint_unlit','paint_with_ao']:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
    scene.render.resolution_x=384;scene.render.resolution_y=384;scene.render.resolution_percentage=100
    scene.render.threads_mode='FIXED';scene.render.threads=4;scene.cycles.samples=64
    body=next(o for o in scene.objects if o.type=='MESH' and len(o.data.vertices)==61589)
    geometry=[tuple(v.co)for v in body.data.vertices];uv=[tuple(v.uv)for v in body.data.uv_layers.active.data]
    beforeimages=[]
    for material in body.data.materials:
        if not material.use_nodes:continue
        nodes=material.node_tree.nodes;links=material.node_tree.links
        image=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image)
        beforeimages.append(image.image.name)
        if mode=='lit_source':continue
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
        colour=image.outputs['Color']
        if mode=='paint_with_ao':
            ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.14
            ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.65,.65,.65,1);ramp.color_ramp.elements[1].color=(1,1,1,1)
            links.new(ao.outputs['AO'],ramp.inputs['Fac'])
            multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
            links.new(colour,multiply.inputs[1]);links.new(ramp.outputs['Color'],multiply.inputs[2]);colour=multiply.outputs['Color']
        links.new(colour,emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
    for frame in [1,33,99]:
        scene.frame_set(frame);bpy.context.view_layer.update();path=OUT/f'{mode}-frame-{frame:03}.png'
        scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        rows.append({'mode':mode,'source_frame':frame,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resolution':[384,384],'body_texture_images':beforeimages,'camera_matrix':[list(r)for r in scene.camera.matrix_world],'camera_ortho_scale':scene.camera.data.ortho_scale})
    assert geometry==[tuple(v.co)for v in body.data.vertices] and uv==[tuple(v.uv)for v in body.data.uv_layers.active.data]
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha
(OUT/'receipt.json').write_text(json.dumps({'state':'CONTROLLED_STATIC_SHADER_EXPERIMENT_NOT_ANIMATION_APPROVAL','source_scene_sha256':source_sha,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'body_only_material_changes':True,'original_geometry_UV_actions_weights_unchanged':True,'actual_render_resolution':[384,384],'samples':64,'frames':rows,'limits':['Original baseline knee/cuff defects remain','Fixed original camera/worldlights; props retain original lighting in all modes','Paint unlit preserves baked illustration colours but may weaken directional volume','AO uses bounded0.14m local occlusion and65–100percent brightness, not force/foot shadow proof','Only three phases tested; full-view/full-motion validation required before choosing a shader']},indent=2)+'\n')
print(str(OUT))
