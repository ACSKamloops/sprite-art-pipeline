extends Control
var sprite: AnimatedSprite2D
var clock := 0.0
var speed := 1.0
static var source_dir := ""
static var source_manifest: Dictionary = {}
var playing := true
var zoom := 2
var viewport: SubViewport
var preview: TextureRect
var status: Label
static func frames_resource() -> SpriteFrames:
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(source_dir+"/manifest.json"))
	source_manifest = manifest
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	frames.add_animation("experimental_walk")
	frames.set_animation_speed("experimental_walk", 60.0)
	frames.set_animation_loop("experimental_walk", true)
	assert(manifest.canvas[0] == 256 and manifest.canvas[1] == 256 and manifest.frames.size() == 72)
	for i in range(72):
		var row = manifest.frames[i]
		assert(row.frame == i and abs(row.duration_ms-1000.0/60.0)<1e-9)
		var path = source_dir+"/"+row.file
		assert(FileAccess.get_sha256(path) == row.sha256)
		frames.add_frame("experimental_walk", ImageTexture.create_from_image(Image.load_from_file(path)), 1.0)
	return frames
func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--source="): source_dir=arg.substr(9)
	assert(not source_dir.is_empty())
	var column := VBoxContainer.new()
	column.position = Vector2(10,10)
	add_child(column)
	var title := Label.new()
	title.text = "Source-bound Captain lab | 72 × 1/60 s | art/contact reviews separate"
	column.add_child(title)
	var buttons := HBoxContainer.new()
	column.add_child(buttons)
	for name in ["Play/Pause", "Restart", "Step", "1× / 2×", "Speed"]:
		var button := Button.new()
		button.text = name
		buttons.add_child(button)
		button.pressed.connect(func(): command(name))
	viewport = SubViewport.new()
	viewport.size = Vector2i(256,256)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.transparent_bg = false
	add_child(viewport)
	var bg := ColorRect.new()
	bg.size = Vector2(256,256)
	bg.color = Color8(61,70,82)
	viewport.add_child(bg)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames_resource()
	sprite.animation = "experimental_walk"
	sprite.centered = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	viewport.add_child(sprite)
	preview = TextureRect.new()
	preview.texture = viewport.get_texture()
	preview.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	preview.stretch_mode = TextureRect.STRETCH_SCALE
	column.add_child(preview)
	status = Label.new()
	column.add_child(status)
	present()
func present() -> void:
	var ticks := clock * 60.0
	if abs(ticks-round(ticks)) < 1e-12*max(1.0,abs(ticks)):
		ticks = round(ticks)
	sprite.set_frame_and_progress(int(floor(ticks))%72, fposmod(ticks,1.0))
	preview.custom_minimum_size = Vector2(256,256)*zoom
	status.text = "Frame %d | %.3f s | 1.2 s loop / 72 ticks at 60 Hz | no contact claim" % [sprite.frame,clock]
func command(name: String) -> void:
	match name:
		"Play/Pause": playing = not playing
		"Restart": clock = 0.0
		"Step":
			playing = false
			clock = (floor(clock*60.0+1e-10)+1.0)/60.0
		"1× / 2×": zoom = 3-zoom
		"Speed": speed = .5 if speed==2.0 else speed*2.0
	present()
func _process(delta: float) -> void:
	if playing: clock += delta*speed
	present()
