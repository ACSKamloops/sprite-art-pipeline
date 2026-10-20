extends Node2D
## Emberwake's hand-authored valley, encounters, checkpoints and journey state.
## Test helpers report state; ordinary play never bypasses combat or ward gates.

const WORLD_SIZE := Vector2(2304, 1728)
const SAVE_PATH := "user://emberwake-save.json"
const SAVE_VERSION := 1
const START := Vector2(390, 1435)
const NPC_POSITION := Vector2(463, 1355)
const LANTERN_POSITION := Vector2(367, 1352)
const BELL_POSITION := Vector2(1900, 260)
const WARD_POSITIONS := [Vector2(470, 850), Vector2(1690, 1120), Vector2(1220, 470)]
const WARD_NAMES := ["Moss", "Tide", "Crown"]
const CHECKPOINTS := {"village": START, "moss": Vector2(470, 935), "tide": Vector2(1690, 1205), "crown": Vector2(1220, 555), "shrine": Vector2(1900, 570)}
const ROUTES := [
	[Vector2(390, 1500), Vector2(390, 1370), Vector2(700, 1260), Vector2(850, 1070), Vector2(930, 790), Vector2(1220, 470)],
	[Vector2(850, 1070), Vector2(620, 1000), Vector2(470, 850)],
	[Vector2(850, 1070), Vector2(1120, 1160), Vector2(1330, 1170), Vector2(1690, 1120)],
	[Vector2(1220, 470), Vector2(1450, 750), Vector2(1730, 770), Vector2(1900, 730), Vector2(1900, 370), Vector2(1900, 240)],
	[Vector2(1220, 470), Vector2(1510, 920), Vector2(1690, 1120)]
]

class AmbientLayer extends Node2D:
	var world: Node2D
	func _draw() -> void:
		world._draw_ambient(self)

var hero: CharacterBody2D
var actors: Node2D
var canopy: Node2D
var camera: Camera2D
var hud: Control
var textures: Dictionary = {}
var mode := "title"
var wards: Array[bool] = [false, false, false]
var encounters_started: Array[bool] = [false, false, false]
var encounter_foes: Array = [[], [], []]
var talked_to_aster := false
var boss_started := false
var boss_defeated := false
var won := false
var epilogue_seen := false
var boss: CharacterBody2D
var heals := 2
var checkpoint := "village"
var muted := false
var music_muted := false
var test_mode := false
var elapsed := 0.0
var session_time := 0.0
var dialogue_lines: Array[String] = []
var dialogue_speaker := ""
var dialogue_index := 0
var dialogue_after := ""
var interact_target := ""
var ward_sprites: Array[Sprite2D] = []
var pickups: Array[Dictionary] = []
var particles: Array[Dictionary] = []
var gate: StaticBody2D
var last_zone := ""
var used_actions: Dictionary = {}
var effects: Dictionary = {}
var music: AudioStreamPlayer
var _hud_timer := 0.0
var _autosave_timer := 0.0
var _shake := 0.0
var _rng := RandomNumberGenerator.new()
var _enemy_script: Script
var canopy_props: Array[Sprite2D] = []
var canopy_shader: Shader
var _save_valid := false
var character_catalog: Array[Dictionary] = []
var selected_character_id := "rowan"
var _character_choice := "rowan"
var _character_return := "title"
var _character_error := ""

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_rng.seed = 824017
	test_mode = "--test-mode" in OS.get_cmdline_user_args()
	_load_character_catalog()
	_load_textures()
	_setup_audio_buses()
	_build_world()
	var hero_script: Script = load("res://scripts/hero.gd")
	_enemy_script = load("res://scripts/enemy.gd")
	hero = CharacterBody2D.new()
	hero.set_script(hero_script)
	hero.position = START
	actors.add_child(hero)
	hero.stats_changed.connect(_on_stats_changed)
	hero.defeated.connect(_on_hero_defeated)
	hero.action_used.connect(_on_action_used)
	camera = Camera2D.new()
	camera.position = Vector2(590, 1300)
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = int(WORLD_SIZE.x)
	camera.limit_bottom = int(WORLD_SIZE.y)
	add_child(camera)
	camera.make_current()
	var interface := CanvasLayer.new()
	interface.layer = 30
	add_child(interface)
	hud = Control.new()
	hud.set_script(load("res://scripts/hud.gd"))
	interface.add_child(hud)
	hud.menu_action.connect(_menu_action)
	_load_audio()
	_update_hud()
	_set_mode("title")
	queue_redraw()

func _load_textures() -> void:
	for name in ["lantern", "ground", "grass", "path", "water", "tree", "rock", "cottage", "shrine", "ward", "ward_lit", "npc"]:
		var path := "res://assets/world/%s.png" % name
		if ResourceLoader.exists(path):
			textures[name] = load(path)

