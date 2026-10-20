extends CharacterBody2D
class_name EmberEnemy

signal defeated(enemy: Node)
signal phase_changed(phase: int)

const FX = preload("res://scripts/combat_fx.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")

var target: Node2D
var kind: String = "scout"
var hp: float = 42.0
var max_hp: float = 42.0
var activated: bool = true
var body_radius: float = 13.0
var state: String = "idle"
var phase: int = 1
var art_ready: bool = false

var _speed: float = 85.0
var _damage: float = 12.0
var _reach: float = 55.0
var _windup: float = 0.56
var _recovery: float = 0.68
var _notice: float = 440.0
var _state_left: float = 0.0
var _state_total: float = 1.0
var _aim := Vector2.DOWN
var _attack_style: String = "sweep"
var _attack_counter: int = 0
var _spawn := Vector2.ZERO
var _knockback := Vector2.ZERO
var _slow_left: float = 0.0
var _slow_factor: float = 1.0
var _flash_left: float = 0.0
var _motion_time: float = 0.0
var _alerted: bool = false
var _sprite: Sprite2D
var _collider: CollisionShape2D
var _poses: Dictionary = {}
var current_art_pose := "neutral"
var _draw_scale := 0.65
var _attack_wait: float = 0.0
var _commit_count: int = 0
var last_strike_result: String = ""

# Reservations are derived from live actors, rather than held in a global queue.
# Death, interruption, a different target, or leaving the encounter releases one
# immediately. Late recovery is an opening for the next foe's telegraph.
const COMMIT_RECOVERY: float = 0.20
const ENCOUNTER_RADIUS: float = 340.0

func setup(enemy_kind: String) -> void:
	kind = enemy_kind if enemy_kind in ["scout", "brute", "warden"] else "scout"
	phase = 1
	match kind:
		"brute":
			max_hp = 100.0
			body_radius = 19.0
			_speed = 58.0
			_damage = 23.0
			_reach = 78.0
			_windup = 0.92
			_recovery = 0.95
			_notice = 450.0
		"warden":
			max_hp = 460.0
			body_radius = 29.0
			_speed = 67.0
			_damage = 24.0
			_reach = 115.0
			_windup = 0.86
			_recovery = 0.9
			_notice = 650.0
		_:
			max_hp = 42.0
			body_radius = 13.0
			_speed = 88.0
			_damage = 12.0
			_reach = 56.0
			_windup = 0.56
			_recovery = 0.68
			_notice = 440.0
	hp = max_hp
	state = "idle"
	_alerted = false
	_attack_counter = 0
	_attack_wait = 0.0
	_commit_count = 0
	last_strike_result = ""
	if is_inside_tree() and _sprite != null:
		_update_shape()
		_load_art()

func _ready() -> void:
	# Main can configure with setup before or after adding to the scene.
	if max_hp == 42.0 and kind != "scout":
		setup(kind)
	add_to_group("foes")
	collision_layer = 4
	collision_mask = 1 | 2 | 4
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	_spawn = global_position
	_collider = CollisionShape2D.new()
	add_child(_collider)
	_update_shape()
	_sprite = Sprite2D.new()
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_load_art()
	if target == null:
		target = get_tree().get_first_node_in_group("hero") as Node2D

func _update_shape() -> void:
	if _collider == null:
		return
	var shape := CircleShape2D.new()
	shape.radius = body_radius
	_collider.shape = shape

