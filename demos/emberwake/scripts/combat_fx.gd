extends Node2D
class_name EmberCombatFX
## Short-lived, gameplay-independent effects. All timings use engine delta.

var style: String = "impact"
var direction: Vector2 = Vector2.RIGHT
var radius: float = 48.0
var tint: Color = Color("ffbe65")
var duration: float = 0.3
var elapsed: float = 0.0
var visual_offset := Vector2.ZERO
var tracking_actor: Node2D
var _atlas: Texture2D

func _ready() -> void:
	if ResourceLoader.exists("res://assets/effects/atlas.png"):
		_atlas = load("res://assets/effects/atlas.png")
	if style == "frost":
		# The map's baked ground is drawn at z=0 by the world parent. A
		# negative z hid the whole spell underneath it. Stay in the actors'
		# y-sorted layer so foreground characters/scenery retain their depth.
		z_index = 0

static func play_sound(host: Node, cue: String, volume: float = -11.0) -> void:
	var path := "res://assets/sfx/" + cue + ".wav"
	# WAV imports also use remapped resources in exports.
	if not ResourceLoader.exists(path):
		return
	# A small voice limit keeps multi-target nova hits from producing a loud pileup.
	if host.get_tree().get_nodes_in_group("combat_audio").size() >= 8:
		return
	var player := AudioStreamPlayer.new()
	player.stream = load(path) as AudioStream
	if player.stream == null:
		player.free()
		return
	player.volume_db = volume
	player.bus = "SFX" if AudioServer.get_bus_index("SFX") >= 0 else "Master"
	player.add_to_group("combat_audio")
	host.add_child(player)
	player.finished.connect(player.queue_free)
	player.play()

static func spawn(host: Node, where: Vector2, effect: String, aim: Vector2 = Vector2.RIGHT, size: float = 48.0, color: Color = Color("ffbe65")) -> Node2D:
	# Runtime script construction also works before an editor has built its
	# global class cache (e.g. a clean checkout's --script smoke test).
	var fx: Variant = load("res://scripts/combat_fx.gd").new()
	fx.style = effect
	fx.direction = aim.normalized() if aim.length_squared() > 0.01 else Vector2.RIGHT
	fx.radius = size
	fx.tint = color
	match effect:
		"slash": fx.duration = 0.22
		"melee_release": fx.duration = 0.16
		"whiff": fx.duration = 0.14
		"frost": fx.duration = 0.62
		"cast_charge": fx.duration = 0.25
		"cast_flash": fx.duration = 0.16
		"heal": fx.duration = 0.8
		"phase": fx.duration = 0.9
		"dodge": fx.duration = 0.3
		_: fx.duration = 0.3

	host.add_child(fx)
	fx.global_position = where
	return fx

func _process(delta: float) -> void:
	if style == "cast_charge" and is_instance_valid(tracking_actor):
		if tracking_actor.get("state") != "cast" or str(tracking_actor.get("_pending_hit")).is_empty():
			queue_free()
			return
		global_position = tracking_actor.global_position
		visual_offset = tracking_actor.get_cast_charge_hand_global() - global_position
	elapsed += delta
	if elapsed >= duration:
		queue_free()
		return
	queue_redraw()

