extends SceneTree
var path=""
var out=""
var checks=[]
var ledger=[]
var thrust_ledger=[]
func _initialize()->void:
 Engine.max_fps=0
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--cache":path=args[i+1]
  if args[i]=="--output":out=args[i+1]
 call_deferred("run")
func check(value:bool,label:String)->void:checks.append({"passed":value,"description":label})
func capture(world,command:String)->Dictionary:
 await process_frame;await RenderingServer.frame_post_draw
 var state=world.observation.duplicate(true);state.command=command
 state.rendered_pixel_sha256=world.hash_bytes(world.vp.get_texture().get_image().get_data());return state
func run()->void:
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var world=load("res://world_v2.gd").new();world.cache_path=path;root.add_child(world);world.set_process(false)
 if not world.error.is_empty():push_error(world.error);quit(2);return
 world.guides.visible=false;world.effects.visible=false
 for view in world.cache.views:
  for weapon in ["sword","blaster"]:
   world.reset();world.set_view(view);world.set_equipment(weapon)
   var states=[];states.append(await capture(world,"select "+weapon))
   var ready="idle_"+weapon+"/"+view
   check(world.binding()==ready,view+weapon+" readyidle selected texture")
   var vector={"right":Vector2.RIGHT,"left":Vector2.LEFT,"front":Vector2.DOWN,"back":Vector2.UP}[view]
   world.set_planar_movement(vector,false);world.advance(8.25);states.append(await capture(world,"walk 8.25"))
   check(world.binding()=="walk_"+weapon+"/"+view and world.body.frame==8,view+weapon+" equipped walking exact hold")
   var position=Vector2(world.physical_x,world.physical_y);world.set_planar_movement(vector,true);states.append(await capture(world,"run phase0"))
   check(Vector2(world.physical_x,world.physical_y)==position,view+weapon+" transition no physical jump")
   world.advance(12.5);world.set_planar_movement(Vector2.ZERO,false)
   var name="slash"if weapon=="sword"else"shoot";world.act(name);world.advance(9.25);states.append(await capture(world,name+"9.25"))
   check(world.equipment==weapon and world.binding()==name+"/"+view,view+weapon+" action equipment retained")
   check(not world.set_equipment("none"),view+weapon+" midattack stow rejected")
   world.take_hit(25);states.append(await capture(world,"hurt interrupt phase0"));check(world.binding()=="hurt_"+weapon+"/"+view,view+weapon+" interrupt uses equipped texture")
   world.advance(35.75);states.append(await capture(world,"hurt final observed hold"));world.advance(0.25);states.append(await capture(world,"hurt completed"));check(world.binding()==ready,view+weapon+" hurt restores readyidle")
   world.take_hit(75);world.advance(65.75);states.append(await capture(world,"knockdown last hold"))
   check(world.binding()=="knockdown_"+weapon+"/"+view and world.body.frame==65,view+weapon+" final fallen equipped frame")
   world.advance(100);check(world.body.frame==65,view+weapon+" fallen endpoint held")
   world.act("recover",true);states.append(await capture(world,"recover opening"));world.advance(77.75);states.append(await capture(world,"recover final hold"))
   check(world.binding()=="recover_"+weapon+"/"+view and world.body.frame==77,view+weapon+" equipped recovery final hold")
   world.advance(0.25);states.append(await capture(world,"recover complete ready"));check(world.binding()==ready and world.health==100,view+weapon+" readyidle after recovery")
   check(not world.act("cast")and not world.act("celebrate"),view+weapon+" cast and celebration require stow")
   check(not world.act("shoot"if weapon=="sword"else"slash"),view+weapon+" mismatched weapon action rejected")
   world.set_equipment("none");world.act("cast");states.append(await capture(world,"explicit stow then cast"));world.advance(float(world.cache.clips[world.binding()].duration_ticks)-0.25);states.append(await capture(world,"cast final observed hold"));world.advance(0.25);states.append(await capture(world,"cast completed"));check(world.equipment=="none"and world.binding()=="idle/"+view,view+weapon+" casting stays stowed")
   ledger.append({"view":view,"equipment":weapon,"states":states,"transitions":world.transitions.duplicate(true),"events":world.events.duplicate(true)})
 for view in world.cache.views:
  world.reset();world.set_view(view);world.set_equipment("sword")
  var ready=await capture(world,"ready before thrust");world.act("thrust");var first=await capture(world,"thrust opening0")
  world.advance(47.75);var last=await capture(world,"thrust final observed47");world.advance(0.25);var after=await capture(world,"thrust complete ready0")
  check(last.held==47 and after.held==0 and after.binding=="idle_sword/"+view,"Observed thrust47 toready0 "+view)
  check(first.rendered_pixel_sha256==ready.rendered_pixel_sha256 and last.rendered_pixel_sha256==ready.rendered_pixel_sha256 and after.rendered_pixel_sha256==ready.rendered_pixel_sha256,"Actual GPU wholethrust endpoints exactready guard "+view)
  thrust_ledger.append({"view":view,"equipment":"sword","states":[ready,first,last,after],"transitions":world.transitions.duplicate(true)})
 # Collision times are invariant under tick partition; actual rendered directional FX follows physics.
 for view in world.cache.views:
  var hit_times=[]
  for partition in [48.0,1.0,0.25]:
   world.reset();world.set_view(view);world.set_equipment("blaster");world.respawn_target();world.act("shoot")
   for i in range(int(48/partition)):world.advance(partition)
   hit_times.append(world.hits[0].tick if world.hits.size()==1 else -1)
  check(hit_times[0]>=0 and absf(hit_times[0]-hit_times[1])<1e-9 and absf(hit_times[0]-hit_times[2])<1e-9,"Exact swept impact time independent of frame rate "+view)
  world.reset();world.set_view(view);world.set_equipment("blaster");world.target_x=10000;world.physical_target_y=10000;world.act("shoot");world.advance(25)
  var bolt=world.effects.items.filter(func(item):return item.type=="bolt")
  check(bolt.size()==1 and bolt[0].heading==world.heading(),"Four-direction FX heading matches physics "+view)
  world.body.visible=false;world.effects.visible=true
  await process_frame;await RenderingServer.frame_post_draw
  var pixels=world.vp.get_texture().get_image();var tip=bolt[0].point+bolt[0].heading*(world.clock-bolt[0].birth)*2-Vector2(world.visual_camera,world.visual_camera_y)
  var color=pixels.get_pixel(int(round(tip.x)),int(round(tip.y)))
  check(color.a>0.99 and color.r>0.9,"Actual GPU bolt at declared physics tip "+view)
  pixels.save_png(out.path_join("projectile-"+view+".png"));world.effects.visible=false;world.body.visible=true
 world.reset();world.set_equipment("sword");world.act("charge");world.advance(60);check(world.events.any(func(event):return event.type=="charge_ready"),"Charge-ready source marker at60")
 world.release_charge();world.advance(54);check(world.hits.size()==1 and world.hits[0].amount==40,"Declared original charged melee damage40")
 world.reset();world.set_equipment("sword");world.set_speed(2);world._process(0.1)
 check(world.clock==12 and world.body.frame==12,"Actual process dt0.1 times speed2 advances12 ticks")
 world.set_speed(0.5);world._process(0.1);check(world.clock==15 and world.body.frame==15,"Speed change preserves clock and advances3 moreticks")
 world.playing=false;world._process(1);check(world.clock==15,"Paused process clock stays fixed")
 world.playing=true;world._process(0.01);check(absf(world.clock-15.3)<1e-12,"Resume retains .3 fractional tick")
 check(not world.set_speed(NAN)and not world.set_speed(0)and not world.set_speed(5),"Invalid speeds reject without clock changes")
 var before=world.clock;check(not world.advance(-1)and not world.advance(INF)and not world.advance(10001)and world.clock==before,"Invalid/budget dt reject unchanged state")
 var failed=checks.filter(func(v):return not v.passed)
 var report={"schema":"copper-scout-world-v2-state-contract/v1","passed":failed.is_empty(),"checks":checks,"failures":failed,"ledger":ledger,"thrust_ledger":thrust_ledger,"controller_sha256":FileAccess.get_sha256("res://world_v2.gd"),"runner_sha256":FileAccess.get_sha256(get_script().resource_path),"effects_sha256":FileAccess.get_sha256("res://world_v2_effects.gd"),"parent_effects_sha256":FileAccess.get_sha256("res://effects.gd"),"cache_sha256":FileAccess.get_sha256(path),"source_bindings":world.cache.source_bindings,"semantics":{"equipment":"Explicit none/sword/blaster; preserved through action/damage/fall/recovery; switches only locomotion/idle","required":{"slash":"sword","thrust":"sword","charge":"sword","shoot":"blaster","cast":"none","celebrate":"none"},"state_transition":"Hard cut toframe0 with unchanged physical XY; nonloops complete after finalhold then matching readyidle; fall holds finalframe","events":"Unique epoch/cycle/index token; original authored tick births despite frame skip; independent physics/VFX TTL","input":"Arrow/WASD+Shift movement; Xslash Tthrust Zshoot Qcharge/release Ccast Bcelebrate Hhurt Kknockdown Vrecover Spacepause Rreplay","scope":"Original game sandbox, not native Mana gameplay or universal art approval"}}
 FileAccess.open(out.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("WORLD_STATES ",checks.size()," failures ",failed.size());quit(0 if failed.is_empty()else 2)
