extends SceneTree
## Run: godot --headless --path . --script tests/systems_smoke.gd
## No generated assets or world scene are needed for these behavioral tests.

const HERO = preload("res://scripts/hero.gd")
const ENEMY = preload("res://scripts/enemy.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
var _world: Node2D
var _checks: int = 0
var _failures: Array[String] = []
var _defeats: int = 0

func _initialize() -> void:
	for action in ["move_left", "move_right", "move_up", "move_down", "attack", "firebolt", "nova", "dodge", "heal"]:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
	Engine.time_scale = 4.0
	_run.call_deferred()

func _run() -> void:
	await _test_hero_damage_and_actions()
	await _test_melee_and_walls()
	await _test_spells_and_walls()
	await _test_enemy_telegraphs_and_pause()
	await _test_enemy_death_and_boss()
	await _test_art_contract_when_present()
	if is_instance_valid(_world):
		_world.queue_free()
	await process_frame
	await create_timer(.15,true,false,true).timeout
	if _failures.is_empty():
		print("SYSTEMS_SMOKE PASS: %d behavioral checks" % _checks)
		quit(0)
	else:
		for failure in _failures:
			printerr("FAIL: " + failure)
		printerr("SYSTEMS_SMOKE FAIL: %d / %d checks" % [_failures.size(), _checks])
		quit(1)

func _fixture() -> Node2D:
	if is_instance_valid(_world):
		_world.free()
	_world = Node2D.new()
	root.add_child(_world)
	return _world

func _hero(where: Vector2 = Vector2.ZERO) -> CharacterBody2D:
	var hero := HERO.new()
	hero.position = where
	_world.add_child(hero)
	return hero

func _enemy(where: Vector2, kind: String = "scout", target: Node2D = null) -> CharacterBody2D:
	var enemy := ENEMY.new()
	enemy.setup(kind)
	enemy.position = where
	_world.add_child(enemy)
	# _ready may discover the hero; null deliberately makes a passive test target.
	enemy.target = target
	return enemy

func _wall(where: Vector2, size: Vector2 = Vector2(8.0, 100.0)) -> StaticBody2D:
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	wall.collision_mask = 0
	wall.position = where
	var collider := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	collider.shape = shape
	wall.add_child(collider)
	_world.add_child(wall)
	return wall

func _advance(seconds: float) -> void:
	await create_timer(seconds, false, true).timeout

func _check(value: bool, message: String) -> void:
	_checks += 1
	if not value:
		_failures.append(message)

func _test_hero_damage_and_actions() -> void:
	_fixture()
	var hero := _hero()
	hero.take_damage(15.0, Vector2(-40.0, 0.0))
	_check(is_equal_approx(hero.hp, 85.0), "hero takes the first hit")
	hero.take_damage(15.0, Vector2(-40.0, 0.0))
	_check(is_equal_approx(hero.hp, 85.0), "hero i-frames prevent duplicate damage")
	await _advance(0.85)
	hero.take_damage(10.0)
	_check(is_equal_approx(hero.hp, 75.0), "hero vulnerability returns after i-frames")
	hero.reset_at(Vector2.ZERO)
	await _advance(1.1)
	hero.request_action("dodge")
	hero.take_damage(90.0)
	_check(is_equal_approx(hero.hp, 100.0), "dodge grants immediate i-frames")
	_check(hero.collision_mask == 1, "dodge passes through actors but collides with walls")
	await _advance(0.4)
	_check(hero.collision_mask == (1 | 4), "dodge restores actor collision")
	hero.set_input_enabled(false)
	var before: float = hero.mana
	hero.request_action("firebolt")
	hero.take_damage(25.0)
	_check(is_equal_approx(hero.mana, before) and is_equal_approx(hero.hp, 100.0), "disabled hero rejects combat and incoming damage")
	hero.set_input_enabled(true)
	hero.reset_at(Vector2.ZERO)
	hero.request_action("firebolt")
	_check(is_equal_approx(hero.mana, 50.0), "firebolt spends ten mana once")
	hero.request_action("firebolt")
	await _advance(0.5)
	_check(is_equal_approx(hero.mana, 50.0), "buffer and cooldown cannot duplicate a cast")
	hero.reset_at(Vector2.ZERO)
	hero.hp = 40.0
	hero.request_action("heal")
	_check(is_equal_approx(hero.hp, 40.0), "healing requests cannot bypass main's charge accounting")
	hero.heal_full()
	_check(hero.hp == hero.max_hp and hero.mana == hero.max_mana, "authorized heal restores both stats")

func _test_melee_and_walls() -> void:
	_fixture()
	var hero := _hero()
	hero._set_aim(Vector2.RIGHT)
	var front := _enemy(Vector2(50.0, 0.0))
	var behind := _enemy(Vector2(-50.0, 0.0))
	hero.request_action("attack")
	await _advance(0.2)
	_check(is_equal_approx(front.hp, 21.0), "melee damages a foe in its facing arc exactly once")
	_check(is_equal_approx(behind.hp, 42.0), "melee does not hit a foe behind the hero")
	await _advance(0.3)
	_check(is_equal_approx(front.hp, 21.0), "melee is not reapplied on every active frame")
	_fixture()
	hero = _hero()
	hero._set_aim(Vector2.RIGHT)
	front = _enemy(Vector2(50.0, 0.0))
	_wall(Vector2(25.0, 0.0))
	await _advance(0.1)
	hero.request_action("attack")
	await _advance(0.25)
	_check(is_equal_approx(front.hp, 42.0), "static walls block melee damage")

func _test_spells_and_walls() -> void:
	_fixture()
	var hero := _hero()
	hero._set_aim(Vector2.RIGHT)
	var foe := _enemy(Vector2(115.0, 0.0))
	hero.request_action("firebolt")
	await _advance(0.6)
	_check(is_equal_approx(foe.hp, 9.0), "swept firebolt hits its target")
	_fixture()
	hero = _hero()
	hero._set_aim(Vector2.RIGHT)
	foe = _enemy(Vector2(115.0, 0.0))
	_wall(Vector2(50.0, 0.0))
	await _advance(0.1)
	hero.request_action("firebolt")
	await _advance(0.6)
	_check(is_equal_approx(foe.hp, 42.0), "static wall intercepts a swept projectile")
	_check(get_nodes_in_group("combat_projectiles").is_empty(), "wall impact removes the projectile")
	_fixture()
	hero = _hero()
	var open := _enemy(Vector2(-100.0, 0.0), "brute")
	var blocked := _enemy(Vector2(100.0, 0.0), "brute")
	_wall(Vector2(45.0, 0.0))
	await _advance(0.1)
	hero.request_action("nova")
	await _advance(0.25)
	_check(is_equal_approx(hero.mana, 36.0), "nova spends 24 mana")
	_check(is_equal_approx(open.hp, 63.0), "nova damages a visible nearby target")
	_check(is_equal_approx(blocked.hp, 100.0), "nova cannot damage through a wall")
	_check(float(open.get("_slow_left")) > 0.0, "nova applies a temporary slow")
	_fixture()
	hero = _hero()
	foe = _enemy(Vector2(100.0, 0.0))
	var fast := PROJECTILE.new()
	fast.speed = 9000.0
	fast.damage = 7.0
	fast.direction = Vector2.RIGHT
	_world.add_child(fast)
	await _advance(0.12)
	_check(is_equal_approx(foe.hp, 35.0), "swept collision catches a target at extreme projectile speed")

func _test_enemy_telegraphs_and_pause() -> void:
	_fixture()
	var hero := _hero(Vector2(65.0, 0.0))
	var foe := _enemy(Vector2.ZERO, "scout", hero)
	await _advance(0.1)
	_check(foe.state == "windup", "enemy enters a readable windup before striking")
	await _advance(0.2)
	_check(is_equal_approx(hero.hp, 100.0), "windup never deals early damage")
	hero.global_position = Vector2(260.0, 0.0)
	await _advance(0.45)
	_check(is_equal_approx(hero.hp, 100.0), "leaving attack range avoids a committed strike")
	_fixture()
	hero = _hero(Vector2(65.0, 0.0))
	foe = _enemy(Vector2.ZERO, "scout", hero)
	await _advance(0.75)
	_check(is_equal_approx(hero.hp, 88.0), "a committed enemy strike deals its configured damage")
	_fixture()
	hero = _hero(Vector2(65.0, 0.0))
	foe = _enemy(Vector2.ZERO, "scout", hero)
	await _advance(0.1)
	hero.set_input_enabled(false)
	await _advance(1.0)
	_check(is_equal_approx(hero.hp, 100.0) and foe.state == "idle", "dialogue disables and clears pending enemy attacks")
	_fixture()
	hero = _hero(Vector2(65.0, 0.0))
	foe = _enemy(Vector2.ZERO, "scout", hero)
	_wall(Vector2(32.0, 0.0))
	await _advance(0.9)
	_check(is_equal_approx(hero.hp, 100.0), "walls prevent enemy aggro and attacks through cover")

func _test_enemy_death_and_boss() -> void:
	_fixture()
	var hero := _hero(Vector2(100.0, 0.0))
	var boss := _enemy(Vector2.ZERO, "warden", hero)
	boss.take_damage(boss.max_hp * 0.46, Vector2(100.0, 0.0))
	_check(boss.phase == 2 and boss.state == "phase", "warden transitions into a readable second phase at 55 percent HP")
	await _advance(1.3)
	_check(boss.state == "windup", "warden resumes combat after its phase transition")
	var scout := _enemy(Vector2(400.0, 0.0))
	_defeats = 0
	scout.defeated.connect(func(_enemy_node: Node) -> void: _defeats += 1)
	scout.take_damage(100.0)
	_check(not scout.is_in_group("foes"), "dead enemies leave the target group immediately")
	scout.take_damage(100.0)
	_check(_defeats == 1, "enemy defeat is emitted exactly once")
	await _advance(0.6)
	_check(not is_instance_valid(scout), "enemy death effect expires and frees the actor")
	hero.reset_at(Vector2(500.0, 500.0))
	await _advance(1.1)
	hero.take_damage(1000.0)
	_check(hero.state == "dead" and hero.hp == 0.0, "lethal damage enters the hero death state")
	hero.reset_at(Vector2(600.0, 600.0))
	_check(hero.hp == hero.max_hp and hero.state == "idle" and hero.global_position == Vector2(600.0, 600.0), "checkpoint reset restores a dead hero")

func _test_art_contract_when_present() -> void:
	var path := "res://assets/hero/animations.json"
	if not FileAccess.file_exists(path):
		print("SYSTEMS_SMOKE: art contract skipped in this asset-free fixture")
		return
	_fixture()
	var hero := _hero()
	_check(hero.art_ready, "delivered hero manifest and atlas load")
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	_check(data is Dictionary, "hero animation manifest is valid JSON")
	if not data is Dictionary:
		return
	var clips: Dictionary = data.get("animations", {})
	var cells: Array = data.get("cell", [128, 128])
	var texture: Texture2D = hero._read_texture("res://assets/hero/atlas.png")
	var capacity: int = 0
	if texture != null:
		capacity = int(texture.get_width() / float(cells[0])) * int(texture.get_height() / float(cells[1]))
	var unique_frames: Dictionary = {}
	for facing in ["south", "east", "north", "west"]:
		for pose in ["idle", "walk", "attack", "cast", "hurt", "dodge"]:
			var name: String = facing + "_" + pose
			_check(clips.has(name), "delivered art includes " + name)
			if not clips.has(name):
				continue
			var frames: Array = clips[name].get("frames", [])
			var holds: Array = clips[name].get("holds", [])
			var valid: bool = not frames.is_empty() and holds.size() == frames.size()
			for index in frames.size():
				valid = valid and int(frames[index]) >= 0 and int(frames[index]) < capacity
				valid = valid and index < holds.size() and float(holds[index]) > 0.0
				unique_frames[int(frames[index])] = true
			_check(valid, "delivered clip has valid atlas indices and hold durations: " + name)
			hero.facing = facing
			hero.state = pose
			hero._update_animation(0.0)
			_check(hero.current_art_clip == name, "runtime selects the authored facing and pose: " + name)
	_check(unique_frames.size() >= 24, "hero states reference distinct atlas cells")
	for kind in ["scout", "brute", "warden"]:
		var enemy := _enemy(Vector2(500.0, 500.0), kind)
		_check(enemy.art_ready, "delivered generated enemy art loads: " + kind)
