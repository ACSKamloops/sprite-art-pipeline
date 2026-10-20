import bpy,json
from pathlib import Path
s=bpy.context.scene;r=bpy.data.objects['CharacterArmature'];bow=bpy.data.objects['Ranger_Bow'];r.animation_data.action=bpy.data.actions['Walk']
for t in r.animation_data.nla_tracks:t.mute=True
out={'source_fps':s.render.fps/s.render.fps_base,'bow':{'hidden_render':bow.hide_render,'hidden_viewport':bow.hide_viewport,'parent':bow.parent.name if bow.parent else None,'parent_type':bow.parent_type,'parent_bone':bow.parent_bone,'own_animation':bow.animation_data is not None},'actions':[a.name for a in bpy.data.actions],'walk_channel_paths':sorted(set(f.data_path for f in bpy.data.actions['Walk'].fcurves)),'samples':[],'interpretation_bound':'Defaultvisible bone-attachedbow proves equipment exists throughoutsource Walk; actionname alone does not prove artist intended exclusively carrying. No unarmedWalk separatelynamed; Run andRun_Holding are separate.'}
for frame in [0,5,10,15,20,25,30]:
 s.frame_set(frame);bpy.context.view_layer.update();ev=r.evaluated_get(bpy.context.evaluated_depsgraph_get());out['samples'].append({'frame':frame,'bow_world_position':list(bow.matrix_world.translation),'left_wrist_world':list(ev.matrix_world@ev.pose.bones['Fist.L'].head),'right_wrist_world':list(ev.matrix_world@ev.pose.bones['Fist.R'].head)})
(Path(__file__).resolve().parent/'equipment-intent-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['bow']));print(out['actions'])
