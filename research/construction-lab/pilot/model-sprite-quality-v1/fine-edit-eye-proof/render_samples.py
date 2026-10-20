"""Render the creator's actual rig/UV texture/walk action, no generated geometry."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source/original'
args=sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []
OUT=ROOT/(args[0] if args else 'baseline')
if OUT.exists():raise RuntimeError('Refuse overwrite prior render candidate')
OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'Blends/Ranger.blend'))
scene=bpy.context.scene
source_fps=scene.render.fps/scene.render.fps_base
rig=bpy.data.objects['CharacterArmature'];rig.animation_data.action=bpy.data.actions['Walk']
for track in rig.animation_data.nla_tracks:track.mute=True
bpy.data.objects['Ranger_Bow'].hide_render=False
# Reconnect the original supplied texture; retain every original UV, vertex and rig weight.
for m in bpy.data.materials:
 texture='Ranger_Bow_Texture.png' if 'Bow'in m.name else 'Ranger_Texture.png'
 im=bpy.data.images.load(str(SOURCE/'Textures'/texture),check_existing=True)
 m.use_nodes=True;m.node_tree.nodes.clear();n=m.node_tree.nodes
 output=n.new('ShaderNodeOutputMaterial');bsdf=n.new('ShaderNodeBsdfPrincipled');tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear'
 bsdf.inputs['Roughness'].default_value=.78
 detail=json.loads((ROOT/'face_detail.json').read_text())
 gamma=n.new('ShaderNodeGamma');gamma.inputs['Gamma'].default_value=detail['texture_gamma'];m.node_tree.links.new(tex.outputs['Color'],gamma.inputs['Color']);color=gamma.outputs['Color']
 if 'Bow' not in m.name:
  uv=n.new('ShaderNodeTexCoord')
  for mark in detail['marks']:
   subtract=n.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT';subtract.inputs[1].default_value=(*mark['center'],0);m.node_tree.links.new(uv.outputs['UV'],subtract.inputs[0])
   scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/mark['radius'][0],1/mark['radius'][1],0);m.node_tree.links.new(subtract.outputs[0],scale.inputs[0])
   length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';m.node_tree.links.new(scale.outputs[0],length.inputs[0])
   mask=n.new('ShaderNodeMath');mask.operation='LESS_THAN';mask.inputs[1].default_value=1;m.node_tree.links.new(length.outputs['Value'],mask.inputs[0])
   mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=mark['color'];m.node_tree.links.new(mask.outputs[0],mix.inputs[0]);m.node_tree.links.new(color,mix.inputs[1]);color=mix.outputs[0]
 m.node_tree.links.new(color,bsdf.inputs['Base Color']);m.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])
# Remove orphan legacy images with stale source paths; keep actual shader textures.
used_images={n.image for m in bpy.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
for image in list(bpy.data.images):
 if image not in used_images and image.type!='RENDER_RESULT':bpy.data.images.remove(image)
# Orthographic camera and lighting are fixed for all animation samples; views are actual quarter turns.
for o in list(bpy.data.objects):
 if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='SpriteCamera';cam.data.type='ORTHO';cam.data.ortho_scale=3.6;scene.camera=cam
world=bpy.data.worlds.new('NeutralStudio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.64,.75,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
for name,loc,power,size in [('Key',(-4,-6,8),800,5),('Fill',(5,-3,4),600,4),('Rim',(1,5,6),600,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
base_light_matrices={name:bpy.data.objects[name].matrix_world.copy() for name in ['Key','Fill','Rim']}
view_angles={'front':0,'right':-math.pi/2,'back':math.pi,'left':math.pi/2}
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False
scene.render.resolution_x=160;scene.render.resolution_y=160;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.fps=24
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.25
scene.render.threads_mode='FIXED';scene.render.threads=8
views={'front':(0,-8,3.15),'right':(-8,0,3.15),'back':(0,8,3.15),'left':(8,0,3.15)}
manifest={'schema':'licensed-rig-walk-sprite-pilot/v1','model':'Quaternius RPG Ranger','action':'Walk','source_action_frames':[0,30],'source_fps':source_fps,'canvas':[160,160],'samples_per_view':3,'cycle_seconds':30/source_fps,'sampling':'Bounded sourceframes0/10/20; editcomparison, not fullcycle','views':{},'renderer':bpy.app.version_string,'render_engine':'Cycles CPU128samples/no denoise','camera':'Orthographic scale3.6,targetZ1.45,elevation12degrees,quarter-turn cameras; no frame recentering','asset_modifications':['Original bone-parented bow restored for source Walk carry. Original texture paths reconnected. Principled diffuse material rebuilt with supplied original UV texture. No geometry, weights, poses or texture pixels edited. Global material gamma0.8 and lighting fill adjusted. Authored sparse eye/brow UV shader marks added from face_detail.json.'],'render_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [SOURCE/'Blends/Ranger.blend',SOURCE/'Textures/Ranger_Texture.png',SOURCE/'Textures/Ranger_Bow_Texture.png',SOURCE/'License.txt',ROOT/'face_detail.json']}}
manifest['lighting_contract']='FullKey/Fill/Rim rig rotates withcamera by sameZangle; isotropicworld. Screen-space studio lighting fixed, equivalent fixedcamera/rotatingactor. No perframe lightchanges.'
manifest['view_transforms']={}
for view,loc in views.items():
 rotation=Matrix.Rotation(view_angles[view],4,'Z')
 for name,base in base_light_matrices.items():bpy.data.objects[name].matrix_world=rotation@base
 cam.location=loc;cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();folder=OUT/view;folder.mkdir();entries=[]
 manifest['view_transforms'][view]={'angle_radians':view_angles[view],'light_properties':{name:{'location':list(bpy.data.objects[name].location),'rotation_euler':list(bpy.data.objects[name].rotation_euler),'scale':list(bpy.data.objects[name].scale)}for name in base_light_matrices},'camera_world_matrix':[list(row)for row in cam.matrix_world],'lights_world_matrices':{name:[list(row)for row in bpy.data.objects[name].matrix_world]for name in base_light_matrices},'lights_camera_space_matrices':{name:[list(row)for row in cam.matrix_world.inverted()@bpy.data.objects[name].matrix_world]for name in base_light_matrices}}
 for i,frame in enumerate([0,10,20]):
  scene.frame_set(int(frame),subframe=frame-int(frame));scene.render.filepath=str(folder/f'{i:02d}.png');bpy.ops.render.render(write_still=True)
  entries.append({'sample':i,'source_frame':frame,'seconds':frame/source_fps,'png':f'{view}/{i:02d}.png','sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
 manifest['views'][view]=entries
# Standalone packed editable scene with actual rig, all actions, original UV textures and render setup.
scene.frame_set(0)
for name,base in base_light_matrices.items():bpy.data.objects[name].matrix_world=base
cam.location=views['front'];cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ranger-walk-render.blend'))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
