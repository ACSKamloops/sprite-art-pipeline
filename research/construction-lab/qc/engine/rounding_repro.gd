extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var player=load("res://scripts/native_obj_player.gd").new();root.add_child(player);player.set_process(false)
 var loaded: bool=player.load_route("res://routes/sword-charge-1/route.json")
 if not loaded:quit(3);return
 player.replay();player.set_speed(2.0);var delta=4.0/float(player.route.video_fps);player._process(delta);var actual=player.read_back()
 player.replay();player.advance_ticks(8.0);var exact=player.read_back()
 var report={"loaded":loaded,"source_sha256":FileAccess.get_sha256("res://scripts/native_obj_player.gd"),"fps":player.route.video_fps,"delta_seconds":delta,"speed":2,"mathematical_target_video_ticks":8,"actual_process_state":actual,"exact_integer_advance_state":exact,"passed":actual.frame_index==8 and abs(float(actual.elapsed_ticks))<0.000000001}
 FileAccess.open("res://rounding-repro.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("ROUNDING_REPRO ",JSON.stringify(report));quit(0 if report.passed else 2)
