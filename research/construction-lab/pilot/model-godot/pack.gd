extends RefCounted
# Only the corrected licensed-source clock is accepted; v7's 30fps/1s metadata rejects.
static func read_pack(path:String)->Dictionary:
 var value=JSON.parse_string(FileAccess.get_file_as_string(path))
 if not value is Dictionary:return {"error":"Invalid manifest"}
 var d:Dictionary=value
 if not d.get("canvas")is Array or d.canvas.size()!=2 or d.canvas[0]!=160 or d.canvas[1]!=160 or d.get("samples_per_view")!=12:return {"error":"Expected160x160,12samples"}
 if d.get("source_fps")!=24 or not d.get("source_action_frames")is Array or d.source_action_frames.size()!=2 or d.source_action_frames[0]!=0 or d.source_action_frames[1]!=30 or absf(float(d.get("cycle_seconds",0))-1.25)>1e-12:return {"error":"Expected corrected24fps,30sourceframes,1.25second cycle"}
 if not d.get("views")is Dictionary or d.views.size()!=4:return {"error":"Four views required"}
 var landmark_path=path.get_base_dir().path_join("landmarks.json")
 var landmarks=JSON.parse_string(FileAccess.get_file_as_string(landmark_path))
 if not landmarks is Dictionary or landmarks.get("manifest_sha256")!=FileAccess.get_sha256(path):return {"error":"Landmark source binding mismatch"}
 var origins={}
 for v in ["front","right","back","left"]:
  origins[v]=landmarks.views[v][0].projected_world_origin
 var frames=SpriteFrames.new();frames.remove_animation("default");var raw={}
 for view in ["front","right","back","left"]:
  if not d.views.has(view)or d.views[view].size()!=12:return {"error":"Missing12poses: "+view}
  frames.add_animation(view);frames.set_animation_speed(view,9.6);frames.set_animation_loop(view,true);raw[view]=[]
  for i in range(12):
   var row=d.views[view][i]
   if row.sample!=i or absf(float(row.source_frame)-i*2.5)>1e-12 or absf(float(row.seconds)-i*2.5/24.0)>1e-12:return {"error":"Sample/order/source time mismatch"}
   var filename=path.get_base_dir().path_join(row.png)
   if filename.simplify_path()!=filename or not filename.begins_with(path.get_base_dir()+"/"):return {"error":"Unsafe PNG path"}
   if FileAccess.get_sha256(filename)!=row.sha256:return {"error":"Stale PNG: "+filename}
   var im=Image.new()
   if im.load(filename)!=OK or im.get_size()!=Vector2i(160,160):return {"error":"Invalid160RGBA image"}
   im.convert(Image.FORMAT_RGBA8);raw[view].append(im);frames.add_frame(view,ImageTexture.create_from_image(im),1.0)
 return {"manifest":d,"manifest_sha256":FileAccess.get_sha256(path),"frames":frames,"images":raw,"interval_seconds":2.5/24.0,"cycle_seconds":1.25,"origins":origins,"landmarks_sha256":FileAccess.get_sha256(landmark_path)}

static func resource_contract(frames:SpriteFrames)->String:
 for view in ["front","right","back","left"]:
  if not frames.has_animation(view)or frames.get_frame_count(view)!=12 or frames.get_animation_speed(view)!=9.6 or not frames.get_animation_loop(view):return "Resource timeline mismatch"
  for i in range(12):
   if frames.get_frame_duration(view,i)!=1.0:return "Resource pose hold mismatch"
 return ""
