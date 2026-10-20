extends SceneTree
## UI/save contract fixture. Extra entries deliberately reuse Rowan's art here;
## this is never evidence for the real Lyra/Brann assets or their art quality.
class SelectionHero extends CharacterBody2D:
	var character_id := "rowan"
	var input_enabled := false
	var hp := 100.0
	var max_hp := 100.0
	var mana := 60.0
	var max_mana := 60.0
	var state := "idle"
	var fail_selection := false
	func set_character(id: String) -> bool:
		if fail_selection or id not in ["rowan", "lyra", "brann"]:
			return false
		character_id = id
		return true
	func reset_at(at: Vector2) -> void:
		position = at
		hp = max_hp
		mana = max_mana
		state = "idle"
	func get_debug_state() -> Dictionary:
		return {"character": character_id}

var world: Node2D
var checks := 0
var failures: Array[String] = []
var save_path := "user://emberwake-test-save.json"
var prior := PackedByteArray()
var had_save := false

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)

func button(action: String) -> Button:
	for control in world.hud.buttons:
		if control.get_meta("action", "") == action:
			return control
	return null

func write_save(data: Dictionary) -> void:
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()

func key(code: int) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)
		await process_frame

func click(control: Button) -> void:
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = root.get_final_transform() * control.get_global_rect().get_center()
		event.global_position = event.position
		event.pressed = pressed
		Input.parse_input_event(event)
		await process_frame