func _build_world() -> void:
	canopy_shader = Shader.new()
	canopy_shader.code = "shader_type canvas_item; uniform float canopy_opacity = 1.0; void fragment() { COLOR.a *= mix(canopy_opacity, 1.0, smoothstep(0.66, 0.95, UV.y)); }"
	actors = Node2D.new()
	actors.name = "YSortedWorld"
	# Main keeps camera, ambience and menus alive while paused. Actors and every
	# sibling projectile/FX inherit this separate simulation boundary instead.
	actors.process_mode = Node.PROCESS_MODE_PAUSABLE
	actors.y_sort_enabled = true
	add_child(actors)
	canopy = AmbientLayer.new()
	canopy.world = self
	canopy.name = "Fireflies"
	canopy.z_index = 20
	add_child(canopy)
	# Solid map edge. Feet collisions keep the walkable valley inside the canvas.
	_wall(Rect2(-60, -60, 2424, 96))
	_wall(Rect2(-60, 1692, 2424, 96))
	_wall(Rect2(-60, 0, 96, 1728))
	_wall(Rect2(2268, 0, 96, 1728))
	# The two ponds are scenic obstacles, with connected routes always clear.
	_pond_collision(Vector2(325, 420), Vector2(235, 133))
	_pond_collision(Vector2(1890, 1480), Vector2(228, 125))
	# Village cottages face the communal lantern; collision is only at their base.
	_prop("cottage", Vector2(245, 1242), Vector2(160, 290), 0.91, Vector2(168, 74))
	_prop("cottage", Vector2(583, 1529), Vector2(160, 290), 0.85, Vector2(157, 72))
	_prop("cottage", Vector2(200, 1559), Vector2(160, 290), 0.78, Vector2(145, 66))
	_prop("npc", NPC_POSITION, Vector2(64, 112), 0.63)
	_prop("lantern", LANTERN_POSITION, Vector2(32,88),0.8,Vector2(8,9))
	_prop("shrine", BELL_POSITION + Vector2(0, -15), Vector2(128, 230), 1.10, Vector2(174, 35))
	for i in range(3):
		ward_sprites.append(_prop("ward", WARD_POSITIONS[i], Vector2(48, 144), 0.73, Vector2(30, 22)))
	# Stone sides frame the one shrine entrance, rather than an invisible quest wall.
	for x in [1628, 1664, 1700, 1736, 1772, 2028, 2064, 2100, 2136, 2172]:
		_prop("rock", Vector2(x, 662), Vector2(64, 82), 0.76, Vector2(48, 37))
	_wall(Rect2(1587, 640, 183, 45))
	_wall(Rect2(2030, 640, 191, 45))
	_wall(Rect2(1580, 130, 42, 555))
	_wall(Rect2(2200, 130, 42, 555))
	_wall(Rect2(1580, 110, 662, 38))
	for y in range(170, 630, 65):
		_prop("rock", Vector2(1603, y), Vector2(64, 82), 0.69)
		_prop("rock", Vector2(2219, y), Vector2(64, 82), 0.69)
	for x in range(1620, 2220, 65):
		_prop("rock", Vector2(x, 145), Vector2(64, 82), 0.69)
	gate = _wall(Rect2(1774, 635, 252, 43))
	gate.name = "ThreeWardSeal"
	# Hand-authored silhouettes reinforce clearing edges and route junctions.
	for p in [Vector2(324, 968), Vector2(650, 779), Vector2(768, 1304), Vector2(1100, 673), Vector2(1053, 399), Vector2(1385, 375), Vector2(1450, 1030), Vector2(1832, 1071), Vector2(1403, 1272), Vector2(664, 1431), Vector2(524, 1140)]:
		_prop("tree", p, Vector2(96, 240), 0.77, Vector2(32, 27))
	# Deterministic woodland dressing, filtered away from paths, arenas and actors.
	var tree_points: Array[Vector2] = []
	for attempt in range(920):
		var p := Vector2(_rng.randf_range(70, 2240), _rng.randf_range(150, 1640))
		if _reserved(p) or _in_pond(p, 25):
			continue
		var crowded := false
		for other in tree_points:
			if other.distance_to(p) < 92:
				crowded = true
				break
		if crowded:
			continue
		tree_points.append(p)
		var tree_scale := _rng.randf_range(0.68, 0.95)
		_prop("tree", p, Vector2(96, 240), tree_scale, Vector2(32, 25))
		if tree_points.size() >= 155:
			break
	for attempt in range(90):
		var p := Vector2(_rng.randf_range(100, 2200), _rng.randf_range(150, 1620))
		if not _reserved(p, 38) and not _in_pond(p, 20):
			_prop("rock", p, Vector2(64, 82), _rng.randf_range(0.34, 0.56), Vector2(32, 22))
	for i in range(48):
		particles.append({"pos": Vector2(_rng.randf_range(60, 2250), _rng.randf_range(80, 1650)), "phase": _rng.randf_range(0, TAU), "speed": _rng.randf_range(0.4, 1.1)})

func _prop(name: String, at: Vector2, pivot: Vector2, scale_value: float, contact := Vector2.ZERO) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.name = name.capitalize()
	sprite.position = at
	sprite.centered = false
	sprite.offset = -pivot
	sprite.scale = Vector2.ONE * scale_value
	if textures.has(name):
		sprite.texture = textures[name]
	actors.add_child(sprite)
	if name in ["tree", "cottage"]:
		var material := ShaderMaterial.new()
		material.shader = canopy_shader
		sprite.material = material
		sprite.set_meta("canopy_fade", 1.0)
		canopy_props.append(sprite)
	if contact != Vector2.ZERO:
		_wall(Rect2(at - Vector2(contact.x * 0.5, contact.y * 0.65), contact))
	return sprite

