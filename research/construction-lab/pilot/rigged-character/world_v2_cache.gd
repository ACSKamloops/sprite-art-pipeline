extends SceneTree
var out=""
var source="res://"
var views=["right","left"]
var selected=[]
var variants=false
func hash_bytes(bytes: PackedByteArray) -> String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func _initialize() -> void:
 Engine.max_fps=0;call_deferred("run")
func presented(vp: SubViewport) -> Image:
 await process_frame;await RenderingServer.frame_post_draw
 var image=vp.get_texture().get_image();image.convert(Image.FORMAT_RGBA8);return image
func run() -> void:
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--output":out=args[i+1]
  if args[i]=="--source":source=args[i+1]
  if args[i]=="--views":views=Array(args[i+1].split(","))
  if args[i]=="--select":selected=Array(args[i+1].split(","))
  if args[i]=="--equipment-variants":variants=true
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh --output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var design=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("design.json")));var clips=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("clips.json")))
 var vp=SubViewport.new();vp.size=Vector2i(192,192);vp.transparent_bg=true;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(vp)
 var rig=load(source.path_join("rig.gd")).new();vp.add_child(rig);rig.configure(design,clips)
 var bindings={}
 for name in ["rig.gd","design.json","clips.json"]+(["rig_side.gd"]if FileAccess.file_exists(source.path_join("rig_side.gd"))else[]):bindings[name]=FileAccess.get_sha256(source.path_join(name))
 var report={"schema":"copper-scout-world-v2-cache/v2","source":source,"source_bindings":bindings,"generator_sha256":FileAccess.get_sha256(get_script().resource_path),"fps":clips.fps,"canvas":[192,192],"renderer":RenderingServer.get_video_adapter_name(),"godot":Engine.get_version_info(),"views":[],"clips":{},"sole_row":169,"camera_policy":"Continuous physical camera; rounded native-pixel visual camera before integer scaling","offset_derivation":{},"limits":["Measured own boot-only raster per view; no inferred mirrored sole offset.","Cache and runtime pixels remain renderer/source bound; no cross-renderer determinism claim."]}
 var names=clips.clips.keys();names.sort()
 var routes=[]
 for name in names:routes.append({"name":name,"id":name,"equipment":"inspection"})
 if variants:
  for name in ["idle","walk","run","hurt","knockdown","recover"]:
   for equipment in ["sword","blaster"]:routes.append({"name":name,"id":name+"_"+equipment,"equipment":equipment})
 for view in views:
  for route in routes:
   var name=route.name;var id=route.id
   if rig.has_method("clear_equipment_selection"):rig.clear_equipment_selection()
   if route.equipment!="inspection"and not rig.set_equipment(route.equipment):push_error("Equipment rejected");quit(2);return
   if not selected.is_empty()and not name in selected:continue
   var spec: Dictionary=clips.clips[name];var n=int(spec.duration_ticks);var rows=[];var offsets={"front":{"x":{},"y":{}},"rear":{"x":{},"y":{}}}
   var probe: Dictionary=rig.pose(name,0.0,view)
   if probe.has("error"):continue
   if not view in report.views:report.views.append(view)
   var folder=out.path_join(view+"/"+id);DirAccess.make_dir_recursive_absolute(folder)
   for tick in range(n):
    var phase=float(tick)/n if spec.loop else float(tick)/maxi(1,n-1)
    rig.visible_layers=[];var meta: Dictionary=rig.pose(name,phase,view);var image=await presented(vp)
    var file=view+"/"+id+"/%04d.png"%tick;image.save_png(out.path_join(file))
    var row={"tick":tick,"phase":phase,"file":file,"pixel_sha256":hash_bytes(image.get_data()),"pose":meta,"soles":{},"sole_points":{},"boots":{},"boot_pixel_sha256":{}}
    if name in ["walk","run","idle"]:
     for side in ["front","rear"]:
      rig.visible_layers=[side+"_boot"];rig.pose(name,phase,view);var boot=await presented(vp);var xmin=null;var ymax=null;var point_x=null
      for x in range(192):
       if boot.get_pixel(x,169).a>0:xmin=x;break
      for y in range(191,-1,-1):
       for x in range(192):
        if boot.get_pixel(x,y).a>0:ymax=y;point_x=x;break
       if ymax!=null:break
      var boot_file=view+"/"+id+"/%04d-%s.png"%[tick,side];boot.save_png(out.path_join(boot_file));row.soles[side]=xmin;row.sole_points[side]=null if ymax==null else [point_x,ymax];row.boots[side]=boot_file;row.boot_pixel_sha256[side]=hash_bytes(boot.get_data())
      if meta.contact_flags[side]and ymax!=null:
       for axis in ["x","y"]:
        var component=0 if axis=="x"else 1;var point=point_x if axis=="x"else ymax
        var offset=int(point)-int(floor(float(meta.feet[side][component])+0.0001));var key=str(offset);offsets[side][axis][key]=offsets[side][axis].get(key,0)+1
    rows.append(row)
   var endpoint: Dictionary=rig.pose(name,1.0,view);var start_root=probe.get("world_root",[0,0]);var end_root=endpoint.get("world_root",[0,0]);var root_motion=[float(end_root[0])-float(start_root[0]),float(end_root[1])-float(start_root[1])]
   report.clips[id+"/"+view]={"base_clip":name,"equipment":route.equipment,"root_motion":root_motion,"name":name,"view":view,"duration_ticks":n,"loop":spec.loop,"events":spec.events,"stride":float(spec.get("gait",{}).get("root_motion_px_per_cycle",0)),"frames":rows}
   if name in ["walk","run","idle"]:
    var chosen={}
    for side in ["front","rear"]:
     var result={"offset":[],"observed_integer_offset_counts":offsets[side]}
     for axis in ["x","y"]:
      var best=0;var count=-1
      for key in offsets[side][axis]:
       if offsets[side][axis][key]>count:best=int(key);count=offsets[side][axis][key]
      result.offset.append(best)
     chosen[side]=result
    report.offset_derivation[id+"/"+view]=chosen
   FileAccess.open(out.path_join("cache.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
   print("CACHE ",id,"/",view," ",n)
 rig.visible_layers=[]
 for name in bindings:
  if FileAccess.get_sha256(source.path_join(name))!=bindings[name]:push_error("Source changed during cache");quit(3);return
 print("CACHE_DONE ",report.clips.size());quit(0)
