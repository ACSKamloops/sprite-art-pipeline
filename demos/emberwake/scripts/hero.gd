extends CharacterBody2D
class_name EmberHero

signal stats_changed()
signal defeated()
signal action_used(action: String)
signal action_rejected(action: String, reason: String)

const FX = preload("res://scripts/combat_fx.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
const MOVE_SPEED: float = 158.0
const BODY_MASK: int = 1 | 4
const CHARACTER_CATALOG := "res://assets/characters/catalog.json"
const DEFAULT_CHARACTER := "rowan"
const FOUR_DIRECTIONS := ["south", "east", "north", "west"]
const EIGHT_DIRECTIONS := ["south", "southeast", "east", "northeast", "north", "northwest", "west", "southwest"]
const ART_ACTIONS := ["idle", "walk", "attack", "cast", "hurt", "dodge"]
const DEFAULT_CAST_HANDS := {"south": [99,72], "east": [102,57], "north": [93,49], "west": [24,60]}

var max_hp: float = 100.0
var hp: float = 100.0
var max_mana: float = 60.0
var mana: float = 60.0
var input_enabled: bool = true
var facing: String = "south"
var state: String = "idle"
var body_radius: float = 10.0
var cooldowns: Dictionary = {"attack": 0.0, "firebolt": 0.0, "nova": 0.0, "dodge": 0.0}
var current_art_clip: String = "south_idle"
var current_art_frame: int = 0
var art_ready: bool = false
var character_id: String = DEFAULT_CHARACTER

var _sprite: Sprite2D
var _animations: Dictionary = {}
var _directions: Array = FOUR_DIRECTIONS.duplicate()
var _cell := Vector2(128.0, 128.0)
var _columns: int = 1
var _animation_time: float = 0.0
var _previous_clip: String = ""
var _aim := Vector2.DOWN
var _action_aim := Vector2.DOWN
var _dodge_aim := Vector2.DOWN
var _state_time: float = 0.0
var _state_left: float = 0.0
var _invulnerable_left: float = 0.0
var _regen_delay: float = 0.0
var _pending_hit: String = ""
var _hit_delay: float = 0.16
var _pending_action: String = ""
var _buffer_left: float = 0.0
var _knockback := Vector2.ZERO
var _animation_bob: float = 0.0
var _pivot := Vector2(64.0, 112.0)
var _cast_hands: Dictionary = DEFAULT_CAST_HANDS.duplicate(true)
var _cast_hand_tracks: Dictionary = {}
var _cast_release_index: Variant = 3

func _ready() -> void:
	add_to_group("hero")
	collision_layer = 2
	collision_mask = BODY_MASK
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var collider := CollisionShape2D.new()
	var shape := CircleShape2D.new()
	shape.radius = body_radius
	collider.shape = shape
	add_child(collider)
	_sprite = Sprite2D.new()
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_load_art()
	_update_animation(0.0)
	stats_changed.emit()

func _unhandled_input(event: InputEvent) -> void:
	if not input_enabled:
		return
	for action in ["attack", "firebolt", "nova", "dodge", "heal"]:
		if InputMap.has_action(action) and event.is_action_pressed(action) and not event.is_echo():
			request_action(action)
			get_viewport().set_input_as_handled()
			return

func _physics_process(delta: float) -> void:
	for action in cooldowns:
		cooldowns[action] = maxf(0.0, float(cooldowns[action]) - delta)
	_invulnerable_left = maxf(0.0, _invulnerable_left - delta)
	_regen_delay = maxf(0.0, _regen_delay - delta)
	_buffer_left = maxf(0.0, _buffer_left - delta)
	if _buffer_left == 0.0:
		_pending_action = ""
	if hp <= 0.0 or not input_enabled:
		velocity = Vector2.ZERO
		return
	if _regen_delay == 0.0 and mana < max_mana:
		mana = minf(max_mana, mana + 3.5 * delta)
		stats_changed.emit()
	var movement := _read_movement()
	_state_time += delta
	if _state_left > 0.0:
		_state_left = maxf(0.0, _state_left - delta)
		if not _pending_hit.is_empty() and _state_time >= _hit_delay:
			var hit := _pending_hit
			_pending_hit = ""
			_perform_action_hit(hit)
		if _state_left == 0.0:
			_set_state("idle")
	if not _pending_action.is_empty() and _state_left == 0.0:
		var buffered := _pending_action
		_pending_action = ""
		request_action(buffered)
	if state == "dodge":
		velocity = _dodge_aim * 470.0 * (0.75 + 0.25 * _state_left / 0.26)
	elif state == "hurt":
		velocity = _knockback
		_knockback = _knockback.move_toward(Vector2.ZERO, 1100.0 * delta)
	else:
		var control: float = 1.0 if _state_left == 0.0 else 0.24
		velocity = velocity.move_toward(movement * MOVE_SPEED * control, 2100.0 * delta)
		if _state_left == 0.0:
			if movement.length_squared() > 0.01:
				_set_aim(movement)
				_set_state("walk")
			else:
				_set_state("idle")
	move_and_slide()
	_animation_bob += delta * (12.0 if movement.length_squared() > 0.01 else 2.5)
	queue_redraw()

func _process(delta: float) -> void:
	_update_animation(delta)
	if _sprite != null:
		var blink: float = 0.58 if _invulnerable_left > 0.0 and fmod(_invulnerable_left, 0.12) < 0.06 else 1.0
		_sprite.modulate = Color(1.0, 1.0, 1.0, blink if hp > 0.0 else 0.55)

func _read_movement() -> Vector2:
	if not InputMap.has_action("move_left"):
		return Vector2.ZERO
	return Input.get_vector("move_left", "move_right", "move_up", "move_down")

func request_action(action: String) -> void:
	if not input_enabled or hp <= 0.0 or not is_inside_tree():
		return
	if action == "heal":
		if state != "hurt" and state != "dodge":
			action_used.emit(action)
		return
	if not cooldowns.has(action):
		return
	if _state_left > 0.0:
		if action == "dodge" and state in ["attack", "cast"] and _state_time >= 0.14:
			_pending_hit = ""
		else:
			_pending_action = action
			_buffer_left = 0.16
			return
	if float(cooldowns[action]) > 0.0:
		action_rejected.emit(action, "cooldown")
		return
	var cost: float = 10.0 if action == "firebolt" else (24.0 if action == "nova" else 0.0)
	if mana < cost:
		action_rejected.emit(action, "mana")
		return
	var movement := _read_movement()
	if movement.length_squared() > 0.01:
		_set_aim(movement)
	_action_aim = _aim
	_state_time = 0.0
	_pending_action = ""
	match action:
		"attack":
			_set_state("attack", 0.41)
			cooldowns[action] = 0.41
			_pending_hit = action
			_hit_delay = 0.16
		"firebolt":
			_set_state("cast", 0.50)
			cooldowns[action] = 0.65
			_pending_hit = action
			_hit_delay = 0.24
		"nova":
			_set_state("cast", 0.50)
			cooldowns[action] = 5.5
			_pending_hit = action
			_hit_delay = 0.24
		"dodge":
			_set_state("dodge", 0.26)
			cooldowns[action] = 0.85
			_invulnerable_left = 0.30
			_dodge_aim = movement.normalized() if movement.length_squared() > 0.01 else _aim
			collision_mask = 1
			FX.spawn(get_parent(), global_position, "dodge", _dodge_aim, 30.0, Color("a7e2ed"))
			FX.play_sound(get_parent(), "dodge", -13.0)
	if action in ["firebolt", "nova"]:
		var charge := FX.spawn(get_parent(), global_position, "cast_charge", _action_aim, 12.0, Color("ffbc65") if action == "firebolt" else Color("9ce8f4"))
		charge.tracking_actor = self
		charge.visual_offset = get_cast_charge_hand_global() - global_position
	mana -= cost
	if cost > 0.0:
		_regen_delay = 2.0
	stats_changed.emit()
	action_used.emit(action)

func _perform_action_hit(action: String) -> void:
	if hp <= 0.0 or not input_enabled:
		return
	match action:
		"attack":
			FX.play_sound(get_parent(), "attack", -11.0)
			FX.spawn(get_parent(), global_position, "slash", _action_aim, 62.0, Color("ffe2a0"))
			for enemy in get_tree().get_nodes_in_group("foes"):
				if not _eligible_foe(enemy):
					continue
				var offset: Vector2 = enemy.global_position - global_position
				if offset.length() <= 72.0 and (offset.length() < 22.0 or offset.normalized().dot(_action_aim) > 0.35) and _line_clear(enemy.global_position):
					enemy.take_damage(21.0, global_position)
		"firebolt":
			FX.play_sound(get_parent(), "cast", -12.0)
			_present_cast_release()
			var bolt := PROJECTILE.new()
			bolt.direction = _action_aim
			bolt.source = global_position
			bolt.damage = 33.0
			bolt.visual_offset = get_cast_hand_global() - global_position
			get_parent().add_child(bolt)
			# Start at the feet so a muzzle offset cannot skip a thin wall.
			bolt.global_position = global_position
			var flash := FX.spawn(get_parent(), global_position, "cast_flash", _action_aim, 17.0, Color("ffbc65"))
			flash.visual_offset = bolt.visual_offset
		"nova":
			FX.play_sound(get_parent(), "nova", -11.0)
			_present_cast_release()
			var flash := FX.spawn(get_parent(), global_position, "cast_flash", _action_aim, 19.0, Color("b7f6ff"))
			flash.visual_offset = get_cast_hand_global() - global_position
			FX.spawn(get_parent(), global_position, "frost", _action_aim, 146.0, Color("9ce8f4"))
			for enemy in get_tree().get_nodes_in_group("foes"):
				if _eligible_foe(enemy) and global_position.distance_to(enemy.global_position) <= 146.0 and _line_clear(enemy.global_position):
					enemy.take_damage(37.0, global_position)
					if enemy.has_method("apply_slow"):
						enemy.apply_slow(0.45, 2.7)

func _eligible_foe(enemy: Node) -> bool:
	return is_instance_valid(enemy) and enemy is Node2D and enemy.has_method("take_damage") and (enemy.get("hp") == null or float(enemy.get("hp")) > 0.0)

func _line_clear(where: Vector2) -> bool:
	var ray := PhysicsRayQueryParameters2D.create(global_position, where, 1)
	return get_world_2d().direct_space_state.intersect_ray(ray).is_empty()

func take_damage(amount: float, source: Vector2 = Vector2.ZERO) -> bool:
	if hp <= 0.0 or not input_enabled or _invulnerable_left > 0.0 or amount <= 0.0:
		return false
	hp = maxf(0.0, hp - amount)
	FX.play_sound(get_parent(), "hit", -10.0)
	_pending_hit = ""
	_pending_action = ""
	_invulnerable_left = 0.72
	FX.spawn(get_parent(), global_position, "impact", (global_position - source).normalized(), 26.0, Color("ff9992"))
	stats_changed.emit()
	if hp == 0.0:
		_set_state("dead")
		velocity = Vector2.ZERO
		collision_mask = 1
		defeated.emit()
		return true
	_set_state("hurt", 0.18)
	_knockback = (global_position - source).normalized() * 185.0 if source != Vector2.ZERO else Vector2.ZERO
	return true

func heal_full() -> void:
	if hp <= 0.0:
		return
	hp = max_hp
	mana = max_mana
	stats_changed.emit()
	if is_inside_tree():
		FX.spawn(get_parent(), global_position, "heal", Vector2.UP, 37.0, Color("a6edb2"))

func reset_at(where: Vector2) -> void:
	global_position = where
	hp = max_hp
	mana = max_mana
	velocity = Vector2.ZERO
	_knockback = Vector2.ZERO
	_pending_hit = ""
	_pending_action = ""
	_buffer_left = 0.0
	_regen_delay = 0.0
	_invulnerable_left = 1.0
	for action in cooldowns:
		cooldowns[action] = 0.0
	_set_state("idle")
	stats_changed.emit()

func set_input_enabled(value: bool) -> void:
	input_enabled = value
	if not value:
		velocity = Vector2.ZERO
		_pending_action = ""
		_pending_hit = ""
		if hp > 0.0:
			_set_state("idle")

func _set_state(value: String, duration: float = 0.0) -> void:
	if state != value:
		_state_time = 0.0
	state = value
	_state_left = duration
	if value != "dodge":
		collision_mask = BODY_MASK

func _set_aim(value: Vector2) -> void:
	# Releasing a stick must retain the last useful aim, including a diagonal.
	if not value.is_finite() or value.length_squared() <= 0.000001:
		return
	if _directions.size() == 8:
		# Clockwise from south in screen coordinates. Half-sector ties advance
		# toward the next declared view; motion itself remains analog.
		var sector := int(floor(wrapf(atan2(value.x, value.y) + PI / 8.0, 0.0, TAU) / (PI / 4.0)))
		facing = EIGHT_DIRECTIONS[sector]
		_aim = Vector2(sin(sector * PI / 4.0), cos(sector * PI / 4.0)).normalized()
	else:
		_aim = value.normalized()
		if absf(value.x) > absf(value.y):
			facing = "east" if value.x > 0.0 else "west"
		else:
			facing = "south" if value.y >= 0.0 else "north"

func _load_art() -> void:
	if not set_character(character_id):
		set_character(DEFAULT_CHARACTER)

func _character_entry(id: String) -> Dictionary:
	if FileAccess.file_exists(CHARACTER_CATALOG):
		var catalog: Variant = JSON.parse_string(FileAccess.get_file_as_string(CHARACTER_CATALOG))
		var entries: Variant = catalog.get("characters", []) if catalog is Dictionary else catalog
		if entries is Array:
			for entry in entries:
				if entry is Dictionary and str(entry.get("id", "")) == id:
					return entry
	if id == DEFAULT_CHARACTER:
		return {"id": DEFAULT_CHARACTER, "atlas": "res://assets/hero/atlas.png", "manifest": "res://assets/hero/animations.json"}
	return {}

func set_character(id: String) -> bool:
	# Validate first. An invalid selection must never blank a working character,
	# spend mana, cancel a pending cast or reset health/cooldowns.
	var entry := _character_entry(id)
	if entry.is_empty():
		return false
	var manifest_path: String = str(entry.get("manifest", ""))
	if not FileAccess.file_exists(manifest_path):
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
	if not parsed is Dictionary or str(parsed.get("schema", "")) != "emberwake-animation/v1":
		return false
	var animations: Variant = parsed.get("animations", {})
	var cells: Variant = parsed.get("cell", [128, 128])
	var pivot: Variant = parsed.get("pivot", [64, 112])
	var directions: Variant = parsed.get("directions", FOUR_DIRECTIONS)
	if not animations is Dictionary or not _valid_point(cells) or not _valid_point(pivot):
		return false
	if not directions is Array or (directions != FOUR_DIRECTIONS and directions != EIGHT_DIRECTIONS):
		return false
	if not _valid_integer(cells[0]) or not _valid_integer(cells[1]) or float(cells[0]) <= 0 or float(cells[1]) <= 0:
		return false
	var draw_scale: Variant = parsed.get("draw_scale", 0.66)
	var column_value: Variant = parsed.get("columns", 1)
	if not _valid_number(draw_scale) or float(draw_scale) <= 0.0 or not _valid_integer(column_value) or int(column_value) <= 0:
		return false
	var hands: Variant = parsed.get("cast_hand", DEFAULT_CAST_HANDS)
	var release_index: Variant = parsed.get("cast_release_index", 3)
	var hand_tracks: Variant = parsed.get("cast_hand_tracks", {})
	# Socket metadata is validated before even reading the atlas. No failed bank
	# may replace a working sprite, including during a pending cast.
	if not _valid_cast_hand_tracks(hand_tracks, hands, release_index, animations, directions, cells):
		return false
	var texture := _read_texture(str(entry.get("atlas", "")))
	if texture == null:
		return false
	var columns := int(column_value)
	var rows := int(texture.get_height() / float(cells[1]))
	if rows <= 0 or columns * int(cells[0]) > texture.get_width() or texture.get_height() % int(cells[1]) != 0:
		return false
	for view in directions:
		for action in ART_ACTIONS:
			var clip: Variant = animations.get(view + "_" + action, {})
			if not _valid_clip(clip, columns * rows, action in ["idle", "walk"]):
				return false
	character_id = id
	_animations = animations.duplicate(true)
	_directions = directions.duplicate()
	_set_aim(_aim)
	_cell = Vector2(float(cells[0]), float(cells[1]))
	_pivot = Vector2(float(pivot[0]), float(pivot[1]))
	_columns = columns
	_cast_hands = hands.duplicate(true)
	_cast_hand_tracks = hand_tracks.duplicate(true)
	_cast_release_index = release_index.duplicate(true) if release_index is Dictionary else release_index
	if _sprite == null:
		return true
	_sprite.scale = Vector2.ONE * float(draw_scale)
	_sprite.offset = _cell * 0.5 - _pivot
	_sprite.texture = texture
	_sprite.region_enabled = true
	_previous_clip = ""
	_animation_time = 0.0
	art_ready = true
	_update_animation(0.0)
	return true

func _valid_number(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value))

