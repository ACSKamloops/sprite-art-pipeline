extends SceneTree
## godot --headless --path . --script tests/cast_charge_tracks.gd
## Add -- --production to also sample every actual bank's cast exposure.
## Synthetic fixture coordinates verify attachment behavior, not painted hands.

const HERO = preload("res://scripts/hero.gd")
const FX = preload("res://scripts/combat_fx.gd")
const VIEWS := ["south", "southeast", "east", "northeast", "north", "northwest", "west", "southwest"]
const ACTIONS := ["idle", "walk", "attack", "cast", "hurt", "dodge"]

class FixtureHero extends "res://scripts/hero.gd":
	var entries: Dictionary = {}
	var texture_reads := 0
	func _character_entry(id: String) -> Dictionary:
		return entries.get(id, {})
	func _read_texture(path: String) -> Texture2D:
		texture_reads += 1
		return super._read_texture(path)

var checks := 0
var failures: Array[String] = []
var fixture: Node2D
var fixture_dir: String
var bank: Dictionary
var actor: FixtureHero

func _initialize() -> void:
	_run.call_deferred()

func check(condition: bool, note: String) -> void:
	checks += 1
	if not condition:
		failures.append(note)
		printerr("CAST_CHARGE_TRACKS FAIL: " + note)

func write_json(path: String, value: Dictionary) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(value))
	file.close()

func add_bank(id: String, value: Dictionary) -> void:
	var path := fixture_dir + "/" + id + ".json"
	write_json(path, value)
	actor.entries[id] = {"manifest":path, "atlas":fixture_dir + "/SYNTHETIC-atlas.png"}

func projected(point: Array) -> Vector2:
	return actor.to_global((Vector2(point[0], point[1]) - actor._pivot) * actor._sprite.scale)

func build_fixture() -> void:
	fixture_dir = "user://cast-charge-track-fixture-" + ProjectSettings.globalize_path("res://").md5_text().left(10)
	DirAccess.make_dir_recursive_absolute(fixture_dir)
	var image := Image.create(256, 128, false, Image.FORMAT_RGBA8)
	image.fill(Color("516d8c"))
	image.save_png(fixture_dir + "/SYNTHETIC-atlas.png")
	bank = {"schema":"emberwake-animation/v1", "cell":[32,32], "pivot":[16,28], "columns":8, "draw_scale":1.25, "directions":VIEWS.duplicate(), "cast_hand":{}, "cast_release_index":3, "cast_hand_tracks":{"northeast":[[13,5],[17,7],[19,8],[24,9],[21,11],[13,5]]}, "animations":{}}
	for view in VIEWS:
		bank.cast_hand[view] = [24,9]
		for action in ACTIONS:
			bank.animations[view + "_" + action] = {"frames":[0], "holds":[.5], "loop":action in ["idle", "walk"]}
		# First and final exposures intentionally share cel 22.
		bank.animations[view + "_cast"] = {"frames":[22,23,24,25,26,22], "holds":[.06,.08,.1,.08,.08,.1], "loop":false}
	fixture = Node2D.new()
	root.add_child(fixture)
	actor = FixtureHero.new()
	add_bank("tracked", bank)
	actor.character_id = "tracked"
	fixture.add_child(actor)
	actor.set_physics_process(false)
	actor.set_process(false)
	actor.position = Vector2(90,120)
	actor.rotation = .15
	actor.scale = Vector2(1.1,.9)
	check(actor.art_ready, "synthetic tracked eight-view bank loads")

func charge_effect() -> Node2D:
	for child in fixture.get_children():
		if child.get_script() == FX and child.style == "cast_charge":
			return child
	return null

