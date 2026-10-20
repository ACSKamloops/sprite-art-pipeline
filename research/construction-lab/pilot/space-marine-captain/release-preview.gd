extends Control
const Clock = preload("res://hold_clock.gd")
var timeline = Clock.new()
var manifest: Dictionary
var contacts: Dictionary
var actor: AnimatedSprite2D
var clock := 0.0
var playing := true
var zoom := 2
var rate := 1.0
var follow := true
var contact_lock := true
var status: Label
var camera := Vector2.ZERO
func _ready() -> void:
	var approval = JSON.parse_string(FileAccess.get_file_as_string("res://approval.json"))
	assert(FileAccess.get_sha256("res://sprites/manifest.json") == approval.candidate_manifest_sha256)
	assert(FileAccess.get_sha256("res://contact-policy.json") == approval.contact_policy_sha256)
	assert(FileAccess.get_sha256("res://captain-walk.tres") == approval.sprite_resource_sha256)
	manifest = JSON.parse_string(FileAccess.get_file_as_string("res://sprites/manifest.json"))
	contacts = JSON.parse_string(FileAccess.get_file_as_string("res://contact-policy.json"))
	for row in manifest.frames:
		assert(FileAccess.get_sha256("res://sprites/"+row.file) == row.sha256)
	assert(timeline.configure(manifest))
	actor = AnimatedSprite2D.new()
	actor.sprite_frames = load("res://captain-walk.tres")
	actor.animation = "combat_ready_walk"
	actor.centered = false
	actor.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(actor)
	var panel := VBoxContainer.new()
	panel.position = Vector2(12,12)
	add_child(panel)
	var title := Label.new()
	title.text = "Captain | combat-ready walk | one authored view"
	panel.add_child(title)
	var controls := HBoxContainer.new()
	panel.add_child(controls)
	for caption in ["Play / Pause", "Restart", "Step", "Native / 2x", "Speed", "Camera", "Contact lock"]:
		var button := Button.new()
		button.text = caption
		button.pressed.connect(func(): command(caption))
		controls.add_child(button)
	status = Label.new()
	panel.add_child(status)
	present()
func command(caption: String) -> void:
	match caption:
		"Play / Pause": playing = not playing
		"Restart": clock = 0.0
		"Step":
			playing = false
			clock = timeline.next_boundary(clock)
		"Native / 2x": zoom = 3-zoom
		"Speed": rate = .5 if rate == 2.0 else rate*2.0
		"Camera": follow = not follow
		"Contact lock": contact_lock = not contact_lock
	present()
func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE: command("Play / Pause")
			KEY_RIGHT: command("Step")
			KEY_R: command("Restart")
			KEY_Z: command("Native / 2x")
func present() -> void:
	var state = timeline.locate(clock)
	var row = manifest.frames[state.frame]
	var physical = timeline.physical_root(manifest,state)
	var correction := Vector2.ZERO
	if contact_lock:
		for side in ["right","left"]:
			if row.landmarks[side].declared_stance:
				# One complete-actor correction from a source-attached stance
				# pose root; never fit separate boots or artwork to the floor.
				var target = contacts.frames[state.frame].support_world[side]
				var sole = row.landmarks[side].actual_sole
				correction = Vector2(target[0]-sole[0],target[1]-sole[1])+Vector2(manifest.root_stride[0],manifest.root_stride[1])*state.cycle-physical
				break
	camera = physical if follow else Vector2.ZERO
	actor.scale = Vector2.ONE*zoom
	actor.position = (Vector2(180,116)+(physical-camera+correction)*zoom).round()
	actor.set_frame_and_progress(state.frame,state.progress)
	status.text = "Pose %02d/72 | %.0f ms / 1200 | %.1fx speed | %dx | %s" % [state.frame+1,fposmod(clock*1000.0,timeline.cycle_ms),rate,zoom,"playing" if playing else "paused"]
	queue_redraw()
func _process(delta: float) -> void:
	if playing: clock += delta*rate
	present()
func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO,size),Color8(43,50,56))
	var shift = -camera*zoom
	for x in range(-1800,1801,16):
		var px = 180+x*zoom+shift.x
		draw_line(Vector2(px,100),Vector2(px,size.y),Color8(62,71,77))
	for y in range(-1800,1801,16):
		var py = 116+y*zoom+shift.y
		if py >= 100: draw_line(Vector2(0,py),Vector2(size.x,py),Color8(62,71,77))
