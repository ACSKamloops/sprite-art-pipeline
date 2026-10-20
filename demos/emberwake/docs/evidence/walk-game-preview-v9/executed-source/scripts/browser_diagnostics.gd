extends Node
## Read-only local browser observability: never bypasses gameplay or writes saves.
const SNAPSHOT_INTERVAL := 1.0 / 30.0
var elapsed := 0.0
func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
func _process(delta: float) -> void:
	if not OS.has_feature("web"):
		return
	elapsed += delta
	if elapsed < SNAPSHOT_INTERVAL:
		return
	# Preserve the fractional remainder; publish current state once after a stall.
	elapsed = fmod(elapsed, SNAPSHOT_INTERVAL)
	var world := get_tree().current_scene
	if world == null or not world.has_method("get_debug_state"):
		return
	var state: Dictionary = world.get_debug_state()
	if is_instance_valid(world.hero):
		state["hero"] = world.hero.get_debug_state()
		# Observations only: browser tests still act through the real UI/keys.
		# Simulation ticks let distance/speed checks avoid wall-clock timing.
		var actor: Node = world.hero
		for property in ["_aim", "_action_aim", "_dodge_aim", "velocity"]:
			var point: Vector2 = actor.get(property)
			state.hero[property.trim_prefix("_")] = [point.x, point.y]
		state.hero["state_time"] = float(actor.get("_state_time"))
		state.hero["state_left"] = float(actor.get("_state_left"))
		state.hero["pending_hit"] = str(actor.get("_pending_hit"))
		state.hero["animation_time"] = float(actor.get("_animation_time"))
		state.hero["directions"] = actor.get("_directions").duplicate()
		var movement: Vector2 = actor._read_movement()
		state.hero["movement_input"] = [movement.x, movement.y]
	if is_instance_valid(world.hud):
		var controls: Array[Dictionary] = []
		for button in world.hud.buttons:
			controls.append({"action": button.get_meta("action", ""), "label": button.text, "disabled": button.disabled, "focused": button.has_focus(), "rect": [button.position.x, button.position.y, button.size.x, button.size.y]})
		state["ui_controls"] = controls
	var projectiles: Array[Dictionary] = []
	for bolt in get_tree().get_nodes_in_group("combat_projectiles"):
		var direction: Vector2 = bolt.get("direction")
		projectiles.append({"direction": [direction.x, direction.y], "position": [bolt.global_position.x, bolt.global_position.y], "hostile": bool(bolt.get("hostile")), "elapsed": float(bolt.get("_elapsed"))})
	state["projectiles"] = projectiles
	state["physics_tick"] = Engine.get_physics_frames()
	state["physics_hz"] = Engine.physics_ticks_per_second
	state["rendered_frames"] = Engine.get_frames_drawn()
	state["fps"] = Engine.get_frames_per_second()
	state["viewport"] = [get_viewport().get_visible_rect().size.x,get_viewport().get_visible_rect().size.y]
	JavaScriptBridge.eval("window.emberwakeState=" + JSON.stringify(state) + ";", true)
