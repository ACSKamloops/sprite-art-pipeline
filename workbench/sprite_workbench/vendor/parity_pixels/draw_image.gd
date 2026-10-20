extends Node

var get_image_helper = load("res://src/Extensions/PixelLab/get_image.gd").new()


func get_cels(tool_data, request_data):
	var cels = {}
	var current_project = ExtensionsApi.project.current_project
	var current_cel = ExtensionsApi.project.get_current_cel()
	var current_layer = current_project.current_layer
	var current_frame = current_project.current_frame
	var next_frame = false
	var number_of_layers = 1
	var skeleton_cels = {}





	var frame_offset = tool_data.get("frame_offset", 0)
	if tool_data.has("layers"):
		number_of_layers = tool_data["layers"]

	if tool_data.has("copy_skeleton"):
		var skeleton_layer = -1
		for layer in current_project.layers:
			if layer.name == "Skeleton":
				skeleton_layer = layer.index
				break

		if skeleton_layer != -1:
			for i in range(tool_data["image_amount"]):
				skeleton_cels[i] = ExtensionsApi.project.get_cel_at(current_project, current_frame + frame_offset + i, skeleton_layer)


	if current_project.layers[current_layer].name in ["Inpainting", "Skeleton"]:

		for layer in current_project.layers:
			if layer.name not in ["Inpainting", "Skeleton"]:
				current_layer = layer.index
				break






	var creates_own_layer = tool_data.has("output_method") and tool_data["output_method"] in ["new layer", "new layer with changes"]
	if not creates_own_layer and current_project.layers[current_layer] is LayerTileMap:
		ExtensionsApi.project.add_new_layer(current_project.layers.size() - 1, "PixelLab - Generation")
		current_layer = current_project.layers.size() - 1



	var source_frame_images = {}
	if tool_data.has("copy_frame_content") and tool_data["copy_frame_content"]:
		for i in range(tool_data["image_amount"]):
			source_frame_images[i] = get_image_helper.get_image(current_frame + i, Color.TRANSPARENT, ["Inpainting", "Skeleton"], "")

	if tool_data.has("output_method") and (tool_data["output_method"] == "new layer" or tool_data["output_method"] == "new layer with changes"):

		var offset = 1
		for layer in current_project.layers:
			if layer.name in ["Inpainting", "Skeleton"]:
				offset += 1
		ExtensionsApi.project.add_new_layer(current_project.layers.size() - offset, "PixelLab - Generation")
		current_layer = current_project.layers.size() - offset

	var number_of_frames_start = len(current_project.frames)
	var created_frame_positions = []
	var image_offset = tool_data["image_amount"] if tool_data.has("skip_frames") and tool_data["skip_frames"] else 1

	for layer_index in range(number_of_layers):
		if layer_index > 0:
			ExtensionsApi.project.add_new_layer(current_layer, "PixelLab - Generation")
			current_layer = current_layer + 1

		cels[layer_index] = {}

		if layer_index == 0:
			for i in range(tool_data["image_amount"]):
				if tool_data.has("output_method") and (tool_data["output_method"] == "modify current layer" or tool_data["output_method"] == "new layer" or tool_data["output_method"] == "new layer with changes" or tool_data["output_method"] == "modify current layer, only changes"):

					while len(current_project.frames) <= current_frame + frame_offset + i:
						ExtensionsApi.project.add_new_frame(len(current_project.frames) - 1)
					created_frame_positions.append(current_frame + frame_offset + i)
				else:
					var frame_position = current_frame + frame_offset + i + image_offset - 1
					if len(current_project.frames) <= frame_position:
						frame_position = len(current_project.frames) - 1
					ExtensionsApi.project.add_new_frame(frame_position)
					created_frame_positions.append(frame_position + 1)


		for i in range(tool_data["image_amount"]):
			if tool_data.has("output_method") and (tool_data["output_method"] == "modify current layer" or tool_data["output_method"] == "new layer" or tool_data["output_method"] == "new layer with changes" or tool_data["output_method"] == "modify current layer, only changes"):
				cels[layer_index][i] = ExtensionsApi.project.get_cel_at(current_project, current_frame + frame_offset + i, current_layer)
			else:
				cels[layer_index][i] = ExtensionsApi.project.get_cel_at(current_project, created_frame_positions[i], current_layer)
				next_frame = true

			if tool_data.has("copy_skeleton") and tool_data["output_method"] == "new frame" and skeleton_cels.has(i):
				var skeleton_cel = skeleton_cels[i]
				if skeleton_cel != null:
					var skeleton_image = skeleton_cel.get_image()
					var skeleton_layer = 0
					for layer in current_project.layers:
						if layer.name == "Skeleton":
							skeleton_layer = layer.index
							break
					PixelLabUtils.set_pixelcel_image_with_undo(skeleton_image, "Copy Skeleton", created_frame_positions[i], skeleton_layer, current_project)


			if tool_data.has("copy_frame_content") and tool_data["copy_frame_content"] and tool_data["output_method"] == "new frame" and source_frame_images.has(i):
				var source_image = source_frame_images[i]
				if source_image != null:
					PixelLabUtils.set_pixelcel_image_with_undo(source_image, "Copy Frame Content", created_frame_positions[i], current_layer, current_project)


		current_project.current_frame = current_frame + 1 * int(next_frame)


	if tool_data.has("add_tag_based_on_parameters") and request_data != null and created_frame_positions.size() > 0:
		add_animation_tag_from_parameters(tool_data, request_data, created_frame_positions)

	return cels

