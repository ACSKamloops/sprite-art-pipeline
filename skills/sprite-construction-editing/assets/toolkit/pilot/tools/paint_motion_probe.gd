extends SceneTree
func _initialize()->void:Engine.max_fps=0;call_deferred("run")
func digest(bytes: PackedByteArray)->String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func run()->void:
 var args=OS.get_cmdline_user_args()
 if args.size()<2:push_error("Provide source folder and fresh output folder");quit(2);return
 var source=args[0];var output=args[1];var samples=int(args[2])if args.size()>2 else 8
 if DirAccess.dir_exists_absolute(output):push_error("Output must be fresh");quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 var design=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("design.json")));var clean=design.duplicate(true);clean.erase("paint_layers")
 var clips=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("clips.json")))
 var selected=Array(args[3].split(","))if args.size()>3 else clips.clips.keys()
 var viewport=SubViewport.new();viewport.size=Vector2i(192,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
 var baseline=load(source.path_join("rig.gd")).new();var painted=load(source.path_join("rig.gd")).new();viewport.add_child(baseline);viewport.add_child(painted)
 baseline.configure(clean,clips);painted.configure(design,clips)
 var rows=[];var total=0;var failures=[]
 for view in ["right","left","front","back"]:
  for clip in selected:
   for tick in range(samples):
    var phase=float(tick)/samples if clips.clips[clip].loop else float(tick)/maxi(samples-1,1)
    baseline.visible_layers=[];painted.visible_layers=[];baseline.pose(clip,phase,view);var meta=painted.pose(clip,phase,view)
    baseline.visible=true;painted.visible=false
    await process_frame;await RenderingServer.frame_post_draw
    var a=viewport.get_texture().get_image();a.convert(Image.FORMAT_RGBA8)
    baseline.visible=false;painted.visible=true
    await process_frame;await RenderingServer.frame_post_draw
    var b=viewport.get_texture().get_image();b.convert(Image.FORMAT_RGBA8)
    var prefix="%s-%s-%03d"%[clip,view,tick];a.save_png(output.path_join(prefix+"-before.png"));b.save_png(output.path_join(prefix+"-after.png"))
    baseline.visible_layers=["torso"];painted.visible_layers=["torso"];baseline.pose(clip,phase,view);painted.pose(clip,phase,view)
    baseline.visible=true;painted.visible=false
    await process_frame;await RenderingServer.frame_post_draw
    var ia=viewport.get_texture().get_image();ia.convert(Image.FORMAT_RGBA8)
    baseline.visible=false;painted.visible=true
    await process_frame;await RenderingServer.frame_post_draw
    var ib=viewport.get_texture().get_image();ib.convert(Image.FORMAT_RGBA8)
    ia.save_png(output.path_join(prefix+"-surface-before.png"));ib.save_png(output.path_join(prefix+"-surface-after.png"))
    var full_changes=[];var surface_changes=[];var alpha_changed=0;var outside=0
    for y in range(192):
     for x in range(192):
      var full=a.get_pixel(x,y)!=b.get_pixel(x,y);var surface=ia.get_pixel(x,y)!=ib.get_pixel(x,y)
      if full:full_changes.append([x,y])
      if surface:surface_changes.append([x,y])
      if full and not surface:outside+=1
      if a.get_pixel(x,y).a!=b.get_pixel(x,y).a or ia.get_pixel(x,y).a!=ib.get_pixel(x,y).a:alpha_changed+=1
    total+=full_changes.size()
    if outside or alpha_changed:failures.append(prefix)
    rows.append({"clip":clip,"view":view,"phase":phase,"prefix":prefix,"before_sha256":digest(a.get_data()),"after_sha256":digest(b.get_data()),"visible_changed_coordinates":full_changes,"surface_changed_coordinates":surface_changes,"outside_surface_changes":outside,"alpha_changes":alpha_changed,"surface_frame":meta.surface_frames.torso,"pose":meta})
 var bindings={}
 for name in ["rig.gd","rig_side.gd","design.json","clips.json"]:bindings[name]=FileAccess.get_sha256(source.path_join(name))
 var report={"schema":"source-paint-motion-proof/v1","passed":total>0 and failures.is_empty(),"source_bindings":bindings,"tester_sha256":FileAccess.get_sha256(get_script().resource_path),"renderer":RenderingServer.get_video_adapter_name(),"samples":rows,"total_visible_changes":total,"failures":failures,"scope":"Actual GPU before/after reusable local torso painting; all view/phase sample masks, foreground occlusion and unchanged alpha. UV placement analysis separate; not art approval."}
 FileAccess.open(output.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("PAINT_MOTION_PROOF ",rows.size()," samples visible_changes=",total," passed=",report.passed);quit(0 if report.passed else 2)