func _wall(rect: Rect2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = rect.get_center()
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = rect.size
	shape.shape = rectangle
	body.add_child(shape)
	add_child(body)
	return body

func _pond_collision(center: Vector2, radius: Vector2) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var shape := CollisionPolygon2D.new()
	var points := PackedVector2Array()
	for i in range(24):
		points.append(Vector2(cos(TAU * i / 24), sin(TAU * i / 24)) * radius)
	shape.polygon = points
	body.add_child(shape)
	add_child(body)

func _reserved(p: Vector2, path_width := 100.0) -> bool:
	if _path_distance(p) < path_width:
		return true
	if Rect2(95, 1120, 590, 510).has_point(p) or Rect2(1590, 130, 650, 600).has_point(p):
		return true
	for ward in WARD_POSITIONS:
		if p.distance_to(ward + Vector2(0, 40)) < 205:
			return true
	return false

func _path_distance(p: Vector2) -> float:
	var result := 100000.0
	for route in ROUTES:
		for i in range(route.size() - 1):
			result = minf(result, Geometry2D.get_closest_point_to_segment(p, route[i], route[i + 1]).distance_to(p))
	return result

func _in_pond(p: Vector2, margin := 0.0) -> bool:
	for pond in [[Vector2(325, 420), Vector2(235 + margin, 133 + margin)], [Vector2(1890, 1480), Vector2(228 + margin, 125 + margin)]]:
		if ((p - pond[0]) / pond[1]).length() < 1:
			return true
	return false

func _draw() -> void:
	# One baked continuous ImageGen ground layer keeps browser draw calls small.
	if textures.has("ground"):
		draw_texture(textures.ground, Vector2.ZERO)
	else:
		draw_rect(Rect2(Vector2.ZERO, WORLD_SIZE), Color("364b43"))
	# Small tufts break up the trail edge, fixed in world coordinates.
	for i in range(420):
		var p := Vector2(50 + (i * 173) % 2190, 70 + (i * 257) % 1580)
		var d := _path_distance(p)
		if d > 47 and d < 90 and not _in_pond(p):
			draw_line(p, p + Vector2(-3, -7), Color("69845b"), 1)
			draw_line(p, p + Vector2(2, -10), Color("69845b"), 1)
	# Deliberate stone rings identify interactable places before any UI text appears.
	for i in range(3):
		var p: Vector2 = WARD_POSITIONS[i]
		draw_circle(p, 55, Color(0.14, 0.23, 0.22, 0.38))
		draw_arc(p, 67, 0, TAU, 32, Color("aaac85") if wards[i] else Color("697e70"), 3, true)
		for j in range(8):
			var angle := TAU * j / 8
			var stone := p + Vector2(cos(angle), sin(angle)) * 67
			draw_rect(Rect2(stone - Vector2(4, 4), Vector2(8, 8)), Color("82917d"))
		if wards[i]:
			draw_circle(p + Vector2(0, -18), 39, Color(0.8, 0.6, 0.25, 0.09))
	# Village lantern and its warm pool use authored ward imagery as a smaller prop.
	draw_circle(LANTERN_POSITION, 65, Color(0.93, 0.67, 0.27, 0.10))
	draw_circle(LANTERN_POSITION, 34, Color(0.94, 0.71, 0.33, 0.10))
	draw_circle(LANTERN_POSITION + Vector2(0, -49), 12, Color(0.97, 0.71, 0.31, 0.12))

func _draw_ambient(canvas: Node2D) -> void:
	if wards.count(true) < 3:
		for x in range(1790, 2030, 24):
			canvas.draw_line(Vector2(x, 636), Vector2(x, 685), Color(0.44, 0.74, 0.69, 0.5 + sin(session_time * 2) * 0.08), 3)
		canvas.draw_line(Vector2(1774, 637), Vector2(2026, 637), Color("70a89a"), 3)
	# Encounter circles are subtle ground marks rather than obstructing VFX.
	if boss_started and not boss_defeated:
		canvas.draw_arc(Vector2(1900, 420), 205, 0, TAU, 64, Color(0.55, 0.66, 0.53, 0.35), 2, true)
	for pickup in pickups:
		var p: Vector2 = pickup.pos
		var bob := sin(session_time * 3 + p.x) * 3
		canvas.draw_circle(p + Vector2(0, bob - 7), 12, Color(0.86, 0.68, 0.3, 0.12))
		canvas.draw_colored_polygon(PackedVector2Array([p + Vector2(0, bob - 15), p + Vector2(6, bob - 7), p + Vector2(0, bob), p + Vector2(-6, bob - 7)]), Color("e2bd6a"))
	for particle in particles:
		var p: Vector2 = particle.pos + Vector2(sin(session_time * particle.speed + particle.phase) * 13, cos(session_time * 0.5 + particle.phase) * 9)
		var alpha: float = (sin(session_time * 1.3 + particle.phase) + 1) * 0.15
		canvas.draw_circle(p, 2, Color(0.85, 0.87, 0.47, alpha))

func _process(delta: float) -> void:
	session_time += delta
	if not is_instance_valid(hero):
		return
	_update_occlusion(delta)
	var goal := hero.position
	if mode in ["title", "help", "confirm"] or (mode == "characters" and _character_return == "title"):
		goal = Vector2(620, 1300)
	camera.position = camera.position.lerp(goal, 1 - exp(-delta * 7))
	_shake = maxf(0, _shake - delta * 12)
	camera.offset = Vector2(sin(session_time * 70), cos(session_time * 83)) * _shake
	if mode == "play":
		elapsed += delta
		_check_encounters()
		_check_pickups()
		_update_interaction()
		_autosave_timer += delta
		if _autosave_timer >= 45:
			_autosave_timer = 0
			_save_game()
	_hud_timer += delta
	if _hud_timer > 0.06:
		_hud_timer = 0
		_update_hud()
	canopy.queue_redraw()

func _update_occlusion(delta: float) -> void:
	# Keep actual combatants readable under crowns/roofs without raising them
	# above world Y sorting. Trunks and feet remain solid in the shader.
	var subjects: Array[Vector3] = [Vector3(hero.position.x, hero.position.y, 32)]
	for foe in get_tree().get_nodes_in_group("foes"):
		if foe.global_position.distance_to(hero.global_position) < 540:
			var height := 65.0 if foe.kind == "warden" else (46.0 if foe.kind == "brute" else 30.0)
			subjects.append(Vector3(foe.position.x, foe.position.y, height))
	for prop in canopy_props:
		var cover := false
		if prop.position.distance_to(hero.position) < 680:
			for subject in subjects:
				if subject.y <= prop.position.y + 4 and prop.get_rect().has_point(prop.to_local(Vector2(subject.x,subject.y-subject.z))):
					cover = true
					break
		var previous := float(prop.get_meta("canopy_fade", 1.0))
		var value := move_toward(previous, 0.23 if cover else 1.0, delta * 5.5)
		if not is_equal_approx(value,previous):
			prop.set_meta("canopy_fade",value)
			(prop.material as ShaderMaterial).set_shader_parameter("canopy_opacity",value)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("pause") and not event.is_echo():
		if mode == "play":
			_set_mode("pause")
		elif mode == "pause":
			_set_mode("play")
		elif mode == "help":
			_set_mode("title")
		elif mode == "characters":
			_set_mode(_character_return)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("interact") and not event.is_echo() and mode in ["play", "dialogue"]:
		if mode == "dialogue":
			_advance_dialogue()
		elif mode == "play":
			_interact()
		get_viewport().set_input_as_handled()

func _set_mode(next_mode: String) -> void:
	mode = next_mode
	if mode == "title":
		_refresh_save_status()
	# set_input_enabled(false) intentionally cancels actions for resets. A modal
	# pause must preserve the current strike/cast/dodge and its pending hit.
	hero.input_enabled = mode == "play"
	get_tree().paused = mode != "play"
	_update_hud()
	hud.set_mode(mode)

func _menu_action(action: String) -> void:
	_play_sound("ui")
	if action.begins_with("character_select:"):
		var requested := action.trim_prefix("character_select:")
		if mode == "characters" and _normalize_character_id(requested) == requested:
			_character_choice = requested
			_character_error = ""
			_update_hud()
			hud.set_mode(mode)
		return
	match action:
		"pause_open": _set_mode("pause")
		"characters":
			if mode not in ["title", "pause"]:
				return
			if mode == "pause" and not _character_switch_reason().is_empty():
				return
			_character_return = mode
			_character_choice = _hero_character_id() if mode == "pause" else selected_character_id
			_character_error = ""
			_set_mode("characters")
		"character_cancel":
			if mode == "characters":
				_set_mode(_character_return)
		"character_apply":
			if mode != "characters":
				return
			if _character_return == "pause":
				if not _character_switch_reason().is_empty() or not _activate_character(_character_choice):
					_character_error = "This character cannot be used here yet. Your journey is unchanged."
					_update_hud()
					return
				selected_character_id = _hero_character_id()
				_save_game()
			else:
				# Title choice belongs to the next new journey, never to Continue.
				selected_character_id = _character_choice
			_set_mode(_character_return)
		"dialogue_next": _advance_dialogue()
		"new":
			if _read_save().is_empty():
				_new_game()
			else:
				_set_mode("confirm")
		"new_confirmed": _new_game()
		"continue":
			var data := _read_save()
			if not data.is_empty():
				_apply_save(data)
				_set_mode("play")
			else:
				# A file may have changed since the title opened. Keep the menu
				# usable rather than retaining a Continue action that cannot load.
				_set_mode("title")
		"resume": _set_mode("play")
		"title": _set_mode("title")
		"help": _set_mode("help")
		"mute":
			muted = not muted
			AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), muted)
			_update_hud()
			hud.set_mode(mode)
		"music_mute":
			music_muted = not music_muted
			AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), music_muted)
			_update_hud()
			hud.set_mode(mode)
		"save_title":
			_save_game()
			_set_mode("title")
		"retry":
			_reset_encounters()
			hero.reset_at(CHECKPOINTS[checkpoint])
			heals = 2
			_set_mode("play")
			hud.toast("The lantern holds. Try a dodge before a heavy strike.")
		"explore":
			_set_mode("play")
			hud.toast("The valley is waking. Aster is waiting by the lantern.")

