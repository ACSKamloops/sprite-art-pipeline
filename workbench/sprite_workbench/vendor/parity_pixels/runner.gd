extends SceneTree
class Cel:
	var image: Image
	func _init(im): image = im
	func get_image(): return image
func load_rgba(name, dimensions):
	return Image.create_from_data(int(dimensions[0]), int(dimensions[1]), false, Image.FORMAT_RGBA8, FileAccess.get_file_as_bytes("res://" + name + ".rgba"))
func save_rgba(image):
	if image == null or image.is_empty():
		return {}
	var file = FileAccess.open("res://output.rgba", FileAccess.WRITE)
	file.store_buffer(image.get_data())
	file.close()
	return {"width": image.get_width(), "height": image.get_height(), "raw_size": image.get_data_size()}
func _init():
	var request = JSON.parse_string(FileAccess.get_file_as_string("res://request.json"))
	var host = load("res://host.gd").new()
	var result = {"input_unchanged": true}
	var before = {}
	var inputs = {}
	for name in request.dimensions:
		inputs[name] = load_rgba(name, request.dimensions[name])
		before[name] = inputs[name].get_data()
	match request.operation:
		"serialize":
			var normalized = Marshalls.base64_to_raw(host.image_to_base64(inputs.input))
			result.merge(save_rgba(Image.create_from_data(inputs.input.get_width(), inputs.input.get_height(), false, Image.FORMAT_RGBA8, normalized)))
		"transparency":
			result["has_exact_zero_alpha"] = host.has_transparent_pixels(inputs.input)
		"reference_palette":
			var palette = host.get_limit_color(inputs.input, null, "reference")
			result.merge(save_rgba(Image.create_from_data(palette.width, palette.height, false, Image.FORMAT_RGBA8, Marshalls.base64_to_raw(palette.base64))))
		"mask":
			host.mask_image = inputs.mask
			host.art_image = inputs.art
			result.merge(save_rgba(host.get_mask(0, Color.WHITE, Color.BLACK, [], "Inpainting", {}, request.fill_background, request.inpaint_empty_image)))
		"decode":
			var received = Marshalls.raw_to_base64(FileAccess.get_file_as_bytes("res://received.bin"))
			result.merge(save_rgba(host.get_image_from_data(received, int(request.width), int(request.height))))
		"place":
			var tool = {"image_size": {"width": int(request.source_size[0]), "height": int(request.source_size[1])}, "selection": {"origin": {"x": int(request.origin[0]), "y": int(request.origin[1])}, "width": int(request.extent[0]), "height": int(request.extent[1])}}
			if inputs.has("preserve_mask"):
				tool["preserve_outside_mask"] = inputs.preserve_mask
			var received = Marshalls.raw_to_base64(inputs.source.get_data())
			host.draw_image(tool, received, [Cel.new(inputs.destination)], 0)
			result.merge(save_rgba(host.PixelLabUtils.last_image))
	for name in inputs:
		result.input_unchanged = result.input_unchanged and before[name] == inputs[name].get_data()
	var file = FileAccess.open("res://result.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(result))
	file.close()
	print("PIXELS_OK")
	quit(0)