func _valid_integer(value: Variant) -> bool:
	return _valid_number(value) and float(value) == floorf(float(value))

func _valid_point(value: Variant) -> bool:
	return value is Array and value.size() == 2 and _valid_number(value[0]) and _valid_number(value[1])

func _valid_cell_point(value: Variant, cells: Array) -> bool:
	return _valid_point(value) and float(value[0]) >= 0.0 and float(value[0]) < float(cells[0]) and float(value[1]) >= 0.0 and float(value[1]) < float(cells[1])

func _valid_cast_hand_tracks(tracks: Variant, hands: Variant, release: Variant, animations: Dictionary, directions: Array, cells: Array) -> bool:
	if not tracks is Dictionary or not hands is Dictionary or (not release is Dictionary and not _valid_integer(release)):
		return false
	for view in directions:
		# Every declared view still needs its fixed release socket.
		if not _valid_cell_point(hands.get(view), cells):
			return false
		var clip: Variant = animations.get(view + "_cast")
		if not clip is Dictionary or not clip.get("frames") is Array:
			return false
		var index: Variant = release.get(view) if release is Dictionary else release
		if not _valid_integer(index) or int(index) < 0 or int(index) >= clip.frames.size():
			return false
	for view in tracks:
		if not view in directions:
			return false
		var points: Variant = tracks[view]
		var frames: Array = animations[view + "_cast"].frames
		if not points is Array or points.size() != frames.size():
			return false
		for index in points.size():
			if not _valid_cell_point(points[index], cells):
				return false
			# Repeated exposures of the same cel must attach to the same pixel.
			if points[index] != points[frames.find(frames[index])]:
				return false
		var release_index := int(release.get(view)) if release is Dictionary else int(release)
		if points[release_index] != hands[view]:
			return false
	return true

