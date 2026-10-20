extends CharacterBody2D
const Clock = preload("res://clip_clock.gd")
var catalog: Dictionary
var clock
var sprite: AnimatedSprite2D
var height_root: Node2D
var shadow: Polygon2D
var fractional_ticks := 0.0
var buffered := ""
var guard_held := false
var held_actions := {"guard":false,"crouch":false,"cast":false}
const HELD_PROFILES = {"guard":["guard_enter","guard_hold","guard_exit"],"crouch":["crouch_enter","crouch_hold","crouch_exit"],"cast":["cast_prepare","cast_hold","cast_release"]}
var terminal := false
var facing := "east"
var freeze_completed := true
var visual_height := 0.0
var note := ""
func setup(data: Dictionary, frames: SpriteFrames):
	catalog = data; clock = Clock.new(data.clips)
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var shape = CollisionShape2D.new(); var circle = CircleShape2D.new(); circle.radius = 12
	shape.shape = circle; add_child(shape)
	shadow = Polygon2D.new(); var pts = PackedVector2Array()
	for i in 32: pts.append(Vector2(cos(i*TAU/32)*20,sin(i*TAU/32)*6))
	shadow.polygon = pts; shadow.color = Color(0,0,0,0.35); add_child(shadow)
	height_root = Node2D.new(); add_child(height_root)
	sprite = AnimatedSprite2D.new(); sprite.sprite_frames = frames; sprite.centered = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	height_root.add_child(sprite)
	request("ready_still",true)
func available(id: String) -> bool:
	return catalog.clips.has(id) and catalog.clips[id].get("direction","east") == facing
func request(id: String, force := false) -> bool:
	if terminal and not force: return false
	if not available(id):
		note = "Unavailable: " + id + " / " + facing; return false
	if not force and not clock.id.is_empty() and not clock.completed and not catalog.clips[clock.id].loop:
		buffered = id; note = "Buffered: " + id; return true
	return _start_clip(id)
func _start_clip(id: String) -> bool:
	clock.interrupt(); clock.start(id); fractional_ticks = 0.0
	terminal = bool(catalog.clips[id].get("terminal",false)) or id == "death"
	note = "Playing " + id; _sync_visual(); return true
func _can_transition(id: String) -> bool:
	# Complete the already-displayed view's lifecycle even if the user has
	# requested a view whose artwork is unavailable. New actions still reject.
	return catalog.clips.has(id) and catalog.clips[id].get("direction","east") == catalog.clips[clock.id].get("direction","east")
func interrupt(id: String) -> bool:
	if terminal: return false
	buffered = ""; _clear_held()
	return request(id,true)
func reset():
	terminal = false; buffered = ""; _clear_held(); facing = "east"
	request("ready_still",true)
func _clear_held():
	guard_held = false
	for key in held_actions: held_actions[key] = false
func set_held(action: String, held: bool) -> bool:
	if not HELD_PROFILES.has(action): return false
	var profile: Array = HELD_PROFILES[action]
	if not held:
		held_actions[action] = false
		if action == "guard": guard_held = false
		if terminal: return false
		# Key-up must clear input even after an unavailable-view request.
		if clock.id == profile[1] and _can_transition(profile[2]): return _start_clip(profile[2])
		return true
	if terminal: return false
	for id in profile:
		if not available(id):
			note = "Unavailable held action: " + action; return false
	if held_actions[action] == held: return true
	held_actions[action] = held
	if action == "guard": guard_held = held
	return request(profile[0])
func set_guard(held: bool): return set_held("guard",held)
func set_crouch(held: bool): return set_held("crouch",held)
func set_cast(held: bool): return set_held("cast",held)
func advance_ticks(n: int):
	var remaining: int = clock.advance(n)
	if clock.completed and not terminal:
		var next_id: String = catalog.clips[clock.id].get("next","")
		for action in HELD_PROFILES:
			var profile: Array = HELD_PROFILES[action]
			if clock.id == profile[0]: next_id = profile[1] if held_actions[action] else profile[2]
		if not buffered.is_empty(): next_id = buffered; buffered = ""
		if next_id.is_empty() and not freeze_completed: next_id = "ready_still"
		if not next_id.is_empty() and _can_transition(next_id):
			var old_hz: int = int(catalog.clips[clock.id].hz)
			# fractional_ticks is still in the outgoing clip's clock. Capture it
			# before request() resets the new action, alongside whole leftover.
			var carry_seconds := (float(remaining) + fractional_ticks) / old_hz
			_start_clip(next_id)
			fractional_ticks = carry_seconds * float(catalog.clips[next_id].hz)
			var whole := int(fractional_ticks); fractional_ticks -= whole
			if whole > 0: advance_ticks(whole)
	_sync_visual()
func _sync_visual():
	if clock.id.is_empty(): return
	var c: Dictionary = catalog.clips[clock.id]
	sprite.animation = clock.id; sprite.pause(); sprite.frame = clock.frame
	sprite.position = -Vector2(float(c.pivot[0]),float(c.pivot[1]))
	# Jump art already contains height; never add a second procedural jump.
	height_root.position.y = 0.0 if c.get("baked_height",clock.id == "jump") else -visual_height
func _physics_process(delta: float):
	if clock == null: return
	var move := Input.get_vector("ui_left","ui_right","ui_up","ui_down")
	velocity = move*110 if not terminal else Vector2.ZERO
	move_and_slide()
	fractional_ticks += delta*float(catalog.clips[clock.id].hz)
	var n := int(fractional_ticks); fractional_ticks -= n
	advance_ticks(n)
