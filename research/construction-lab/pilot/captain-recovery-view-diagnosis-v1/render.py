import bpy,sys,json,math,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;c=s.camera
baseline={'location':c.location.copy(),'rotation_euler':c.rotation_euler.copy(),'rotation_quaternion':c.rotation_quaternion.copy(),'rotation_axis_angle':list(c.rotation_axis_angle),'rotation_mode':c.rotation_mode,'scale':c.scale.copy()};r=math.hypot(c.location.x,c.location.y);yaw=math.atan2(c.location.x,-c.location.y)
s.render.threads_mode='FIXED';s.render.threads=6;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';records=[];arm=bpy.data.objects['Captain_BODY_mocap_prototype'];traj=[]
for f in [83,93,103,113,121]:
 s.frame_set(f);bpy.context.view_layer.update();traj.append({'source_frame':f,'cel':(f-1)//2,'bones':{n:{'head_world':list(arm.matrix_world@arm.pose.bones[n].head),'tail_world':list(arm.matrix_world@arm.pose.bones[n].tail)} for n in ['rfoot','rshin','rthigh','lfoot','lshin','lthigh']}})
for angle in [math.degrees(yaw),35.,45.]:
 name='baseline' if angle<30 else f'yaw{int(angle)}'
 # Baseline is restored using exact saved components, never a decomposed matrix.
 c.rotation_mode=baseline['rotation_mode'];c.location=baseline['location'];c.rotation_euler=baseline['rotation_euler'];c.rotation_quaternion=baseline['rotation_quaternion'];c.rotation_axis_angle=baseline['rotation_axis_angle'];c.scale=baseline['scale']
 if name!='baseline':
  theta=math.radians(angle);c.location.x=r*math.sin(theta);c.location.y=-r*math.cos(theta);c.rotation_euler.z=baseline['rotation_euler'].z+theta-yaw
 for size in [256,384]:
  s.render.resolution_x=size;s.render.resolution_y=size;s.render.resolution_percentage=100
  for f in [83,93,103,113,121]:
   s.frame_set(f);bpy.context.view_layer.update();p=out/f'{name}-{size}-cel{(f-1)//2:02}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);records.append({'file':p.name,'source_frame':f,'cel':(f-1)//2,'yaw_deg':angle,'native':size,'camera_location':list(c.location),'camera_euler':list(c.rotation_euler),'camera_scale':list(c.scale),'camera_matrix':[list(row)for row in c.matrix_world],'ortho_scale':c.data.ortho_scale,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'render-receipt.json').write_text(json.dumps({'baseline_components':{k:list(v) if k!='rotation_mode' else v for k,v in baseline.items()},'policy':'Fixed global yaw only; original lighting and ortho3.0, elevation/distance/target retained; original full visible geometry; exact component restore for baseline; no scene save, masks, perposefit or motion edits','renders':records,'bone_trajectory_source_world_m':traj},indent=2)+'\n')
