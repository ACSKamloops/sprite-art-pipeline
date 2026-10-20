extends Control
var sprite: AnimatedSprite2D
var clock := 0.0
var playing := true
var zoom := 2
var viewport: SubViewport
var preview: TextureRect
var status: Label
static func frames_resource() -> SpriteFrames:
	var manifest = JSON.parse_string(FileAccess.get_file_as_string("res://assets/manifest.json"))
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	frames.add_animation("experimental_walk")
	frames.set_animation_speed("experimental_walk", 10.0)
	frames.set_animation_loop("experimental_walk", true)
	assert(manifest.canvas[0] == 256 and manifest.canvas[1] == 256 and manifest.frames.size() == 12)
	for i in range(12):
		var row = manifest.frames[i]
		assert(row.frame == i and row.duration_ms == 100)
		var path = "res://assets/" + row.file
		assert(FileAccess.get_sha256(path) == row.sha256)
		frames.add_frame("experimental_walk", ImageTexture.create_from_image(Image.load_from_file(path)), 1.0)
	return frames
func _ready() -> void:
	var column := VBoxContainer.new()
	column.position = Vector2(10,10)
	add_child(column)
	var title := Label.new()
	title.text = "Experimental, art not approved | Captain walk probe | 12 × 100 ms"
	column.add_child(title)
	var buttons := HBoxContainer.new()
	column.add_child(buttons)
	for name in ["Play/Pause", "Restart", "Step", "1× / 2×"]:
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
	var ticks := clock * 10.0
	if abs(ticks-round(ticks)) < 1e-12*max(1.0,abs(ticks)):
		ticks = round(ticks)
	sprite.set_frame_and_progress(int(floor(ticks))%12, fposmod(ticks,1.0))
	preview.custom_minimum_size = Vector2(256,256)*zoom
	status.text = "Frame %d | %.3f s | 1.2 s loop / 72 ticks at 60 Hz | no contact claim" % [sprite.frame,clock]
func command(name: String) -> void:
	match name:
		"Play/Pause": playing = not playing
		"Restart": clock = 0.0
		"Step":
			playing = false
			clock = (floor(clock*10.0+1e-10)+1.0)/10.0
		"1× / 2×": zoom = 3-zoom
	present()
func _process(delta: float) -> void:
	if playing: clock += delta
	present()
