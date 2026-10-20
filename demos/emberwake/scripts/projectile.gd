extends Node2D
class_name EmberProjectile
## Swept collision prevents fast bolts tunnelling through walls or actors.

const FX = preload("res://scripts/combat_fx.gd")
var direction: Vector2 = Vector2.RIGHT
var speed: float = 480.0
var damage: float = 30.0
var lifetime: float = 1.65
var hit_radius: float = 11.0
var hostile: bool = false
var source: Vector2 = Vector2.ZERO
var tint: Color = Color("ffad56")
## Render from the painted release hand while sweeping on the foot plane.
## This is deliberately not an initial position/muzzle offset: a glove can
## extend beyond a nearby thin wall without letting the projectile skip it.
var visual_offset := Vector2(0.0, -20.0)
var _elapsed: float = 0.0
var _trail: Array[Vector2] = []
var _atlas: Texture2D

func _ready() -> void:
	add_to_group("combat_projectiles")
	if not hostile and ResourceLoader.exists("res://assets/effects/atlas.png"):
		_atlas = load("res://assets/effects/atlas.png")
	direction = direction.normalized()
	if direction.length_squared() < 0.1:
		direction = Vector2.RIGHT

func _physics_process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= lifetime:
		queue_free()
		return
	var start := global_position
	var end := start + direction * speed * delta
	var query := PhysicsRayQueryParameters2D.create(start, end, 1)
	var wall: Dictionary = get_world_2d().direct_space_state.intersect_ray(query)
	var wall_distance: float = INF
	if not wall.is_empty():
		end = wall["position"]
		wall_distance = start.distance_to(end)
	var victim: Node2D = null
	var victim_distance: float = INF
	var group: String = "hero" if hostile else "foes"
	for candidate in get_tree().get_nodes_in_group(group):
		if not is_instance_valid(candidate) or not candidate is Node2D or not candidate.has_method("take_damage"):
			continue
		if candidate.get("hp") != null and float(candidate.get("hp")) <= 0.0:
			continue
		var body_size: float = 12.0
		if candidate.get("body_radius") != null:
			body_size = float(candidate.get("body_radius"))
		var closest := Geometry2D.get_closest_point_to_segment(candidate.global_position, start, end)
		var distance: float = start.distance_to(closest)
		if closest.distance_to(candidate.global_position) <= hit_radius + body_size and distance < victim_distance and distance < wall_distance:
			victim = candidate
			victim_distance = distance
	if victim != null:
		global_position = start + direction * victim_distance
		var accepted: Variant = victim.take_damage(damage, source)
		# Actors already render their own painted damage impact. A second burst
		# used to obscure the hit pose and falsely decorate invulnerable hits.
		if accepted == false:
			FX.spawn(get_parent(), global_position, "whiff", direction, 14.0, Color("d5c7ac"))
		queue_free()
		return
	global_position = end
	if not wall.is_empty():
		# Impact art itself is centered 18 pixels above its floor origin.
		FX.spawn(get_parent(), global_position + visual_offset + Vector2(0.0,18.0), "impact", -direction, 18.0, tint)
		queue_free()
		return
	_trail.push_front(global_position)
	if _trail.size() > 9:
		_trail.pop_back()
	queue_redraw()

func _draw() -> void:
	var lift := visual_offset
	for index in range(1, _trail.size()):
		var opacity: float = 0.5 * (1.0 - float(index) / float(_trail.size()))
		draw_line(to_local(_trail[index - 1]) + lift, to_local(_trail[index]) + lift, Color(tint, opacity), 8.0 - float(index) * 0.65, true)
	draw_circle(lift, 13.0, Color(tint, 0.12))
	draw_circle(lift, 7.0, tint)
	draw_circle(lift - direction * 1.5, 3.5, Color("fff3d2"))
	if _atlas != null:
		var slot := int(_elapsed * 14.0) % 6
		draw_set_transform(lift, direction.angle())
		draw_texture_rect_region(_atlas, Rect2(-45,-32,64,64), Rect2(slot*128,0,128,128))
		draw_set_transform(Vector2.ZERO)
