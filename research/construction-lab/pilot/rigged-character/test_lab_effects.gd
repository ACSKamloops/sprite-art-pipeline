extends SceneTree
var checks=[]
func check(ok: bool,label: String) -> void:checks.append({"passed":ok,"description":label})
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var lab=load("res://lab.gd").new();root.add_child(lab);lab.set_process(false)
 for viewport in [lab.live_viewport,lab.baked_viewport]:viewport.get_meta("guide").visible=false
 check(not lab.effects_enabled and not lab.effects.visible,"Body pixel oracle defaults effects off")
 lab.set_effects(true)
 for clip in ["shoot","cast"]:
  for view in ["right","left"]:
   lab.select_clip(clip);lab.set_view(view);lab.replay();var c: Dictionary=lab.clips.clips[clip]
   var event=c.events.filter(func(e):return e.type in ["projectile_emit","cast_emit"])[0]
   lab.advance_ticks(event.tick+3.0)
   var state: Dictionary=lab.effects.snapshot();var expected_pose=lab.rig.pose(clip,float(event.tick)/(int(c.duration_ticks)-1),view)
   var key="muzzle"if clip=="shoot"else"cast"
   check(state.history.size()==1 and state.history[0].born_tick==event.tick,clip+view+" original event birth retained across skip")
   check(state.history[0].anchor==expected_pose.fx_anchors[key],clip+view+" original event pose anchor")
   check(state.history[0].direction==(-1.0 if view=="left"else 1.0),clip+view+" mirror direction")
   lab.show_pose();await process_frame;await RenderingServer.frame_post_draw
   var with_fx=lab.baked_viewport.get_texture().get_image().get_data();lab.effects.visible=false
   await process_frame;await RenderingServer.frame_post_draw
   check(with_fx!=lab.baked_viewport.get_texture().get_image().get_data(),clip+view+" actual GPU overlay visible")
   lab.effects.visible=true;lab.pause();var paused=lab.effects.snapshot();lab.advance_ticks(10);check(paused==lab.effects.snapshot(),clip+view+" Pause freezes effects clock")
   lab.set_effects(false);lab.set_effects(true);check(lab.effects.snapshot()==paused,clip+view+" toggle rebuild preserves original age")
   lab.replay(false);check(lab.effects.snapshot().live_count==0,clip+view+" Replay cleanup")
   lab.replay();lab.advance_ticks(c.duration_ticks);check(lab.effects.snapshot().live_count==0,clip+view+" late event expires at current clock")
 lab.select_clip("charge");lab.replay();lab.advance_ticks(61);check(lab.effects.snapshot().live_count==1 and lab.effects.snapshot().history.size()==2,"Charge ready replaces expired begin lifecycle")
 lab.select_clip("shoot");lab.set_view("right");lab.loop_override=true;lab.replay();lab.advance_ticks(67)
 var looped=lab.effects.snapshot();check(looped.history.size()==2 and looped.history[0].born_tick==18.0 and looped.history[1].born_tick==66.0,"Forced loop keeps absolute VFX event birth")
 check(looped.live_count==2,"Forced loop second emission has only its current flash/bolt")
 check(looped.history[0].anchor==looped.history[1].anchor,"Repeated emission uses original local event pose")
 lab.loop_override=false;lab.select_clip("charge");lab.replay();lab.advance_ticks(91)
 check(lab.effects.snapshot().history.size()==3 and lab.effects.snapshot().live_count==1,"Looping charge begins new cycle on absolute clock")
 var failures=checks.filter(func(c):return not c.passed)
 FileAccess.open("res://generated/lab-effects-proof.json",FileAccess.WRITE).store_string(JSON.stringify({"schema":"copper-scout-lab-effects/v1","passed":failures.is_empty(),"check_count":checks.size(),"checks":checks,"failures":failures,"lab_sha256":FileAccess.get_sha256("res://lab.gd"),"effects_sha256":FileAccess.get_sha256("res://effects.gd"),"source_bindings":lab.manifest.source_bindings,"scope":"Optional authored VFX overlay; original event-time pose/birth and shared absolute clock; no gameplay collision"},"  "))
 print("LAB_EFFECTS ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty()else 2)
