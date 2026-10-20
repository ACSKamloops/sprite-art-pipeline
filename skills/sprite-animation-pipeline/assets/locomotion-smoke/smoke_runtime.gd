extends SceneTree
var room
var checks:Array=[]
var failures:=0
func check(ok:bool,name:String,data=null)->void:
 checks.append({"pass":ok,"name":name,"data":data})
 if not ok:
  failures+=1
  push_error(name+" "+str(data))
func ticks(n:int)->void:
 for i in n:await physics_frame
 await process_frame
func until_state(target:String,limit:=150)->bool:
 for i in limit:
  await physics_frame
  await process_frame
  if room.state==target:return true
 return false
func key(code:int,pressed:bool)->void:
 var e:=InputEventKey.new();e.keycode=code;e.physical_keycode=code;e.pressed=pressed;Input.parse_input_event(e)
func _initialize()->void:call_deferred("run")
func run()->void:
 Engine.max_fps=144
 room=load("res://room.tscn").instantiate();root.add_child(room);await process_frame
 check(room.textures.size()==3 and room.textures[0].get_width()==12 and room.textures[0].get_height()==10,"three12x10 source frames, no96/16 assumption")
 check(room.manifest.pivot==[4.0,8.0],"source pivot4,8 preserved")
 check(room.idle_variant=="rest" and room.idle_clips.size()==1,"unique rest key normalized without A/B or initial_idle")
 check(abs(room.cycle-0.25)<1e-15,"asymmetric rational cycle exactly quarter-second",room.cycle)
 check(room.textures[0].get_image().get_pixel(0,0)==Color8(117,107,105,255),"reordered first binding isrgba2, not filename sort")
 var bounds:Array=[1.0/24.0,1.0/8.0]
 for i in bounds.size():
  var t:float=bounds[i]
  check(room.select_frame(t-1e-10)==i,"truly-before rational boundary remains previous pose%d"%i)
  check(room.select_frame(t)==i+1,"exact rational boundary selects next pose%d"%i)
  check(room.select_frame(t+1e-10)==i+1,"after rational boundary selects next pose%d"%i)
 check(room.select_frame(0.25-1e-10)==2 and room.select_frame(0.25)==0 and room.select_frame(0.25+1e-10)==0 and room.select_frame(0.5)==0,"strict before/exact/after cycle and two-cycle wrap")
 var finite:Dictionary=room.stop_clips[0].clip
 check(room.clip_frame(finite,1.0/30.0-1e-10)==0 and room.clip_frame(finite,1.0/30.0)==1,"two-key finite clip strict rational boundary")
 check(room.clip_frame(finite,1.0/12.0)==1,"finite endpoint holds final key, never wraps")
 room.capture_mode=true
 room.begin_transition("stop",room.stop_clips[0])
 room.transition_phase=1.0/12.0-1e-10
 room.bank_tick(0.0,false)
 check(room.state=="stop","finite state cannot complete1e-10s early")
 room.transition_phase=1.0/12.0
 room.bank_tick(0.0,false)
 check(room.state=="idle","finite state completes at exact rational endpoint")
 room.capture_mode=false
 # Every source pose can stop at both interior and immediately-before-next samples.
 for i in 3:
  for fraction in [0.0,0.5,0.999]:
   room.reset();room.state="walk";room.walking=true;room.actor.position=Vector2(200,250);room.frame_index=i;room.phase=0.0
   for j in i:room.phase+=room.holds[j]
   room.phase+=room.holds[i]*fraction
   room.visual_bias=Vector2(0.625,-0.375);room.present()
   var first:PackedByteArray=room.sprite.texture.get_image().get_data();var origin:Vector2=room.actor.position
   key(KEY_D,true);key(KEY_D,false)
   check(await until_state("stop",5),"real release enters two-key stop%d/%.3f"%[i,fraction])
   check(room.sprite.texture.get_image().get_data()==first,"two-key stop starts source-exact%d/%.3f"%[i,fraction])
   check(await until_state("idle"),"two-key stop finishes rest%d/%.3f"%[i,fraction])
   check(room.actor.position.distance_to(origin+Vector2(2,-1))<0.001,"native curve scaled2x endpoint%d/%.3f"%[i,fraction])
   check(room.visual_bias==Vector2(0.625,-0.375),"entry bias retained through rest%d/%.3f"%[i,fraction])
 # Real input starts, reaches declared walk entry1, then queues a release.
 room.reset();key(KEY_D,true)
 check(await until_state("start",5),"D starts from rest")
 key(KEY_D,false)
 check(await until_state("walk"),"release queues through finite two-key start")
 check(room.frame_index==1,"start enters declared reordered walk frame1")
 check(await until_state("idle"),"queued release completes authored stop")
 # Source and physical clock behavior at three render caps; no transition confound.
 for fps in [30,60,144]:
  room.reset();room.state="walk";room.walking=true;room.toggled_walk=true;room.rate=1.0;room.actor.position=Vector2(180,250);Engine.max_fps=fps
  var count:int=room.physics_steps;var origin:Vector2=room.actor.position
  await ticks(75)
  var elapsed:int=room.physics_steps-count
  check(room.seen.size()==3,"actual source clock covers all asymmetric poses FPS%d"%fps)
  check(abs(room.actor.position.x-origin.x-float(elapsed)/120.0*24.0)<0.01,"render cap independent24px/sec FPS%d"%fps)
 Engine.max_fps=144
 for speed in [0.5,1.0,2.0]:
  room.reset();room.rate=speed;room.command("Walk / stop");await until_state("start",5)
  var begin:int=room.physics_steps;var origin:Vector2=room.actor.position
  await until_state("walk")
  check(abs((room.physics_steps-begin)-(10.0/speed))<=2,"two-key finite rational clock rate%.1f"%speed)
  check(room.actor.position.distance_to(origin+Vector2(-2,1))<0.001,"native start curve endpoint independent of rate%.1f"%speed)
 room.reset();room.rate=1.0;room.command("Walk / stop");await until_state("start",5)
 key(KEY_P,true);key(KEY_P,false);await process_frame
 var phase:float=room.transition_phase;var position:Vector2=room.actor.position
 await ticks(10)
 check(room.paused and room.transition_phase==phase and room.actor.position==position,"actual P freezes source and physical transition clock")
 key(KEY_N,true);key(KEY_N,false);await process_frame
 check(room.clip_frame(room.active_clip,room.transition_phase)==1 and room.actor.position==position,"actual N steps second key at fixed inspection root")
 key(KEY_R,true);key(KEY_R,false);await ticks(2)
 check(room.state=="idle" and room.idle_variant=="rest" and room.visual_bias==Vector2.ZERO,"actual R resets unique rest variant and bias")
 room.state="walk";room.walking=true;room.toggled_walk=true;room.actor.position=Vector2(float(room.config.lane_end)-10.01,250)
 await ticks(35)
 check(room.state=="idle" and room.blocked and room.actor.position.x<=float(room.config.lane_end)-9.9,"real collision constrains explicit curve and inhibits restart")
 var f:=FileAccess.open("res://SMOKE-RUNTIME-RESULTS.json",FileAccess.WRITE);f.store_string(JSON.stringify({"failed":failures,"checks":checks,"engine":Engine.get_version_info(),"scope":"fresh12x10 three-frame reordered/asymmetric rational source, unique rest idle, two-key finite native-root curves; actual input/state/clock/render-cap/rate/pause/reset/step/collision tests"},"  "))
 print("PORTABLE SMOKE CHECKS ",checks.size()," failures ",failures);quit(1 if failures else 0)
