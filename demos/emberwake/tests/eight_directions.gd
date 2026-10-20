extends SceneTree
## godot --headless --path . --script tests/eight_directions.gd -- --test-mode
## Add --production to REQUIRE Rowan/Lyra/Brann's actual eight-direction banks.
## Default mode uses synthetic, explicitly named fixture pixels for mechanics;
## it never certifies production diagonal artwork or visual quality.

const HERO = preload("res://scripts/hero.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
const VIEWS := ["south", "southeast", "east", "northeast", "north", "northwest", "west", "southwest"]
const ACTIONS := ["idle", "walk", "attack", "cast", "hurt", "dodge"]
const COUNTS := [2, 8, 8, 6, 3, 5]
const HOLDS := [[.58,.58], [.05625,.05625,.05625,.05625,.05625,.05625,.05625,.05625], [.06,.07,.055,.055,.065,.035,.035,.035], [.06,.08,.1,.08,.08,.1], [.09,.1,.1], [.045,.105,.055,.0275,.0275]]
const EVIDENCE := "res://docs/evidence/eight-directions-systems"

class FixtureHero extends "res://scripts/hero.gd":
	var entries: Dictionary = {}
	func _character_entry(id: String) -> Dictionary:
		if entries.has(id):
			return entries[id]
		return super._character_entry(id)

class Target extends Node2D:
	var hp := 100.0
	var body_radius := 6.0
	var hits := 0
	func take_damage(amount: float, _source: Vector2) -> bool:
		hp -= amount
		hits += 1
		return true

var checks := 0
var failures: Array[String] = []
var fixture: Node2D
var bank: Dictionary
var entries: Dictionary
var fixture_dir: String
var receipts: Array[Dictionary] = []
var production := false

func _initialize() -> void:
	production = "--production" in OS.get_cmdline_user_args()
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)
		printerr("EIGHT_DIRECTIONS FAIL: " + note)

func vector(index: int) -> Vector2:
	return Vector2(sin(index * PI / 4.0), cos(index * PI / 4.0)).normalized()

func write_json(path: String, data: Dictionary) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()

func build_fixture() -> void:
	fixture_dir = "user://eight-direction-logic-fixture-" + ProjectSettings.globalize_path("res://").md5_text().left(10)
	DirAccess.make_dir_recursive_absolute(fixture_dir)
	bank = {"schema":"emberwake-animation/v1", "cell":[32,32], "pivot":[16,28], "columns":16, "draw_scale":1.0, "directions":VIEWS.duplicate(), "cast_hand":{}, "cast_release_index":{}, "animations":{}, "fixture_only":"Synthetic direction/action colors; not production hero artwork."}
	var image := Image.create(512,512,false,Image.FORMAT_RGBA8)
	var cell := 0
	for direction in VIEWS.size():
		var view: String = VIEWS[direction]
		bank.cast_hand[view] = [20 + direction % 3, 8 + direction]
		bank.cast_release_index[view] = 3
		for action_index in ACTIONS.size():
			var frames: Array = []
			for pose in COUNTS[action_index]:
				frames.append(cell)
				image.fill_rect(Rect2i((cell % 16)*32,(cell / 16)*32,32,32),Color.from_hsv(direction/8.0,.35 + .08*action_index,.55 + .04*pose,1))
				cell += 1
			bank.animations[view + "_" + ACTIONS[action_index]] = {"frames":frames,"holds":HOLDS[action_index].duplicate(),"loop":action_index < 2}
	var atlas := fixture_dir + "/SYNTHETIC-logic-fixture-atlas.png"
	image.save_png(atlas)
	var manifest := fixture_dir + "/SYNTHETIC-eight-direction-manifest.json"
	write_json(manifest,bank)
	entries = {"fixture-eight":{"manifest":manifest,"atlas":atlas}}
	var legacy: Dictionary = bank.duplicate(true)
	legacy.erase("directions")
	legacy.erase("cast_release_index")
	legacy.cast_hand = {"south":[20,8],"east":[20,8],"north":[20,8],"west":[20,8]}
	var legacy_path := fixture_dir + "/SYNTHETIC-legacy-four-manifest.json"
	write_json(legacy_path,legacy)
	entries["fixture-four"] = {"manifest":legacy_path,"atlas":atlas}

func fresh() -> void:
	for action in ["move_left","move_right","move_up","move_down"]:
		Input.action_release(action)
	keys([])
	if is_instance_valid(fixture):
		fixture.free()
	fixture = Node2D.new()
	root.add_child(fixture)