func _new_game() -> void:
	if not _activate_character(selected_character_id):
		_activate_character("rowan")
	selected_character_id = _hero_character_id()
	wards.assign([false, false, false])
	talked_to_aster = false
	boss_defeated = false
	won = false
	epilogue_seen = false
	heals = 2
	checkpoint = "village"
	elapsed = 0
	used_actions.clear()
	_reset_encounters()
	_update_ward_art()
	hero.reset_at(START)
	camera.position = hero.position
	_set_mode("play")
	_save_game()
	_show_dialogue("BELLWETHER · DUSK", ["For three nights the Hollow Bell has been silent. Without its song, the old forest is forgetting the paths home.", "You carry the village's last living ember. Find Aster beside the lantern, then bring the light into the trees."], "")

func _reset_encounters() -> void:
	for enemy in get_tree().get_nodes_in_group("foes"):
		enemy.remove_from_group("foes")
		enemy.queue_free()
	encounters_started.assign([false, false, false])
	encounter_foes = [[], [], []]
	boss_started = false
	boss = null
	pickups.clear()

func _check_encounters() -> void:
	for i in range(3):
		if not wards[i] and not encounters_started[i] and hero.position.distance_to(WARD_POSITIONS[i]) < 230:
			_start_encounter(i)
	if wards.count(true) == 3 and not boss_defeated and not boss_started and hero.position.y < 570 and hero.position.x > 1650:
		boss_started = true
		checkpoint = "shrine"
		_save_game()
		boss = _spawn_enemy("warden", Vector2(1900, 390), -1)
		hud.toast("The Rootbound Warden stirs. Watch the ground; dodge the amber marks.", 6)
		_play_sound("ward")

