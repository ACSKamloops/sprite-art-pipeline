"""Render the creator's actual rig/UV texture/walk action, no generated geometry."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source/original'
args=sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []
OUT=ROOT/(args[0] if args else 'candidate-baseline160-v8')
if OUT.exists():raise RuntimeError('Refuse overwrite prior render candidate')
OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'Blends/Ranger.blend'))
scene=bpy.context.scene
rig=bpy.data.objects['CharacterArmature'];rig.animation_data.action=bpy.data.actions['Walk']
for track in rig.animation_data.nla_tracks:track.mute=True
bpy.data.objects['Ranger_Bow'].hide_render=True
# Reconnect the original supplied texture; retain every original UV, vertex and rig weight.
for m in bpy.data.materials:
 texture='Ranger_Bow_Texture.png' if 'Bow'in m.name else 'Ranger_Texture.png'
 im=bpy.data.images.load(str(SOURCE/'Textures'/texture),check_existing=True)
 m.use_nodes=True;m.node_tree.nodes.clear();n=m.node_tree.nodes
 output=n.new('ShaderNodeOutputMaterial');bsdf=n.new('ShaderNodeBsdfPrincipled');tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear'
 bsdf.inputs['Roughness'].default_value=.78
 m.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);m.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])
# Remove orphan legacy images with stale source paths; keep actual shader textures.
used_images={n.image for m in bpy.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
for image in list(bpy.data.images):
 if image not in used_images and image.type!='RENDER_RESULT':bpy.data.images.remove(image)
# Orthographic camera and lighting are fixed for all animation samples; views are actual quarter turns.
for o in list(bpy.data.objects):
 if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='SpriteCamera';cam.data.type='ORTHO';cam.data.ortho_scale=3.6;scene.camera=cam
world=bpy.data.worlds.new('NeutralStudio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.64,.75,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('Key',(-4,-6,8),650,5),('Fill',(5,-3,4),350,4),('Rim',(1,5,6),600,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=160;scene.render.resolution_y=160;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.fps=30
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.25
scene.render.threads_mode='FIXED';scene.render.threads=8
views={'front':(0,-8,3.15),'right':(-8,0,3.15),'back':(0,8,3.15),'left':(8,0,3.15)}
manifest={'schema':'licensed-rig-walk-sprite-pilot/v1','model':'Quaternius RPG Ranger','action':'Walk','source_action_frames':[0,30],'source_fps':30,'canvas':[160,160],'samples_per_view':12,'cycle_seconds':1,'sampling':'frame=i*30/12, exclude duplicate endpoint','views':{},'renderer':bpy.app.version_string,'render_engine':'Cycles CPU32samples/denoise','camera':'Orthographic scale3.6,targetZ1.45,elevation12degrees,quarter-turn cameras; no frame recentering','asset_modifications':['Original bow hidden for unequipped Walk. Original texture paths reconnected. Principled diffuse material rebuilt with supplied original UV texture. No geometry, weights, poses or texture pixels edited.'],'render_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [SOURCE/'Blends/Ranger.blend',SOURCE/'Textures/Ranger_Texture.png',SOURCE/'License.txt']}}
for view,loc in views.items():
 cam.location=loc;cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler();folder=OUT/view;folder.mkdir();entries=[]
 for i in range(12):
  frame=i*30/12;scene.frame_set(int(frame),subframe=frame-int(frame));scene.render.filepath=str(folder/f'{i:02d}.png');bpy.ops.render.render(write_still=True)
  entries.append({'sample':i,'source_frame':frame,'seconds':i/12,'png':f'{view}/{i:02d}.png','sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
 manifest['views'][view]=entries
# Standalone packed editable scene with actual rig, all actions, original UV textures and render setup.
scene.frame_set(0);cam.location=views['front'];cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ranger-walk-render.blend'))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
