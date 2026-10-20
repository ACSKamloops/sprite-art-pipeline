extends SceneTree
func key(code: int,pressed: bool) -> void:
 var e:=InputEventKey.new()
 e.keycode=code;e.physical_keycode=code;e.pressed=pressed
 Input.parse_input_event(e)
func _initialize() -> void:call_deferred("run")
func run() -> void:
 root.size=Vector2i(640,360)
 var room=load("res://room.tscn").instantiate()
 root.add_child(room)
 await process_frame
 assert(room.bank_enabled)
 var records: Array=[]
 DirAccess.make_dir_recursive_absolute("res://live-capture")
 for i in 210:
  if i in [10,130]:key(KEY_D,true)
  if i in [90,170]:key(KEY_D,false)
  await process_frame
  await RenderingServer.frame_post_draw
  var path:="res://live-capture/%04d.png"%i
  root.get_texture().get_image().save_png(path)
  var source_manifest:String=room.config.manifest
  var source_frame:int=room.frame_index
  if room.state=="start" or room.state=="stop":
   source_manifest=room.active_clip.path
   source_frame=room.clip_frame(room.active_clip,room.transition_phase)
  elif room.state=="idle":
   source_manifest=room.idle_clips[room.idle_variant].path
   source_frame=0
  records.append({"sample":i,"group":room.state,"state":room.state,"file":path,"source_manifest":source_manifest,"source_frame":source_frame,"root":[room.actor.position.x,room.actor.position.y],"bias":[room.visual_bias.x,room.visual_bias.y],"draw_origin":[room.sprite.position.x,room.sprite.position.y],"scale":room.config.scale,"walk_phase":room.phase,"transition_phase":room.transition_phase,"physics_tick":room.physics_steps})
 var file:=FileAccess.open("res://LIVE-CAPTURE-RECORDS.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"records":records,"fps":60,"scope":"Real injected D press/release drives live room._physics_process and authored state machine; engine fixed60FPS capture clock, no direct pose/root assignment; actual frame_post_draw screenshots","renderer":RenderingServer.get_video_adapter_name(),"state_events":room.state_log},"  "))
 print("LIVE CAPTURES ",records.size())
 quit()