func test_displayed_exposures_and_fx() -> void:
	actor._set_aim(Vector2(1,-1))
	actor._update_animation(0)
	var release := actor.get_cast_hand_global()
	var points: Array = bank.cast_hand_tracks.northeast
	actor.request_action("firebolt")
	var charge := charge_effect()
	check(charge != null, "real request_action creates cast_charge FX")
	if charge == null:
		return
	charge.set_process(false)
	check(actor.current_art_clip == "northeast_idle", "request begins before cast display changes")
	check(actor.get_cast_charge_hand_global().is_equal_approx(projected(points[0])), "before cast display starts charge uses exposure zero")
	check((charge.global_position + charge.visual_offset).is_equal_approx(projected(points[0])), "real charge initialization uses preparation getter")
	check(actor.get_cast_hand_global().is_equal_approx(release), "fixed release getter remains independent of preparation")
	actor._state_time = .03
	actor._update_animation(0)
	check(actor.current_art_frame == 22, "early cast displays duplicate cel 22")
	charge._process(0)
	var first: Vector2 = charge.global_position + charge.visual_offset
	check(first.is_equal_approx(projected(points[0])), "real FX tracks first preparation point")
	actor._state_time = .10
	actor._update_animation(0)
	check(actor.current_art_frame == 23, "later preparation actually displays the second exposure")
	# Deliberately disagree with the state clock after rendering: attachment
	# must follow the displayed cel instead of independently estimating time.
	actor._state_time = .01
	actor.position += Vector2(11,4)
	charge._process(0)
	var second: Vector2 = charge.global_position + charge.visual_offset
	check(actor.facing == "northeast" and not second.is_equal_approx(first), "same facing has distinct charge positions across prep exposures")
	check(second.is_equal_approx(projected(points[1])), "real FX follows displayed frame and actor movement despite changed state clock")
	actor._state_time = .24
	actor._update_animation(0)
	check(actor.current_art_frame == 25, "unchanged .24 gameplay time selects authored release exposure")
	charge._process(0)
	check(actor.get_cast_charge_hand_global().is_equal_approx(actor.get_cast_hand_global()), "charge recovers fixed release socket at release")
	check((charge.global_position + charge.visual_offset).is_equal_approx(actor.get_cast_hand_global()), "real FX reaches fixed release point")
	actor._perform_action_hit("firebolt")
	var bolts := get_nodes_in_group("combat_projectiles")
	check(bolts.size() == 1, "release still creates exactly one projectile")
	if not bolts.is_empty():
		var bolt: Node2D = bolts[0]
		check(bolt.global_position == actor.global_position and bolt.damage == 33.0, "projectile physical source and damage remain unchanged")
		check((bolt.global_position + bolt.visual_offset).is_equal_approx(actor.get_cast_hand_global()) and bolt.direction.is_equal_approx(Vector2(1,-1).normalized()), "projectile retains fixed release socket and committed aim")
		bolt.free()
	for child in fixture.get_children():
		if child.get_script() == FX and child.style == "cast_flash":
			check((child.global_position + child.visual_offset).is_equal_approx(actor.get_cast_hand_global()), "release flash retains fixed release socket")
	actor._state_time = .49
	actor._update_animation(0)
	check(actor.current_art_frame == 22 and actor.get_cast_charge_hand_global().is_equal_approx(projected(points[0])), "final duplicate cel 22 shares the first exposure attachment")
	actor._pending_hit = ""
	charge._process(0)
	check(charge.is_queued_for_deletion(), "charge stops tracking after pending release is cleared")

func snapshot() -> Dictionary:
	return {"debug":actor.get_debug_state(), "texture":actor._sprite.texture, "scale":actor._sprite.scale, "offset":actor._sprite.offset, "region":actor._sprite.region_rect, "animations":actor._animations.duplicate(true), "directions":actor._directions.duplicate(), "cell":actor._cell, "pivot":actor._pivot, "columns":actor._columns, "hands":actor._cast_hands.duplicate(true), "tracks":actor._cast_hand_tracks.duplicate(true), "release":actor._cast_release_index, "aim":actor._aim, "action_aim":actor._action_aim, "left":actor._state_left, "time":actor._state_time, "animation_time":actor._animation_time, "pending":actor._pending_hit, "previous_clip":actor._previous_clip, "mask":actor.collision_mask}

func test_validation_is_atomic() -> void:
	actor._state_time = .10
	actor._pending_hit = "firebolt"
	actor._update_animation(0)
	actor.hp = 71
	actor.mana = 39
	actor.cooldowns.attack = .19
	var before := snapshot()
	var reads_before := actor.texture_reads
	for defect in ["tracks-array", "unknown-view", "short-track", "long-track", "track-object", "short-point", "long-point", "string-point", "null-point", "boolean-coordinate", "string-coordinate", "negative-x", "negative-y", "outside-x", "outside-y", "release-disagrees", "duplicate-disagrees"]:
		var broken: Dictionary = bank.duplicate(true)
		match defect:
			"tracks-array": broken.cast_hand_tracks = []
			"unknown-view": broken.cast_hand_tracks["northeest"] = broken.cast_hand_tracks.northeast.duplicate(true)
			"short-track": broken.cast_hand_tracks.northeast.pop_back()
			"long-track": broken.cast_hand_tracks.northeast.append([13,5])
			"track-object": broken.cast_hand_tracks.northeast = {"0":[13,5]}
			"short-point": broken.cast_hand_tracks.northeast[1] = [17]
			"long-point": broken.cast_hand_tracks.northeast[1] = [17,7,2]
			"string-point": broken.cast_hand_tracks.northeast[1] = "17,7"
			"null-point": broken.cast_hand_tracks.northeast[1] = null
			"boolean-coordinate": broken.cast_hand_tracks.northeast[1] = [true,7]
			"string-coordinate": broken.cast_hand_tracks.northeast[1] = ["17",7]
			"negative-x": broken.cast_hand_tracks.northeast[1] = [-.01,7]
			"negative-y": broken.cast_hand_tracks.northeast[1] = [17,-.01]
			"outside-x": broken.cast_hand_tracks.northeast[1] = [32,7]
			"outside-y": broken.cast_hand_tracks.northeast[1] = [17,32]
			"release-disagrees": broken.cast_hand_tracks.northeast[3] = [23,9]
			"duplicate-disagrees": broken.cast_hand_tracks.northeast[5] = [14,5]
		add_bank("rejected", broken)
		check(not actor.set_character("rejected"), "reject " + defect)
		check(actor.texture_reads == reads_before, "reject before resource load: " + defect)
		check(snapshot() == before, "invalid tracks preserve working bank and pending cast: " + defect)
	# JSON cannot normally encode nonfinite values. Test the validation boundary
	# directly, then also try overflowing numeric JSON through the real loader.
	for coordinate in [INF, -INF, NAN]:
		var tracks: Dictionary = bank.cast_hand_tracks.duplicate(true)
		tracks.northeast[1] = [coordinate,7]
		check(not actor._valid_cast_hand_tracks(tracks, bank.cast_hand, bank.cast_release_index, bank.animations, VIEWS, bank.cell), "reject nonfinite native coordinate")
	var path := fixture_dir + "/overflow.json"
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(bank).replace("[17,7]", "[1e999,7]"))
	file.close()
	actor.entries.overflow = {"manifest":path, "atlas":fixture_dir + "/SYNTHETIC-atlas.png"}
	check(not actor.set_character("overflow"), "real loader rejects overflowing JSON coordinate")
	check(actor.texture_reads == reads_before and snapshot() == before, "nonfinite manifest preserves bank before any texture read")

