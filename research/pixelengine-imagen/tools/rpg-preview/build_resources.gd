extends SceneTree
## Direct PNG loading avoids importer alpha-border repair. Saved textures are read back.

func digest(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()

func fail(message: String) -> void:
	push_error(message)
	quit(1)

func _initialize() -> void:
	var bank = JSON.parse_string(FileAccess.get_file_as_string("res://bank.json"))
	if not bank is Dictionary or bank.get("schema") != "rpg-godot-inspector/v1":
		fail("Missing inspector bank")
		return
	var resource := SpriteFrames.new()
	resource.remove_animation("default")
	var count := 0
	for clip in bank.clips:
		var name: String = clip.name
		resource.add_animation(name)
		resource.set_animation_speed(name, float(bank.tick_rate))
		resource.set_animation_loop(name, clip.loop)
		for frame in clip.frames:
			var path: String = "res://" + frame.file
			if FileAccess.get_sha256(path) != frame.sha256:
				fail("PNG hash mismatch " + path)
				return
			var image := Image.load_from_file(path)
			if image == null or image.get_size() != Vector2i(80,80):
				fail("Invalid80px PNG " + path)
				return
			image.convert(Image.FORMAT_RGBA8)
			if digest(image.get_data()) != frame.rgba_sha256:
				fail("Decoded PNG RGBA mismatch " + path)
				return
			resource.add_frame(name, ImageTexture.create_from_image(image), float(frame.ticks))
			count += 1
	if ResourceSaver.save(resource, "res://hero_frames.res") != OK:
		fail("SpriteFrames save failed")
		return
	var saved := ResourceLoader.load("res://hero_frames.res", "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE) as SpriteFrames
	if saved == null or saved.get_animation_names().size() != 48:
		fail("SpriteFrames reload/count failed")
		return
	for clip in bank.clips:
		if saved.get_frame_count(clip.name) != clip.frames.size() or saved.get_animation_loop(clip.name) != clip.loop or saved.get_animation_speed(clip.name) != float(bank.tick_rate):
			fail("Saved clip metadata mismatch " + clip.name)
			return
		var duration := 0.0
		for index in clip.frames.size():
			var frame: Dictionary = clip.frames[index]
			var texture := saved.get_frame_texture(clip.name,index)
			if texture == null or saved.get_frame_duration(clip.name,index) != float(frame.ticks):
				fail("Saved frame duration mismatch")
				return
			var image := texture.get_image()
			image.convert(Image.FORMAT_RGBA8)
			if digest(image.get_data()) != frame.rgba_sha256:
				fail("Saved texture RGBA mismatch")
				return
			duration += saved.get_frame_duration(clip.name,index) / saved.get_animation_speed(clip.name)
		if absf(duration-float(clip.duration[0])/float(clip.duration[1])) > 0.000000001:
			fail("Saved hold sum mismatch")
			return
	var report := {"schema":"rpg-godot-resources/v1","godot_version":Engine.get_version_info().string,"animations":48,"frames":count,
		"loops_speeds_durations_exact":true,"all_source_png_and_saved_resource_rgba_exact":true,"common_tick_rate":bank.tick_rate,
		"resource_sha256":FileAccess.get_sha256("res://hero_frames.res"),"scope":"Resource save/reload and decoded pixels/clocks; no rendered contact or art acceptance"}
	FileAccess.open("res://RESOURCE-VALIDATION.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("RPG_RESOURCES_OK ",JSON.stringify(report))
	quit(0)
