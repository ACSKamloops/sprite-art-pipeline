extends SceneTree
var cache_path=""
var out=""
var checks=[]
var routes=[]
func check(value: bool,label: String)->void:checks.append({"passed":value,"description":label})
func _initialize()->void:
 Engine.max_fps=0
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--cache":cache_path=args[i+1]
  if args[i]=="--output":out=args[i+1]
 call_deferred("run")
func image(world)->Image:
 await process_frame;await RenderingServer.frame_post_draw
 var result=world.vp.get_texture().get_image();result.convert(Image.FORMAT_RGBA8);return result
func run()->void:
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var world=load("res://world_v2.gd").new();world.cache_path=cache_path;root.add_child(world);world.set_process(false)
 if not world.error.is_empty():push_error(world.error);quit(2);return
 world.set_equipment("inspection");world.guides.visible=false;world.effects.visible=false
 # Every held tick is drawn by an actual AnimatedSprite2D in Godot, not a JS timing mirror.
 for binding in world.cache.clips:
  var c=world.cache.clips[binding];var name=c.get("base_clip",c.name);var view=c.view;world.reset();world.set_equipment("inspection");world.set_view(view);world.set_equipment(c.get("equipment","inspection"));world.set_state(name);world.advance(0.25)
  var good=true;var rows=[]
  for tick in range(int(c.duration_ticks)):
   if tick>0:world.advance(1.0)
   var frame=await image(world);var position=Vector2i(world.body.position);var cut=frame.get_region(Rect2i(position,Vector2i(192,192)))
   var row=c.frames[tick];var sha=world.hash_bytes(cut.get_data());var ok=world.body.frame==tick and world.binding()==binding and sha==row.pixel_sha256
   good=good and ok;rows.append({"tick":tick,"held":world.body.frame,"pixel_sha256":sha,"passed":ok})
  check(good,"Every rendered hold/order/pixel "+binding);routes.append({"binding":binding,"frames":rows})
  if c.loop:
   world.advance(1);check(world.body.frame==0,"Exact loop boundary "+binding)
  elif name=="knockdown":
   world.advance(100);check(world.body.frame==int(c.duration_ticks)-1 and world.clip==name,"Knockdown holds final pose "+view)
  else:
   world.advance(1);check(world.clip=="idle","One-shot recovery policy "+binding)
 # Four headings have actual swept projectile and independently authored melee collisions.
 for view in world.cache.views:
  world.reset();world.set_equipment("inspection");world.set_view(view);world.respawn_target();world.act("shoot");world.advance(48)
  check(world.hits.size()==1 and world.target_health==28 and world.projectiles.is_empty(),"Low-rate swept projectile hit and cleanup "+view)
  world.act("slash");world.advance(54);check(world.target_health==8,"Melee overlap exactly once "+view)
  world.act("slash");world.advance(54);check(world.target_health==0 and not world.target_visible,"Independent target-death cleanup "+view)
  world.reset();world.set_view(view);world.act("shoot");world.advance(5);world.take_hit(25);world.advance(100)
  check(world.hits.is_empty()and world.health==75 and world.clip=="idle","Pre-emission interruption cancels attack "+view)
  world.take_hit(75);var before=world.clock;world.advance(180);check(world.clip=="knockdown"and world.clock==before+180,"Lethal interruption and held endpoint "+view)
  world.act("recover",true);world.advance(78);check(world.health==100 and world.clip=="idle","Recovery health/animation completion "+view)
 world.reset();world.set_equipment("inspection");world.act("shoot");world.target_x=10000;world.physical_target_y=10000;world.advance(100)
 check(world.projectiles.is_empty()and world.effects.snapshot().live_count==0,"Missed projectile physics and FX expire")
 world.reset();world.set_equipment("inspection");world.act("shoot");world.advance(20);var born=world.events.duplicate(true);var clock=world.clock;world.playing=false;world.advance(100)
 check(world.clock==clock and world.events==born,"Pause freezes event and absolute clock")
 world.playing=true;world.advance(20);var keys={};var unique=true
 for event in world.events:
  if keys.has(event.token):unique=false
  keys[event.token]=true
 check(unique and world.events.slice(0,born.size())==born,"Resume preserves markers without duplicate tokens")
 world.reset();check(world.events.is_empty()and world.projectiles.is_empty()and world.hits.is_empty(),"Replay clears markers, collision and effects")
 var failed=checks.filter(func(v):return not v.passed)
 var report={"schema":"copper-scout-world-v2-action-proof/v1","passed":failed.is_empty(),"checks":checks,"failures":failed,"routes":routes,"source_bindings":world.cache.source_bindings,"cache_sha256":FileAccess.get_sha256(cache_path),"world_sha256":FileAccess.get_sha256("res://world_v2.gd"),"effects_sha256":FileAccess.get_sha256("res://world_v2_effects.gd"),"parent_effects_sha256":FileAccess.get_sha256("res://effects.gd"),"runner_sha256":FileAccess.get_sha256(get_script().resource_path),"limits":["Original authored swept-point projectile and rectangle melee damage rules, not native Mana hitboxes.","One-shot returns idle except held knockdown; transitions reset phase with physical root preserved.","Mechanical rendering evidence does not approve source art."]}
 FileAccess.open(out.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("WORLD_ACTIONS ",checks.size()," failures ",failed.size());quit(0 if failed.is_empty()else 2)