func _valid_clip(value: Variant, capacity: int, should_loop: bool) -> bool:
	if not value is Dictionary:
		return false
	var frames: Variant = value.get("frames", null)
	var holds: Variant = value.get("holds", null)
	var loop_value: Variant = value.get("loop", null)
	if not frames is Array or frames.is_empty() or not holds is Array or holds.size() != frames.size():
		return false
	if not loop_value is bool or loop_value != should_loop:
		return false
	var total := 0.0
	for index in frames.size():
		if not _valid_integer(frames[index]) or int(frames[index]) < 0 or int(frames[index]) >= capacity:
			return false
		if not _valid_number(holds[index]) or float(holds[index]) <= 0.0:
			return false
		total += float(holds[index])
	return is_finite(total)

func get_cast_hand_global(view: String = "") -> Vector2:
	var selected_view := facing if view.is_empty() else view
	var point: Variant = _cast_hands.get(selected_view, DEFAULT_CAST_HANDS.get(selected_view, [64,64]))
	if not point is Array or point.size() != 2:
		point = DEFAULT_CAST_HANDS.get(selected_view, [64,64])
	var native_point := Vector2(float(point[0]), float(point[1]))
	var scale_factor := _sprite.scale if _sprite != null else Vector2.ONE * 0.66
	return to_global((native_point - _pivot) * scale_factor)

