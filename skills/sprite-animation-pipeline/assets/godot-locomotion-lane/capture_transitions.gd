extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 root.size=Vector2i(640,360)
 var room=load("res://room.tscn").instantiate()
 root.add_child(room)
 await process_frame
 assert(room.bank_enabled)
 room.capture_mode=true
 room.capture_bank=true
 var groups: Array=[]
 for i in room.textures.size():groups.append({"name":"stop-%02d"%i,"state":"stop","record":room.stop_clips[i]})
 for variant in room.start_clips:groups.append({"name":"start-"+variant,"state":"start","record":room.start_clips[variant]})
 var records: Array=[]
 DirAccess.make_dir_recursive_absolute("res://transition-capture")
 for group in groups:
  room.active_clip=group.record.clip
  room.active_binding=group.record.binding
  room.stance_episode=""
  for bias in [Vector2.ZERO,Vector2(-1.333333,2.0)]:
   for frame in room.active_clip.holds.size():
    for fraction in [0.0,0.25,0.5,0.75,0.999]:
     var t:float=(0.0 if frame==0 else float(room.active_clip.boundaries[frame-1]))+room.active_clip.holds[frame]*fraction
     var physical:Vector2=Vector2(250,250)+room.curve_offset(room.active_binding.root_curve,t)
     room.captured_state={"x":physical.x,"y":physical.y,"phase":0.0,"walking":false,"state":group.state,"transition_phase":t,"visual_bias":[bias.x,bias.y]}
     await process_frame
     await RenderingServer.frame_post_draw
     var index:=records.size()
     var path:="res://transition-capture/%04d.png"%index
     root.get_texture().get_image().save_png(path)
     records.append({"sample":index,"group":group.name,"state":room.state,"file":path,"source_manifest":room.active_clip.path,"source_frame":room.clip_frame(room.active_clip,room.transition_phase),"time":t,"fraction":fraction,"root":[room.actor.position.x,room.actor.position.y],"bias":[room.visual_bias.x,room.visual_bias.y],"draw_origin":[room.sprite.position.x,room.sprite.position.y],"scale":room.config.scale})
 var file:=FileAccess.open("res://TRANSITION-CAPTURE-RECORDS.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"records":records,"scope":"actual llvmpipe screenshots; every authored stop/start pose at5 hold fractions and2 entry biases; state assigned in_process before rendering; not live-clock evidence","renderer":RenderingServer.get_video_adapter_name()},"  "))
 print("TRANSITION CAPTURES ",records.size())
 quit()
