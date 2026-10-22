extends SceneTree
## Actual supplied-bank resource, state, physical input and deterministic motion checks.
const Inspector = preload("res://inspector.gd")
var checks := 0
var failures: Array[String] = []
var completions := 0
var action_inputs := 0

func check(value: bool, label: String) -> void:
	checks += 1
	if not value:
		failures.append(label)

func press(code: int, down: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = down
	Input.parse_input_event(event)
	await process_frame

func duration(clip: Dictionary) -> float:
	return float(clip.duration[0])/float(clip.duration[1])

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var bank = JSON.parse_string(FileAccess.get_file_as_string("res://bank.json"))
	var resource := load("res://hero_frames.res") as SpriteFrames
	if not bank is Dictionary or resource == null:
		push_error("Run build_resources.gd first")
		quit(1)
		return
	check(resource.get_animation_names().size() == bank.directions.size()*bank.actions.size(),"Declared resource coverage")
	var inspector = Inspector.new()
	inspector.autoplay = false
	root.add_child(inspector)
	await process_frame
	check(inspector.is_ready,"Inspector configured outside assert")
	if not inspector.is_ready:
		quit(1)
		return
	var actor = inspector.actor
	var axes := {"N":Vector2.UP,"NE":Vector2(1,-1),"E":Vector2.RIGHT,"SE":Vector2(1,1),"S":Vector2.DOWN,"SW":Vector2(-1,1),"W":Vector2.LEFT,"NW":Vector2(-1,-1)}
	for view in bank.directions:
		actor.reset_actor()
		actor.tick(0.01,axes[view])
		check(actor.facing == view and actor.state == "walk","Movement direction "+view)
		actor.tick(0.0,Vector2.ZERO)
		check(actor.state == "idle","Movement release idle "+view)
		actor.enter("walk",true)
		var walk: Dictionary = actor.clips[actor.clip_name]
		var hold := float(walk.frames[0].hold[0])/float(walk.frames[0].hold[1])
		actor.advance(duration(walk)*2.0+hold*0.5)
		check(actor.loop_count == 2 and actor.frame_index == 0,"Exact loops "+view)
		check(absf(actor.frame_elapsed-hold*0.5) < 0.00000001,"Fractional hold "+view)
		for action in bank.actions:
			actor.reset_actor()
			actor.set_facing(view)
			if action in ["idle","walk","run"]:
				check(actor.enter(action,true),"Locomotion resource "+view+action)
				continue
			if action in ["guard","crouch"]:
				actor.set_controls(false,action == "guard",action == "crouch")
				actor.tick(0.01,axes[view])
				check(actor.state == action and not actor.one_shot,"Held input "+view+action)
				var held_position: Vector2 = actor.position
				actor.tick(duration(actor.clips[actor.clip_name])*2.1,axes[view])
				check(actor.position == held_position and actor.state == action,"Held stationary "+view+action)
				actor.set_controls(false,false,false)
				actor.tick(0,Vector2.ZERO)
				check(actor.state == "idle","Held release "+view+action)
				continue
			check(actor.request_action(action),"Action entry "+view+action)
			check(actor.one_shot and actor.state == action,"Action lock "+view+action)
			check(not actor.request_action(action),"No duplicate action "+view+action)
			check(not actor.set_facing("N"),"Locked facing "+view+action)
			var before: int = actor.finished_count
			actor.advance(duration(actor.clips[actor.clip_name])+0.0037)
			completions += 1
			if action == "death":
				check(actor.terminal and actor.state == "death","Terminal death "+view)
				var snap: Dictionary = actor.snapshot()
				actor.tick(2,axes[view])
				check(actor.snapshot() == snap and not actor.request_action("hurt"),"Death immutable until reset "+view)
				check(actor.frame_index == resource.get_frame_count(actor.clip_name)-1,"Death final frame "+view)
			else:
				var target: String = bank.config.completion_return.get(action,"idle")
				check(actor.state == target,"Configured completion "+view+action)
				check(actor.finished_count == before+1 and actor.last_finished == action,"Completion count "+view+action)
				if target == "idle":
					check(absf(actor.cycle_elapsed-0.0037) < 0.00000001,"Fractional carry "+view+action)
				elif bank.config.ready_states.has(target):
					var ready = bank.config.ready_states[target]
					check(actor.frame_index == int(ready.frame) and actor.clips[actor.clip_name].action == ready.source_action,"Ready source "+view+action)
					actor.advance(0.23)
					check(actor.cycle_elapsed == 0,"Ready holds "+view+action)
				else:
					check(actor.one_shot,"Dependent action locks "+view+action)
					actor.advance(duration(actor.clips[actor.clip_name]))
					check(actor.state == "idle","Dependent action recovers "+view+action)
		if bank.actions.has("run"):
			actor.reset_actor()
			actor.set_controls(true,false,false)
			var origin: Vector2 = actor.position
			actor.tick(0.25,axes[view])
			check(actor.state == "run" and actor.position.is_equal_approx(origin+axes[view].normalized()*float(bank.config.run_speed)*0.25),"Run speed "+view)
			actor.set_controls(false,false,false)
			actor.tick(0,axes[view])
			check(actor.state == "walk","Run release walks "+view)
			actor.tick(0,Vector2.ZERO)
			check(actor.state == "idle","Run stop idles "+view)
		# Integrated distances must be identical for cardinal/diagonal and subdivided time.
		for action in ["dash","dodge"]:
			if not bank.actions.has(action):
				continue
			actor.reset_actor()
			actor.set_facing(view)
			var origin: Vector2 = actor.position
			actor.request_action(action,axes[view]*0.1)
			var length := duration(actor.clips[actor.clip_name])
			actor.tick(length,Vector2.ZERO)
			var displacement: Vector2 = actor.position-origin
			check(displacement.is_equal_approx(axes[view].normalized()*float(bank.config[action+"_distance"])),"Normalized full distance "+view+action)
			actor.reset_actor()
			actor.position = origin
			actor.request_action(action,axes[view])
			for step in 37:
				actor.tick(length/37.0,Vector2.ZERO)
			check(actor.position.is_equal_approx(origin+displacement),"Subdivision invariant "+view+action)
		if bank.actions.has("jump"):
			actor.reset_actor()
			actor.set_facing(view)
			var ground: Vector2 = actor.position
			actor.request_action("jump",axes[view])
			var length := duration(actor.clips[actor.clip_name])
			actor.tick(length/2,Vector2.ZERO)
			check(is_equal_approx(actor.jump_height,float(bank.config.jump_height)) and is_equal_approx(actor.sprite.position.y,-actor.jump_height),"Separate jump height "+view)
			check(actor.position.is_equal_approx(ground+axes[view].normalized()*float(bank.config.jump_move_speed)*length/2),"Jump ground travel "+view)
			actor.tick(length/2,Vector2.ZERO)
			check(actor.state == "land" and actor.jump_height == 0 and actor.sprite.position.y == 0,"Jump land transition "+view)
		if bank.actions.has("hurt") and bank.actions.has("punch"):
			actor.reset_actor()
			actor.request_action("punch")
			check(actor.request_action("hurt") and not actor.request_action("punch"),"Hurt interrupts attack "+view)
			if bank.actions.has("stun"):
				check(actor.request_action("stun") and not actor.request_action("hurt"),"Stun priority "+view)
			if bank.actions.has("knockdown"):
				check(actor.request_action("knockdown") and not actor.request_action("stun"),"Knockdown priority "+view)
			if bank.actions.has("death"):
				check(actor.request_action("death") and not actor.request_action("knockdown"),"Death priority "+view)
	# Physical input goes through Godot event dispatch and the inspector bridge.
	var movement_keys := {"N":[KEY_UP],"NE":[KEY_UP,KEY_RIGHT],"E":[KEY_RIGHT],"SE":[KEY_DOWN,KEY_RIGHT],"S":[KEY_DOWN],"SW":[KEY_DOWN,KEY_LEFT],"W":[KEY_LEFT],"NW":[KEY_UP,KEY_LEFT]}
	for view in movement_keys:
		actor.reset_actor()
		for code in movement_keys[view]:
			await press(code,true)
		actor.tick(0.01,inspector.keyboard_axis())
		check(actor.facing == view and actor.state == "walk","Physical movement "+view)
		for code in movement_keys[view]:
			await press(code,false)
		check(inspector.keyboard_axis() == Vector2.ZERO,"Physical movement release "+view)
	var bindings := {KEY_J:"punch",KEY_K:"cast",KEY_L:"dodge",KEY_H:"hurt"}
	if inspector.expanded_controls():
		bindings = {KEY_Z:"punch",KEY_V:"cast",KEY_Q:"dash",KEY_SPACE:"dodge",KEY_J:"jump",KEY_H:"hurt",KEY_T:"stun",KEY_K:"knockdown",KEY_X:"death",KEY_F:"interact"}
	for code in bindings:
		if not bank.actions.has(bindings[code]):
			continue
		actor.reset_actor()
		await press(code,true)
		await press(code,false)
		check(actor.state == bindings[code] and actor.one_shot,"Physical action "+bindings[code])
		action_inputs += 1
	if inspector.expanded_controls():
		for code in [KEY_G,KEY_C,KEY_SHIFT]:
			actor.reset_actor()
			await press(code,true)
			inspector.update_controls()
			actor.tick(0.01,Vector2.RIGHT if code == KEY_SHIFT else Vector2.ZERO)
			var expected: String = {KEY_G:"guard",KEY_C:"crouch",KEY_SHIFT:"run"}[code]
			if bank.actions.has(expected):
				check(actor.state == expected,"Physical held "+expected)
			await press(code,false)
			inspector.update_controls()
			actor.tick(0,Vector2.ZERO)
			check(actor.state == "idle","Physical held release "+expected)
		actor.request_action("death")
		await press(KEY_R,true)
		await press(KEY_R,false)
		check(actor.state == "idle" and not actor.terminal,"Physical reset")
	actor.reset_actor()
	var unchanged: Dictionary = actor.snapshot()
	actor.tick(-1,Vector2.RIGHT)
	actor.tick(NAN,Vector2.ZERO)
	actor.tick(0.1,Vector2(INF,0))
	check(actor.snapshot() == unchanged,"Invalid time and axis ignored")
	var toggle: int = KEY_I if inspector.expanded_controls() else KEY_SPACE
	await press(toggle,true)
	await press(toggle,false)
	check(actor.state == "walk" and actor.walk_in_place,"In-place walk input")
	await press(toggle,true)
	await press(toggle,false)
	check(actor.state == "idle" and not actor.walk_in_place,"In-place walk release")
	actor.set_facing("N")
	actor.set_aim(Vector2.RIGHT)
	check(actor.facing == "N" and actor.aim == "E","Independent aim")
	if bank.actions.has("cast"):
		actor.request_action("cast")
		check(actor.clip_name == "cast_N" and actor.aim == "E","Cast facing art")
	var se: Dictionary = actor.clips["walk_SE"]
	check(se.source_clip_id == bank.preferred_source_clip and se.role == "preferred","Preferred SE original")
	var report := {"schema":"rpg-godot-inspector-validation/v1","godot_version":Engine.get_version_info().string,"checks":checks,"failures":failures,
		"resource_animations":resource.get_animation_names().size(),"direction_action_completions":completions,"physical_direction_inputs":8,"physical_action_inputs":action_inputs,
		"fractional_completion_carry_checked":true,"independent_aim_checked":true,"preferred_SE_original_checked":true,
		"scope":"Actual headless resources, input dispatch, controller clocks/states and motion. No GPU rendering, collision, damage, invulnerability or human art-quality approval. Fixture aliases do not prove new art coverage."}
	FileAccess.open("res://RUNTIME-VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("RPG_INSPECTOR_VALIDATION ",JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
