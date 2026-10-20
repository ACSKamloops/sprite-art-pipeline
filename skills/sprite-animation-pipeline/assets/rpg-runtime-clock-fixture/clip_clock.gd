extends RefCounted
# Integer source ticks. All frame boundaries/events share this one clock.
var clips: Dictionary
var id := ""
var tick := 0
var frame := 0
var cycle := 0
var completed := false
var active := false
var log_events: Array = []
func _init(data: Dictionary = {}):
	clips = data
func start(key: String) -> bool:
	if not clips.has(key): return false
	id = key; tick = 0; frame = 0; cycle = 0; completed = false; active = false
	log_events.clear()
	_emit_frame(0)
	return true
func _emit_frame(f: int):
	for e in clips[id].get("events", []):
		if int(e.frame) == f:
			log_events.append({"name":e.name,"frame":f,"cycle":cycle})
			if e.name == "active_start": active = true
			if e.name == "active_end": active = false
func advance(amount: int):
	if id.is_empty() or completed: return amount
	var c: Dictionary = clips[id]
	# Iterate crossed boundaries, including many loops at low update rates.
	while amount > 0 and not completed:
		var boundary := 0
		for i in range(frame + 1): boundary += int(c.ticks[i])
		var step: int = mini(amount, boundary-tick)
		tick += step; amount -= step
		if tick == boundary:
			if frame + 1 == c.ticks.size():
				if c.loop:
					tick = 0; frame = 0; cycle += 1; _emit_frame(0)
				else:
					completed = true; active = false
					log_events.append({"name":"completed","frame":frame,"cycle":cycle})
			else:
				frame += 1; _emit_frame(frame)
	return amount
func interrupt():
	active = false
	log_events.append({"name":"cleanup","frame":frame,"cycle":cycle})
