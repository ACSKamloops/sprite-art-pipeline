extends RefCounted
# Declared source holds, not simulation tick counts. Times are milliseconds.
var boundaries: Array[float] = [0.0]
var cycle_ms := 0.0
var error := ""
func configure(manifest: Dictionary) -> bool:
	boundaries = [0.0]; cycle_ms = 0.0; error = ""
	if not manifest.has("frames") or not manifest.frames is Array or manifest.frames.size() != 72:
		error = "Expected72 ordered source frames"; return false
	for i in range(72):
		var row = manifest.frames[i]
		if not row is Dictionary or not row.has("frame") or row.frame != i or not row.has("duration_ms"):
			error = "Missing/order-invalid frame"; return false
		var duration = row.duration_ms
		if not (duration is int or duration is float) or not is_finite(float(duration)) or float(duration) <= 0.0:
			error = "Nonpositive/nonfinite hold"; return false
		cycle_ms += float(duration); boundaries.append(cycle_ms)
	if not manifest.has("cycle_ms") or not (manifest.cycle_ms is int or manifest.cycle_ms is float) or not is_finite(float(manifest.cycle_ms)) or abs(cycle_ms-float(manifest.cycle_ms)) > 1e-8:
		error = "Cycle/hold sum mismatch"; return false
	return true
func locate(seconds: float) -> Dictionary:
	assert(error.is_empty() and cycle_ms > 0.0 and is_finite(seconds) and seconds >= 0.0)
	var absolute_ms := seconds*1000.0
	var cycle := int(floor(absolute_ms/cycle_ms))
	var local := absolute_ms-cycle*cycle_ms
	# Roundoff-only normalization: genuine early probes remain early.
	var epsilon: float = 1e-12*max(1.0,abs(absolute_ms))
	for boundary in boundaries:
		if abs(local-boundary) <= epsilon:
			local = boundary; break
	if local == cycle_ms: cycle += 1; local = 0.0
	var index := 0
	while index < 71 and local >= boundaries[index+1]: index += 1
	var fraction := (local-boundaries[index])/(boundaries[index+1]-boundaries[index])
	return {"frame":index,"progress":fraction,"cycle":cycle,"source_pose_phase":(cycle*72.0+index+fraction)/72.0,"absolute_ms":absolute_ms}
func next_boundary(seconds: float) -> float:
	var state := locate(seconds)
	return (state.cycle*cycle_ms+boundaries[state.frame+1])/1000.0
func pose_time(cycle: int, frame: int, fraction: float) -> float:
	assert(frame >= 0 and frame < 72 and fraction >= 0.0 and fraction < 1.0)
	return (cycle*cycle_ms+boundaries[frame]+fraction*(boundaries[frame+1]-boundaries[frame]))/1000.0
func physical_root(manifest: Dictionary, state: Dictionary) -> Vector2:
	var i: int = state.frame
	var a = manifest.frames[i].physical_root
	var stride := Vector2(manifest.root_stride[0],manifest.root_stride[1])
	var next := stride
	if i < 71:
		var b = manifest.frames[i+1].physical_root; next = Vector2(b[0],b[1])
	return Vector2(a[0],a[1]).lerp(next,state.progress)+stride*state.cycle