func get_cast_charge_hand_global() -> Vector2:
	if not _cast_hand_tracks.has(facing):
		return get_cast_hand_global()
	var points: Array = _cast_hand_tracks[facing]
	var frames: Array = _animations[facing + "_cast"].frames
	# request_action runs before the next render update. Begin at the first
	# preparation exposure until the cast clip is actually displayed.
	var exposure := 0
	if current_art_clip == facing + "_cast":
		for index in frames.size():
			# JSON numbers may be floats while current_art_frame is an int.
			if int(frames[index]) == current_art_frame:
				exposure = index
				break
	var point: Array = points[exposure]
	var scale_factor := _sprite.scale if _sprite != null else Vector2.ONE * 0.66
	return to_global((Vector2(float(point[0]), float(point[1])) - _pivot) * scale_factor)

func _present_cast_release() -> void:
	# Gameplay releases at .24 s for every character. The authored socket names
	# the actual release cel, independently of render-vs-physics frame scheduling.
	var clip: Dictionary = _animations.get(facing + "_cast", {})
	var frames: Array = clip.get("frames", [])
	if frames.is_empty() or _sprite == null:
		return
	var index := int(_cast_release_index.get(facing, 3)) if _cast_release_index is Dictionary else int(_cast_release_index)
	index = clampi(index, 0, frames.size() - 1)
	current_art_clip = facing + "_cast"
	current_art_frame = int(frames[index])
	_set_art_region()

