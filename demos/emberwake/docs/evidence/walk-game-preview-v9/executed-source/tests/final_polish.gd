extends SceneTree
## Real file/menu rejection cases and simultaneous combat-HUD occupied regions.
## This case only writes the test-mode file and restores its prior bytes.
var world: Node2D
var checks := 0
var failures: Array[String] = []
var save_path := "user://emberwake-test-save.json"
var prior_save := PackedByteArray()
var had_prior_save := false

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)

func write_test_save(content: String) -> void:
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string(content)
	file.close()

func has_continue_button() -> bool:
	for button in world.hud.buttons:
		if button.text == "Continue journey":
			return true
	return false

func _run() -> void:
	had_prior_save = FileAccess.file_exists(save_path)
	if had_prior_save:
		prior_save = FileAccess.get_file_as_bytes(save_path)
	world = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	await process_frame
	check(world.test_mode and world._save_path() == save_path, "case cannot write the player's ordinary save")
	world._menu_action("new_confirmed")
	while world.mode == "dialogue":
		world._advance_dialogue()
	var valid_save: Dictionary = world._read_save()
	var valid_text := JSON.stringify(valid_save)
	var invalid_version: Dictionary = valid_save.duplicate(true)
	invalid_version.version = 99
	var invalid_checkpoint: Dictionary = valid_save.duplicate(true)
	invalid_checkpoint.checkpoint = "missing-ward"
	var inconsistent_progress: Dictionary = valid_save.duplicate(true)
	inconsistent_progress.won = true
	for invalid in ["{broken", JSON.stringify(invalid_version), JSON.stringify(invalid_checkpoint), JSON.stringify(inconsistent_progress)]:
		write_test_save(invalid)
		world._menu_action("title")
		check(world._read_save().is_empty(), "malformed or incompatible save is rejected")
		check(not world.hud.snapshot.has_save, "rejected save does not advertise Continue")
		check(not has_continue_button(), "title offers Begin rather than an unusable Continue")
	write_test_save(valid_text)
	world._menu_action("title")
	check(world.hud.snapshot.has_save and has_continue_button(), "valid file restores Continue on title entry")
	world.checkpoint = "crown"
	world._menu_action("continue")
	check(world.mode == "play" and world.checkpoint == "village", "Continue loads the actual valid checkpoint")
	world._menu_action("title")
	write_test_save("{}")
	# Frequent HUD/browser observation uses the last validated availability,
	# rather than opening and parsing the file on every screen update.
	for iteration in range(30):
		world._update_hud()
		world.get_debug_state()
	check(world.hud.snapshot.has_save, "HUD refreshes retain cached title availability")
	check(world.get_debug_state().save_valid, "diagnostics also use cached validation")
	world._menu_action("continue")
	check(world.mode == "title", "a save changed after title entry cannot start play")
	check(not world.hud.snapshot.has_save and not has_continue_button(), "stale Continue refreshes into a usable Begin menu")
	# Actual shrine encounter + actual bell interaction, together with the
	# introduction toast: this is the combination that obscured the Warden.
	world._menu_action("new_confirmed")
	while world.mode == "dialogue":
		world._advance_dialogue()
	world.wards.assign([true, true, true])
	world.hero.position = Vector2(1900, 520)
	world._check_encounters()
	if "--capture-polish" in OS.get_cmdline_user_args():
		await capture_shrine("boss-approach")
	world.hero.position = world.BELL_POSITION + Vector2(0, 65)
	world._update_interaction()
	world._update_hud()
	check(is_instance_valid(world.boss) and not world.hud.snapshot.boss.is_empty(), "actual encounter supplies the boss HUD")
	check(world.hud.snapshot.prompt == "Touch the bell", "actual bell proximity supplies a simultaneous interaction")
	var regions: Dictionary = world.hud.overlay_regions()
	check(regions.has("boss") and regions.has("interaction") and regions.has("notice"), "all simultaneous HUD regions are represented")
	var names: Array = regions.keys()
	var screen := Rect2(0, 0, 960, 540)
	for i in range(names.size()):
		var region: Rect2 = regions[names[i]]
		check(screen.encloses(region), "%s remains inside the logical viewport" % names[i])
		for j in range(i + 1, names.size()):
			check(not region.intersects(regions[names[j]]), "%s and %s are simultaneously readable" % [names[i], names[j]])
	check((regions.boss as Rect2).position.y >= 400, "boss HUD leaves the upper central combat arena visible")
	if "--capture-polish" in OS.get_cmdline_user_args():
		await capture_shrine("boss-bell-prompt")
	world.hud.notice_time = 0
	world.hud.snapshot.hint = "Watch the amber marks."
	regions = world.hud.overlay_regions()
	check(not (regions.boss as Rect2).intersects(regions.hint), "the hint replacement also stays clear of the boss bar")
	world._set_mode("play")
	# The rapid menu fixture creates overlapping UI/ward playbacks. Release
	# their streams while the players still exist, before freeing the world.
	for child in world.get_children():
		if child is AudioStreamPlayer:
			child.stop()
			child.stream = null
	await process_frame
	world.queue_free()
	await process_frame
	# Give stopped Ogg/audio playbacks time to release in native fixtures too.
	await create_timer(.35, true, false, true).timeout
	if had_prior_save:
		var file := FileAccess.open(save_path, FileAccess.WRITE)
		file.store_buffer(prior_save)
		file.close()
	else:
		DirAccess.remove_absolute(save_path)
	if failures.is_empty():
		print("FINAL_POLISH PASS: %d assertions" % checks)
		quit(0)
	else:
		for failure in failures:
			printerr(failure)
		quit(1)

func capture_shrine(name: String) -> void:
	# Optional arranged visual fixture; normal browser-play evidence is separate.
	world.actors.process_mode = Node.PROCESS_MODE_DISABLED
	world.camera.position = world.hero.position
	world._update_interaction()
	world._update_hud()
	DisplayServer.window_set_size(Vector2i(960, 540))
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://output")
	root.get_texture().get_image().save_png("res://output/final-polish-%s.png" % name)
