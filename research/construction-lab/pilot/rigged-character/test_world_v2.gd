extends SceneTree
var checks=[]
var rows=[]
var out=""
var cache_path=""
func check(ok: bool,label: String) -> void:checks.append({"passed":ok,"description":label})
func _initialize() -> void:
 Engine.max_fps=0
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--cache":cache_path=args[i+1]
  if args[i]=="--output":out=args[i+1]
 call_deferred("run")
func rendered(world: Control) -> Image:
 await process_frame;await RenderingServer.frame_post_draw
 var image=world.vp.get_texture().get_image();image.convert(Image.FORMAT_RGBA8);return image
func sole(image: Image,scale: int,camera_xy: Array) -> Variant:
 var used=image.get_used_rect()
 if not used.has_area():return null
 var y=used.end.y-1
 for x in range(used.position.x,used.end.x):
  if image.get_pixel(x,y).a>0:return [float(x)/scale+camera_xy[0],float(y+1)/scale-1.0+camera_xy[1]]
 return null
func run() -> void:
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh --output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var world=load("res://world_v2.gd").new();world.cache_path=cache_path;root.add_child(world);world.set_process(false)
 if not world.error.is_empty():push_error(world.error);quit(2);return
 world.set_equipment("inspection");world.guides.visible=false;world.effects.visible=false
 var metrics=[]
 for view in world.cache.views:
  for name in ["walk","run"]:
   for scale in [1,2,3]:
    for camera_mode in ["fixed","scroll"]:
     world.reset();world.set_view(view);world.set_scale_factor(scale);world.camera_mode=camera_mode;world.physical_x=400 if view=="left"else 120;world.physical_y=64;world.set_planar_movement({"right":Vector2.RIGHT,"left":Vector2.LEFT,"front":Vector2.DOWN,"back":Vector2.UP}[view],name=="run")
     var n=int(world.cache.clips[world.binding()].duration_ticks);var episodes={};var mismatches=0;var snapshots=[]
     # Both boots independently presented; same whole-actor draw transform throughout.
     for side in ["front","rear"]:
      world.debug_boot=side;world.clock=0;world.elapsed=0;world.physical_x=400 if view=="left"else 120;world.physical_y=64;world.camera=0;world.camera_y=0;world.present()
      for sample in range(n*10+1):
       if sample>0:world.advance(0.2)
       var image=await rendered(world);var value=sole(image,scale,[world.visual_camera,world.visual_camera_y]);var obs=world.observation.duplicate(true)
       var phase=world.elapsed/n;var contact=obs.contact_flags[side];var episode=int(floor(phase+(0.5 if side=="rear"else 0.0)));var key=side+":"+str(episode)
       if contact:
        if not episodes.has(key):episodes[key]=[]
        if value==null:mismatches+=1
        else:episodes[key].append(value)
       if sample in [0,5,n*5,n*10]:snapshots.append({"side":side,"sample":sample,"world_sole":value,"observation":obs})
     var ranges={};var passed=mismatches==0;var maximum=0.0
     for key in episodes:
      var xs=episodes[key].map(func(v):return v[0]);var ys=episodes[key].map(func(v):return v[1]);var span=maxf(xs.max()-xs.min(),ys.max()-ys.min());maximum=maxf(maximum,span);ranges[key]={"x_span":xs.max()-xs.min(),"y_span":ys.max()-ys.min(),"span":span};passed=passed and span<=0.5
     check(passed,"Actual GPU stance "+view+" "+name+" "+str(scale)+"x "+camera_mode)
     print("STANCE ",view," ",name," ",scale," ",camera_mode," span ",maximum)
     metrics.append({"view":view,"clip":name,"scale":scale,"camera":camera_mode,"threshold_native_px":0.5,"max_span":maximum,"episodes":ranges,"missing":mismatches,"snapshots":snapshots,"sample_count_per_boot":n*10+1})
 world.debug_boot="";world.reset();world.set_planar_movement(Vector2.DOWN,false);world.advance(8-1e-9);check(world.body.frame==7,"Genuine preboundary does not advance early")
 var physical=Vector2(world.physical_x,world.physical_y);world.playing=false;world.advance(10);check(Vector2(world.physical_x,world.physical_y)==physical,"Pause freezes XY physical root")
 world.playing=true;world.advance(0.25);check(world.clock>8.0,"Resume retains fractional clock")
 physical=Vector2(world.physical_x,world.physical_y);world.set_planar_movement(Vector2.DOWN,true);check(Vector2(world.physical_x,world.physical_y)==physical,"Walk to run preserves physical root")
 world.advance(0.25);world.set_planar_movement(Vector2.ZERO,false);check(world.clip=="idle","Run to idle transition")
 world.reset();check(world.clock==0 and world.hits.is_empty()and world.projectiles.is_empty(),"Replay resets simulation")
 await rendered(world);root.get_texture().get_image().save_png(out.path_join("sandbox-screen.png"))
 var failures=checks.filter(func(c):return not c.passed)
 var report={"schema":"copper-scout-world-v2-proof/v1","passed":failures.is_empty(),"checks":checks,"failures":failures,"contact_contexts":metrics,"cache_sha256":FileAccess.get_sha256(cache_path),"source_bindings":world.cache.source_bindings,"offset_derivation":world.cache.offset_derivation,"runner_sha256":FileAccess.get_sha256(get_script().resource_path),"world_sha256":FileAccess.get_sha256("res://world_v2.gd"),"renderer":RenderingServer.get_video_adapter_name(),"limits":["Four-source candidate movement-only proof; actions and final art are separate pending tests.","Hard-cut transitions do not claim artistic blending; physical root is preserved.","Contact gate uses actual perboot GPU pixels measured in world native units; visual camera explicitly quantized.","Original authored combat hitboxes/lifetimes are separate from sprite pose events and not Mana gameplay."]}
 FileAccess.open(out.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("WORLD_V2 ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty()else 2)
