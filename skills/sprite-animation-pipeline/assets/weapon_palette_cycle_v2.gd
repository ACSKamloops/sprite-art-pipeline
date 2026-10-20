extends RefCounted
## Native C0:EDD7 five-color cycle and C0:EDA8 range rotation. No body-animation clock or renderer required.
const NATIVE_VIDEO_FPS := 60.098811862348406
var flags := 0
var start := 0
var end := 0
var phase := 0
var timer := 0
var palette_bank: Dictionary = {}
var palette_buffer: Array = []
var displayed_colors: Array = []
var video_fps := NATIVE_VIDEO_FPS
var fractional_ticks := 0.0
var tick_count := 0
var last_error := ""

var max_ticks_per_advance := 10000

func _integer_in_range(value: Variant, upper: int) -> bool:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return false
	return is_finite(float(value)) and value >= 0 and value <= upper and float(value) == floorf(float(value))

func _valid_state(value: Variant) -> bool:
	if typeof(value) != TYPE_DICTIONARY:
		last_error = "State must be a dictionary"
		return false
	for key in ["flags", "start", "end", "phase", "timer"]:
		if not value.has(key) or not _integer_in_range(value[key], 255):
			last_error = "Missing or invalid byte state: " + key
			return false
	return true

func _valid_colors(value: Variant, count: int = 5) -> bool:
	if typeof(value) != TYPE_ARRAY or value.size() != count:
		last_error = "Palette must be an array with the expected RGB15 word count"
		return false
	for word in value:
		if not _integer_in_range(word, 32767):
			last_error = "Palette word must be a finite integer in 0..32767"
			return false
	return true

func _valid_buffer(value: Variant) -> bool:
	if typeof(value) != TYPE_ARRAY or value.size() not in [5, 15]:
		last_error = "Palette buffer must contain five or fifteen RGB15 words"
		return false
	return _valid_colors(value, value.size())

func _valid_rotation(value: Dictionary, count: int) -> bool:
	if int(value.flags) & 0x20:
		var first := int(value.start) & 15
		var last := int(value.phase) & 15
		if first >= last or last >= count:
			last_error = "bit20 rotation requires ascending endpoints within the palette buffer"
			return false
	return true

func _valid_event(event: Variant) -> bool:
	if typeof(event) != TYPE_DICTIONARY:
		last_error = "Event must be a dictionary"
		return false
	if event.has("state") and (not _valid_state(event.state) or not _valid_rotation(event.state, palette_buffer.size())):
		return false
	if event.has("reset_palette_phase"):
		if not _integer_in_range(event.reset_palette_phase, 255):
			last_error = "Reset palette phase must be a byte integer"
			return false
		var key := str(int(event.reset_palette_phase))
		if not palette_bank.has(key):
			last_error = "Missing reset palette entry"
			return false
		if not _valid_colors(palette_bank[key]):
			return false
	return true

func configure(initial: Variant, entries: Variant, initial_buffer: Variant, fps: Variant = NATIVE_VIDEO_FPS, tick_limit: Variant = 10000) -> bool:
	last_error = ""
	if not _valid_state(initial) or not _valid_buffer(initial_buffer):
		return false
	if not _valid_rotation(initial, initial_buffer.size()):
		return false
	if (typeof(fps) != TYPE_INT and typeof(fps) != TYPE_FLOAT) or not is_finite(float(fps)) or fps <= 0.0:
		last_error = "Positive finite numeric video clock required"
		return false
	if not _integer_in_range(tick_limit, 10000) or tick_limit < 1:
		last_error = "Tick budget must be an integer in 1..10000"
		return false
	if typeof(entries) != TYPE_DICTIONARY:
		last_error = "Palette bank must be a dictionary"
		return false
	for key in entries:
		if typeof(key) != TYPE_STRING or not key.is_valid_int() or not _integer_in_range(int(key), 255) or str(int(key)) != key:
			last_error = "Palette bank keys must be canonical decimal byte strings"
			return false
		if not _valid_colors(entries[key]):
			return false
	palette_bank = entries.duplicate(true)
	_apply_state(initial)
	palette_buffer = initial_buffer.duplicate()
	displayed_colors = initial_buffer.duplicate()
	video_fps = float(fps)
	max_ticks_per_advance = int(tick_limit)
	fractional_ticks = 0.0
	tick_count = 0
	return true

func _apply_state(value: Dictionary) -> void:
	flags = int(value.flags)
	start = int(value.start)
	end = int(value.end)
	phase = int(value.phase)
	timer = int(value.timer)

