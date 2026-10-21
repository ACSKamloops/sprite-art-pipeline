extends SceneTree
## Bounded resource/state/input check against the actual supplied48clip bank.

const Inspector = preload("res://inspector.gd")
var checks := 0
var failures: Array[String] = []

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
	check(resource.get_animation_names().size() == 48,"All48resource animations")
	var inspector = Inspector.new()
	inspector.autoplay = false
	root.add_child(inspector)
	await process_frame
	check(inspector.is_ready,"Inspector configured outside assert")
	if not inspector.is_ready:
		quit(1)
		return
	var actor = inspector.actor
	var axes := {"N":Vector2(0,-1),"NE":Vector2(1,-1),"E":Vector2(1,0),"SE":Vector2(1,1),"S":Vector2(0,1),"SW":Vector2(-1,1),"W":Vector2(-1,0),"NW":Vector2(-1,-1)}
	for direction in bank.directions:
		actor.enter("idle",true)
		actor.walk_in_place = false
		actor.tick(0.01,axes[direction])
		check(actor.facing == direction and actor.state == "walk","Movement direction "+direction)
		actor.tick(0.0,Vector2.ZERO)
		check(actor.state == "idle","Movement release idle "+direction)
		actor.enter("walk",true)
		var walk: Dictionary = actor.clips[actor.clip_name]
		var first_hold := float(walk.frames[0].hold[0])/float(walk.frames[0].hold[1])
		actor.advance(duration(walk)*2.0+first_hold*0.5)
		check(actor.loop_count == 2 and actor.frame_index == 0,"Two exact walk loops "+direction)
		check(absf(actor.frame_elapsed-first_hold*0.5) < 0.00000001,"Walk fractional hold retained "+direction)
		for action in ["punch","cast","dodge","hurt"]:
			actor.enter("idle",true)
			var before: int = actor.finished_count
			check(actor.request_action(action),"Action entry "+direction+" "+action)
			check(actor.one_shot and actor.state == action,"Action lock "+direction+" "+action)
			check(not actor.request_action(action),"No accidental restart during one-shot")
			var selected: Dictionary = actor.clips[actor.clip_name]
			var last_texture := resource.get_frame_texture(actor.clip_name,resource.get_frame_count(actor.clip_name)-1)
			var last_pixels := last_texture.get_image().get_data()
			actor.advance(duration(selected)+0.0037)
			var target: String = bank.config.completion_return[action]
			check(actor.state == target and not actor.one_shot,"Configured completion "+direction+" "+action)
			check(actor.finished_count == before+1 and actor.last_finished == action,"Visible finished marker")
			var ready_pixels := resource.get_frame_texture(actor.clip_name,actor.frame_index).get_image().get_data()
			check(last_pixels == ready_pixels,"Exact painted completion endpoint "+direction+" "+action)
			if target == "idle":
				check(absf(actor.cycle_elapsed-0.0037) < 0.00000001,"Fractional carry into idle")
			else:
				check(actor.frame_index == int(bank.config.ready_states[target].frame),"Configured existing ready frame")
				check(actor.clips[actor.clip_name].action == action,"Ready uses own action source")
				actor.advance(0.23)
				check(actor.cycle_elapsed == 0.0,"Configured ready stays held")
	# Input events go through Godot's event dispatch and the actual UI/controller bridge.
	var movement_keys := {"N":[KEY_UP],"NE":[KEY_UP,KEY_RIGHT],"E":[KEY_RIGHT],"SE":[KEY_DOWN,KEY_RIGHT],"S":[KEY_DOWN],"SW":[KEY_DOWN,KEY_LEFT],"W":[KEY_LEFT],"NW":[KEY_UP,KEY_LEFT]}
	for direction in movement_keys:
		actor.enter("idle",true)
		for code in movement_keys[direction]:
			await press(code,true)
		actor.tick(0.01,inspector.keyboard_axis())
		check(actor.facing == direction and actor.state == "walk","Physical-key direction "+direction)
		for code in movement_keys[direction]:
			await press(code,false)
		check(inspector.keyboard_axis() == Vector2.ZERO,"Physical-key release cleared")
	for code in [KEY_J,KEY_K,KEY_L,KEY_H]:
		actor.enter("idle",true)
		await press(code,true)
		await press(code,false)
		var action: String = {KEY_J:"punch",KEY_K:"cast",KEY_L:"dodge",KEY_H:"hurt"}[code]
		check(actor.state == action and actor.one_shot,"Physical action key "+action)
		actor.advance(duration(actor.clips[actor.clip_name])+0.001)
	actor.enter("idle",true)
	actor.walk_in_place = false
	await press(KEY_SPACE,true)
	await press(KEY_SPACE,false)
	check(actor.state == "walk" and actor.walk_in_place,"Space starts in-place walk")
	await press(KEY_SPACE,true)
	await press(KEY_SPACE,false)
	check(actor.state == "idle" and not actor.walk_in_place,"Space returns idle")
	actor.set_facing("N")
	actor.set_aim(Vector2.RIGHT)
	check(actor.facing == "N" and actor.aim == "E","Aim remains independent from facing")
	actor.request_action("cast")
	check(actor.clip_name == "cast_N" and actor.aim == "E","Casting does not invent aim-facing art")
	var se: Dictionary = actor.clips["walk_SE"]
	check(se.source_clip_id == bank.preferred_source_clip and se.role == "preferred","Preferred SE walk binding preserved")
	check(bank.config.anchors.hand == "pending measurement" and bank.config.anchors.grip == "pending measurement" and bank.config.anchors.release == "pending measurement","No invented anchors")
	var report := {"schema":"rpg-godot-inspector-validation/v1","godot_version":Engine.get_version_info().string,"checks":checks,"failures":failures,
		"resource_animations":48,"direction_action_completions":32,"physical_direction_inputs":8,"physical_action_inputs":4,
		"fractional_completion_carry_checked":true,"independent_aim_checked":true,"preferred_SE_original_checked":true,
		"scope":"Actual headless Godot resources, input dispatch and controller clocks/states. No GPU rendering, contact/collision or human art-quality approval."}
	FileAccess.open("res://RUNTIME-VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("RPG_INSPECTOR_VALIDATION ",JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
