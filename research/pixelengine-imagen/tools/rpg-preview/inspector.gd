extends Node2D
## Native inspector UI; input calls the same controller checked by validate.gd.

const Controller = preload("res://controller.gd")
var actor
var bank: Dictionary = {}
var is_ready := false
var autoplay := true
var status: Label
var events: Label
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
	actor.position = Vector2(550,500)
	actor.scale = Vector2(4,4)
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := VBoxContainer.new()
	panel.position = Vector2(22,16)
	canvas.add_child(panel)
	var title := Label.new()
	title.text = "HERO RPG BANK INSPECTOR · 8 DIRECTIONS / 6 ACTIONS"
	title.add_theme_font_size_override("font_size",22)
	panel.add_child(title)
	var help := Label.new()
	help.text = "Arrows / WASD move   J punch   K cast   L dodge   H hurt   Space idle / in-place walk\nRight mouse sets aim independently. Direction selector changes facing while ready."
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
	for action in ["idle","walk","punch","cast","dodge","hurt"]:
		var button := Button.new()
		button.text = action.capitalize()
		button.focus_mode = Control.FOCUS_NONE
		button.pressed.connect(func(): choose_action(action))
		row.add_child(button)
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
	note.text = "Punch → punch frame0 ready; cast → cast frame0 ready; hurt/dodge → idle.\nBody only. Anchors pending. Movement, collision, contact and damage windows unverified. New art needs review."
	note.modulate = Color(0.7,0.8,0.85)
	panel.add_child(note)
	is_ready = true
	queue_redraw()

func choose_action(action: String) -> void:
	if not is_ready:
		return
	if action in ["idle","walk"]:
		if not actor.one_shot:
			actor.walk_in_place = action == "walk"
			actor.enter(action,true)
	else:
		actor.request_action(action)

func key_action(code: int) -> void:
	if not is_ready:
		return
	match code:
		KEY_J: actor.request_action("punch")
		KEY_K: actor.request_action("cast")
		KEY_L: actor.request_action("dodge")
		KEY_H: actor.request_action("hurt")
		KEY_SPACE: actor.toggle_walk()

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
