import bpy,json,sys
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;c=s.camera
r={'camera':c.name,'location':list(c.location),'rotation_mode':c.rotation_mode,'rotation_euler':list(c.rotation_euler),'rotation_quaternion':list(c.rotation_quaternion),'scale':list(c.scale),'matrix_world':[list(v) for v in c.matrix_world],'ortho':c.data.ortho_scale,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'lights':[o.name for o in s.objects if o.type=='LIGHT'],'armatures':[{'name':o.name,'bones':[b.name for b in o.pose.bones if any(x in b.name.lower() for x in ['foot','shin','thigh','knee'])]} for o in s.objects if o.type=='ARMATURE']}
p.write_text(json.dumps(r,indent=2));print(json.dumps(r))
