extends SceneTree
var checks=[]
func check(ok: bool,description: String) -> void:checks.append({"passed":ok,"description":description})
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var world=load("res://moving_world.gd").new();root.add_child(world);world.set_process(false)
 await process_frame
 check(world.error.is_empty(),"Current source/cache/policy/frame bindings accepted")
 if not world.error.is_empty():print(world.error);quit(2);return
 world.guide.visible=false
 var rows=[]
 for clip in ["walk","run"]:
  world.clip=clip
  for tick in [0.0,0.2,1.2,7.8,18.6,29.8,35.8,59.8,60.0,60.2]:
   world.clock=tick;world.mode="contact-locked visual root";world.present()
   await process_frame;await RenderingServer.frame_post_draw
   var actual=world.viewport.get_texture().get_image();actual.convert(Image.FORMAT_RGBA8)
   var expected=Image.create(512,192,false,Image.FORMAT_RGBA8)
   var binding: Dictionary=world.manifest.clips[clip+"/right"]
   var held=int(world.observation.held_tick)
   var source=Image.load_from_file("res://generated/"+binding.frames[held].png);source.convert(Image.FORMAT_RGBA8)
   var xpos=int(world.ORIGIN+world.observation.draw_root)
   expected.blit_rect(source,Rect2i(0,0,192,192),Vector2i(xpos,0))
   check(actual.get_data()==expected.get_data(),clip+" %.1f fixed-camera actual GPU whole-sprite translation"%tick)
   check(absf(world.observation.physical_root-float(world.clips.clips[clip].gait.root_motion_px_per_cycle)*tick/int(world.clips.clips[clip].duration_ticks))<=1.0e-12*maxf(1.0,absf(world.observation.physical_root)),clip+" physical root independent "+str(tick))
   for value in world.observation.policy.active_contact_residual_px.values():check(absf(value)<=0.5,clip+" active cache contact residual")
   rows.append(world.observation.duplicate(true))
  world.mode="baked physical root";world.present();check(world.observation.draw_root==world.observation.physical_root,clip+" raw mode has no contact compensation")
  world.mode="live physical root";world.present();check(world.rig.visible and not world.sprite.visible,clip+" live renderer selected")
 var before=world.clock;check(not world.advance(NAN)and world.clock==before,"Invalid elapsed tick rejected atomically")
 var cache_path="res://contact-proof/held-sole-cache.json";var original=FileAccess.get_file_as_string(cache_path)
 for kind in ["source","raster","reordered","fractional","out_of_canvas"]:
  var broken=world.cache.duplicate(true)
  if kind=="source":broken.source_sha256["clips.json"]="0".repeat(64)
  elif kind=="raster":broken.clips.walk.frames[0].whole_frame_rgba_sha256="0".repeat(64)
  elif kind=="reordered":var first=broken.clips.walk.frames[0];broken.clips.walk.frames[0]=broken.clips.walk.frames[1];broken.clips.walk.frames[1]=first
  elif kind=="fractional":broken.clips.walk.frames[0].sole_xmin.front=102.5
  else:broken.clips.walk.frames[0].sole_xmin.front=9999
  FileAccess.open(cache_path,FileAccess.WRITE).store_string(JSON.stringify(broken))
  var reject=load("res://moving_world.gd").new();check(not reject.configure_sources(),"Actual loader rejects stale "+kind+" binding");reject.free()
  FileAccess.open(cache_path,FileAccess.WRITE).store_string(original)
 var resource_path="res://generated/frames.tres";var resource_original=FileAccess.get_file_as_bytes(resource_path)
 FileAccess.open(resource_path,FileAccess.WRITE).store_string("corrupted SpriteFrames resource")
 var rejected_resource=load("res://moving_world.gd").new();check(not rejected_resource.configure_sources(),"Actual loader rejects corrupt SpriteFrames before resource load");rejected_resource.free()
 FileAccess.open(resource_path,FileAccess.WRITE).store_buffer(resource_original)
 var left=world.rig.pose("walk",0.0,"left")
 check(load("res://foot_contact.gd").contact_draw_root(left,0.0,{"front":1,"rear":1}).has("error"),"Unsupported left contact policy rejected")
 world.mode="contact-locked visual root";world.clock=0;world.present()
 await process_frame;await RenderingServer.frame_post_draw
 world.guide.visible=true;await process_frame;await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://generated/moving-world-screenshot.png")
 var failures=checks.filter(func(c):return not c.passed)
 var report={"schema":"copper-scout-moving-world-consumer/v1","passed":failures.is_empty(),"checks":checks,"check_count":checks.size(),"failures":failures,"observations":rows,"source_bindings":world.cache.source_sha256,"policy_sha256":world.cache.policy_sha256,"consumer_sha256":FileAccess.get_sha256("res://moving_world.gd"),"tester_sha256":FileAccess.get_sha256("res://test_moving_world.gd"),"limits":["Fixed camera, authored right walk/run only.","Whole-body contact lock is a visual translation, separate from continuous physical root.","Bounded integration samples do not replace two-cycle boot sole proof or art review.","No physics/collision implementation."]}
 FileAccess.open("res://generated/moving-world-proof.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("WORLD_PROOF ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty()else 2)
