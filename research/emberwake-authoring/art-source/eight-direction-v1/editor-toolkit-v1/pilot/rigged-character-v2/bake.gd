extends SceneTree
const SIZE=192
func _initialize() -> void:
 Engine.max_fps=0
 call_deferred("run")
func hash_bytes(data: PackedByteArray) -> String:
 var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(data);return hash.finish().hex_encode()
func source_bindings() -> Dictionary:
 var result={}
 for name in ["rig.gd","rig_side.gd","design.json","clips.json","bake.gd"]:result[name]=FileAccess.get_sha256("res://"+name)
 return result
func run() -> void:
 var args=OS.get_cmdline_user_args();var output="";var selected: Array=[];var isolate=false;var views: Array=["right","left","front","back"]
 for i in range(args.size()):
  if args[i]=="--output" and i+1<args.size():output=args[i+1]
  if args[i]=="--select" and i+1<args.size():selected=args[i+1].split(",")
  if args[i]=="--isolate":isolate=true
  if args[i]=="--views" and i+1<args.size():views=Array(args[i+1].split(","))
 if output.is_empty():push_error("bake.gd requires --output fresh-directory");quit(2);return
 if DirAccess.dir_exists_absolute(output):push_error("Output directory already exists");quit(2);return
 var design: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://design.json"));var clips: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://clips.json"))
 var viewport=SubViewport.new();viewport.size=Vector2i(SIZE,SIZE);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;viewport.canvas_item_default_texture_filter=Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST;root.add_child(viewport)
 var rig=load("res://rig.gd").new();viewport.add_child(rig);rig.configure(design,clips)
 if clips.get("fps")!=60 or views.is_empty():push_error("Invalid FPS or empty views");quit(2);return
 var unique_views={}
 for view in views:
  if view not in ["right","left","front","back"] or unique_views.has(view):push_error("Invalid or duplicate view");quit(2);return
  unique_views[view]=true
 DirAccess.make_dir_recursive_absolute(output)
 var result={"schema":"copper-scout-bake/v2","fps":clips.fps,"canvas":[SIZE,SIZE],"origin_policy":"Fixed authored192canvas; no per-pose recentering","source_bindings":source_bindings(),"godot_version":Engine.get_version_info(),"rendering_driver":RenderingServer.get_video_adapter_name(),"views":views,"clips":{},"limits":["Original authored pilot; semantic events are authored, not discovered gameplay hit windows.","PNG file bytes are not claimed deterministic across renderers; RGBA pixels are tested within this renderer.","Front/back authored orthographic planar views; left mirrors right. Art and raster contacts require separate review.","Base48 are clip-declared inspection bindings; equipped48 retain selected gear through locomotion and injury states."]}
 var names=clips.clips.keys()
 for base in ["idle","walk","run","hurt","knockdown","recover"]:
  for gear in ["sword","blaster"]:names.append(base+"_"+gear)
 names.sort()
 for wanted in selected:
  if wanted not in names:push_error("Unknown selected binding "+str(wanted));quit(2);return
 for name in names:
  if not selected.is_empty() and not name in selected:continue
  var base_clip: String=name
  var selection=""
  if name.ends_with("_sword") or name.ends_with("_blaster"):
   selection=name.get_slice("_",1);base_clip=name.get_slice("_",0)
  var c: Dictionary=clips.clips[base_clip];var count=int(c.duration_ticks)
  if count<=0 or count>441:push_error("Clip ticks outside1..441 atlas budget "+name);quit(2);return
  for view in views:
   if not view in ["right","left","front","back"]:push_error("Unsupported view");quit(2);return
   rig.clear_equipment_selection()
   if not selection.is_empty() and not rig.set_equipment(selection):push_error("Equipment selection rejected");quit(2);return
   var columns=mini(21,int(ceil(sqrt(float(count)))));var rows=int(ceil(float(count)/columns));var atlas=Image.create(columns*SIZE,rows*SIZE,false,Image.FORMAT_RGBA8);atlas.fill(Color.TRANSPARENT)
   var folder=output+"/frames/"+name+"/"+view;DirAccess.make_dir_recursive_absolute(folder)
   var frames: Array=[]
   for tick in range(count):
    var phase=float(tick)/count if c.loop else float(tick)/maxi(1,count-1)
    var pose: Dictionary=rig.pose(base_clip,phase,view)
    if pose.has("error"):push_error(str(pose));quit(3);return
    await process_frame;await RenderingServer.frame_post_draw
    var image=viewport.get_texture().get_image();image.convert(Image.FORMAT_RGBA8)
    if image.get_size()!=Vector2i(SIZE,SIZE):push_error("Missing real rendered viewport");quit(3);return
    var png="frames/%s/%s/%04d.png" % [name,view,tick]
    if image.save_png(output+"/"+png)!=OK:push_error("Cannot save frame");quit(3);return
    var region=Rect2i((tick%columns)*SIZE,(tick/columns)*SIZE,SIZE,SIZE);atlas.blit_rect(image,Rect2i(0,0,SIZE,SIZE),region.position)
    frames.append({"tick":tick,"duration_ticks":1,"png":png,"pixel_sha256":hash_bytes(image.get_data()),"region":[region.position.x,region.position.y,SIZE,SIZE],"pose":pose})
   var atlas_path="atlases/"+name+"-"+view+".png";DirAccess.make_dir_recursive_absolute(output+"/atlases");atlas.save_png(output+"/"+atlas_path)
   result.clips[name+"/"+view]={"name":name,"base_clip":base_clip,"equipment_selection":selection,"equipment_mode":"persistent" if not selection.is_empty() else "declared_clip_inspection_only","view":view,"duration_ticks":count,"loop":c.loop,"events":c.events,"atlas":atlas_path,"atlas_pixel_sha256":hash_bytes(atlas.get_data()),"frames":frames,"completion_policy":"hold_final_until_replay_or_clip_change"}
   print("BAKED ",name,"/",view," ",count," ticks")
 if isolate:
  DirAccess.make_dir_recursive_absolute(output+"/isolated")
  rig.clear_equipment_selection()
  var isolated={"schema":"copper-scout-layer-isolation/v2","source_bindings":source_bindings(),"canvas":[192,192],"layer_order":["rear_leg","rear_boot","rear_arm","front_leg","front_boot","torso","scarf","head","front_arm","shoulder_armor","hands","equipment"],"poses":[],"scope":"Actual separately rendered named rig draw layers; no inferred hidden cutout geometry."}
  for sample in [["idle",0],["walk",15],["slash",21],["cast",29],["hurt",0]]:
   var name: String=sample[0]
   if not result.clips.has(name+"/right"):continue
   var count=int(clips.clips[name].duration_ticks);var phase=float(sample[1])/count if clips.clips[name].loop else float(sample[1])/maxi(1,count-1)
   var folder="isolated/"+name+"-"+str(sample[1]);DirAccess.make_dir_recursive_absolute(output+"/"+folder)
   rig.visible_layers=[];var meta: Dictionary=rig.pose(name,phase,"right");await process_frame;await RenderingServer.frame_post_draw
   var full=viewport.get_texture().get_image();full.convert(Image.FORMAT_RGBA8);full.save_png(output+"/"+folder+"/full.png")
   var record={"id":name+"-"+str(sample[1]),"clip":name,"tick":sample[1],"phase":phase,"view":"right","full_png":folder+"/full.png","full_pixel_sha256":hash_bytes(full.get_data()),"pose":meta,"layers":[]}
   for layer in rig.layer_ids:
    rig.visible_layers=[layer];rig.pose(name,phase,"right");await process_frame;await RenderingServer.frame_post_draw
    var image=viewport.get_texture().get_image();image.convert(Image.FORMAT_RGBA8);var png=folder+"/"+layer+".png";image.save_png(output+"/"+png)
    record.layers.append({"id":layer,"png":png,"pixel_sha256":hash_bytes(image.get_data())})
   isolated.poses.append(record)
  rig.visible_layers=[]
  FileAccess.open(output+"/isolated/manifest.json",FileAccess.WRITE).store_string(JSON.stringify(isolated,"  "))
 FileAccess.open(output+"/manifest.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 if result.clips.is_empty():push_error("No binding rendered");quit(2);return
 viewport.queue_free();print("BAKE_COMPLETE ",result.clips.size()," clip-view bindings");quit(0)
