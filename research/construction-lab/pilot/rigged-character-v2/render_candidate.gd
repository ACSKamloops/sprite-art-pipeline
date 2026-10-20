extends SceneTree
func _initialize():call_deferred("run")
func run():
 var b=get_script().resource_path.get_base_dir()+"/"
 var args=OS.get_cmdline_user_args()
 var folder=args[0] if args.size()==1 else "candidate-five"
 var valid=RegEx.new();valid.compile("^[A-Za-z0-9_-]+$")
 if args.size()>1 or valid.search(folder)==null:
  push_error("Use one relative output directory name");quit(2);return
 var output=b+folder+"/"
 if FileAccess.file_exists(output+"samples.json"):
  push_error("Refuse overwrite existing review evidence");quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 var viewport=SubViewport.new();viewport.size=Vector2i(192,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
 root.add_child(viewport)
 var rig=load(b+"rig.gd").new();viewport.add_child(rig)
 rig.configure(JSON.parse_string(FileAccess.get_file_as_string(b+"design.json")),JSON.parse_string(FileAccess.get_file_as_string(b+"clips.json")))
 var samples=[]
 for view in ["right","left","front","back"]:
  for clip in rig.master_clips.clips:
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