func _physics_process(delta: float) -> void:
	_flash_left = maxf(0.0, _flash_left - delta)
	_slow_left = maxf(0.0, _slow_left - delta)
	if _slow_left <= 0.0:
		_slow_factor = 1.0
	_motion_time += delta
	if hp <= 0.0:
		_state_left -= delta
		velocity = velocity.move_toward(Vector2.ZERO, 500.0 * delta)
		move_and_slide()
		if _state_left <= 0.0:
			queue_free()
		queue_redraw()
		return
	if not _can_act():
		velocity = Vector2.ZERO
		_attack_wait = 0.0
		if state in ["windup", "strike", "chase"]:
			_change_state("idle")
		queue_redraw()
		return
	var offset := target.global_position - global_position
	var distance := offset.length()
	if not _alerted and distance < _notice and _line_clear(target.global_position):
		_alerted = true
	if not _alerted:
		velocity = Vector2.ZERO
		queue_redraw()
		return
	if kind != "warden" and global_position.distance_to(_spawn) > 700.0 and distance > 220.0:
		_alerted = false
		_change_state("idle")
	if state in ["windup", "strike", "recover", "hurt", "phase"]:
		_state_left = maxf(0.0, _state_left - delta)
		velocity = _knockback if state == "hurt" else Vector2.ZERO
		_knockback = _knockback.move_toward(Vector2.ZERO, 750.0 * delta)
		if _state_left <= 0.0:
			match state:
				"windup":
					_perform_strike()
					_change_state("strike", 0.14)
				"strike": _change_state("recover", _recovery * (0.83 if phase == 2 else 1.0))
				_: _change_state("chase")
		move_and_slide()
	else:
		_change_state("chase")
		var trigger_reach: float = _reach + 14.0
		if kind == "warden" and _attack_counter % 3 == 2:
			trigger_reach = 290.0
		var in_range: bool = distance <= trigger_reach and _line_clear(target.global_position)
		_attack_wait = minf(4.0, _attack_wait + delta) if in_range else maxf(0.0, _attack_wait - delta)
		if in_range and _can_commit_attack():
			_start_attack(offset)
			velocity = Vector2.ZERO
		else:
			# Waiting foes stay involved: approach a useful striking distance, then
			# make room for neighbouring silhouettes. This is no fixed orbit/queue.
			var desired := offset.normalized()
			var approach: float = clampf((distance - (_reach + 4.0)) / 34.0, -0.45, 1.0) if in_range else 1.0
			var separation := _crowd_separation()
			var travel := _steer((desired * approach + separation * 1.35).limit_length(1.0))
			var speed_factor: float = 1.15 if phase == 2 else 1.0
			velocity = travel * _speed * speed_factor * _slow_factor
			_aim = desired
			move_and_slide()
	_update_sprite()
	queue_redraw()

func _can_act() -> bool:
	if not activated or not is_instance_valid(target):
		return false
	if target.get("hp") != null and float(target.get("hp")) <= 0.0:
		return false
	if target.get("input_enabled") != null and not bool(target.get("input_enabled")):
		return false
	return true

func _steer(desired: Vector2) -> Vector2:
	# A short fan avoids corners without allowing attacks through the obstacle.
	var query := PhysicsRayQueryParameters2D.create(global_position, global_position + desired * (body_radius + 42.0), 1)
	var hit: Dictionary = get_world_2d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return desired
	var best := Vector2.ZERO
	var best_score: float = -INF
	for turn in [-0.7, 0.7, -1.25, 1.25, -1.75, 1.75]:
		var alternative := desired.rotated(float(turn))
		query.to = global_position + alternative * (body_radius + 48.0)
		if get_world_2d().direct_space_state.intersect_ray(query).is_empty():
			var score := alternative.dot(desired)
			if score > best_score:
				best = alternative
				best_score = score
	return best

func _reserves_attack() -> bool:
	return hp > 0.0 and _can_act() and (state in ["windup", "strike", "phase"] or (state == "recover" and _state_total - _state_left < COMMIT_RECOVERY))

func _can_commit_attack() -> bool:
	# One close committing threat per target. Longer waiting time wins once a
	# reservation opens; distance only breaks near ties so brutes aren't starved.
	for other in get_tree().get_nodes_in_group("foes"):
		if other == self or not other is EmberEnemy or other.target != target or other.hp <= 0.0 or not other.activated:
			continue
		if global_position.distance_to(other.global_position) > ENCOUNTER_RADIUS:
			continue
		if other._reserves_attack():
			return false
		if other.state in ["idle", "chase"] and other._can_act():
			var other_distance: float = other.global_position.distance_to(target.global_position)
			if other_distance <= other._reach + 14.0 and other._line_clear(target.global_position):
				var wait_gap: float = other._attack_wait - _attack_wait
				if wait_gap > 0.08:
					return false
				if absf(wait_gap) <= 0.08:
					var own_distance: float = global_position.distance_to(target.global_position)
					if other_distance < own_distance - 2.0:
						return false
					if absf(other_distance - own_distance) <= 2.0 and other.get_instance_id() < get_instance_id():
						return false
	return true

