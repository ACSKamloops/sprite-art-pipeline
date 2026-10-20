extends SceneTree
func _initialize():call_deferred("run")
func run():
 var b=get_script().resource_path.get_base_dir()+"/"
 var output=b+"candidate-first/"
 if FileAccess.file_exists(output+"samples.json"):
  push_error("Refuse overwrite historical first review; use render_candidate.gd with a new output name");quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 var viewport=SubViewport.new();viewport.size=Vector2i(192,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
 root.add_child(viewport)
 var rig=load(b+"rig.gd").new();viewport.add_child(rig)
 rig.configure(JSON.parse_string(FileAccess.get_file_as_string(b+"design.json")),JSON.parse_string(FileAccess.get_file_as_string(b+"clips.json")))
 var samples=[]
 for view in ["right","left","front","back"]:
  for clip in ["idle","walk","slash","cast"]:
   for i in range(8):
    var phase=float(i)/8 if rig.master_clips.clips[clip].loop else float(i)/7
    var m=rig.pose(clip,phase,view)
    await process_frame
    await RenderingServer.frame_post_draw
    var file=clip+"-"+view+"-"+str(i)+".png"
    viewport.get_texture().get_image().save_png(output+file)
    samples.append({"file":file,"pose":m})
 var f=FileAccess.open(output+"samples.json",FileAccess.WRITE);f.store_string(JSON.stringify(samples,"  "))
 print("Rendered ",samples.size()," actual GPU samples")
 quit()