func hero(eight: bool = true) -> FixtureHero:
	var actor := FixtureHero.new()
	actor.entries = entries.duplicate(true)
	actor.character_id = "fixture-eight" if eight else "fixture-four"
	fixture.add_child(actor)
	check(actor.art_ready, "synthetic fixture art loads without a production alias")
	return actor

func target(at: Vector2) -> Target:
	var foe := Target.new()
	foe.position = at
	fixture.add_child(foe)
	foe.add_to_group("foes")
	return foe

func wall(at: Vector2, rotation_radians: float = 0.0) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = at
	body.rotation = rotation_radians
	var shape := RectangleShape2D.new()
	shape.size = Vector2(4,160)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	body.add_child(collider)
	fixture.add_child(body)

func keys(held: Array) -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = code in held
		Input.parse_input_event(event)
	Input.flush_buffered_events()

func ticks(count: int) -> void:
	for tick in count:
		await physics_frame

func advance(seconds: float) -> void:
	await create_timer(seconds,false,true).timeout

func _run() -> void:
	build_fixture()
	await test_input_and_sectors()
	await test_turning_animation_clock()
	await test_movement_and_dodge()
	await test_locked_actions_and_hits()
	await test_diagonal_walls_and_projectiles()
	await test_atomic_bank_validation()
	await test_pause_and_legacy_save()
	if production:
		await test_production_banks()
	fresh()
	fixture.queue_free()
	await process_frame
	await create_timer(.35,true,false,true).timeout
	DirAccess.make_dir_recursive_absolute(EVIDENCE)
	var path := EVIDENCE + ("/production-checks.json" if production else "/fixture-checks.json")
	write_json(path,{"checks":checks,"failures":failures,"production_required":production,"receipts":receipts,"scope":"Engine mechanics and manifest validation only. Synthetic fixture passes do not verify production diagonal frames, hand artwork, appearance or motion quality."})
	if failures.is_empty():
		print("EIGHT_DIRECTIONS PASS: %d assertions; production_required=%s; synthetic fixture is not an art review" % [checks,production])
		quit(0)
	else:
		quit(1)

func test_input_and_sectors() -> void:
	fresh()
	var actor := hero()
	actor.set_physics_process(false)
	keys([KEY_W,KEY_D])
	await process_frame
	check(actor._read_movement().is_equal_approx(Vector2(1,-1).normalized()), "actual W+D input produces a normalized northeast vector")
	actor._set_aim(actor._read_movement())
	check(actor.facing == "northeast" and actor._aim.is_equal_approx(vector(3)), "W+D selects northeast facing and combat aim")
	keys([])
	await process_frame
	for index in VIEWS.size():
		actor._set_aim(vector(index))
		check(actor.facing == VIEWS[index] and actor._aim.is_equal_approx(vector(index)), "eight-sector center " + VIEWS[index])
		actor._set_aim(Vector2.ZERO)
		check(actor.facing == VIEWS[index] and actor._aim.is_equal_approx(vector(index)), "zero analog input retains " + VIEWS[index])
		for side in [-1,1]:
			var angle: float = index*PI/4.0 + PI/8.0 + side*.0001
			actor._set_aim(Vector2(sin(angle),cos(angle)))
			var expected: String = VIEWS[index if side < 0 else (index+1)%8]
			check(actor.facing == expected, "sector boundary %s side %d" % [VIEWS[index],side])
	actor._set_aim(Vector2(.12,-.4))
	check(actor.facing == "north" and actor._aim.is_equal_approx(Vector2.UP), "analog combat snaps to a view while movement remains analog")
	var legacy := hero(false)
	legacy.set_physics_process(false)
	legacy._set_aim(Vector2(1,-1))
	check(legacy.facing == "north" and legacy._aim.is_equal_approx(Vector2(1,-1).normalized()), "missing directions preserves legacy four-view presentation and free-angle aim")
	legacy._set_aim(Vector2.ZERO)
	check(legacy.facing == "north" and legacy._aim.is_equal_approx(Vector2(1,-1).normalized()), "legacy zero also retains useful aim")
	check(actor.set_character("fixture-four"), "switch from eight to a legacy bank succeeds")
	check(actor.facing in HERO.FOUR_DIRECTIONS, "switching banks selects a facing actually provided by that bank")

