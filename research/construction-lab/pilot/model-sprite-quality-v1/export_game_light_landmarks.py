"""Source-authoritative evaluated bone positions and actual orthographic projection."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []
OUT=Path(args[0]) if args else ROOT/'candidate-walk-bow160-game-light-v11'
scene=bpy.context.scene;rig=bpy.data.objects['CharacterArmature'];N=scene.render.resolution_x
views={'front':(0,-8,3.15),'right':(-8,0,3.15),'back':(0,8,3.15),'left':(8,0,3.15)}
mapping={'head_base':('Head','head'),'head_tip':('Head','tail'),'pelvis':('Hips','head'),'left_hip':('UpperLeg.L','head'),'right_hip':('UpperLeg.R','head'),'left_knee':('LowerLeg.L','head'),'right_knee':('LowerLeg.R','head'),'left_ankle':('LowerLeg.L','tail'),'right_ankle':('LowerLeg.R','tail'),'left_foot_control':('Foot.L','head'),'right_foot_control':('Foot.R','head'),'left_wrist':('Fist.L','head'),'right_wrist':('Fist.R','head'),'bow_socket':('Weapon.R','head')}
report={'schema':'evaluated-rig-landmark-projection/v1','scene_sha256':hashlib.sha256((OUT/'ranger-walk-render.blend').read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),'source_action':'Walk','fps':scene.render.fps/scene.render.fps_base,'canvas':[N,N],'mapping':mapping,'missing':['No anatomical toe bones exist; no invented toe landmarks. Foot.L/R are exported as controls, not presumed sole-contact points.'],'scope':'Evaluated constraint/deformation bone endpoints transformed through actual armature world matrix and fixed render camera. Projections are source evidence, not stance or raster-contact acceptance.','bone_roles':{b.name:{'deform':b.use_deform,'parent':b.parent.name if b.parent else None}for b in rig.data.bones},'views':{}}
for view,location in views.items():
 scene.camera.location=location;scene.camera.rotation_euler=(Vector((0,0,1.45))-scene.camera.location).to_track_quat('-Z','Y').to_euler();entries=[]
 # Every source video tick, plus endpoint; not just the 12 raster keys.
 for frame in range(31):
  scene.frame_set(frame);bpy.context.view_layer.update();evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());landmarks={}
  for name,(bone,endpoint) in mapping.items():
   world=evaluated.matrix_world@getattr(evaluated.pose.bones[bone],endpoint);v=world_to_camera_view(scene,scene.camera,world);landmarks[name]={'world':list(world),'pixel':[v.x*N,(1-v.y)*N],'camera_depth':v.z}
  root=evaluated.matrix_world@evaluated.pose.bones['Root'].head;v=world_to_camera_view(scene,scene.camera,Vector((0,0,0)));entries.append({'source_frame':frame,'seconds':frame/(scene.render.fps/scene.render.fps_base),'phase':frame/30,'landmarks':landmarks,'root_world':list(root),'bow_origin_world':list(bpy.data.objects['Ranger_Bow'].matrix_world.translation),'projected_world_origin':[v.x*N,(1-v.y)*N]})
 report['views'][view]=entries
(OUT/'landmarks.json').write_text(json.dumps(report,indent=2)+'\n');print('Exported',len(views)*31,'evaluated source samples')
