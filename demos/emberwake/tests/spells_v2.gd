extends SceneTree
## Logic: godot --headless --path . --script tests/spells_v2.gd
## Pixels: LP_NUM_THREADS=4 xvfb-run -a godot --path . --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --script tests/spells_v2.gd -- --spells-render
## Uses real engine rendering when requested; neither a pixel count nor a pass
## grants an art score. Review the saved native-size captures separately.

const HERO = preload("res://scripts/hero.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
const FX = preload("res://scripts/combat_fx.gd")
var checks: int = 0
var failures: Array[String] = []
var fixture: Node2D
var receipts: Array[Dictionary] = []

class Ground extends Node2D:
	func _draw() -> void:
		draw_rect(Rect2(0,0,640,480),Color("29382f"))

class Target extends Node2D:
	var hp := 100.0
	var body_radius := 8.0
	func take_damage(amount: float, _source: Vector2) -> bool:
		hp -= amount
		return true

func _initialize() -> void:
	for action in ["move_left", "move_right", "move_up", "move_down", "attack", "firebolt", "nova", "dodge", "heal"]:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
	_run.call_deferred()

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("FAIL: " + message)

func fresh() -> void:
	if is_instance_valid(fixture):
		fixture.free()
	fixture = Node2D.new()
	fixture.y_sort_enabled = true
	root.add_child(fixture)

func _run() -> void:
	await test_catalog_and_sockets()
	await test_collision_and_pause()
	if "--spells-render" in OS.get_cmdline_user_args():
		await test_rendered_pixels()
	if is_instance_valid(fixture):
		fixture.queue_free()
	await process_frame
	await create_timer(.15,true,false,true).timeout
	var folder := ProjectSettings.globalize_path("res://docs/evidence/spells-v2")
	DirAccess.make_dir_recursive_absolute(folder)
	var receipt_name := "/spell-checks.json" if "--spells-render" in OS.get_cmdline_user_args() else "/spell-logic-checks.json"
	var output := FileAccess.open(folder + receipt_name,FileAccess.WRITE)
	output.store_string(JSON.stringify({"checks":checks,"failures":failures,"receipts":receipts,"renderer_requested":"--spells-render" in OS.get_cmdline_user_args(),"note":"Engine behavior and rendered pixel evidence; no art quality rating."},"\t") + "\n")
	output.close()
	if failures.is_empty():
		print("SPELLS_V2 PASS: %d assertions" % checks)
		quit(0)
	else:
		quit(1)

func test_catalog_and_sockets() -> void:
	fresh()
	var hero := HERO.new()
	check(hero.set_character("rowan"), "valid character can be selected before ready")
	fixture.add_child(hero)
	check(hero.art_ready and hero.character_id == "rowan", "default art is ready after selection")
	hero.hp = 71.0
	hero.mana = 39.0
	hero.cooldowns.attack = .19
	check(not hero.set_character("missing-not-a-character"), "invalid ID is rejected")
	check(hero.character_id == "rowan" and hero.art_ready, "invalid selection retains working character")
	check(hero.hp == 71.0 and hero.mana == 39.0 and hero.cooldowns.attack == .19, "character selection preserves health mana and cooldowns")
	check(hero.get_debug_state().character == "rowan", "diagnostic contains actual live character")
	var ids := character_ids()
	for required_id in ["rowan", "lyra", "brann"]:
		check(ids.has(required_id), "production catalog includes " + required_id)
	for id in ids:
		check(hero.set_character(id), id + " loads complete four-direction bank")
		for view in ["south", "east", "north", "west"]:
			hero.facing = view
			hero._set_state("cast",.5)
			hero._state_time = .24
			hero._update_animation(0)
			var authored: Array = hero._cast_hands.get(view, HERO.DEFAULT_CAST_HANDS[view])
			var expected: Vector2 = hero.global_position + (Vector2(authored[0],authored[1]) - hero._pivot) * hero._sprite.scale
			check(hero.get_cast_hand_global().is_equal_approx(expected), id + " " + view + " projects native socket through pivot and scale")
			var original_frame: int = hero.current_art_frame
			hero._action_aim = {"south":Vector2.DOWN,"east":Vector2.RIGHT,"north":Vector2.UP,"west":Vector2.LEFT}[view]
			hero._perform_action_hit("firebolt")
			var bolts := get_nodes_in_group("combat_projectiles")
			check(bolts.size() == 1, id + " " + view + " releases exactly one projectile")
			if not bolts.is_empty():
				var bolt: Node2D = bolts[0]
				check(bolt.global_position.is_equal_approx(hero.global_position), id + " " + view + " physical launch stays on feet")
				check((bolt.global_position + bolt.visual_offset).is_equal_approx(expected), id + " " + view + " visual launch is on hand")
				check(hero.current_art_frame == original_frame, id + " " + view + " release pose is synchronized to gameplay")
				receipts.append({"character":id,"facing":view,"release_frame":hero.current_art_frame,"socket_native":authored,"visual_offset":[bolt.visual_offset.x,bolt.visual_offset.y]})
				bolt.free()
			for child in fixture.get_children():
				if child.get_script() == FX:
					child.free()

func character_ids() -> Array[String]:
	var ids: Array[String] = ["rowan"]
	if FileAccess.file_exists(HERO.CHARACTER_CATALOG):
		var catalog: Variant = JSON.parse_string(FileAccess.get_file_as_string(HERO.CHARACTER_CATALOG))
		var entries: Variant = catalog.get("characters", []) if catalog is Dictionary else catalog
		if entries is Array:
			for entry in entries:
				if entry is Dictionary and str(entry.get("id", "")) not in ids:
					ids.append(str(entry.id))
	return ids

func test_collision_and_pause() -> void:
	fresh()
	var hero := HERO.new()
	fixture.add_child(hero)
	hero._set_aim(Vector2.RIGHT)
	hero._action_aim = Vector2.RIGHT
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	wall.position = Vector2(12,0)
	var collider := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(2,100)
	collider.shape = shape
	wall.add_child(collider)
	fixture.add_child(wall)
	var victim := Target.new()
	victim.position = Vector2(60,0)
	victim.add_to_group("foes")
	fixture.add_child(victim)
	await physics_frame
	hero._perform_action_hit("firebolt")
	var bolt: Node2D = get_nodes_in_group("combat_projectiles")[0]
	check(bolt.visual_offset.x > wall.position.x, "authored forward glove extends beyond the near wall in this test")
	await create_timer(.15,false,true).timeout
	check(victim.hp == 100.0, "hand offset cannot bypass a two-pixel near wall")
	check(not is_instance_valid(bolt), "near wall consumes bolt before target")
	fresh()
	hero = HERO.new()
	fixture.add_child(hero)
	hero.request_action("nova")
	await create_timer(.12,false,true).timeout
	var charge_count := 0
	for child in fixture.get_children():
		if child.get_script() == FX and child.style == "cast_charge":
			charge_count += 1
	check(charge_count == 1, "frost visibly charges before unchanged damage release")
	check(hero.mana < 36.1, "frost still spends 24 mana")
	fixture.process_mode = Node.PROCESS_MODE_PAUSABLE
	paused = true
	var before: float = hero._state_time
	await create_timer(.09,true,false,true).timeout
	check(hero._state_time == before, "pending cast remains frozen through pause")
	paused = false
	await create_timer(.15,false,true).timeout
	var frost: Node2D
	for child in fixture.get_children():
		if child.get_script() == FX and child.style == "frost":
			frost = child
	check(frost != null and frost.z_index == 0, "frost is above baked ground in actor depth layer")
	if frost != null:
		paused = true
		before = frost.elapsed
		await create_timer(.08,true,false,true).timeout
		check(frost.elapsed == before, "released frost visual lifetime freezes through pause")
		paused = false

func screenshot(viewport: SubViewport) -> Image:
	await process_frame
	await RenderingServer.frame_post_draw
	return viewport.get_texture().get_image()

func test_rendered_pixels() -> void:
	fresh()
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640,480)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ground := Ground.new()
	viewport.add_child(ground)
	var actors := Node2D.new()
	actors.y_sort_enabled = true
	ground.add_child(actors)
	var hero := HERO.new()
	hero.position = Vector2(320,280)
	actors.add_child(hero)
	hero.set_physics_process(false)
	hero.set_process(false)
	var baseline: Image = await screenshot(viewport)
	var fx: Node2D = FX.spawn(actors,hero.position,"frost",Vector2.DOWN,146,Color("9ce8f4"))
	fx.set_process(false)
	fx.elapsed = .21
	fx.z_index = -1
	fx.queue_redraw()
	var hidden: Image = await screenshot(viewport)
	check(not baseline.is_empty(), "real renderer returns nonempty viewport pixels")
	check(baseline.get_data() == hidden.get_data(), "old negative frost depth reproduces invisible effect beneath opaque ground")
	fx.z_index = 0
	fx.queue_redraw()
	var shown: Image = await screenshot(viewport)
	var changed := 0
	var cyan := 0
	for y in range(480):
		for x in range(640):
			var pixel := shown.get_pixel(x,y)
			if pixel != baseline.get_pixel(x,y):
				changed += 1
				if pixel.b > pixel.r * 1.08 and pixel.g > pixel.r * 1.08:
					cyan += 1
	check(changed > 3000, "fixed frost changes thousands of actual ground pixels")
	check(cyan > 1500, "fixed frost has substantial visible ice-blue paint and ring")
	var foreground := Polygon2D.new()
	foreground.position = Vector2(340,310)
	foreground.polygon = PackedVector2Array([Vector2(-8,-8),Vector2(8,-8),Vector2(8,8),Vector2(-8,8)])
	foreground.color = Color("e75a91")
	actors.add_child(foreground)
	var occluded: Image = await screenshot(viewport)
	check(occluded.get_pixel(340,310).is_equal_approx(foreground.color), "foreground actor depth remains over frost rather than global z overlay")
	var folder := ProjectSettings.globalize_path("res://docs/evidence/spells-v2")
	DirAccess.make_dir_recursive_absolute(folder)
	baseline.save_png(folder + "/frost-baseline.png")
	hidden.save_png(folder + "/frost-old-negative-depth.png")
	shown.save_png(folder + "/frost-visible.png")
	occluded.save_png(folder + "/frost-foreground-depth.png")
	receipts.append({"rendered_changed_pixels":changed,"ice_blue_pixels":cyan,"rendering_method":RenderingServer.get_current_rendering_method()})
	for id in character_ids():
		await render_character_casts(viewport,ground,actors,id,folder)
	viewport.queue_free()
	await process_frame