func test_turning_animation_clock() -> void:
	fresh()
	var actor := hero()
	actor.set_physics_process(false)
	actor.set_process(false)
	actor._set_state("walk")
	actor._set_aim(vector(0))
	actor._update_animation(0)
	actor._update_animation(.19)
	check(actor.current_art_frame == int(bank.animations.south_walk.frames[3]), "walk reaches a nonzero authored gait phase")
	actor._set_aim(vector(1))
	actor._update_animation(0)
	check(is_equal_approx(actor._animation_time,.19) and actor.current_art_frame == int(bank.animations.southeast_walk.frames[3]), "turn while walking retains the corresponding loop phase")
	actor._set_aim(vector(2))
	actor._update_animation(.02)
	check(is_equal_approx(actor._animation_time,.21), "a second walking turn advances its phase normally")
	actor.request_action("attack")
	actor._update_animation(0)
	check(actor.current_art_frame == int(bank.animations.east_attack.frames[0]) and actor._animation_time == 0, "walk to attack resets the action's animation clock")
	actor._set_state("idle")
	actor._update_animation(0)
	actor._update_animation(.7)
	actor._set_aim(vector(3))
	actor._update_animation(0)
	check(is_equal_approx(actor._animation_time,.7) and actor.current_art_frame == int(bank.animations.northeast_idle.frames[1]), "idle facing change also retains the breathing loop phase")

func travel(held: Array) -> Vector2:
	fresh()
	var actor := hero()
	keys(held)
	await ticks(5)
	var start := actor.position
	await ticks(30)
	var moved := actor.position-start
	check(actor.velocity.length() <= HERO.MOVE_SPEED + .001, "movement cannot exceed the nominal speed")
	keys([])
	await process_frame
	return moved

func test_movement_and_dodge() -> void:
	var straight: Vector2 = await travel([KEY_D])
	var diagonal: Vector2 = await travel([KEY_W,KEY_D])
	check(absf(straight.length()-diagonal.length()) < .1, "diagonal and cardinal travel cover the same distance in equal physics ticks")
	check(absf(diagonal.x+diagonal.y) < .01, "actual diagonal path has equal x/y displacement")
	fresh()
	var actor := hero()
	keys([KEY_W,KEY_D])
	await process_frame
	actor.request_action("dodge")
	check(actor.facing == "northeast" and actor._dodge_aim.is_equal_approx(vector(3)), "diagonal dodge direction matches facing and unit movement")
	check(is_equal_approx(actor._state_left,.26) and actor.collision_mask == 1, "dodge keeps its .26-second clock and wall-only collision mask")
	keys([])
	await advance(.12)
	check(actor.position.x > 20 and actor.position.y < -20 and absf(actor.position.x+actor.position.y) < .1, "released diagonal dodge travels continuously along its locked vector")
	await advance(.20)
	check(actor.state == "idle" and actor.collision_mask == HERO.BODY_MASK, "dodge recovery restores actor collisions")
	fresh()
	actor = hero()
	wall(vector(3)*40,-PI/4)
	await ticks(2)
	keys([KEY_W,KEY_D])
	actor.request_action("dodge")
	keys([])
	await advance(.32)
	check(actor.position.dot(vector(3)) < 29, "diagonal dodge collides with a diagonal wall")
	check(actor._dodge_aim.is_equal_approx(vector(3)) and actor.facing == "northeast", "wall contact retains the committed diagonal dodge direction")

