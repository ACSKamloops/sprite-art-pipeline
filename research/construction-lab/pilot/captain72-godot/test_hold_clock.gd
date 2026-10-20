extends SceneTree
const Clock = preload("res://hold_clock.gd")
var checks := 0
var failures: Array = []
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)
func fixture() -> Dictionary:
	var frames: Array = []
	# Explicit synthetic timing fixture, not a frozen art candidate.
	for i in range(72): frames.append({"frame":i,"duration_ms":[13,21,16][i%3],"physical_root":[-60.0*i/72.0,20.0*i/72.0]})
	return {"frames":frames,"cycle_ms":1200,"root_stride":[-60,20]}
func _initialize() -> void:
	var m := fixture(); var c = Clock.new()
	check(c.configure(m),"Valid synthetic integer hold sum")
	for cycle in range(3):
		for i in range(72):
			var time = c.pose_time(cycle,i,0.0)
			var state = c.locate(time)
			check(state.frame==i and state.cycle==cycle,"Cumulative exact boundary%d/%d"%[cycle,i])
			if time > 0.0: check(c.locate(time-1e-8).frame==(i+71)%72,"Genuine10ns early rejects nextpose%d/%d"%[cycle,i])
			check(c.locate(time+1e-8).frame==i,"Genuine10ns after boundary%d/%d"%[cycle,i])
			check(abs(c.next_boundary(time)-(cycle*c.cycle_ms+c.boundaries[i+1])/1000.0)<1e-12,"Step cumulative boundary%d/%d"%[cycle,i])
			for f in [0.0,.2,.4,.6,.8]:
				var t = c.pose_time(cycle,i,f);var s=c.locate(t)
				check(s.frame==i and abs(s.progress-f)<1e-10,"Held interval%d/%d/%.1f"%[cycle,i,f])
				var expected=Vector2(-60,20)*(cycle+(i+f)/72.0)
				check(c.physical_root(m,s).distance_to(expected)<.00002,"Source physical interpolation%d/%d/%.1f"%[cycle,i,f])
	check(c.locate(1.2).frame==0 and c.locate(1.2).cycle==1,"Actual1.2second wrap")
	# Perturbations must change selection or fail input contract, never silently normalize.
	var bad=m.duplicate(true);bad.frames[0].duration_ms=14
	check(not Clock.new().configure(bad),"Hold sum corruption rejected")
	bad=m.duplicate(true);bad.frames[0].frame=1
	check(not Clock.new().configure(bad),"Frame order corruption rejected")
	bad=m.duplicate(true);bad.frames[0].duration_ms=0
	check(not Clock.new().configure(bad),"Zero hold rejected")
	bad=m.duplicate(true);bad.frames[0].duration_ms=NAN
	check(not Clock.new().configure(bad),"Nonfinite hold rejected")
	bad=m.duplicate(true);bad.frames[0].erase("duration_ms")
	check(not Clock.new().configure(bad),"Missing hold rejected")
	bad=m.duplicate(true);bad.frames[0].duration_ms+=1;bad.frames[1].duration_ms-=1
	var changed=Clock.new();check(changed.configure(bad),"Positive balanced mutation valid but distinct")
	check(changed.locate(.0135).frame!=c.locate(.0135).frame,"One ms altered timing detected")
	var file=FileAccess.open("res://proof/variable-hold-clock-scaffold.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"captain-variable-hold-scaffold/v1","passed":failures.is_empty(),"checks":checks,"failures":failures,"scope":"Synthetic clock contract only; no final art PNG/GPU run","engine":Engine.get_version_info(),"code_sha256":FileAccess.get_sha256("res://hold_clock.gd")},"\t"));file.close()
	print("HOLD_CLOCK ",checks," failures ",failures.size());quit(0 if failures.is_empty() else 1)