func test_fallbacks() -> void:
	actor._set_aim(Vector2.DOWN)
	actor._update_animation(0)
	check(actor.get_cast_charge_hand_global().is_equal_approx(actor.get_cast_hand_global()), "undeclared view in partial track bank uses fixed release fallback")
	var per_view: Dictionary = bank.duplicate(true)
	per_view.cast_release_index = {}
	for view in VIEWS:
		per_view.cast_release_index[view] = 3
	add_bank("per-view", per_view)
	check(actor.set_character("per-view"), "tracks also accept per-view release indices")
	var legacy: Dictionary = bank.duplicate(true)
	legacy.erase("directions")
	legacy.erase("cast_hand_tracks")
	add_bank("legacy", legacy)
	check(actor.set_character("legacy") and actor._cast_hand_tracks.is_empty(), "legacy four-view selection clears previous tracks")
	actor._set_aim(Vector2.RIGHT)
	actor._update_animation(0)
	check(actor.get_cast_charge_hand_global().is_equal_approx(actor.get_cast_hand_global()), "legacy four-view getter keeps fixed release fallback")
	actor._set_state("idle")
	actor.cooldowns.nova = 0
	actor.request_action("nova")
	var charge := charge_effect()
	check(charge != null, "legacy nova still creates actual charge")
	if charge != null:
		charge.set_process(false)
		charge._process(0)
		check((charge.global_position + charge.visual_offset).is_equal_approx(actor.get_cast_hand_global()), "legacy actual charge FX uses fixed socket fallback")

func test_production_tracks() -> void:
	var production_actor := HERO.new()
	fixture.add_child(production_actor)
	production_actor.set_physics_process(false)
	production_actor.set_process(false)
	for id in ["rowan", "lyra", "brann"]:
		var loaded := production_actor.set_character(id)
		check(loaded and production_actor._directions == VIEWS, id + " actual eight-view bank loads")
		if not loaded or production_actor._directions != VIEWS:
			continue
		var entry := production_actor._character_entry(id)
		print("CAST_CHARGE_TRACKS production %s manifest_sha256=%s atlas_sha256=%s" % [id, FileAccess.get_sha256(entry.manifest), FileAccess.get_sha256(entry.atlas)])
		for view in VIEWS:
			if view in ["southeast", "northeast", "northwest", "southwest"]:
				check(production_actor._cast_hand_tracks.has(view), id + " actual diagonal declares track: " + view)
			production_actor.facing = view
			production_actor._set_state("cast")
			production_actor._previous_clip = ""
			production_actor._update_animation(0)
			var clip: Dictionary = production_actor._animations[view + "_cast"]
			var elapsed := 0.0
			for index in clip.frames.size():
				production_actor._animation_time = elapsed + float(clip.holds[index]) * .5
				production_actor._update_animation(0)
				var expected := production_actor.get_cast_hand_global()
				if production_actor._cast_hand_tracks.has(view):
					var point: Array = production_actor._cast_hand_tracks[view][index]
					expected = production_actor.to_global((Vector2(point[0], point[1]) - production_actor._pivot) * production_actor._sprite.scale)
				check(production_actor.current_art_frame == int(clip.frames[index]) and production_actor.get_cast_charge_hand_global().is_equal_approx(expected), "%s %s actual exposure %d projects declared charge point" % [id,view,index])
				elapsed += float(clip.holds[index])

func _run() -> void:
	build_fixture()
	test_displayed_exposures_and_fx()
	test_validation_is_atomic()
	# Flush the completed firebolt charge before finding the legacy nova FX.
	await process_frame
	test_fallbacks()
	if "--production" in OS.get_cmdline_user_args():
		test_production_tracks()
	fixture.queue_free()
	await process_frame
	# Let Godot's audio mixer retire playback references after fixture removal.
	await create_timer(.35, true, false, true).timeout
	print("CAST_CHARGE_TRACKS %s: %d assertions; synthetic coordinates do not certify painted anatomy" % ["PASS" if failures.is_empty() else "FAIL", checks])
	quit(0 if failures.is_empty() else 1)