func test_locked_actions_and_hits() -> void:
	for action in ["attack","firebolt","nova"]:
		fresh()
		var actor := hero()
		var ahead := target(vector(3)*52)
		var behind := target(-vector(3)*52)
		keys([KEY_W,KEY_D])
		actor.request_action(action)
		var duration := .41 if action == "attack" else .50
		var release := .16 if action == "attack" else .24
		check(actor.facing == "northeast" and actor._action_aim.is_equal_approx(vector(3)), action + " commits northeast aim")
		check(is_equal_approx(actor._state_left,duration) and is_equal_approx(actor._hit_delay,release), action + " preserves gameplay clocks")
		keys([KEY_S,KEY_A])
		await advance(.08)
		check(actor.facing == "northeast" and actor._action_aim.is_equal_approx(vector(3)), action + " cannot swivel during windup")
		check(ahead.hp == 100 and behind.hp == 100 and actor._pending_hit == action, action + " has no early release")
		keys([])
		await advance(release-.08+.025)
		check(actor._pending_hit.is_empty(), action + " releases its pending diagonal hit once")
		check(actor.facing == "northeast" and actor._action_aim.is_equal_approx(vector(3)), action + " keeps facing and aim through recovery")
		if action == "attack":
			check(ahead.hits == 1 and behind.hits == 0, "diagonal melee damages only the forward cone target")
		elif action == "firebolt":
			var bolts := get_nodes_in_group("combat_projectiles")
			check(bolts.size() == 1, "diagonal firebolt releases exactly one projectile")
			if not bolts.is_empty():
				check(bolts[0].direction.is_equal_approx(vector(3)), "diagonal firebolt keeps its committed northeast direction")
		else:
			check(ahead.hits == 1 and behind.hits == 1, "diagonal nova preserves its radial damage behavior")
		await advance(maxf(.001,actor._state_left-.08))
		keys([KEY_S,KEY_A])
		await ticks(1)
		check(actor.facing == "northeast" and actor._action_aim.is_equal_approx(vector(3)), action + " stays locked through the end of recovery")
		keys([])
		await advance(.08)
		check(ahead.hits == 1, action + " does not duplicate damage during recovery")
		check(actor.state == "idle" and actor.facing == "northeast", action + " returns to idle retaining released diagonal facing")
	fresh()
	var buffered_actor := hero()
	keys([KEY_W,KEY_D])
	buffered_actor.request_action("attack")
	await advance(.28)
	keys([KEY_S,KEY_A])
	buffered_actor.request_action("firebolt")
	check(buffered_actor.facing == "northeast" and buffered_actor._pending_action == "firebolt", "buffering an opposite diagonal cast cannot turn the committed punch")
	await advance(.15)
	check(buffered_actor.state == "cast" and buffered_actor.facing == "southwest" and buffered_actor._action_aim.is_equal_approx(vector(7)), "buffered cast acquires the new diagonal only after punch recovery")
	keys([])
	# Test the central target, then include targets that distinguish the broad
	# diagonal cone from either accidental cardinal selection.
	fresh()
	var actor := hero()
	var diagonal_only := target(vector(3)*60)
	actor._set_aim(vector(3))
	actor.request_action("attack")
	await advance(.20)
	check(diagonal_only.hits == 1, "diagonal attack hits the diagonal target")
	# Boundaries behind one cardinal side distinguish the committed diagonal
	# cone from accidental north-only or east-only direction selection.
	fresh()
	actor = hero()
	var north_only := target(Vector2(-44,-36))
	var east_only := target(Vector2(36,44))
	var northeast := target(vector(3)*60)
	actor._set_aim(vector(3))
	actor.request_action("attack")
	await advance(.20)
	check(northeast.hits == 1 and north_only.hits == 0 and east_only.hits == 0, "diagonal cone rejects targets an erroneous cardinal aim would hit")

func test_diagonal_walls_and_projectiles() -> void:
	fresh()
	var actor := hero()
	var blocked := target(vector(3)*60)
	wall(vector(3)*30,-PI/4)
	await ticks(2)
	actor._set_aim(vector(3))
	actor.request_action("attack")
	await advance(.20)
	check(blocked.hits == 0, "diagonal wall blocks the committed melee ray")
	fresh()
	actor = hero()
	actor._set_aim(vector(3))
	blocked = target(vector(3)*110)
	wall(vector(3)*8,-PI/4)
	await ticks(2)
	actor.request_action("firebolt")
	await advance(.50)
	check(blocked.hits == 0 and get_nodes_in_group("combat_projectiles").is_empty(), "hand projection cannot skip a close diagonal wall")
	fresh()
	var victim := target(vector(3)*100)
	var bolt := PROJECTILE.new()
	bolt.direction = Vector2(1,-1)
	bolt.speed = 9000
	bolt.damage = 7
	bolt.visual_offset = Vector2(80,-80)
	fixture.add_child(bolt)
	await advance(.05)
	check(victim.hp == 93 and victim.hits == 1, "swept collision catches a diagonal target at extreme speed independently of visual hand offset")

func snapshot(actor: Node) -> Dictionary:
	return {"debug":actor.get_debug_state(),"texture":actor._sprite.texture,"scale":actor._sprite.scale,"offset":actor._sprite.offset,"region":actor._sprite.region_rect,"animations":actor._animations.duplicate(true),"cell":actor._cell,"pivot":actor._pivot,"columns":actor._columns,"hands":actor._cast_hands.duplicate(true),"release_index":actor._cast_release_index,"aim":actor._aim,"action_aim":actor._action_aim,"left":actor._state_left,"time":actor._state_time,"animation_time":actor._animation_time,"pending_hit":actor._pending_hit,"previous_clip":actor._previous_clip,"mask":actor.collision_mask}