func render_character_casts(viewport: SubViewport, ground: Node2D, actors: Node2D, id: String, folder: String) -> void:
	for child in ground.get_children():
		if child is Label:
			child.free()
	for child in actors.get_children():
		child.free()
	var cast_heroes: Array[CharacterBody2D] = []
	var views := ["south","east","north","west"]
	for index in views.size():
		var caster := HERO.new()
		caster.position = Vector2(80 + index * 160,280)
		actors.add_child(caster)
		check(caster.set_character(id), id + " render fixture loads actual art")
		caster.set_physics_process(false)
		caster.set_process(false)
		caster.facing = views[index]
		caster._action_aim = {"south":Vector2.DOWN,"east":Vector2.RIGHT,"north":Vector2.UP,"west":Vector2.LEFT}[views[index]]
		caster._set_state("cast",.5)
		caster._state_time = .24
		caster._update_animation(0)
		cast_heroes.append(caster)
		var label := Label.new()
		label.text = views[index].capitalize()
		label.position = Vector2(index * 160 + 45,315)
		label.add_theme_font_size_override("font_size",16)
		ground.add_child(label)
	var before_bolts: Image = await screenshot(viewport)
	for caster in cast_heroes:
		caster._perform_action_hit("firebolt")
	for actor in actors.get_children():
		if actor.get_script() == PROJECTILE:
			actor.set_physics_process(false)
		if actor.get_script() == FX:
			actor.set_process(false)
			actor.elapsed = .01
			actor.queue_redraw()
	var with_bolts: Image = await screenshot(viewport)
	for caster in cast_heroes:
		var hand: Vector2 = caster.get_cast_hand_global()
		var near_hand := 0
		for y in range(int(hand.y) - 5,int(hand.y) + 6):
			for x in range(int(hand.x) - 5,int(hand.x) + 6):
				var pixel := with_bolts.get_pixel(x,y)
				if pixel != before_bolts.get_pixel(x,y) and pixel.r > pixel.b * 1.15:
					near_hand += 1
		check(near_hand > 15, id + " " + caster.facing + " projectile renders actual warm pixels at authored glove")
	before_bolts.save_png(folder + "/" + id + "-cast-release-plain.png")
	with_bolts.save_png(folder + "/" + id + "-cast-release-fire.png")
