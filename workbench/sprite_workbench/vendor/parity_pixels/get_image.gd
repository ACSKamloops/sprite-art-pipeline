extends Node

var missing_image_texture = preload("res://src/Extensions/PixelLab/assets/missing-image.png")

func has_transparent_pixels(image: Image) -> bool:
	if not image:
		return false

	for x in range(image.get_width()):
		for y in range(image.get_height()):
			if image.get_pixel(x, y).a == 0:
				return true
	return false

func get_image(frame, background_color = Color.TRANSPARENT, ignore_layers = ["Inpainting", "Skeleton"], only_layer = "", selection = {"x": 0, "y": 0, "width": 0, "height": 0}):
	var current_project = ExtensionsApi.project.current_project
	var base_image = Image.new()

	var rect
	if selection.x != 0 or selection.y != 0 or selection.width != 0 or selection.height != 0:
		base_image = Image.create(selection.width, selection.height, false, Image.FORMAT_RGBA8)
		base_image.fill(background_color)
		rect = Rect2(Vector2(selection.x, selection.y), Vector2(selection.width, selection.height))
	else:
		base_image = Image.create(current_project.size[0], current_project.size[1], false, Image.FORMAT_RGBA8)
		base_image.fill(background_color)
		rect = Rect2(Vector2.ZERO, base_image.get_size())

	if frame >= len(current_project.frames):
		return base_image

	var layer_index = 0
	for layer in current_project.layers:
		if (only_layer != "" or layer.visible):
			if ( not layer.name in ignore_layers and only_layer == "") or (only_layer != "" and only_layer == layer.name):
				var cel = ExtensionsApi.project.get_cel_at(current_project, frame, layer_index)
				base_image.blend_rect(cel.get_image(), rect, Vector2.ZERO)

		layer_index += 1

	return base_image

func get_mask(frame, mask_color = Color.WHITE, background_color = Color.BLACK, ignore_layers = [], only_layer = "Inpainting", selection = {"x": 0, "y": 0, "width": 0, "height": 0}, fill_background = false, inpaint_empty_image = false):
	var current_project = ExtensionsApi.project.current_project

	var image = get_image(frame, Color.TRANSPARENT, ignore_layers, only_layer, selection)
	var no_mask = image.is_invisible()

	for x in range(image.get_width()):
		for y in range(image.get_height()):
			var color = image.get_pixel(x, y)
			if color.a > 0:
				image.set_pixel(x, y, mask_color)
			else:
				image.set_pixel(x, y, background_color)

	if inpaint_empty_image:
		if no_mask:
			var temp_im = get_image(frame, Color.TRANSPARENT, ["Inpainting", "Skeleton"], "", selection)
			if temp_im.is_invisible():
				for x in range(temp_im.get_width()):
					for y in range(temp_im.get_height()):
						image.set_pixel(x, y, mask_color)

	if fill_background:
		var temp_im = get_image(frame, Color.TRANSPARENT, ["Inpainting", "Skeleton"], "", selection)
		for x in range(temp_im.get_width()):
			for y in range(temp_im.get_height()):
				var color = temp_im.get_pixel(x, y)
				if color.a == 0:
					image.set_pixel(x, y, mask_color)

	return image

func get_mask_base64(frame, only_layer = "Inpainting", selection = {"x": 0, "y": 0, "width": 0, "height": 0}, fill_background = false, inpaint_empty_image = false):
	var im = get_mask(frame, Color.WHITE, Color.BLACK, ["Skeleton"], only_layer, selection, fill_background, inpaint_empty_image)
	if im.is_empty() or im.is_invisible():
		return ""
	var im_raw = im.get_data()
	for i in range(0, im_raw.size(), 4):
		if im_raw[i + 3] == 0:
			im_raw[i] = 0
			im_raw[i + 1] = 0
			im_raw[i + 2] = 0
	var im_base64 = Marshalls.raw_to_base64(im_raw)
	return im_base64

func get_image_base64(frame, ignore_layers = ["Inpainting", "Skeleton"], selection = {"x": 0, "y": 0, "width": 0, "height": 0}, allow_empty = false):
	var im = get_image(frame, Color.TRANSPARENT, ignore_layers, "", selection)
	if !allow_empty and (im.is_empty() or im.is_invisible()):
		return ""
	var im_raw = im.get_data()
	for i in range(0, im_raw.size(), 4):
		if im_raw[i + 3] == 0:
			im_raw[i] = 0
			im_raw[i + 1] = 0
			im_raw[i + 2] = 0
	var im_base64 = Marshalls.raw_to_base64(im_raw)
	return im_base64

func image_to_base64(image):
	var image_raw = image.get_data()
	for i in range(0, image_raw.size(), 4):
		if image_raw[i + 3] == 0:
			image_raw[i] = 0
			image_raw[i + 1] = 0
			image_raw[i + 2] = 0
	var image_base64 = Marshalls.raw_to_base64(image_raw)
	return image_base64

func get_limit_color(frame, palettes, option = "image"):
	var color_table = {}
	if option == "image":
		var current_project = ExtensionsApi.project.current_project
		var im = get_image(frame, Color.TRANSPARENT, ["Inpainting", "Skeleton"])
		var width = current_project.size[1]
		var height = current_project.size[0]
		for x in range(width):
			for y in range(height):
				var color = im.get_pixel(x, y)

				if color.a != 0:
					var color_key = color
					if not color_table.has(color_key):
						color_table[color_key] = 1
					else:
						color_table[color_key] += 1
	elif option == "palette":
		if palettes:
			var current_palette = palettes.current_palette
			for c in current_palette.colors:
				var color_key = current_palette.get_color(c)
				if not color_table.has(color_key):
					color_table[color_key] = 1
				else:
					color_table[color_key] += 1

		else:
			print("Palettes autoload not found.")
	elif option == "reference":
		var im = frame
		var width = frame.get_width()
		var height = frame.get_height()
		for x in range(width):
			for y in range(height):
				var color = im.get_pixel(x, y)

				if color.a != 0:
					var color_key = color
					if not color_table.has(color_key):
						color_table[color_key] = 1
					else:
						color_table[color_key] += 1
	else:
		return ""

	var size = 64
	var color_image = Image.new()
	color_image = Image.create(size, size, false, Image.FORMAT_RGBA8)


	var colors = color_table.keys()

	for x in range(size):
		for y in range(size):
			if colors.size() > 0:
				var color_key = colors[0]
				var color_value = color_table[color_key]
				if color_value > 0:

					var color = Color(color_key)
					color_image.set_pixel(x, y, color)


					color_table[color_key] = color_value - 1



					colors.erase(color_key)

	var im_raw = color_image.get_data()
	var im_base64 = Marshalls.raw_to_base64(im_raw)
	return {"base64": im_base64, "width": size, "height": size}