func _start_encounter(index: int) -> void:
	encounters_started[index] = true
	var p: Vector2 = WARD_POSITIONS[index]
	var layouts := [
		[["scout", Vector2(-112, -20)], ["scout", Vector2(112, 20)], ["scout", Vector2(0, 130)]],
		[["brute", Vector2(0, -80)], ["scout", Vector2(-115, 60)], ["scout", Vector2(115, 60)], ["scout", Vector2(35, 150)]],
		[["brute", Vector2(-95, -35)], ["brute", Vector2(105, 35)], ["scout", Vector2(-110, 120)], ["scout", Vector2(115, 145)], ["scout", Vector2(0, -125)]]
	]
	for entry in layouts[index]:
		var enemy := _spawn_enemy(entry[0], p + entry[1], index)
		encounter_foes[index].append(enemy)
	hud.toast("%s ward · clear the restless roots, then press E at the stone." % WARD_NAMES[index], 5)

func _spawn_enemy(kind: String, at: Vector2, encounter: int) -> CharacterBody2D:
	var enemy := CharacterBody2D.new()
	enemy.set_script(_enemy_script)
	enemy.kind = kind
	enemy.position = at
	enemy.target = hero
	actors.add_child(enemy)
	enemy.setup(kind)
	enemy.defeated.connect(func(foe: Node): _on_enemy_defeated(foe, encounter))
	return enemy

func _on_enemy_defeated(enemy: Node, encounter: int) -> void:
	var p: Vector2 = enemy.position
	_shake = 2.8 if enemy.kind == "warden" else 1.1
	if encounter >= 0:
		encounter_foes[encounter].erase(enemy)
		if encounter_foes[encounter].is_empty():
			hud.toast("The roots fall quiet. Return to the %s ward and kindle it with E." % WARD_NAMES[encounter], 6)
	if enemy.kind == "warden":
		boss_defeated = true
		boss = null
		hero.heal_full()
		_save_game()
		hud.toast("The Warden rests. Approach the Hollow Bell and press E.", 6)
	else:
		pickups.append({"pos": p, "kind": "ember"})

func _check_pickups() -> void:
	for i in range(pickups.size() - 1, -1, -1):
		if hero.position.distance_to(pickups[i].pos) < 30:
			hero.hp = minf(hero.max_hp, hero.hp + 7)
			hero.mana = minf(hero.max_mana, hero.mana + 8)
			hero.stats_changed.emit()
			pickups.remove_at(i)
			_play_sound("pickup")

func _update_interaction() -> void:
	interact_target = ""
	var distance := 100000.0
	var candidates := {"aster": NPC_POSITION, "lantern": LANTERN_POSITION, "bell": BELL_POSITION, "gate": Vector2(1900, 676)}
	for i in range(3):
		candidates["ward_%d" % i] = WARD_POSITIONS[i]
	for key in candidates:
		var next: float = hero.position.distance_to(candidates[key])
		if next < 96 and next < distance:
			distance = next
			interact_target = key

func _interact() -> void:
	_update_interaction()
	match interact_target:
		"aster":
			talked_to_aster = true
			_save_game()
			if won:
				_show_dialogue("ASTER · THE LANTERN KEEPER", ["There. Do you hear it? Even the kettle is trying to sing along.", "No one will remember how small the flame was when you left. I will. Welcome home, emberkeeper."], "epilogue")
			elif wards.count(true) == 3:
				_show_dialogue("ASTER · THE LANTERN KEEPER", ["All three lights are answering. The old seal must be open now. Follow the upper path east to the bell.", "The Warden was once our guardian. Give it rest, then touch the bell. We'll be listening."], "")
			else:
				_show_dialogue("ASTER · THE LANTERN KEEPER", ["The Moss, Tide and Crown wards keep the paths alive. Their stones have gone cold. Drive the restless roots away, then press E beside each ward to share your ember.", "J is your strike. K sends a firebolt, L releases frost around you. Use Space to dodge the amber marks before a heavy blow lands.", "H drinks a healing flask. You carry two; this lantern and every newly kindled ward refill them. The lantern also remembers where you last rested.", "Follow the pale paths. Moss lies northwest, Tide to the east, Crown far north. The journal under Esc holds a map. Your ember will point the way."], "")
		"lantern":
			checkpoint = "village"
			_rest()
			hud.toast("Rested at the village lantern · health, mana and flasks restored.")
		"gate":
			if wards.count(true) < 3:
				_show_dialogue("THE THREEWARD SEAL", ["Three sleeping lights hold this threshold. Kindle the Moss, Tide and Crown wards, and the bell path will open."], "")
		"bell":
			if wards.count(true) < 3:
				_show_dialogue("THE HOLLOW BELL", ["The bell is cold. Three forest lights must answer before it can wake."], "")
			elif not boss_defeated:
				hud.toast("The Warden still binds the bell. Give the guardian its rest.")
			elif not won:
				_show_dialogue("THE HOLLOW BELL", ["You place the ember against the old bronze. It does not burn. Deep within the bell, something remembers the shape of a song."], "ending")
			else:
				hud.toast("The bell sings for the waking valley.")
		_:
			if interact_target.begins_with("ward_"):
				var index := int(interact_target.trim_prefix("ward_"))
				if wards[index]:
					checkpoint = WARD_NAMES[index].to_lower()
					_rest()
					hud.toast("Rested at the %s ward · your light is renewed." % WARD_NAMES[index])
				elif encounters_started[index] and encounter_foes[index].is_empty():
					_kindle_ward(index)
				else:
					hud.toast("Restless roots bind this stone. Clear the nearby creatures first.")