func _run() -> void:
	had_save = FileAccess.file_exists(save_path)
	if had_save:
		prior = FileAccess.get_file_as_bytes(save_path)
	world = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	await process_frame
	check(world.test_mode, "isolated test save selected")
	check(not world._character_data("rowan").is_empty(), "original character remains available with or without catalog")
	var original: CharacterBody2D = world.hero
	original.process_mode = Node.PROCESS_MODE_DISABLED
	var fixture := SelectionHero.new()
	fixture.position = world.START
	world.actors.add_child(fixture)
	world.hero = fixture
	world.character_catalog.clear()
	for id in ["rowan", "lyra", "brann"]:
		world.character_catalog.append({"id": id, "name": id.capitalize(), "subtitle": "Selection contract fixture", "description": "Fixture art only. Not a new character review.", "atlas": "res://assets/hero/atlas.png", "manifest": "res://assets/hero/animations.json"})
	world._menu_action("title")
	check(is_instance_valid(button("characters")), "title exposes character gallery")
	await click(button("characters"))
	check(world.mode == "characters" and paused, "title gallery is modal and paused")
	check(button("character_select:rowan").has_focus(), "selected card receives keyboard focus")
	await click(button("character_select:lyra"))
	check(world._character_choice == "lyra", "clickable card changes draft")
	check(button("character_select:lyra").has_focus(), "focus follows selected card after rebuild")
	await key(KEY_TAB)
	check(button("character_select:brann").has_focus(), "Tab moves between character card buttons")
	await key(KEY_ENTER)
	check(world._character_choice == "brann", "Enter selects the focused card through real GUI input")
	await click(button("character_select:lyra"))
	await click(button("character_apply"))
	check(world.mode == "title" and world.selected_character_id == "lyra", "title applies next-journey selection")
	check(fixture.character_id == "rowan", "title choice leaves live/current-save character alone")
	world._menu_action("new_confirmed")
	while world.mode == "dialogue":
		world._advance_dialogue()
	check(fixture.character_id == "lyra", "new journey applies selected character before reset")
	check(world._read_save().character_id == "lyra", "new character saved with checkpoint")
	check(button("pause_open").focus_mode == Control.FOCUS_NONE, "play Journal cannot consume Space dodge")
	var saved: Dictionary = world._read_save()
	world._menu_action("title")
	world._menu_action("characters")
	world._menu_action("character_select:brann")
	world._menu_action("character_apply")
	check(world.selected_character_id == "brann", "different next-journey choice accepted")
	check(world._read_save().character_id == "lyra", "previewing another character never rewrites current save")
	world._menu_action("continue")
	check(world.mode == "play" and fixture.character_id == "lyra", "Continue restores saved character, overriding pending title choice")
	check(world.selected_character_id == "lyra", "selection reflects restored character")
	var legacy: Dictionary = saved.duplicate(true)
	legacy.erase("character_id")
	write_save(legacy)
	check(world._read_save().character_id == "rowan", "legacy version-one saves default to Rowan")
	world._apply_save(world._read_save())
	check(fixture.character_id == "rowan", "legacy Continue applies original art")
	for invalid in ["retired-character", 9, null, {}, []]:
		var unknown: Dictionary = saved.duplicate(true)
		unknown.character_id = invalid
		write_save(unknown)
		check(world._read_save().character_id == "rowan", "invalid selection falls back without destroying valid progress")
	write_save(saved)
	world._apply_save(saved)
	world._menu_action("pause_open")
	check(not button("characters").disabled, "safe paused journey can change character")
	fixture.hp = 51
	fixture.mana = 13
	var position_before := fixture.position
	button("characters").pressed.emit()
	world._menu_action("character_select:brann")
	await key(KEY_ESCAPE)
	check(world.mode == "pause" and fixture.character_id == "lyra", "Back cancels staged pause choice")
	world._menu_action("characters")
	check(world._character_choice == "lyra", "opening pause gallery starts from actual live character")
	world._menu_action("character_select:brann")
	world._menu_action("character_apply")
	check(world.mode == "pause" and paused and fixture.character_id == "brann", "safe apply swaps character without unpausing combat")
	check(fixture.hp == 51 and fixture.mana == 13 and fixture.position == position_before, "appearance change cannot heal/refill/teleport")
	check(world._read_save().character_id == "brann", "safe switch persists with current checkpoint")
	fixture.state = "cast"
	world._set_mode("pause")
	check(button("characters").disabled, "pending cast cannot be cancelled by character switching")
	world._menu_action("characters")
	check(world.mode == "pause", "direct switch request also rejects committed action")
	fixture.state = "idle"
	var enemy := CharacterBody2D.new()
	enemy.set_script(load("res://scripts/enemy.gd"))
	enemy.target = fixture
	enemy.position = fixture.position + Vector2(100, 0)
	world.actors.add_child(enemy)
	world._set_mode("pause")
	check(button("characters").disabled, "nearby living foe blocks swapping")
	enemy.remove_from_group("foes")
	enemy.queue_free()
	var projectile := Node2D.new()
	world.actors.add_child(projectile)
	projectile.add_to_group("combat_projectiles")
	check(not world._character_switch_reason().is_empty(), "in-flight spell blocks swapping")
	projectile.remove_from_group("combat_projectiles")
	projectile.queue_free()
	world._set_mode("pause")
	world._menu_action("characters")
	world._menu_action("character_select:rowan")
	fixture.fail_selection = true
	var saved_before := FileAccess.get_file_as_string(save_path)
	world._menu_action("character_apply")
	check(world.mode == "characters" and fixture.character_id == "brann", "failed art load keeps old character and gallery")
	check(FileAccess.get_file_as_string(save_path) == saved_before, "failed art load leaves saved journey untouched")
	check(not world.hud.snapshot.character_error.is_empty(), "failure gives visible gallery message")
	fixture.fail_selection = false
	world._menu_action("character_cancel")
	world._menu_action("title")
	world._menu_action("new")
	check(world.mode == "confirm" and world._read_save().character_id == "brann", "new journey still requires explicit save overwrite confirmation")
	var state: Dictionary = world.get_debug_state()
	check(state.selected_character == "brann" and state.live_character == "brann" and state.character_count == 3, "diagnostics distinguish selected and live character IDs")
	if "--capture-character-ui" in OS.get_cmdline_user_args():
		world._menu_action("title")
		await capture("title-fixture")
		world._menu_action("characters")
		await capture("gallery-fixture")
	world._set_mode("play")
	world.queue_free()
	await process_frame
	await create_timer(.35, true, false, true).timeout
	if had_save:
		var file := FileAccess.open(save_path, FileAccess.WRITE)
		file.store_buffer(prior)
		file.close()
	else:
		DirAccess.remove_absolute(save_path)
	if failures.is_empty():
		print("CHARACTER_SELECTION PASS: %d assertions; UI contract fixture, not character art quality" % checks)
		quit(0)
	else:
		for failure in failures:
			printerr("CHARACTER_SELECTION FAIL: " + failure)
		quit(1)

func capture(name: String) -> void:
	DisplayServer.window_set_size(Vector2i(960, 540))
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://output/character-ui")
	root.get_texture().get_image().save_png("res://output/character-ui/%s.png" % name)