func _crowd_separation() -> Vector2:
	var result := Vector2.ZERO
	for other in get_tree().get_nodes_in_group("foes"):
		if other == self or not other is EmberEnemy or other.hp <= 0.0 or not other.activated:
			continue
		var away: Vector2 = global_position - other.global_position
		# Sprite bodies extend above the physics feet. An elliptical personal
		# space reduces vertical stacks as well as touching collision circles.
		var visual := Vector2(away.x, away.y * 0.72)
		var spacing: float = body_radius + other.body_radius + 28.0
		var distance: float = visual.length()
		if distance < spacing:
			if distance < 0.1:
				away = Vector2.RIGHT if get_instance_id() > other.get_instance_id() else Vector2.LEFT
			else:
				away = away.normalized()
			result += away * (1.0 - distance / spacing)
	return result.limit_length(1.0)

func _start_attack(offset: Vector2) -> void:
	_attack_wait = 0.0
	_commit_count += 1
	last_strike_result = "pending"
	_aim = offset.normalized() if offset.length_squared() > 0.1 else Vector2.DOWN
	_attack_style = "sweep"
	var windup: float = _windup
	if kind == "warden":
		match _attack_counter % 3:
			1:
				_attack_style = "pulse"
				windup = 1.18
			2:
				_attack_style = "fan"
				windup = 0.95
		_attack_counter += 1
	if phase == 2:
		windup *= 0.85
	_change_state("windup", windup)

func _perform_strike() -> void:
	if not _can_act():
		last_strike_result = "cancelled"
		return
	last_strike_result = "miss"
	var tint := Color("ffb36b") if phase == 1 else Color("f6927d")
	match _attack_style:
		"fan":
			last_strike_result = "projectiles"
			FX.play_sound(get_parent(), "cast", -16.0)
			var spread: Array = [-0.32, 0.0, 0.32] if phase == 1 else [-0.48, -0.24, 0.0, 0.24, 0.48]
			for angle in spread:
				var bolt := PROJECTILE.new()
				bolt.hostile = true
				bolt.direction = _aim.rotated(float(angle))
				bolt.source = global_position
				bolt.speed = 185.0 if phase == 1 else 220.0
				bolt.damage = 16.0
				bolt.lifetime = 2.8
				bolt.tint = tint
				get_parent().add_child(bolt)
				bolt.global_position = global_position
		"pulse":
			FX.play_sound(get_parent(), "nova", -14.0)
			var radius: float = 145.0 if phase == 1 else 166.0
			FX.spawn(get_parent(), global_position, "phase", _aim, radius, tint)
			if global_position.distance_to(target.global_position) <= radius and _line_clear(target.global_position):
				last_strike_result = "hit" if target.take_damage(_damage + 3.0, global_position) else "guarded"
		_:
			FX.spawn(get_parent(), global_position, "melee_release", _aim, _reach + 14.0, tint)
			FX.play_sound(get_parent(), "attack", -19.0)
			var offset := target.global_position - global_position
			if offset.length() <= _reach + 14.0 and (offset.length() < 20.0 or offset.normalized().dot(_aim) > 0.4) and _line_clear(target.global_position):
				last_strike_result = "hit" if target.take_damage(_damage, global_position) else "guarded"
			# A short, hollow contact tick differs from the painted damage burst.
			# It does not add damage, freeze actors, or extend the warning window.
			if last_strike_result != "hit":
				FX.spawn(get_parent(), global_position + _aim * (_reach + 5.0), "whiff", _aim, 12.0, Color("d5c7ac"))

func _line_clear(where: Vector2) -> bool:
	var ray := PhysicsRayQueryParameters2D.create(global_position, where, 1)
	return get_world_2d().direct_space_state.intersect_ray(ray).is_empty()

func take_damage(amount: float, source: Vector2 = Vector2.ZERO) -> bool:
	if hp <= 0.0 or not activated or amount <= 0.0:
		return false
	hp = maxf(0.0, hp - amount)
	FX.play_sound(get_parent(), "hit", -15.0)
	_alerted = true
	_flash_left = 0.14
	FX.spawn(get_parent(), global_position, "impact", (global_position - source).normalized(), 23.0, Color("fff0be"))
	if hp <= 0.0:
		remove_from_group("foes")
		collision_layer = 0
		collision_mask = 1
		_collider.set_deferred("disabled", true)
		_change_state("dead", 0.65 if kind == "warden" else 0.42)
		velocity = (global_position - source).normalized() * 80.0
		defeated.emit(self)
		return true
	if kind == "warden":
		if phase == 1 and hp <= max_hp * 0.55:
			phase = 2
			_change_state("phase", 1.05)
			FX.spawn(get_parent(), global_position, "phase", _aim, 90.0, Color("e8b3ee"))
			phase_changed.emit(phase)
		# The boss remains committed to telegraphs; ordinary hits cannot stun-lock it.
		return true
	# Heavy enemies resist stagger during a clear windup. Scouts can be interrupted.
	if kind == "scout" or not state in ["windup", "strike"]:
		_knockback = (global_position - source).normalized() * (135.0 if kind == "scout" else 65.0)
		_change_state("hurt", 0.16 if kind == "scout" else 0.1)
	return true

