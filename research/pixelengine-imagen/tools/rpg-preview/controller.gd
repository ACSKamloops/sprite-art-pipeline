extends Node2D
## Deterministic action clock. Events are observation metadata, not combat hits.
signal authored_event(event: Dictionary)

const LOCOMOTION := ["idle","walk","run"]
const HELD := ["guard","crouch"]
const INTERRUPTS := {"hurt":1,"stun":2,"knockdown":3,"death":4}
var bank: Dictionary = {}
var clips: Dictionary = {}
var frames: SpriteFrames
var sprite: AnimatedSprite2D
var facing := "SE"
var aim := "SE"
var aim_axis := Vector2(1,1).normalized()
var state := "idle"
var clip_name := ""
var frame_index := 0
var frame_elapsed := 0.0
var cycle_elapsed := 0.0
var loop_count := 0
var one_shot := false
var terminal := false
var walk_in_place := false
var run_in_place := false
var playback_speed := 1.0
var finished_count := 0
var last_finished := ""
var event_log: Array[Dictionary] = []
var action_axis := Vector2.ZERO
var jump_height := 0.0
var held_action := ""
var run_held := false

func configure(data: Dictionary, resource: SpriteFrames) -> bool:
	bank = data
	frames = resource
	if frames == null:
		return false
	clips.clear()
	for clip in bank.clips:
		clips[clip.name] = clip
	facing = str(bank.config.get("start_direction","SE"))
	if is_instance_valid(sprite):
		sprite.queue_free()
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.offset = Vector2(40,40)-Vector2(40,72)
	add_child(sprite)
	return enter("idle",true)

func direction_of(axis: Vector2) -> String:
	if axis.length_squared() < 0.0001:
		return facing
	var sector := posmod(roundi(axis.angle()/(PI/4.0)),8)
	return ["E","SE","S","SW","W","NW","N","NE"][sector]

func facing_axis() -> Vector2:
	return {"N":Vector2.UP,"NE":Vector2(1,-1),"E":Vector2.RIGHT,"SE":Vector2(1,1),"S":Vector2.DOWN,"SW":Vector2(-1,1),"W":Vector2.LEFT,"NW":Vector2(-1,-1)}[facing].normalized()

func set_facing(direction: String) -> bool:
	if one_shot or terminal or not bank.directions.has(direction):
		return false
	facing = direction
	return enter(state,true)

func set_aim(axis: Vector2) -> void:
	if axis.is_finite() and axis.length_squared() > 0.0001:
		aim_axis = axis.normalized()
		aim = direction_of(aim_axis)
		queue_redraw()

func enter(next_state: String, force := false) -> bool:
	var ready_state: Dictionary = bank.config.ready_states.get(next_state,{})
	var action: String = str(ready_state.get("source_action",next_state))
	var name := action+"_"+facing
	if not clips.has(name):
		return false
	var first := int(ready_state.get("frame",0))
	if first < 0 or first >= frames.get_frame_count(name):
		return false
	if not force and state == next_state and clip_name == name:
		return true
	state = next_state
	clip_name = name
	frame_index = first
	frame_elapsed = 0.0
	cycle_elapsed = 0.0
	loop_count = 0
	terminal = false
	one_shot = ready_state.is_empty() and not LOCOMOTION.has(state) and not HELD.has(state)
	jump_height = 0.0
	sprite.position.y = 0.0
	sprite.animation = name
	sprite.pause()
	sprite.set_frame_and_progress(frame_index,0.0)
	if ready_state.is_empty():
		emit_events(-0.000000001,0.0)
	queue_redraw()
	return true

func request_action(action: String, movement := Vector2.ZERO) -> bool:
	if not bank.actions.has(action) or LOCOMOTION.has(action) or HELD.has(action) or terminal or state == "death" or action == state:
		return false
	if one_shot and (not INTERRUPTS.has(action) or int(INTERRUPTS[action]) <= int(INTERRUPTS.get(state,0))):
		return false
	if not movement.is_finite():
		return false
	var next_axis := movement.limit_length(1.0)
	if action in ["dash","dodge"] and next_axis == Vector2.ZERO:
		next_axis = facing_axis()
	if action in ["dash","dodge"]:
		next_axis = next_axis.normalized()
	if next_axis != Vector2.ZERO:
		facing = direction_of(next_axis)
	if not enter(action,true):
		return false
	action_axis = next_axis
	return true

func set_controls(running: bool, guard: bool, crouch: bool) -> void:
	run_held = running and bank.actions.has("run")
	held_action = "guard" if guard and bank.actions.has("guard") else ("crouch" if crouch and bank.actions.has("crouch") else "")

func reset_actor() -> bool:
	walk_in_place = false
	run_in_place = false
	held_action = ""
	run_held = false
	action_axis = Vector2.ZERO
	return enter("idle",true)

func toggle_walk() -> void:
	if one_shot or terminal:
		return
	walk_in_place = not walk_in_place
	run_in_place = false
	enter("walk" if walk_in_place else "idle",true)

func emit_events(start: float, end: float) -> void:
	for entry in clips[clip_name].get("events",[]):
		var at := float(entry.time[0])/float(entry.time[1])
		if start < at and at <= end+0.0000000001:
			var event: Dictionary = entry.duplicate(true)
			event.merge({"clip":clip_name,"loop":loop_count,"scope":"Authored metadata only; no damage/effect behavior"},true)
			event_log.append(event)
			if event_log.size() > 64:
				event_log.pop_front()
			authored_event.emit(event)

