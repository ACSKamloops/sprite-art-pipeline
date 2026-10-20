extends SceneTree
## Real renderer isolation, one complete clip/view per bounded editor project.
func _initialize()->void:
 Engine.max_fps=0
 call_deferred("run")
func digest(bytes: PackedByteArray)->String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func run()->void:
 var args=OS.get_cmdline_user_args()
 if args.size()!=3:push_error("Provide source folder, clip/view binding and fresh output folder");quit(2);return
 var source=args[0];var binding=args[1];var output=args[2]
 if DirAccess.dir_exists_absolute(output):push_error("Preserve prior clip projects; output must be fresh");quit(2);return
 var manifest_path=source.path_join("generated/manifest.json")
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
 if not manifest is Dictionary or not manifest.clips.has(binding):push_error("Missing baked binding");quit(2);return
 for name in manifest.source_bindings:
  if FileAccess.get_sha256(source.path_join(name))!=manifest.source_bindings[name]:push_error("Stale baked source: "+name);quit(2);return
 var entry: Dictionary=manifest.clips[binding]
 var base_clip: String=entry.get("base_clip",entry.name)
 var design=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("design.json")))
 var clips=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("clips.json")))
 var viewport=SubViewport.new();viewport.size=Vector2i(192,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
 var rig=load(source.path_join("rig.gd")).new();viewport.add_child(rig);rig.configure(design,clips)
 if entry.has("equipment_selection"):
  if not rig.has_method("set_equipment"):push_error("Variant has no equipment adapter");quit(2);return
  if entry.equipment_selection.is_empty():rig.clear_equipment_selection()
  elif not rig.set_equipment(entry.equipment_selection):push_error("Invalid equipment variant");quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 var records=[];var order: Array=[]
 for frame in entry.frames:
  var phase=float(frame.tick)/entry.duration_ticks if entry.loop else float(frame.tick)/maxi(1,entry.duration_ticks-1)
  rig.visible_layers=[];var pose=rig.pose(base_clip,phase,entry.view)
  await process_frame;await RenderingServer.frame_post_draw
  var full=viewport.get_texture().get_image();full.convert(Image.FORMAT_RGBA8)
  if digest(full.get_data())!=frame.pixel_sha256:push_error("Live clip differs from baked frame "+str(frame.tick));quit(3);return
  if order.is_empty():order=rig.layer_ids.duplicate()
  if order!=rig.layer_ids:push_error("Layer order changed within one view");quit(3);return
  var prefix="%04d"%frame.tick;full.save_png(output.path_join(prefix+"-full.png"))
  var row={"id":prefix,"tick":frame.tick,"duration_ticks":frame.duration_ticks,"full_png":prefix+"-full.png","full_pixel_sha256":frame.pixel_sha256,"pose":pose,"layers":[]}
  for layer in order:
   rig.visible_layers=[layer];rig.pose(base_clip,phase,entry.view)
   await process_frame;await RenderingServer.frame_post_draw
   var image=viewport.get_texture().get_image();image.convert(Image.FORMAT_RGBA8)
   var png=prefix+"-"+layer+".png";image.save_png(output.path_join(png))
   row.layers.append({"id":layer,"png":png,"pixel_sha256":digest(image.get_data())})
  records.append(row)
 var header={"name":entry.name,"base_clip":base_clip,"equipment_selection":entry.get("equipment_selection",""),"view":entry.view,"duration_ticks":entry.duration_ticks,"loop":entry.loop,"events":entry.events}
 # Bind the original manifest bytes and exact sampler header. Do not round-trip
 # its thousands of floating pose fields through Godot's JSON decimal parser.
 var report={"schema":"editable-full-clip-isolation/v2","binding":binding,"clip":header,"layer_order":order,"fps":manifest.fps,"source_bindings":manifest.source_bindings,"bake_manifest_sha256":FileAccess.get_sha256(manifest_path),"tester_sha256":FileAccess.get_sha256(get_script().resource_path),"poses":records,"scope":"All ticks of one clip/view, actual named draw layers; hidden areas are rig-owned contours, not inferred image cutouts."}
 FileAccess.open(output.path_join("isolation.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  ",true,true))
 print("EDITABLE_CLIP_ISOLATED ",binding," frames=",records.size()," layers=",order.size());quit(0)
