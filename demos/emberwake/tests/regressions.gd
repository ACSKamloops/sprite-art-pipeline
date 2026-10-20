extends SceneTree
## End-to-end Godot input dispatch, occlusion and quest-closure regressions.
var world: Node2D
var checks := 0
var failures: Array[String] = []
func _initialize() -> void:
	_run.call_deferred()
func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)
func key(code: int) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	var release := InputEventKey.new()
	release.keycode = code
	release.physical_keycode = code
	release.pressed = false
	Input.parse_input_event(release)
	await process_frame
func _run() -> void:
	world = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	await process_frame
	world._menu_action("new_confirmed")
	while world.mode == "dialogue": world._advance_dialogue()
	await process_frame
	for attempt in range(3):
		await key(KEY_ESCAPE)
		check(world.mode == "pause", "Esc opens journal")
		await key(KEY_ESCAPE)
		check(world.mode == "play", "Esc resumes")
		await key(KEY_SPACE)
		check(world.mode == "play", "Space never opens focused Journal")
		check(world.hero.cooldowns.dodge > 0.0, "Space reaches actual dodge input after modal use")
		await create_timer(0.9,true).timeout
	# The troublesome Moss approach from actual independent browser evidence.
	world.hero.position = Vector2(425,1023)
	await create_timer(0.3,true).timeout
	var faded := 0
	for prop in world.canopy_props:
		if float(prop.get_meta("canopy_fade",1.0)) < .9: faded += 1
	check(faded>0,"Moss approach occluders fade while hero is underneath")
	world.hero.position = Vector2(850,1070)
	await create_timer(0.3,true).timeout
	var hidden_foe: Node2D = world._spawn_enemy("scout",Vector2(425,1023),-1)
	await create_timer(0.3,true).timeout
	var foe_fade := 0
	for prop in world.canopy_props:
		if float(prop.get_meta("canopy_fade",1.0)) < .9: foe_fade += 1
	check(foe_fade>0,"nearby foes also keep occluding crowns transparent")
	hidden_foe.queue_free()
	world.wards.assign([true,true,true])
	world.boss_defeated = true
	world.won = true
	world.hero.position = world.NPC_POSITION + Vector2(0,40)
	world._interact()
	while world.mode == "dialogue": world._advance_dialogue()
	check(world.epilogue_seen,"return conversation completes epilogue")
	check(not world._objective().contains("Return"),"completed objective clears return request")
	check(world._goal().is_equal_approx(world.hero.position),"completed compass no longer directs to a completed objective")
	var saved: Dictionary=world._read_save()
	check(saved.get("epilogue_seen",false),"epilogue completion persists")
	world.epilogue_seen = false
	world._apply_save(saved)
	check(world.epilogue_seen,"Continue restores epilogue completion")
	world._new_game()
	check(not world.epilogue_seen and not world.won,"new journey resets closure")
	world._set_mode("play")
	world.queue_free()
	await process_frame
	await create_timer(.15,true,false,true).timeout
	if failures.is_empty():
		print("REGRESSIONS PASS: %d assertions"%checks)
		quit(0)
	else:
		for failure in failures: printerr(failure)
		quit(1)
