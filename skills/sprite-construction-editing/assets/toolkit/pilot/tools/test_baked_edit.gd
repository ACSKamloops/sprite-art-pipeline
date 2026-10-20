extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var lab=load("res://lab.gd").new();root.add_child(lab);lab.set_process(false)
 if not lab.load_error.is_empty():push_error(lab.load_error);quit(2);return
 for viewport in [lab.live_viewport,lab.baked_viewport]:viewport.get_meta("guide").visible=false
 var proof=JSON.parse_string(FileAccess.get_file_as_string("res://generated/pixel-edit-proof.json"))
 lab.select_clip(proof.binding.split("/")[0]);lab.set_view(proof.binding.split("/")[1]);lab.replay(false);lab.advance_ticks(float(proof.tick),true)
 await process_frame;await RenderingServer.frame_post_draw
 var actual=lab.baked_viewport.get_texture().get_image();actual.convert(Image.FORMAT_RGBA8)
 var original=lab.live_viewport.get_texture().get_image();original.convert(Image.FORMAT_RGBA8)
 var changed=[]
 for y in range(192):
  for x in range(192):
   if actual.get_pixel(x,y)!=original.get_pixel(x,y):changed.append([x,y])
 var digest=HashingContext.new();digest.start(HashingContext.HASH_SHA256);digest.update(actual.get_data());var hash=digest.finish().hex_encode()
 var sorted_expected=[]
 for point in proof.changed_coordinates:sorted_expected.append([int(point[0]),int(point[1])])
 sorted_expected.sort_custom(func(a,b):return a[1]*192+a[0]<b[1]*192+b[0])
 var passed=hash==proof.candidate_rgba_sha256 and changed==sorted_expected
 actual.save_png("res://generated/pixel-edited-actual-gpu.png")
 var report={"schema":"baked-pixel-gpu-proof/v1","passed":passed,"actual_rgba_sha256":hash,"expected_rgba_sha256":proof.candidate_rgba_sha256,"changed_coordinates":changed,"unchanged_rgba_outside_coordinates":passed,"manifest_sha256":FileAccess.get_sha256("res://generated/manifest.json"),"resource_sha256":FileAccess.get_sha256("res://generated/frames.tres"),"tester_sha256":FileAccess.get_sha256(get_script().resource_path),"scope":"Actual lab AnimatedSprite2D atlas playback equals edited composite; live original differs only at explicit edit coordinates. Not temporal/art approval."}
 FileAccess.open("res://generated/pixel-edit-gpu-proof.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("BAKED_PIXEL_GPU_PROOF ",passed," changed_pixels=",changed.size());quit(0 if passed else 2)
