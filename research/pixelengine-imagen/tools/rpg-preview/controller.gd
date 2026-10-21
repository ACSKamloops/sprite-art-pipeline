extends Node2D
## Inspector clock and state routes. Authored events are inert observation data.

signal authored_event(event: Dictionary)

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
var walk_in_place := false
var playback_speed := 1.0
var finished_count := 0
var last_finished := ""
var event_log: Array[Dictionary] = []

func configure(data: Dictionary, resource: SpriteFrames) -> bool:
	bank = data
	frames = resource
	if frames == null:
		return false
	clips.clear()
	for clip in bank.clips:
		clips[clip.name] = clip
	facing = str(bank.config.get("start_direction","SE"))
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.offset = Vector2(40,40)-Vector2(40,72)
	add_child(sprite)
	return enter("idle")

func direction_of(axis: Vector2) -> String:
	if axis.length_squared() < 0.0001:
		return facing
	var sector := posmod(roundi(axis.angle()/(PI/4.0)),8)
	return ["E","SE","S","SW","W","NW","N","NE"][sector]

func set_facing(direction: String) -> bool:
	if one_shot or not bank.directions.has(direction):
		return false
	facing = direction
	return enter(state, true)

func set_aim(axis: Vector2) -> void:
	if axis.length_squared() > 0.0001:
		aim_axis = axis.normalized()
		aim = direction_of(aim_axis)
		queue_redraw()

func enter(next_state: String, force := false) -> bool:
	var ready_state: Dictionary = bank.config.ready_states.get(next_state,{})
	var action: String = str(ready_state.get("source_action",next_state))
	var name := action + "_" + facing
	if not clips.has(name):
		return false
	if not force and state == next_state and clip_name == name:
		return true
	state = next_state
	clip_name = name
	frame_index = int(ready_state.get("frame",0))
	if frame_index < 0 or frame_index >= frames.get_frame_count(name):
		return false
	frame_elapsed = 0.0
	cycle_elapsed = 0.0
	loop_count = 0
	one_shot = not bool(clips[name].loop) and ready_state.is_empty()
	sprite.animation = name
	sprite.pause()
	sprite.set_frame_and_progress(frame_index,0.0)
	if ready_state.is_empty():
		emit_events(-0.000000001,0.0)
	return true

func request_action(action: String) -> bool:
	if one_shot or not ["punch","cast","hurt","dodge"].has(action):
		return false
	return enter(action,true)

func toggle_walk() -> void:
	if one_shot:
		return
	walk_in_place = not walk_in_place
	enter("walk" if walk_in_place else "idle",true)

func emit_events(start: float, end: float) -> void:
	for entry in clips[clip_name].get("events",[]):
		var at := float(entry.time[0])/float(entry.time[1])
		if start < at and at <= end+0.0000000001:
			var event: Dictionary = entry.duplicate(true)
			event.merge({"clip":clip_name,"loop":loop_count,"scope":"Authored metadata only; no damage/effect behavior"},true)
			event_log.append(event)
			if event_log.size() > 24:
				event_log.pop_front()
			authored_event.emit(event)

func tick(delta: float, axis: Vector2) -> void:
	if not is_finite(delta) or delta < 0 or not is_finite(playback_speed) or playback_speed <= 0:
		return
	var movement := axis.limit_length(1.0)
	if not one_shot:
		if movement.length_squared() > 0:
			facing = direction_of(movement)
			enter("walk")
			position += movement*float(bank.config.move_speed)*delta
		elif state == "walk" and not walk_in_place:
			enter("idle")
	advance(delta*playback_speed)

func advance(seconds: float) -> void:
	if bank.config.ready_states.has(state) or clip_name.is_empty():
		return
	var left := seconds
	var budget := 10000
	while left > 0.0000000001 and budget > 0:
		budget -= 1
		var hold := frames.get_frame_duration(clip_name,frame_index)/frames.get_animation_speed(clip_name)
		var step := minf(left,maxf(0.0,hold-frame_elapsed))
		emit_events(cycle_elapsed,cycle_elapsed+step)
		frame_elapsed += step
		cycle_elapsed += step
		left -= step
		if frame_elapsed+0.0000000001 < hold:
			sprite.set_frame_and_progress(frame_index,frame_elapsed/hold)
			break
		frame_elapsed = 0.0
		frame_index += 1
		if frame_index >= frames.get_frame_count(clip_name):
			if bool(clips[clip_name].loop):
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
		"loops":loop_count,"one_shot":one_shot,"finished_count":finished_count,"last_finished":last_finished,"position":[position.x,position.y],"events":event_log.size()}

func _draw() -> void:
	draw_circle(Vector2.ZERO,2.0,Color(0.3,0.9,0.8,0.35))
	draw_line(Vector2.ZERO,aim_axis*10,Color(0.9,0.75,0.3,0.8),0.5)