func tick(delta: float, axis: Vector2) -> void:
	if not is_finite(delta) or delta < 0 or not is_finite(playback_speed) or playback_speed <= 0 or not axis.is_finite():
		return
	var movement := axis.limit_length(1.0)
	if not one_shot and not terminal:
		if not held_action.is_empty():
			enter(held_action)
		elif movement.length_squared() > 0:
			facing = direction_of(movement)
			enter("run" if run_held or run_in_place else "walk")
		elif HELD.has(state):
			enter("idle")
		elif state in ["walk","run"] and not walk_in_place:
			enter("idle")
	advance_clock(delta*playback_speed,movement,true)

func advance(seconds: float) -> void:
	advance_clock(seconds,Vector2.ZERO,false)

func update_motion(start: float, end: float, movement: Vector2, apply_ground: bool) -> void:
	var duration := float(clips[clip_name].duration[0])/float(clips[clip_name].duration[1])
	var p0 := clampf(start/duration,0.0,1.0)
	var p1 := clampf(end/duration,0.0,1.0)
	if apply_ground:
		if state in ["dash","dodge"]:
			# Integrated displacement, independent of frame cadence or delta subdivision.
			var progress0 := 1.0-pow(1.0-p0,3.0) if state == "dash" else p0-sin(TAU*p0)/TAU
			var progress1 := 1.0-pow(1.0-p1,3.0) if state == "dash" else p1-sin(TAU*p1)/TAU
			position += action_axis*float(bank.config.get(state+"_distance",42))*(progress1-progress0)
		elif state == "jump":
			var delay := float(bank.config.get("jump_takeoff_delay",0.1))
			# Only the airborne interval contributes displacement, including a step crossing takeoff.
			position += action_axis*float(bank.config.get("jump_move_speed",90))*(maxf(0.0,end-delay)-maxf(0.0,start-delay))
		elif state in ["walk","run"]:
			position += movement*float(bank.config.get("run_speed",160) if state == "run" else bank.config.move_speed)*(end-start)
	if state == "jump":
		var delay := float(bank.config.get("jump_takeoff_delay",0.1))
		var airborne_progress := clampf((end-delay)/maxf(duration-delay,0.000000001),0.0,1.0)
		jump_height = 4.0*float(bank.config.get("jump_height",22))*airborne_progress*(1.0-airborne_progress)
		sprite.position.y = -jump_height
		queue_redraw()

func advance_clock(seconds: float, movement: Vector2, apply_ground: bool) -> void:
	if not is_finite(seconds) or seconds < 0 or bank.config.ready_states.has(state) or terminal or clip_name.is_empty():
		return
	var left := seconds
	var budget := 10000
	while left > 0.0000000001 and budget > 0:
		budget -= 1
		var hold := frames.get_frame_duration(clip_name,frame_index)/frames.get_animation_speed(clip_name)
		var step := minf(left,maxf(0.0,hold-frame_elapsed))
		emit_events(cycle_elapsed,cycle_elapsed+step)
		update_motion(cycle_elapsed,cycle_elapsed+step,movement,apply_ground)
		frame_elapsed += step
		cycle_elapsed += step
		left -= step
		if frame_elapsed+0.0000000001 < hold:
			sprite.set_frame_and_progress(frame_index,frame_elapsed/hold)
			break
		frame_elapsed = 0.0
		frame_index += 1
		if frame_index >= frames.get_frame_count(clip_name):
			if state == "death":
				last_finished = state
				finished_count += 1
				terminal = true
				one_shot = false
				frame_index -= 1
				sprite.set_frame_and_progress(frame_index,1.0)
				return
			if not one_shot:
				if HELD.has(state) and not bool(clips[clip_name].loop):
					frame_index -= 1
					frame_elapsed = hold
					sprite.set_frame_and_progress(frame_index,1.0)
					return
				frame_index = 0
				cycle_elapsed = 0.0
				loop_count += 1
				emit_events(-0.000000001,0.0)
			else:
				last_finished = state
				finished_count += 1
				var target := str(bank.config.completion_return.get(state,"idle"))
				if not enter(target,true):
					push_error("Configured completion target unavailable")
					return
				if bank.config.ready_states.has(target):
					return
			sprite.set_frame_and_progress(frame_index,0.0)
		else:
			sprite.set_frame_and_progress(frame_index,0.0)
	if budget == 0:
		push_error("Inspector clock catch-up budget exceeded")

func snapshot() -> Dictionary:
	return {"state":state,"facing":facing,"aim":aim,"clip":clip_name,"frame":frame_index,"frame_elapsed":frame_elapsed,"cycle_elapsed":cycle_elapsed,
		"loops":loop_count,"one_shot":one_shot,"terminal":terminal,"jump_height":jump_height,"finished_count":finished_count,"last_finished":last_finished,"position":[position.x,position.y],"events":event_log.size()}

func _draw() -> void:
	# Ground shadow stays at the actor origin while the image rises during a jump.
	var radius := maxf(2.5,6.0-jump_height*0.10)
	draw_set_transform(Vector2.ZERO,0,Vector2(1,0.4))
	draw_circle(Vector2.ZERO,radius,Color(0,0,0,0.28))
	draw_set_transform(Vector2.ZERO)
	draw_circle(Vector2.ZERO,1.0,Color(0.3,0.9,0.8,0.35))
	draw_line(Vector2.ZERO,aim_axis*10,Color(0.9,0.75,0.3,0.8),0.5)