func state() -> Dictionary:
	return {"flags": flags, "start": start, "end": end, "phase": phase, "timer": timer}

## Event: {state: byte-state, reset_palette_phase: int} explicitly models script setup/reset.
## The displayed palette is the PREVIOUS tick's buffer (native NMI presentation).
func video_tick(event: Variant = {}) -> Dictionary:
	last_error = ""
	if not _valid_state(state()) or not _valid_rotation(state(), palette_buffer.size()) or not _valid_event(event):
		return {}
	var next_state := state()
	var update := false
	if event.has("state"):
		next_state = event.state.duplicate()
	elif flags & 0x80:
		if (timer & 0xf0) and (timer & 0x0f):
			next_state.timer = (timer - 1) & 255
		else:
			if timer & 0xf0:
				next_state.timer = timer | (timer >> 4)
			if flags & 0x20:
				pass # Phase is a rotation endpoint; native routine does not change it.
			elif flags & 0x40:
				if phase > start:
					next_state.phase = phase - 1
				else:
					next_state.phase = (phase + 1) & 255
					next_state.flags = flags ^ 0x40
			elif phase < end:
				next_state.phase = (phase + 1) & 255
			elif flags & 1:
				next_state.phase = (phase - 1) & 255
				next_state.flags = flags ^ 0x40
			else:
				next_state.phase = start
			update = true
	if update and not (flags & 0x20):
		var key := str(int(next_state.phase))
		if not palette_bank.has(key):
			last_error = "Missing phase palette entry"
			return {}
		if not _valid_colors(palette_bank[key]):
			return {}
	displayed_colors = palette_buffer.duplicate()
	_apply_state(next_state)
	if event.has("reset_palette_phase"):
		palette_buffer = palette_bank[str(int(event.reset_palette_phase))].duplicate() + palette_buffer.slice(5)
	elif update:
		if flags & 0x20:
			var first := start & 15
			var last := phase & 15
			var old_color: Variant = palette_buffer[first]
			for index in range(first, last):
				palette_buffer[index] = palette_buffer[index + 1]
			palette_buffer[last] = old_color
		else:
			palette_buffer = palette_bank[str(phase)].duplicate() + palette_buffer.slice(5)
	tick_count += 1
	return {"tick": tick_count, "state": state(), "palette_buffer": palette_buffer.duplicate(), "displayed_colors": displayed_colors.duplicate(), "updated": update}

## Returns every video-tick result, retaining a fractional tick between calls.
## Events use one-based absolute tick numbers. Schedule setup/reset on that tick.
func advance_wall_clock(delta_seconds: Variant, events: Variant = {}) -> Array:
	last_error = ""
	if (typeof(delta_seconds) != TYPE_INT and typeof(delta_seconds) != TYPE_FLOAT) or not is_finite(float(delta_seconds)) or delta_seconds < 0.0:
		last_error = "Finite nonnegative numeric delta required"
		return []
	if not _integer_in_range(max_ticks_per_advance, 10000) or max_ticks_per_advance < 1:
		last_error = "Tick budget must be an integer in 1..10000"
		return []
	if not is_finite(video_fps) or video_fps <= 0.0:
		last_error = "Positive finite video clock required"
		return []
	var available := fractional_ticks + float(delta_seconds) * video_fps
	if not is_finite(available) or available + 1.0e-12 >= max_ticks_per_advance + 1.0:
		last_error = "Wall-clock call exceeds configured tick budget"
		return []
	var ticks := int(floorf(available + 1.0e-12))
	if typeof(events) != TYPE_DICTIONARY:
		last_error = "Events must be a dictionary"
		return []
	var normalized_events := {}
	for key in events:
		var index: Variant = key
		if typeof(key) == TYPE_STRING and key.is_valid_int():
			index = int(key)
		if not _integer_in_range(index, 9007199254740991) or index < 1 or not _valid_event(events[key]):
			if last_error.is_empty():
				last_error = "Event tick index must be a positive integer"
			return []
		normalized_events[int(index)] = events[key]
	# All upfront checks precede mutation of clocks, state and palettes.
	fractional_ticks = available
	var results: Array = []
	for _index in ticks:
		var result := video_tick(normalized_events.get(tick_count + 1, {}))
		if result.is_empty():
			break
		fractional_ticks = maxf(0.0, fractional_ticks - 1.0)
		results.append(result)
	return results