func test_atomic_bank_validation() -> void:
	fresh()
	var actor := hero()
	actor.set_physics_process(false)
	actor.set_process(false)
	actor._set_aim(vector(5))
	actor.hp = 71
	actor.request_action("firebolt")
	actor._state_time = .12
	actor._update_animation(0)
	var before := snapshot(actor)
	var cases: Array[Dictionary] = []
	var broken: Dictionary = bank.duplicate(true)
	broken.animations.erase("southwest_hurt")
	cases.append({"note":"missing diagonal action","bank":broken})
	broken = bank.duplicate(true)
	broken.directions = ["south","east","north","west","southwest"]
	cases.append({"note":"incomplete direction declaration","bank":broken})
	broken = bank.duplicate(true)
	broken.cast_hand.erase("northwest")
	cases.append({"note":"missing diagonal hand socket","bank":broken})
	broken = bank.duplicate(true)
	broken.cast_hand.northeast = [33,8]
	cases.append({"note":"out-of-cell hand socket","bank":broken})
	broken = bank.duplicate(true)
	broken.cast_release_index.erase("southwest")
	cases.append({"note":"missing per-view release index","bank":broken})
	broken = bank.duplicate(true)
	broken.cast_release_index.northeast = 6
	cases.append({"note":"out-of-range release index","bank":broken})
	for defect in ["empty","fractional","negative","outside","short-holds","zero-hold","bad-hold","missing-loop","wrong-loop","wrong-type-loop"]:
		broken = bank.duplicate(true)
		var clip: Dictionary = broken.animations.northeast_attack
		match defect:
			"empty": clip.frames = []
			"fractional": clip.frames[0] = 2.5
			"negative": clip.frames[0] = -1
			"outside": clip.frames[0] = 256
			"short-holds": clip.holds.pop_back()
			"zero-hold": clip.holds[0] = 0
			"bad-hold": clip.holds[0] = "0.1"
			"missing-loop": clip.erase("loop")
			"wrong-loop": clip.loop = true
			"wrong-type-loop": clip.loop = 0
		cases.append({"note":defect,"bank":broken})
	for defect in ["numeric-string-cell","fractional-cell","zero-scale","fractional-columns","bad-pivot","numeric-string-frame","boolean-hold"]:
		broken = bank.duplicate(true)
		match defect:
			"numeric-string-cell": broken.cell[0] = "32"
			"fractional-cell": broken.cell[0] = 32.5
			"zero-scale": broken.draw_scale = 0
			"fractional-columns": broken.columns = 15.5
			"bad-pivot": broken.pivot[0] = null
			"numeric-string-frame": broken.animations.northwest_cast.frames[0] = "9"
			"boolean-hold": broken.animations.southwest_idle.holds[0] = true
		cases.append({"note":defect,"bank":broken})
	for invalid in cases:
		var path := fixture_dir + "/SYNTHETIC-rejected-bank.json"
		write_json(path,invalid.bank)
		actor.entries["fixture-rejected"] = {"manifest":path,"atlas":entries["fixture-eight"].atlas}
		check(not actor.set_character("fixture-rejected"), "reject malformed bank: " + invalid.note)
		check(snapshot(actor) == before, "failed bank is atomic during a pending cast: " + invalid.note)
	broken = bank.duplicate(true)
	broken.animations.northeast_walk.holds[0] = .005
	var short_path := fixture_dir + "/SYNTHETIC-short-positive-hold.json"
	write_json(short_path,broken)
	actor.entries["fixture-short"] = {"manifest":short_path,"atlas":entries["fixture-eight"].atlas}
	check(actor.set_character("fixture-short"), "positive sub-15ms authored holds remain valid")
	actor._set_state("walk")
	actor._set_aim(vector(3))
	actor._previous_clip = ""
	actor._update_animation(0)
	actor._update_animation(.006)
	check(actor.current_art_frame == int(broken.animations.northeast_walk.frames[1]), "playback honors the actual hold instead of imposing a hidden minimum")