func _draw() -> void:
	var progress: float = clampf(elapsed / duration, 0.0, 1.0)
	var fade: float = 1.0 - progress
	var color := Color(tint, fade)
	var center := Vector2(0.0, -18.0)
	if _atlas != null and style in ["frost","impact"]:
		var slot := mini(5, int(progress * 6.0))
		var row := 1 if style == "frost" else 2
		var side := radius * (2.05 if style == "frost" else 2.8)
		var origin := Vector2.ZERO if style == "frost" else center
		var painted_opacity := fade * (0.68 if style == "frost" else 0.8)
		draw_texture_rect_region(_atlas,Rect2(origin-Vector2.ONE*side*.5,Vector2.ONE*side),Rect2(slot*128,row*128,128,128),Color(1,1,1,painted_opacity))
	match style:
		"cast_charge":
			var size := radius * (0.3 + 0.7 * progress)
			draw_circle(visual_offset, size, Color(tint, 0.10 + progress * 0.10))
			draw_arc(visual_offset, size * 0.75, progress * TAU, progress * TAU + 4.9, 20, Color(tint, 0.45 + progress * 0.5), 1.5, true)
			for index in range(4):
				var ray := Vector2.from_angle(float(index) * TAU / 4.0 + progress * 1.7)
				draw_line(visual_offset + ray * size * 1.4, visual_offset + ray * size * 0.6, Color(tint,progress * 0.8), 1.5, true)
		"cast_flash":
			var size := radius * (0.3 + progress * 0.8)
			draw_circle(visual_offset, size, Color(tint,fade * 0.16))
			draw_circle(visual_offset, 4.0 * fade, Color("fff4df",fade))
			for index in range(6):
				var ray := Vector2.from_angle(float(index) * TAU / 6.0 + 0.25)
				draw_line(visual_offset + ray * size * 0.35, visual_offset + ray * size, Color(tint,fade), 1.5, true)
		"melee_release":
			# Exactly the locked melee sector at floor level; a short release
			# trace, rather than another large opaque silhouette over the actors.
			var angle := direction.angle()
			var half_angle: float = acos(0.4)
			draw_arc(Vector2.ZERO, radius, angle - half_angle, angle + half_angle, 30, Color(tint, fade * 0.9), 2.0, true)
			for side in [-1.0, 1.0]:
				var edge := direction.rotated(half_angle * side)
				draw_line(edge * radius * 0.82, edge * radius, Color(tint, fade * 0.75), 2.0, true)
		"whiff":
			var side := direction.orthogonal()
			draw_line(side * -radius * 0.5, side * radius * 0.5, Color(tint, fade * 0.7), 1.5, true)
			draw_line(side * -radius * 0.35 - direction * 4.0, side * radius * 0.35 - direction * 4.0, Color(tint, fade * 0.35), 1.0, true)
		"slash":
			var angle := direction.angle()
			var sweep := angle - 1.0 + progress * 0.7
			draw_arc(center, radius * (0.7 + progress * 0.3), sweep, sweep + 1.45, 24, Color(tint, fade * 0.55), 11.0, true)
			draw_arc(center, radius * (0.75 + progress * 0.3), sweep + 0.08, sweep + 1.32, 24, color, 3.0, true)
		"frost", "phase":
			var reach: float = radius * (1.0 - pow(1.0 - progress, 3.0))
			draw_circle(Vector2.ZERO, reach, Color(tint, fade * 0.08))
			draw_arc(Vector2.ZERO, reach, 0.0, TAU, 64, Color(tint, fade * 0.75), 3.0, true)
			for index in range(12):
				var spoke := Vector2.from_angle(float(index) * TAU / 12.0)
				var point := spoke * reach
				draw_line(point * 0.82, point, color, 2.0, true)
				if style == "frost":
					draw_line(point, point * 0.88 + spoke.rotated(PI / 2.0) * 7.0 * fade, color, 2.0, true)
		"heal":
			draw_arc(Vector2.ZERO, radius * (0.8 + progress * 0.2), 0.0, TAU, 40, Color(tint, fade * 0.55), 2.0, true)
			for index in range(7):
				var angle := float(index) * TAU / 7.0
				var point := Vector2(cos(angle) * radius * 0.65, sin(angle) * radius * 0.25 - 60.0 * progress)
				draw_line(point - Vector2(3.0, 0.0), point + Vector2(3.0, 0.0), color, 2.0)
				draw_line(point - Vector2(0.0, 3.0), point + Vector2(0.0, 3.0), color, 2.0)
		"dodge":
			for index in range(4):
				var offset := -direction * float(index) * 9.0 - direction * progress * 22.0
				draw_arc(center + offset, 12.0 - float(index), direction.angle() + 1.8, direction.angle() + 4.5, 12, Color(tint, fade * (0.5 - float(index) * 0.1)), 2.0, true)
		_:
			for index in range(8):
				var ray := Vector2.from_angle(float(index) * TAU / 8.0 + 0.2)
				draw_line(center + ray * radius * progress * 0.35, center + ray * radius * progress, color, 2.5 * fade + 0.5, true)
			draw_circle(center, 6.0 * fade, Color(tint, fade * 0.75))
