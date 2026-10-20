extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
 root.size = Vector2i(640,360)
 var room = load("res://room.tscn").instantiate()
 root.add_child(room)
 await process_frame
 assert(not room.contacts.is_empty(), "Configure source-bound contacts before contact capture")
 room.capture_mode = true
 var records: Array = []
 var sample := 0
 for locked in [false,true]:
  room.stance_enabled = locked
  room.stance_episode = ""
  var dir := "res://contact-locked" if locked else "res://contact-raw"
  DirAccess.make_dir_recursive_absolute(dir)
  for loop in 2:
   for pose in room.holds.size():
    for fraction in [0.0,0.25,0.5,0.75,0.999]:
     var local_phase: float = (0.0 if pose == 0 else room.boundaries[pose-1]) + room.holds[pose]*fraction
     var t: float = loop*room.cycle + local_phase
     room.captured_state = {"x":float(room.config.start_root[0])+t*float(room.config.stride_pixels)/room.cycle,"y":room.config.start_root[1],"phase":local_phase,"walking":true}
     await process_frame
     await RenderingServer.frame_post_draw
     var path := dir.path_join("%04d.png"%sample)
     root.get_texture().get_image().save_png(path)
     records.append({"file":path,"mode":"locked" if locked else "raw","sample":sample,"loop":loop,"fraction":fraction,"time":t,"pose":room.frame_index,"root":[room.actor.position.x,room.actor.position.y],"correction":[room.draw_correction.x,room.draw_correction.y],"episode":room.stance_episode,"contact":room.contacts[room.frame_index],"scale":room.config.scale,"pivot":room.manifest.pivot})
     sample += 1
 var out := FileAccess.open("res://CONTACT-CAPTURE-RECORDS.json",FileAccess.WRITE)
 out.store_string(JSON.stringify({"records":records,"scope":"actual OpenGL screenshots; fixed state assigned in _process; raw and one-whole-actor visual lock, two cycles and five hold fractions per pose","renderer":RenderingServer.get_video_adapter_name()},"  "))
 print("CONTACT SAMPLES ",sample)
 quit()