func test_pause_and_legacy_save() -> void:
	fresh()
	var actor := hero()
	actor._set_aim(vector(7))
	actor.request_action("firebolt")
	await advance(.08)
	var before := snapshot(actor)
	paused = true
	await create_timer(.12,true,false,true).timeout
	check(snapshot(actor) == before, "pause freezes diagonal facing, pending release, action, animation, mana and cooldowns")
	paused = false
	await advance(.20)
	var bolts := get_nodes_in_group("combat_projectiles")
	check(bolts.size() == 1 and bolts[0].direction.is_equal_approx(vector(7)), "resume releases one southwest projectile without losing the committed aim")
	fresh()
	# Exercise the real pre-character-selection save path without writing a save.
	var world: Node2D = load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	world._apply_save({"version":1,"checkpoint":"village","wards":[false,false,false],"talked_to_aster":true,"boss_defeated":false,"won":false,"heals":3})
	check(world.hero.character_id == "rowan" and world.selected_character_id == "rowan", "version-one save with no character still restores Rowan")
	check(world.hero.art_ready, "legacy save restoration loads a real available bank")
	world._set_mode("play")
	world.queue_free()
	await process_frame
	await create_timer(.35,true,false,true).timeout

func test_production_banks() -> void:
	fresh()
	var actor := HERO.new()
	fixture.add_child(actor)
	actor.set_physics_process(false)
	actor.set_process(false)
	for id in ["rowan","lyra","brann"]:
		var loaded: bool = actor.set_character(id)
		check(loaded, id + " production bank loads atomically")
		if not loaded:
			continue
		var entry: Dictionary = actor._character_entry(id)
		var manifest_sha := FileAccess.get_sha256(str(entry.manifest))
		var atlas_sha := FileAccess.get_sha256(str(entry.atlas))
		check(actor._directions == VIEWS, id + " production manifest explicitly declares every eight-way view")
		if actor._directions != VIEWS:
			continue
		for direction in VIEWS.size():
			var view: String = VIEWS[direction]
			actor._set_aim(vector(direction))
			for action in ACTIONS:
				actor._set_state(action,.50 if action == "cast" else .41)
				actor._state_time = 0
				actor._previous_clip = ""
				actor._update_animation(0)
				var clip: Dictionary = actor._animations[view + "_" + action]
				check(actor.current_art_clip == view + "_" + action, id + " selects actual " + view + " " + action)
				var elapsed := 0.0
				for index in clip.frames.size():
					# Cast uses a remapped visual clock; sample authored holds with
					# the gameplay lock disabled to inspect every actual atlas cell.
					actor._state_left = 0
					actor._animation_time = elapsed + float(clip.holds[index])*.5
					actor._update_animation(0)
					var frame := int(clip.frames[index])
					var region := Rect2(Vector2((frame % actor._columns)*actor._cell.x,floorf(float(frame)/actor._columns)*actor._cell.y),actor._cell)
					check(actor.current_art_frame == frame and actor._sprite.region_rect == region, id + " " + view + " " + action + " actual frame %d" % index)
					elapsed += float(clip.holds[index])
			actor._set_state("cast",.50)
			actor._state_time = .24
			actor._action_aim = vector(direction)
			actor._update_animation(0)
			var point: Array = actor._cast_hands[view]
			var expected := actor.to_global((Vector2(point[0],point[1])-actor._pivot)*actor._sprite.scale)
			check(actor.get_cast_hand_global().is_equal_approx(expected), id + " " + view + " actual socket projects through declared pivot and scale")
			var release_frame: int = actor.current_art_frame
			actor._perform_action_hit("firebolt")
			var bolts := get_nodes_in_group("combat_projectiles")
			check(bolts.size() == 1, id + " " + view + " actual bank releases exactly one projectile")
			if not bolts.is_empty():
				var bolt: Node2D = bolts[0]
				check(bolt.global_position == actor.global_position and (bolt.global_position + bolt.visual_offset).is_equal_approx(expected), id + " " + view + " keeps physical feet and rendered socket separate")
				check(bolt.direction.is_equal_approx(vector(direction)) and actor.current_art_frame == release_frame, id + " " + view + " release cel agrees with committed projectile")
				receipts.append({"character":id,"view":view,"manifest_sha256":manifest_sha,"atlas_sha256":atlas_sha,"release_frame":release_frame,"socket_native":point,"visual_offset":[bolt.visual_offset.x,bolt.visual_offset.y],"columns":actor._columns,"cell":[actor._cell.x,actor._cell.y]})
				bolt.free()
