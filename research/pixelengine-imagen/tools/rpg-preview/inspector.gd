extends Node2D
## Native inspector UI; input calls the same controller checked by validate.gd.

const Controller = preload("res://controller.gd")
const PREVIEW_ORIGIN := Vector2(550,640)
var actor
var bank: Dictionary = {}
var is_ready := false
var autoplay := true
var status: Label
var events: Label
var button_hold := ""
var direction: OptionButton

func _ready() -> void:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://bank.json"))
	if not parsed is Dictionary:
		push_error("Missing bank.json")
		return
	bank = parsed
	var resource := load("res://hero_frames.res") as SpriteFrames
	actor = Controller.new()
	add_child(actor)
	if not actor.configure(bank,resource):
		push_error("Inspector resource/configuration failed; run build_resources.gd first")
		return
	actor.position = PREVIEW_ORIGIN
	actor.scale = Vector2(3,3)
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := VBoxContainer.new()
	panel.position = Vector2(22,16)
	canvas.add_child(panel)
	var title := Label.new()
	title.text = "HERO RPG BANK INSPECTOR · %d DIRECTIONS / %d ACTIONS" % [bank.directions.size(),bank.actions.size()]
	title.add_theme_font_size_override("font_size",22)
	panel.add_child(title)
	var help := Label.new()
	help.text = ("Arrows/WASD move · Shift run · Z punch · V cast · Q dash · Space dodge · J jump\nG guard (hold) · C crouch (hold) · H hurt · T stun · K knockdown · X death · F interact · R reset · I walk in place"
		if expanded_controls() else "Arrows/WASD move · J punch · K cast · L dodge · H hurt · Space walk in place")
	panel.add_child(help)
	var row := HBoxContainer.new()
	panel.add_child(row)
	direction = OptionButton.new()
	direction.focus_mode = Control.FOCUS_NONE
	for view in bank.directions:
		direction.add_item(view)
	direction.select(bank.directions.find(actor.facing))
	direction.item_selected.connect(func(index): actor.set_facing(str(bank.directions[index])))
	row.add_child(direction)
	var reset := Button.new()
	reset.text = "Reset"
	reset.focus_mode = Control.FOCUS_NONE
	reset.pressed.connect(reset_preview)
	row.add_child(reset)
	var buttons := GridContainer.new()
	buttons.columns = 9
	panel.add_child(buttons)
	for action in bank.actions:
		var button := Button.new()
		button.text = action.capitalize()
		button.focus_mode = Control.FOCUS_NONE
		if action in ["guard","crouch"]:
			button.button_down.connect(func(): button_hold = action)
			button.button_up.connect(func(): button_hold = "")
		else:
			button.pressed.connect(func(): choose_action(action))
		buttons.add_child(button)
	var speed := OptionButton.new()
	speed.focus_mode = Control.FOCUS_NONE
	for label in ["0.25×","0.5×","1×","2×"]:
		speed.add_item(label)
	speed.select(2)
	speed.item_selected.connect(func(index): actor.playback_speed = [0.25,0.5,1.0,2.0][index])
	row.add_child(speed)
	status = Label.new()
	panel.add_child(status)
	events = Label.new()
	panel.add_child(events)
	var note := Label.new()
	note.text = "Punch/cast -> own ready pose. Jump -> land -> idle. Knockdown -> get-up -> idle. Death holds until reset.\nGround movement and jump height are explicit mechanics. No collision, damage or invulnerability. Art needs playback review."
	note.modulate = Color(0.7,0.8,0.85)
	panel.add_child(note)
	is_ready = true
	queue_redraw()

func reset_preview() -> void:
	actor.reset_actor()
	actor.position = PREVIEW_ORIGIN

func expanded_controls() -> bool:
	return str(bank.config.get("controls","legacy")) == "expanded"

func choose_action(action: String) -> void:
	if not is_ready:
		return
	if action in ["idle","walk","run"]:
		if not actor.one_shot and not actor.terminal:
			actor.walk_in_place = action != "idle"
			actor.run_in_place = action == "run"
			actor.enter(action,true)
	else:
		actor.request_action(action,keyboard_axis())

func key_action(code: int) -> void:
	if not is_ready:
		return
	if expanded_controls():
		var actions := {KEY_Z:"punch",KEY_V:"cast",KEY_Q:"dash",KEY_SPACE:"dodge",KEY_J:"jump",KEY_H:"hurt",KEY_T:"stun",KEY_K:"knockdown",KEY_X:"death",KEY_F:"interact"}
		if actions.has(code):
			actor.request_action(actions[code],keyboard_axis())
		elif code == KEY_R:
			reset_preview()
		elif code == KEY_I:
			actor.toggle_walk()
	else:
		match code:
			KEY_J: actor.request_action("punch")
			KEY_K: actor.request_action("cast")
			KEY_L: actor.request_action("dodge",keyboard_axis())
			KEY_H: actor.request_action("hurt")
			KEY_SPACE: actor.toggle_walk()

func update_controls() -> void:
	actor.set_controls(Input.is_physical_key_pressed(KEY_SHIFT),
		button_hold == "guard" or Input.is_physical_key_pressed(KEY_G),
		button_hold == "crouch" or Input.is_physical_key_pressed(KEY_C))

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		key_action(event.physical_keycode if event.physical_keycode != 0 else event.keycode)
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT and event.pressed and is_ready:
		actor.set_aim(get_global_mouse_position()-actor.position)

func keyboard_axis() -> Vector2:
	var x := int(Input.is_physical_key_pressed(KEY_RIGHT) or Input.is_physical_key_pressed(KEY_D))-int(Input.is_physical_key_pressed(KEY_LEFT) or Input.is_physical_key_pressed(KEY_A))
	var y := int(Input.is_physical_key_pressed(KEY_DOWN) or Input.is_physical_key_pressed(KEY_S))-int(Input.is_physical_key_pressed(KEY_UP) or Input.is_physical_key_pressed(KEY_W))
	return Vector2(x,y).limit_length(1.0)

func _physics_process(delta: float) -> void:
	if is_ready and autoplay:
		update_controls()
		actor.tick(delta,keyboard_axis())
		actor.position = actor.position.clamp(Vector2(40,330),get_viewport_rect().size-Vector2(40,20))

func _process(_delta: float) -> void:
	if not is_ready:
		return
	var frame = actor.clips[actor.clip_name]
	status.text = "STATE %s   FACING %s   AIM %s   FRAME %d/%d   FINISHED %s (%d)\n%s · %s · %s" % [actor.state,actor.facing,actor.aim,actor.frame_index+1,frame.frames.size(),actor.last_finished,actor.finished_count,actor.clip_name,frame.role,frame.review_status]
	direction.select(bank.directions.find(actor.facing))
	if actor.event_log.is_empty():
		events.text = "Authored events: none crossed"
	else:
		var event: Dictionary = actor.event_log[-1]
		events.text = "Authored event: %s @ %s/%s s · metadata only" % [event.name,event.time[0],event.time[1]]

func _draw() -> void:
	for x in range(0,1200,40):
		draw_line(Vector2(x,300),Vector2(x,800),Color(0.2,0.28,0.34,0.5))
	for y in range(300,800,40):
		draw_line(Vector2(0,y),Vector2(1200,y),Color(0.2,0.28,0.34,0.5))
