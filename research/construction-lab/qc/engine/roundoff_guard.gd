extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var player=load("res://scripts/native_obj_player.gd").new();root.add_child(player);player.set_process(false)
 var cases=[];var ok: bool=player.load_route("res://routes/sword-charge-1/route.json")
 for ticks in [7.999999999999999,8.0,7.999999999,7.99999999999,7.999999,7.75,0.999999999,0.75]:
  player.replay();player.advance_ticks(ticks);var state=player.read_back()
  var wanted=8 if abs(ticks-8.0)<1.0e-12 else int(floor(ticks))
  var passed=state.frame_index==wanted
  # Inputs outside the normalization bound must retain the fractional phase.
  if wanted==int(floor(ticks)) and ticks!=8.0:passed=passed and abs(state.elapsed_ticks-(ticks-floor(ticks)))<1.0e-14
  cases.append({"input_ticks_decimal":"%.17f" % ticks,"input_ticks":ticks,"wanted_frame":wanted,"actual_frame":state.frame_index,"elapsed_ticks":state.elapsed_ticks,"passed":passed});ok=ok and passed
 # Legitimate process-clock advance one billionth of a tick early must not cross.
 player.replay();player.set_speed(2.0);player._process((8.0-1.0e-9)/(float(player.route.video_fps)*2.0))
 var early=player.read_back();var early_ok=early.frame_index==7;cases.append({"case":"process clock 1e-9 tick before boundary","actual_frame":early.frame_index,"elapsed_ticks":early.elapsed_ticks,"passed":early_ok});ok=ok and early_ok
 var report={"passed":ok,"source_sha256":FileAccess.get_sha256("res://scripts/native_obj_player.gd"),"normalization":"abs(elapsed-round(elapsed)) <= 1e-12 * max(1,abs(elapsed))","cases":cases}
 FileAccess.open("res://roundoff-guard-report.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("ROUNDOFF_GUARD ",JSON.stringify(report));quit(0 if ok else 2)