func _kindle_ward(index: int) -> void:
	wards[index] = true
	checkpoint = WARD_NAMES[index].to_lower()
	_update_ward_art()
	_rest()
	_play_sound("ward")
	var descriptions := ["The Moss ward catches your ember. Beneath your feet, the roots loosen their grip on the trail.", "The Tide ward shines like a moon seen through water. Far away, the hollow bell gives a single, uncertain breath.", "The Crown ward wakes. A warm wind passes through the highest branches, carrying the scent of home."]
	var lines: Array[String] = [descriptions[index]]
	if wards.count(true) == 3:
		lines.append("Three lights answer. The seal to the northeast falls open. Follow the high path to the shrine and give its Warden rest.")
	else:
		lines.append("Your wounds close and your flasks fill. This ward is now a safe place to return.")
	_show_dialogue("%s WARD · KINDLED" % WARD_NAMES[index].to_upper(), lines, "")

func _rest() -> void:
	hero.heal_full()
	heals = 2
	_save_game()
	_play_sound("pickup")

func _update_ward_art() -> void:
	for i in range(ward_sprites.size()):
		if wards[i] and textures.has("ward_lit"):
			ward_sprites[i].texture = textures.ward_lit
			ward_sprites[i].modulate = Color.WHITE
		else:
			ward_sprites[i].texture = textures.get("ward")
			ward_sprites[i].modulate = Color("ffe2a0") if wards[i] else Color("859f99")
	if is_instance_valid(gate):
		gate.collision_layer = 0 if wards.count(true) == 3 else 1
	queue_redraw()

func _show_dialogue(speaker: String, lines: Array[String], after: String) -> void:
	dialogue_speaker = speaker
	dialogue_lines = lines
	dialogue_index = 0
	dialogue_after = after
	_set_mode("dialogue")
	hud.set_dialogue(speaker, lines[0], 1, lines.size())

func _advance_dialogue() -> void:
	dialogue_index += 1
	if dialogue_index < dialogue_lines.size():
		hud.set_dialogue(dialogue_speaker, dialogue_lines[dialogue_index], dialogue_index + 1, dialogue_lines.size())
		_play_sound("ui")
	elif dialogue_after == "ending":
		won = true
		_save_game()
		_play_sound("ward")
		_set_mode("ending")
	else:
		if dialogue_after == "epilogue":
			epilogue_seen = true
			_save_game()
		_set_mode("play")

func _on_action_used(action: String) -> void:
	used_actions[action] = true
	if action == "heal":
		if heals > 0 and (hero.hp < hero.max_hp or hero.mana < hero.max_mana):
			heals -= 1
			hero.heal_full()
			_play_sound("pickup")
			hud.toast("A flask of lantern tea · health and mana restored.", 2.5)
		elif heals <= 0:
			hud.toast("Both flasks are empty. Rest at a kindled ward or the village lantern.")
		else:
			hud.toast("Your health and mana are already full.", 2)

func _on_stats_changed() -> void:
	_update_hud()

func _on_hero_defeated() -> void:
	_play_sound("death")
	_set_mode("dead")

func _objective() -> String:
	if won:
		return "Bellwether is safe. The waking woods are yours to explore." if epilogue_seen else "The bell is singing. Return to Aster."
	if boss_defeated:
		return "Wake the Hollow Bell. Press E at the shrine."
	if wards.count(true) == 3:
		return "Follow the high path. Face the shrine Warden."
	if not talked_to_aster and wards.count(true) == 0:
		return "Speak to Aster beside the village lantern."
	return "Kindle the forest wards. %d of 3 are awake." % wards.count(true)

func _goal() -> Vector2:
	if won:
		return hero.position if epilogue_seen else NPC_POSITION
	if wards.count(true) == 3:
		return BELL_POSITION
	if not talked_to_aster:
		return NPC_POSITION
	var closest := Vector2.ZERO
	var best := 100000.0
	for i in range(3):
		if not wards[i] and hero.position.distance_to(WARD_POSITIONS[i]) < best:
			best = hero.position.distance_to(WARD_POSITIONS[i])
			closest = WARD_POSITIONS[i]
	return closest

