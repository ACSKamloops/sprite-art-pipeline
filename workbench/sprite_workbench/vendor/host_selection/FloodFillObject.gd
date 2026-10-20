class_name FloodFillObject
extends RefCounted

var tolerance: = 0.0
var selection_matters: = false


var _allegro_flood_segments: Array[Segment]

var _allegro_image_segments: Array[Segment]
var _area_start_idx: = 0
var _area_end_idx: = 0


class Segment:
	var flooding: = false
	var todo_above: = false
	var todo_below: = false
	var left_position: = -5
	var right_position: = -5
	var y: = 0
	var next: = 0

	func _init(_y: int, _next: int) -> void :
		y = _y
		next = _next




func flood_fill(
	pos: Vector2i, source_image: Image, target_image: Image, project: Project, callable: Callable
) -> void :
	var color: = source_image.get_pixelv(pos)

	_allegro_flood_segments = []
	_allegro_image_segments = []
	_compute_segments_for_image(pos, project, source_image, color)


	callable.call(target_image, _allegro_image_segments)


func _compute_segments_for_image(
	pos: Vector2i, project: Project, image: Image, src_color: Color
) -> void :

	var y_range: = PackedInt32Array([0, image.get_height()])
	_area_end_idx = image.get_height() - 1
	_area_start_idx = 0
	if selection_matters and project.has_selection:
		var selection_rect: = project.selection_map.get_selection_rect(project)
		_area_start_idx = selection_rect.position.y
		_area_end_idx = selection_rect.end.y - 1
		y_range = [selection_rect.position.y, selection_rect.end.y]
	for j in range(y_range[0], y_range[1]):
		_add_new_segment(j)

	_flood_line_around_point(pos, project, image, src_color)

	var done: = false
	while not done:
		done = true
		var max_index: = _allegro_flood_segments.size()
		for c in max_index:
			var p: = _allegro_flood_segments[c]
			if p.todo_below:
				p.todo_below = false
				if _check_flooded_segment(
					p.y + 1, p.left_position, p.right_position, project, image, src_color
				):
					done = false
			if p.todo_above:
				p.todo_above = false
				if _check_flooded_segment(
					p.y - 1, p.left_position, p.right_position, project, image, src_color
				):
					done = false



func _add_new_segment(y: = 0) -> void :
	_allegro_flood_segments.append(Segment.new(y, _area_start_idx))





func _flood_line_around_point(
	pos: Vector2i, project: Project, image: Image, src_color: Color
) -> int:


	if not DrawingAlgos.similar_colors(image.get_pixelv(pos), src_color, tolerance):
		return pos.x + 1
	var west: = pos
	var east: = pos
	if selection_matters and project.has_selection:
		while (
			project.can_pixel_get_drawn(west)
			&& DrawingAlgos.similar_colors(image.get_pixelv(west), src_color, tolerance)
		):
			west += Vector2i.LEFT
		while (
			project.can_pixel_get_drawn(east)
			&& DrawingAlgos.similar_colors(image.get_pixelv(east), src_color, tolerance)
		):
			east += Vector2i.RIGHT
	else:
		while (
			west.x >= 0 && DrawingAlgos.similar_colors(image.get_pixelv(west), src_color, tolerance)
		):
			west += Vector2i.LEFT
		while (
			east.x < project.size.x
			&& DrawingAlgos.similar_colors(image.get_pixelv(east), src_color, tolerance)
		):
			east += Vector2i.RIGHT


	var c: = pos.y - _area_start_idx
	var segment: = _allegro_flood_segments[c]

	if segment.flooding:
		while segment.next > _area_start_idx:
			c = segment.next - _area_start_idx
			segment = _allegro_flood_segments[c]

		c = _allegro_flood_segments.size()
		segment.next = c + _area_start_idx
		_add_new_segment(pos.y)
		segment = _allegro_flood_segments[c]

	segment.flooding = true
	segment.left_position = west.x + 1
	segment.right_position = east.x - 1
	segment.y = pos.y
	segment.next = _area_start_idx







	segment.todo_above = pos.y > _area_start_idx
	segment.todo_below = pos.y < _area_end_idx


	if segment.right_position >= segment.left_position:
		_allegro_image_segments.append(segment)


	return east.x + 1


func _check_flooded_segment(
	y: int, left: int, right: int, project: Project, image: Image, src_color: Color
) -> bool:
	var ret: = false
	var c: = 0
	while left <= right:
		c = y - _area_start_idx
		while true:
			var segment: = _allegro_flood_segments[c]
			if left >= segment.left_position and left <= segment.right_position:
				left = segment.right_position + 2
				break
			c = segment.next - _area_start_idx
			if c == 0:
				left = _flood_line_around_point(Vector2i(left, y), project, image, src_color)
				ret = true
				break
	return ret