func apply_slow(factor: float, duration: float) -> void:
	_slow_factor = clampf(factor, 0.25, 1.0)
	_slow_left = maxf(_slow_left, duration)

func _change_state(value: String, duration: float = 0.0) -> void:
	state = value
	_state_left = duration
	_state_total = maxf(0.001, duration)

func _load_art() -> void:
	if _sprite == null:
		return
	var path := "res://assets/enemies/" + kind + ".png"
	_poses.clear()
	for pose in ["neutral","step","windup","strike","back_neutral","back_step","back_windup","back_strike"]:
		var pose_path: String = "res://assets/enemies/poses/" + kind + "/" + str(pose) + ".png"
		if ResourceLoader.exists(pose_path):
			_poses[pose] = load(pose_path)
	if _poses.has("neutral"):
		path = "res://assets/enemies/poses/" + kind + "/neutral.png"
	var pivot := Vector2(64.0, 112.0)
	var scale_value: float = 0.65
	if kind == "brute":
		pivot = Vector2(80.0, 144.0)
		scale_value = 0.7
	elif kind == "warden":
		pivot = Vector2(128.0, 224.0)
		scale_value = 0.7
	var texture: Texture2D = null
	# Imported art is remapped in PCK/Web exports; load it before trying raw PNG.
	if ResourceLoader.exists(path):
		texture = load(path) as Texture2D
	elif FileAccess.file_exists(path):
		var bitmap := Image.load_from_file(path)
		if bitmap != null and not bitmap.is_empty():
			texture = ImageTexture.create_from_image(bitmap)
	_sprite.texture = texture
	art_ready = texture != null
	if art_ready:
		_sprite.offset = texture.get_size() * 0.5 - pivot
	_sprite.scale = Vector2.ONE * scale_value
	_draw_scale = scale_value
	var shader := Shader.new()
	shader.code = "shader_type canvas_item; uniform float flash = 0.0; void fragment() { vec4 c = texture(TEXTURE, UV); COLOR = vec4(mix(c.rgb, vec3(1.0, 0.94, 0.78), flash), c.a) * COLOR; }"
	var material := ShaderMaterial.new()
	material.shader = shader
	_sprite.material = material

func _update_sprite() -> void:
	if _sprite == null:
		return
	var material := _sprite.material as ShaderMaterial
	if material != null:
		material.set_shader_parameter("flash", _flash_left / 0.14 * 0.85)
	var walk: bool = state == "chase" and velocity.length() > 1.0
	var pose := "neutral"
	if walk and int(_motion_time * 6.0) % 2 == 1:
		pose = "step"
	elif state in ["windup","phase"]:
		pose = "windup"
	elif state == "strike" or (state == "recover" and _state_left > _state_total - 0.09):
		pose = "strike"
	var back_view := _aim.y < -0.2 and _poses.has("back_neutral")
	if back_view:
		# Validation can leave an incomplete rear pose bank. A missing key uses
		# valid rear neutral plus a separate ground effect, never front artwork.
		pose = "back_" + pose if _poses.has("back_" + pose) else "back_neutral"
	if _poses.has(pose):
		_sprite.texture = _poses[pose]
	current_art_pose = pose
	var compensation: float = {"scout":1.0017050298380223,"brute":1.1092468307233407,"warden":0.9989121794067194}.get(kind,1.0) if back_view else 1.0
	_sprite.scale = Vector2.ONE * _draw_scale * compensation
	# Front/back three-quarter paint supplies upper/lower facings. Leftquadrants
	# use an explicit mirror; these enemies have no gameplay handedness rule.
	_sprite.flip_h = _aim.x < -0.12
	_sprite.position = Vector2(0.0, sin(_motion_time * 11.0) * 1.8 if walk else sin(_motion_time * 2.4) * 0.6)
	_sprite.rotation = sin(_motion_time * 11.0) * 0.025 if walk else 0.0
	# These are small whole-cel staging offsets between the existing painted
	# anticipation/contact/neutral poses, not newly authored limb animation.
	if state == "windup":
		var progress: float = 1.0 - _state_left / _state_total
		_sprite.position -= _aim * smoothstep(0.0, 0.7, progress) * 3.0
	elif state == "strike":
		_sprite.position += _aim * sin((1.0 - _state_left / _state_total) * PI) * 6.0
	elif state == "recover":
		var recovery_time: float = _state_total - _state_left
		_sprite.position += _aim * maxf(0.0, 1.0 - recovery_time / 0.18) * 2.0
	_sprite.modulate = Color("c4edff") if _slow_left > 0.0 else Color.WHITE