func _zone() -> String:
	if hero.position.x > 1580 and hero.position.y < 720:
		return "The Hollow Shrine"
	if hero.position.y > 1150 and hero.position.x < 730:
		return "Bellwether Village"
	if hero.position.y < 690:
		return "Crownwood Heights"
	if hero.position.x > 1330:
		return "The Tidewood"
	return "Mosslight Forest"

func _prompt() -> String:
	match interact_target:
		"aster": return "Speak to Aster"
		"lantern": return "Rest & save at the lantern"
		"bell": return "Wake the Hollow Bell" if boss_defeated and not won else "Touch the bell"
		"gate": return "Read the threeward seal" if wards.count(true) < 3 else ""
	if interact_target.begins_with("ward_"):
		var i := int(interact_target.trim_prefix("ward_"))
		if wards[i]: return "Rest & save at the %s ward" % WARD_NAMES[i]
		if encounters_started[i] and encounter_foes[i].is_empty(): return "Kindle the %s ward" % WARD_NAMES[i]
		return "Clear the roots around the %s ward" % WARD_NAMES[i]
	return ""

func _update_hud() -> void:
	if not is_instance_valid(hud) or not is_instance_valid(hero):
		return
	var boss_data := {}
	if is_instance_valid(boss) and not boss_defeated:
		boss_data = {"hp": boss.hp, "max_hp": boss.max_hp}
	var hint := ""
	if elapsed < 32:
		hint = "Walk with WASD or arrows. Speak with E. Your field journal and map are under Esc."
	elif not used_actions.has("dodge") and encounters_started.count(true) > 0:
		hint = "Amber marks warn of a strike. Press Space to dodge before it lands."
	elif not used_actions.has("nova") and wards.count(true) > 0:
		hint = "Surrounded? L releases a frost nova. Mana slowly returns; collect fallen embers."
	hud.update_snapshot({"hp": hero.hp, "max_hp": hero.max_hp, "mana": hero.mana, "max_mana": hero.max_mana, "heals": heals, "wards": wards.duplicate(), "ward_count": wards.count(true), "objective": _objective(), "position": hero.position, "goal_direction": _goal() - hero.position, "goal_label": "ASTER" if ((won and not epilogue_seen) or not talked_to_aster) else ("WARD" if wards.count(true)<3 else ("SHRINE" if not boss_defeated else "BELL")), "zone": _zone(), "prompt": _prompt(), "boss": boss_data, "won": won, "muted": muted, "music_muted": music_muted, "has_save": _save_valid, "hint": hint, "characters": character_catalog, "selected_character": selected_character_id, "live_character": _hero_character_id(), "character_choice": _character_choice, "character_return": _character_return, "character_error": _character_error, "character_switch_reason": _character_switch_reason()})

func _save_game() -> void:
	var data := {"version": SAVE_VERSION, "wards": wards, "talked_to_aster": talked_to_aster, "boss_defeated": boss_defeated, "won": won, "checkpoint": checkpoint, "elapsed": elapsed, "muted": muted, "music_muted": music_muted}
	data["epilogue_seen"] = epilogue_seen
	data["character_id"] = _hero_character_id()
	var file := FileAccess.open(_save_path() + ".tmp", FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))
		file.close()
		DirAccess.rename_absolute(_save_path() + ".tmp", _save_path())
	_refresh_save_status()

func _refresh_save_status() -> void:
	# HUD snapshots run frequently; validate only when opening the title or
	# writing a save. Continue still reads and validates the file before loading.
	_save_valid = not _read_save().is_empty()

func _save_path() -> String:
	return "user://emberwake-test-save.json" if test_mode else SAVE_PATH

func _read_save() -> Dictionary:
	if not FileAccess.file_exists(_save_path()):
		return {}
	var file := FileAccess.open(_save_path(), FileAccess.READ)
	if not file:
		return {}
	var parser := JSON.new()
	var parse_error := parser.parse(file.get_as_text())
	file.close()
	if parse_error != OK:
		return {}
	var data: Variant = parser.data
	if not data is Dictionary or data.get("version", 0) != SAVE_VERSION:
		return {}
	if not data.get("wards") is Array or data.wards.size() != 3:
		return {}
	for value in data.wards:
		if not value is bool:
			return {}
	if not data.get("checkpoint", "") is String or not CHECKPOINTS.has(data.checkpoint):
		return {}
	for flag in ["talked_to_aster", "boss_defeated", "won", "muted", "music_muted", "epilogue_seen"]:
		if not data.get(flag, false) is bool:
			return {}
	if not (data.get("elapsed", 0) is float or data.get("elapsed", 0) is int):
		return {}
	if data.get("boss_defeated", false) and data.wards.count(true) != 3:
		return {}
	if data.get("won", false) and not data.get("boss_defeated", false):
		return {}
	if data.checkpoint in ["moss", "tide", "crown"] and not data.wards[["moss", "tide", "crown"].find(data.checkpoint)]:
		return {}
	if data.checkpoint == "shrine" and data.wards.count(true) != 3:
		return {}
	# Version-one saves predate character selection. Missing, malformed or
	# retired choices fall back to Rowan without losing valid quest progress.
	data["character_id"] = _normalize_character_id(data.get("character_id", "rowan"))
	return data