func _read_texture(path: String) -> Texture2D:
	# Exported PCKs remap imported PNGs; their source path need not be a raw file.
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if not FileAccess.file_exists(path):
		return null
	var bitmap := Image.load_from_file(path)
	return ImageTexture.create_from_image(bitmap) if bitmap != null and not bitmap.is_empty() else null

func _update_animation(delta: float) -> void:
	var pose: String = "hurt" if state == "dead" else state
	if not pose in ["idle", "walk", "attack", "cast", "hurt", "dodge"]:
		pose = "idle"
	current_art_clip = facing + "_" + pose
	if current_art_clip != _previous_clip:
		var previous: Dictionary = _animations.get(_previous_clip, {})
		var next: Dictionary = _animations.get(current_art_clip, {})
		if pose in ["idle", "walk"] and _previous_clip.ends_with("_" + pose) and bool(previous.get("loop", false)) and bool(next.get("loop", false)):
			# Directional clips share gait roles. Retain normalized loop phase
			# through a turn rather than restarting the contact pose every time.
			var previous_duration := _clip_duration(previous)
			var next_duration := _clip_duration(next)
			_animation_time = fmod(_animation_time, previous_duration) / previous_duration * next_duration + delta
		else:
			_animation_time = 0.0
		_previous_clip = current_art_clip
	else:
		_animation_time += delta
	if state in ["attack", "cast", "hurt", "dodge"] and _state_left > 0.0:
		_animation_time = _state_time
	if not art_ready or not _animations.has(current_art_clip):
		return
	var clip: Dictionary = _animations[current_art_clip]
	var frames: Array = clip.get("frames", [0])
	var holds: Array = clip.get("holds", [])
	if frames.is_empty():
		return
	var total: float = 0.0
	for index in frames.size():
		total += float(holds[index])
	if state == "cast" and _state_left > 0.0:
		var release_index := int(_cast_release_index.get(facing, 3)) if _cast_release_index is Dictionary else int(_cast_release_index)
		release_index = clampi(release_index, 0, frames.size() - 1)
		var release_time := 0.0
		for index in release_index:
			release_time += float(holds[index])
		_animation_time = _state_time / 0.24 * release_time if _state_time < 0.24 else release_time + (_state_time - 0.24) / 0.26 * (total - release_time)
	var time: float = fmod(_animation_time, total) if bool(clip.get("loop", false)) else minf(_animation_time, total)
	var selected: int = frames.size() - 1
	for index in frames.size():
		time -= float(holds[index])
		if time < 0.0:
			selected = index
			break
	current_art_frame = int(frames[selected])
	_set_art_region()

func _clip_duration(clip: Dictionary) -> float:
	var duration := 0.0
	for hold in clip.get("holds", []):
		duration += float(hold)
	return duration

func _set_art_region() -> void:
	_sprite.region_rect = Rect2(Vector2(float(current_art_frame % _columns) * _cell.x, floorf(float(current_art_frame) / float(_columns)) * _cell.y), _cell)

func _draw() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, 0.4))
	draw_circle(Vector2.ZERO, 15.0, Color(0.02, 0.04, 0.04, 0.3))
	draw_set_transform(Vector2.ZERO)
	if not art_ready:
		# Visible diagnostic while art is being integrated, never a replacement sprite.
		draw_circle(Vector2(0.0, -17.0), 7.0, Color("d768e8"), false, 2.0)

func get_debug_state() -> Dictionary:
	return {"hp": hp, "mana": mana, "state": state, "facing": facing, "input_enabled": input_enabled, "invulnerable": _invulnerable_left > 0.0, "cooldowns": cooldowns.duplicate(), "art_ready": art_ready, "art_clip": current_art_clip, "art_frame": current_art_frame, "character": character_id, "directions": _directions.duplicate(), "cast_hand": get_cast_hand_global()}