func _draw() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, 0.42))
	draw_circle(Vector2.ZERO, body_radius * 1.22, Color(0.025, 0.025, 0.035, 0.32))
	draw_set_transform(Vector2.ZERO)
	if state == "windup" and hp > 0.0:
		var progress: float = 1.0 - _state_left / _state_total
		var tint := Color("ffbb76") if phase == 1 else Color("ff9b92")
		if _attack_style == "pulse":
			var radius: float = 145.0 if phase == 1 else 166.0
			draw_circle(Vector2.ZERO, radius, Color(tint, 0.09 + 0.08 * progress))
			draw_arc(Vector2.ZERO, radius, 0.0, TAU, 72, Color(0.12,0.055,0.035,0.8), 8.0, true)
			draw_arc(Vector2.ZERO, radius, 0.0, TAU, 72, Color(tint, 0.95), 3.0, true)
			draw_arc(Vector2.ZERO, radius * progress, 0.0, TAU, 64, Color(tint, 0.6), 2.0, true)
		elif _attack_style == "fan":
			var spread: Array = [-0.32, 0.0, 0.32] if phase == 1 else [-0.48, -0.24, 0.0, 0.24, 0.48]
			for angle in spread:
				var direction := _aim.rotated(float(angle))
				draw_line(direction * 32.0, direction * 310.0, Color(0.12,0.055,0.035,0.6), 6.0, true)
				draw_line(direction * 32.0, direction * 310.0, Color(tint, 0.5 + progress * 0.4), 2.5, true)
		else:
			var angle := _aim.angle()
			var points := PackedVector2Array([Vector2.ZERO])
			for step in range(21):
				points.append(Vector2.from_angle(angle - 1.16 + float(step) / 20.0 * 2.32) * (_reach + 14.0))
			draw_colored_polygon(points, Color(0.30,0.095,0.035,0.17 + progress * 0.15))
			draw_arc(Vector2.ZERO, _reach + 14.0, angle - 1.16, angle + 1.16, 30, Color(0.12,0.055,0.035,0.8), 8.0, true)
			draw_arc(Vector2.ZERO, _reach + 14.0, angle - 1.16, angle + 1.16, 30, Color(tint, 0.75 + progress * 0.25), 3.0, true)
		draw_arc(Vector2(0.0, -body_radius - 9.0), 5.0, -PI / 2.0, -PI / 2.0 + TAU * maxf(progress, 0.01), 24, Color("ffe9bd"), 2.5, true)
	if hp > 0.0 and hp < max_hp and kind != "warden":
		var width: float = 44.0 if kind == "scout" else 56.0
		var y: float = -68.0 if kind == "scout" else -96.0
		draw_style_box(_health_style(Color("101d20")), Rect2(-width * 0.5 - 2.0, y - 2.0, width + 4.0, 9.0))
		draw_rect(Rect2(-width * 0.5, y, width * hp / max_hp, 5.0), Color("f4b378"))
	if not art_ready:
		draw_circle(Vector2(0.0, -body_radius), body_radius * 0.65, Color("e865aa"), false, 2.0)
	if state == "dead" and _sprite != null:
		_sprite.modulate.a = clampf(_state_left / _state_total, 0.0, 1.0)
		_sprite.rotation = (1.0 - _state_left / _state_total) * 0.28

func _health_style(color: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.corner_radius_top_left = 2
	box.corner_radius_top_right = 2
	box.corner_radius_bottom_left = 2
	box.corner_radius_bottom_right = 2
	return box

func get_debug_state() -> Dictionary:
	return {"kind": kind, "hp": hp, "max_hp": max_hp, "state": state, "phase": phase, "activated": activated, "attack_style": _attack_style, "art_ready": art_ready,"art_pose":current_art_pose,"attack_wait":_attack_wait,"commit_count":_commit_count,"strike_result":last_strike_result,"reserves_attack":_reserves_attack()}