func _apply_save(data: Dictionary) -> void:
	if not _activate_character(_normalize_character_id(data.get("character_id", "rowan"))):
		_activate_character("rowan")
	selected_character_id = _hero_character_id()
	wards.assign(data.wards)
	talked_to_aster = data.get("talked_to_aster", false)
	boss_defeated = data.get("boss_defeated", false)
	won = data.get("won", false)
	epilogue_seen = data.get("epilogue_seen", false) and won
	checkpoint = data.checkpoint
	elapsed = clampf(float(data.get("elapsed", 0)), 0, 360000)
	muted = data.get("muted", false)
	music_muted = data.get("music_muted", false)
	AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), muted)
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), music_muted)
	heals = 2
	_reset_encounters()
	_update_ward_art()
	hero.reset_at(CHECKPOINTS[checkpoint])
	camera.position = hero.position
	hud.toast("The lantern remembers. Restored at your last kindled light.")

func _setup_audio_buses() -> void:
	for bus_name in ["Music", "SFX"]:
		if AudioServer.get_bus_index(bus_name) < 0:
			AudioServer.add_bus()
			AudioServer.set_bus_name(AudioServer.bus_count - 1, bus_name)

func _load_audio() -> void:
	for name in ["ward", "pickup", "ui", "death"]:
		var path := "res://assets/sfx/%s.wav" % name
		if ResourceLoader.exists(path):
			effects[name] = load(path)
	var path := "res://assets/audio/music.ogg"
	if ResourceLoader.exists(path):
		music = AudioStreamPlayer.new()
		music.stream = load(path)
		if music.stream is AudioStreamOggVorbis:
			music.stream.loop = true
		music.bus = "Music"
		music.volume_db = -17
		music.process_mode = Node.PROCESS_MODE_ALWAYS
		add_child(music)
		music.finished.connect(func(): music.play())
		music.play()

func _play_sound(name: String) -> void:
	if muted or not effects.has(name):
		return
	var player := AudioStreamPlayer.new()
	player.stream = effects[name]
	player.bus = "SFX"
	player.volume_db = -12 if name == "attack" else -8
	player.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(player)
	player.finished.connect(player.queue_free)
	player.play()

func get_debug_state() -> Dictionary:
	var living: Array[Dictionary] = []
	for foe in get_tree().get_nodes_in_group("foes"):
		living.append({"kind": foe.kind, "hp": foe.hp, "state":foe.state,"art_pose":foe.current_art_pose,"position": [foe.position.x, foe.position.y]})
	return {"mode": mode, "test_mode": test_mode, "position": [hero.position.x, hero.position.y], "wards": wards.duplicate(), "encounters_started": encounters_started.duplicate(), "boss_started": boss_started, "boss_defeated": boss_defeated, "won": won, "epilogue_seen":epilogue_seen,"checkpoint": checkpoint, "heals": heals, "objective": _objective(), "interact_target": interact_target, "foes": living, "save_valid": _save_valid, "elapsed": elapsed, "selected_character": selected_character_id, "live_character": _hero_character_id(), "character_choice": _character_choice, "character_count": character_catalog.size()}

func _load_character_catalog() -> void:
	character_catalog.clear()
	var path := "res://assets/characters/catalog.json"
	if FileAccess.file_exists(path):
		var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if document is Dictionary and document.get("schema", "") == "emberwake-characters/v1" and document.get("characters") is Array:
			var ids: Dictionary = {}
			for candidate in document.characters:
				if not candidate is Dictionary:
					continue
				var valid := true
				for field in ["id", "name", "atlas", "manifest"]:
					if not candidate.get(field) is String or str(candidate.get(field, "")).is_empty():
						valid = false
				if not valid or ids.has(candidate.id):
					continue
				if not str(candidate.atlas).begins_with("res://") or not str(candidate.manifest).begins_with("res://"):
					continue
				if not ResourceLoader.exists(candidate.atlas) or not FileAccess.file_exists(candidate.manifest):
					continue
				ids[candidate.id] = true
				character_catalog.append(candidate.duplicate(true))
	if _character_data("rowan").is_empty():
		character_catalog.push_front({"id": "rowan", "name": "Rowan", "subtitle": "Bearer of the first ember", "description": "A village wanderer carrying a stubborn light.", "atlas": "res://assets/hero/atlas.png", "manifest": "res://assets/hero/animations.json"})

func _character_data(id: String) -> Dictionary:
	for character in character_catalog:
		if character.id == id:
			return character
	return {}

func _normalize_character_id(value: Variant) -> String:
	return value if value is String and not _character_data(value).is_empty() else "rowan"

func _hero_character_id() -> String:
	return str(hero.character_id) if hero.has_method("set_character") else "rowan"

func _activate_character(id: String) -> bool:
	if hero.has_method("set_character"):
		return hero.set_character(id)
	return id == "rowan"

func _character_switch_reason() -> String:
	if hero.hp <= 0 or hero.state not in ["idle", "walk"]:
		return "Finish your current action before changing emberkeeper."
	for foe in get_tree().get_nodes_in_group("foes"):
		if is_instance_valid(foe) and foe.hp > 0 and foe.global_position.distance_to(hero.global_position) < 430:
			return "Find a quiet clearing before changing emberkeeper."
	for projectile in get_tree().get_nodes_in_group("combat_projectiles"):
		if not projectile.is_queued_for_deletion():
			return "Let the last spell settle before changing emberkeeper."
	return ""

func _exit_tree() -> void:
	if is_instance_valid(music):
		music.stop()
		music.stream = null
