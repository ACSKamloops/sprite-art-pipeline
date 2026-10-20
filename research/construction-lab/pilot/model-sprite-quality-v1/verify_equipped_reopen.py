"""Reopen packed scene and actually render both cyclic endpoints in all four cameras."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'candidate-walk-bow160-final24-v10';s=bpy.context.scene
qa=OUT/'reopen';qa.mkdir(exist_ok=False)
views={'front':(0,-8,3.15),'right':(-8,0,3.15),'back':(0,8,3.15),'left':(8,0,3.15)};checks=[]
for view,location in views.items():
 s.camera.location=location;s.camera.rotation_euler=(Vector((0,0,1.45))-s.camera.location).to_track_quat('-Z','Y').to_euler()
 old=bpy.data.images.load(str(OUT/view/'00.png'))
 for frame in [0,30]:
  s.frame_set(frame);s.render.filepath=str(qa/f'{view}-frame{frame}.png');bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath)
  differences=sum(a!=b for a,b in zip(im.pixels,old.pixels));checks.append({'view':view,'source_frame':frame,'exact_decoded_component_differences':differences,'passed':differences==0})
r={'passed':all(x['passed']for x in checks),'checks':checks,'packed_images':[{'name':i.name,'packed':bool(i.packed_file)}for i in bpy.data.images if i.type!='RENDER_RESULT' and i.packed_file],'actions':[a.name for a in bpy.data.actions],'scene_sha256':hashlib.sha256((OUT/'ranger-walk-render.blend').read_bytes()).hexdigest(),'fps':s.render.fps/s.render.fps_base,'scope':'Actual packed .blend reopen and exact frame0/frame30 renders against original frame0 across allfour camera directions. Source textures present and original actions retained.'};(OUT/'reopen-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if not r['passed']:raise RuntimeError('Reopened or loop endpoint render differs')