func add_animation_tag_from_parameters(tool_data, request_data, created_frame_positions):
	var current_project = ExtensionsApi.project.current_project
	var tag_parameters = tool_data["add_tag_based_on_parameters"]


	var tag_name_parts = []
	for param in tag_parameters:
		var value = null


		if "." in param:
			var param_parts = param.split(".")
			var current_data = request_data


			for i in range(param_parts.size()):
				var part = param_parts[i]
				if current_data.has(part):
					current_data = current_data[part]
				else:
					current_data = null
					break

			value = current_data
		else:

			if request_data.has(param):
				value = request_data[param]


		if value != null:
			var param_value = str(value).strip_edges()
			if param_value != "":
				tag_name_parts.append(param_value)


	var tag_name = " - ".join(tag_name_parts)


	if tag_name == "":
		tag_name = "Generated Animation"


	var start_frame = created_frame_positions[0] + 1
	var end_frame = created_frame_positions[-1] + 1


	var new_animation_tags: Array[AnimationTag] = []



	for tag in current_project.animation_tags:
		new_animation_tags.append(tag.duplicate())


	var tag_color = Color(0.3, 0.7, 1.0)
	var new_tag = AnimationTag.new(tag_name, tag_color, start_frame, end_frame)
	new_animation_tags.append(new_tag)


	current_project.undo_redo.create_action("Adding Animation Tag")
	current_project.undo_redo.add_do_method(Global.general_redo)
	current_project.undo_redo.add_undo_method(Global.general_undo)
	current_project.undo_redo.add_do_property(
		current_project, "animation_tags", new_animation_tags
	)
	current_project.undo_redo.add_undo_property(
		current_project, "animation_tags", current_project.animation_tags
	)
	current_project.undo_redo.commit_action()

func get_image_from_data(raw_data_image, width, height):
	var raw_image = Marshalls.base64_to_raw(raw_data_image)



	if raw_image.size() >= 8 and raw_image[0] == 137 and raw_image[1] == 80\
	and raw_image[2] == 78 and raw_image[3] == 71:
		var png_image = Image.new()
		if png_image.load_png_from_buffer(raw_image) == OK:
			if png_image.get_format() != Image.FORMAT_RGBA8:
				png_image.convert(Image.FORMAT_RGBA8)
			return png_image
	var image = Image.create_from_data(width, height, false, Image.FORMAT_RGBA8, raw_image)
	return image

func draw_image(tool_data, received_image, cels, index):

	var image = get_image_from_data(received_image, tool_data["image_size"]["width"], tool_data["image_size"]["height"])


	var rect = Rect2(0, 0, 64, 64)
	if tool_data.has("image_size"):
		rect = Rect2(0, 0, tool_data["image_size"]["width"], tool_data["image_size"]["height"])
	if tool_data.has("selection"):
		rect = Rect2(0, 0, tool_data["selection"]["width"], tool_data["selection"]["height"])

	var origin = Vector2(0, 0)
	if tool_data.has("selection"):
		origin = Vector2(tool_data["selection"]["origin"]["x"], tool_data["selection"]["origin"]["y"])


	var copy_image = Image.new()
	copy_image.copy_from(cels[index].get_image())
	if tool_data.has("preserve_outside_mask"):
		copy_image.blit_rect_mask(image, tool_data["preserve_outside_mask"], rect, origin)
	else:
		copy_image.blit_rect(image, rect, origin)

	var cel_position = PixelLabUtils.get_cel_position(cels[index])

	var frame = cel_position[0]
	var layer = cel_position[1]
	var project = cel_position[2]
	PixelLabUtils.set_pixelcel_image_with_undo(copy_image, "Draw Progress Image", frame, layer, project)
