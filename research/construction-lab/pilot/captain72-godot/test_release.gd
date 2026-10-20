extends SceneTree
# Run this absolute script against the standalone release project, not this lab.
var output := "/tmp/captain-release-proof"
var checks: Array = []
var screenshots: Array = []
var leg_source := ""
var episode_targets_independently_checked := false
var scene
var manifest: Dictionary
var policy: Dictionary
func check(ok: bool, label: String) -> void:
	checks.append({"passed":ok,"description":label})
func digest(bytes: PackedByteArray) -> String:
	var ctx = HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(bytes)
	return ctx.finish().hex_encode()
func close(a: Vector2,b: Vector2) -> bool: return a.distance_to(b)<.0001
func button(node: Node, caption: String):
	if node is Button and node.text == caption: return node
	for child in node.get_children():
		var found = button(child,caption)
		if found != null: return found
	return null
func press(caption: String) -> void:
	var control = button(scene,caption)
	check(control != null,"Actual UI button exists: "+caption)
	if control != null: control.pressed.emit()
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): output=arg.substr(9)
		if arg.begins_with("--legs="): leg_source=arg.substr(7)
	call_deferred("run")
func independent_state(seconds: float) -> Dictionary:
	var elapsed = seconds*1000.0
	var total = float(manifest.cycle_ms)
	var cycle = int(floor(elapsed/total))
	var local = elapsed-cycle*total
	var cumulative := 0.0
	for i in range(72):
		var duration = float(manifest.frames[i].duration_ms)
		if local < cumulative+duration or i == 71:
			return {"frame":i,"cycle":cycle,"progress":(local-cumulative)/duration}
		cumulative += duration
	return {}
func independent_position(seconds: float, zoom: int, follow: bool, locked: bool) -> Vector2:
	var s = independent_state(seconds);var row = manifest.frames[s.frame]
	var a = Vector2(row.physical_root[0],row.physical_root[1])
	var stride = Vector2(manifest.root_stride[0],manifest.root_stride[1])
	var b = stride
	if s.frame < 71:
		var next = manifest.frames[s.frame+1].physical_root;b=Vector2(next[0],next[1])
	var physical = a.lerp(b,s.progress)+stride*s.cycle
	var draw_root = physical
	if locked:
		for side in ["right","left"]:
			if row.landmarks[side].declared_stance:
				var target = policy.frames[s.frame].support_world[side]
				var sole = row.landmarks[side].actual_sole
				draw_root=Vector2(target[0]-sole[0],target[1]-sole[1])+stride*s.cycle
				break
	return (Vector2(180,116)+(draw_root-(physical if follow else Vector2.ZERO))*zoom).round()
func file_ledger_valid(ledger: Dictionary) -> bool:
	for path in ledger.files:
		if FileAccess.get_sha256("res://"+path) != ledger.files[path]: return false
	return true
func run() -> void:
	DirAccess.make_dir_recursive_absolute(output)
	assert(FileAccess.file_exists("res://release-files.json"),"Standalone release missing; no test claim")
	manifest=JSON.parse_string(FileAccess.get_file_as_string("res://sprites/manifest.json"))
	policy=JSON.parse_string(FileAccess.get_file_as_string("res://contact-policy.json"))
	var source_sha=FileAccess.get_sha256("res://sprites/manifest.json")
	var ledger=JSON.parse_string(FileAccess.get_file_as_string("res://release-files.json"))
	check(file_ledger_valid(ledger),"All actual release-files source hashes")
	check(policy.candidate_manifest_sha256==source_sha,"Contact policy binds exact actor manifest")
	check(policy.leg_manifest_sha256==manifest.leg_source_manifest_sha256,"Contact policy binds exact leg manifest")
	var approval=JSON.parse_string(FileAccess.get_file_as_string("res://approval.json"))
	if leg_source.is_empty() and FileAccess.file_exists(approval.source_legs+"/manifest.json"):leg_source=approval.source_legs
	if not leg_source.is_empty():
		var legs=JSON.parse_string(FileAccess.get_file_as_string(leg_source+"/manifest.json"))
		check(FileAccess.get_sha256(leg_source+"/manifest.json")==policy.leg_manifest_sha256,"Independent leg input exact SHA")
		for i in range(72):
			check(policy.frames[i].frame==i,"Contact policy ordered source pose%d"%i)
			for side in ["right","left"]:
				var leg=legs.frames[i].legs[side]
				check(bool(leg.contact)==bool(manifest.frames[i].landmarks[side].declared_stance),"Actor/leg stance agrees%d/%s"%[i,side])
				if leg.contact:
					var d=legs.registered_design.legs[side]
					var episode=floor(float(legs.frames[i].phase)+float(d.phase_offset))
					var declared=policy.frames[i].support_world[side]
					for axis in [0,1]:
						var value=float(d.rest_sole[axis])+float(legs.root_stride[axis])*(.3-float(d.phase_offset)+episode)
						check(float(declared[axis])==round(value),"Independent fixed-episode target%d/%s/%d"%[i,side,axis])
					var changed=float(declared[0])+1.0
					var target=float(d.rest_sole[0])+float(legs.root_stride[0])*(.3-float(d.phase_offset)+episode)
					check(changed!=round(target),"Onepixel target corruption detected%d/%s"%[i,side])
		episode_targets_independently_checked=true
	var bad_ledger=ledger.duplicate(true);bad_ledger.files["sprites/"+manifest.frames[0].file]="0".repeat(64)
	check(not file_ledger_valid(bad_ledger),"Wrong declared PNG hash detected without release mutation")
	var resource=load("res://captain-walk.tres")
	check(resource is SpriteFrames,"Real imported SpriteFrames")
	check(resource.get_frame_count("combat_ready_walk")==72,"Imported72 ordered frames")
	check(resource.get_animation_speed("combat_ready_walk")==60.0 and resource.get_animation_loop("combat_ready_walk"),"Imported60fps relative-hold loop")
	var sum := 0.0
	for i in range(72):
		var row=manifest.frames[i];var duration=resource.get_frame_duration("combat_ready_walk",i)
		check(row.frame==i and duration>0.0 and abs(duration-float(row.duration_ms)*.06)<1e-6,"Imported frame order/hold%d"%i)
		sum+=duration/60.0
		var png=Image.load_from_file("res://sprites/"+row.file);png.convert(Image.FORMAT_RGBA8)
		var tex=resource.get_frame_texture("combat_ready_walk",i).get_image();tex.convert(Image.FORMAT_RGBA8)
		check(png.get_data()==tex.get_data(),"Actual imported sourceRGBA%d"%i)
	check(abs(sum-float(manifest.cycle_ms)/1000.0)<1e-6,"Imported duration sum")
	check(ResourceSaver.save(resource,output+"/reopened.res")==OK,"Save standalone imported resource")
	var reopened=ResourceLoader.load(output+"/reopened.res","",ResourceLoader.CACHE_MODE_IGNORE)
	for i in range(72):check(abs(reopened.get_frame_duration("combat_ready_walk",i)-resource.get_frame_duration("combat_ready_walk",i))<1e-9,"Actual reopened hold%d"%i)
	var altered=resource.duplicate(true);altered.set_frame("combat_ready_walk",0,altered.get_frame_texture("combat_ready_walk",0),altered.get_frame_duration("combat_ready_walk",0)+.06)
	check(abs(altered.get_frame_duration("combat_ready_walk",0)-float(manifest.frames[0].duration_ms)*.06)>.01,"One ms actual resource mutation detected")
	scene=load("res://main.tscn").instantiate();root.add_child(scene)
	await process_frame;scene.playing=false;scene.set_process(false)
	root.size=Vector2i(960,760)
	press("Play / Pause");check(scene.playing,"UI play toggles on")
	press("Play / Pause");check(not scene.playing,"UI pause toggles off")
	var held_clock=scene.clock;scene._process(.1);check(scene.clock==held_clock,"Paused process clock frozen")
	press("Restart");check(scene.clock==0 and scene.actor.frame==0,"UI restart exact first hold")
	press("Step");check(scene.actor.frame==1 and not scene.playing,"UI step next cumulative hold")
	press("Native / 2x");check(scene.zoom==1,"UI native zoom")
	press("Native / 2x");check(scene.zoom==2,"UI nearest2x zoom")
	for expected in [2.0,.5,1.0]:press("Speed");check(scene.rate==expected,"UI speed%.1f"%expected)
	press("Camera");check(not scene.follow,"UI fixed camera")
	press("Camera");check(scene.follow,"UI follow camera")
	press("Contact lock");check(not scene.contact_lock,"UI raw physical policy")
	press("Contact lock");check(scene.contact_lock,"UI shared stance policy")
	var cumulative := 0.0
	for i in range(72):
		# Interior sampling avoids conflating the independent oracle with the player's roundoff policy.
		var time=(cumulative+float(manifest.frames[i].duration_ms)*.4)/1000.0
		for cycle in [0,1]:
			scene.clock=time+cycle*float(manifest.cycle_ms)/1000.0;scene.present()
			check(scene.actor.frame==i,"Release actual cumulative hold%d cycle%d"%[i,cycle])
			check(close(scene.actor.position,independent_position(scene.clock,scene.zoom,scene.follow,scene.contact_lock)),"Release episode-target position%d cycle%d"%[i,cycle])
		cumulative+=float(manifest.frames[i].duration_ms)
	for rate in [.5,1.0,2.0]:
		scene.rate=rate;scene.clock=0.0;scene.playing=true
		for row in manifest.frames:scene._process(float(row.duration_ms)/1000.0/rate)
		check(scene.actor.frame==0 and abs(scene.clock-float(manifest.cycle_ms)/1000.0)<1e-12,"UI scaled full-loop clock%.1f"%rate)
	scene.playing=false
	var shot_id:=0
	for zoom in [1,2]:
		for follow in [false,true]:
			for locked in [false,true]:
				scene.zoom=zoom;scene.follow=follow;scene.contact_lock=locked
				# Visible full-actor phase in first cycle: fixed origins, never fit to bbox.
				scene.clock=scene.timeline.pose_time(0,42,.4);scene.present()
				check(close(scene.actor.position,independent_position(scene.clock,zoom,follow,locked)),"Actual scene position z%d follow%s lock%s"%[zoom,follow,locked])
				await process_frame;await RenderingServer.frame_post_draw
				var gpu=root.get_texture().get_image();gpu.convert(Image.FORMAT_RGBA8)
				var source=Image.load_from_file("res://sprites/"+manifest.frames[42].file);source.convert(Image.FORMAT_RGBA8)
				var differences:=0;var tested:=0
				for y in range(256):
					for x in range(256):
						var color=source.get_pixel(x,y)
						# Opaque actor pixels over the actual moving grid; transparent background is separate UI artwork.
						if color.a==1.0:
							for dy in range(zoom):
								for dx in range(zoom):
									var point=Vector2i(scene.actor.position)+Vector2i(x*zoom+dx,y*zoom+dy)
									if point.x<0 or point.y<0 or point.x>=gpu.get_width() or point.y>=gpu.get_height():differences+=1
									elif gpu.get_pixelv(point)!=color:differences+=1
									tested+=1
				check(tested>0 and differences==0,"Actual UI wholeactor opaque readback z%d follow%s lock%s"%[zoom,follow,locked])
				var path=output+"/release-%02d.png"%shot_id;gpu.save_png(path);shot_id+=1
				screenshots.append({"path":path,"sha256":FileAccess.get_sha256(path),"zoom":zoom,"follow":follow,"contact_lock":locked,"clock_seconds":scene.clock,"frame":scene.actor.frame,"draw_position":[scene.actor.position.x,scene.actor.position.y],"opaque_pixels_checked":tested,"different_pixels":differences})
	check(FileAccess.get_sha256("res://sprites/manifest.json")==source_sha,"Release source unchanged")
	check(file_ledger_valid(ledger),"Release ledger unchanged after controls/GPU proof")
	var failures=checks.filter(func(c):return not c.passed)
	var report={"schema":"captain-standalone-release-integration/v1","candidate_manifest_sha256":source_sha,"leg_manifest_sha256":policy.leg_manifest_sha256,"release_ledger_sha256":FileAccess.get_sha256("res://release-files.json"),"passed":failures.is_empty(),"episode_targets_independently_checked":episode_targets_independently_checked,"checks":checks,"failures":failures,"screenshots":screenshots,"engine":Engine.get_version_info(),"preview_sha256":FileAccess.get_sha256("res://preview.gd"),"clock_sha256":FileAccess.get_sha256("res://hold_clock.gd"),"test_source_sha256":FileAccess.get_sha256(get_script().resource_path),"limits":["One released combat-ready Walk only","No art approval from engineering checks","UI GPU grid comparison checks opaque actor pixels; full soft-alpha light/dark fixture belongs to separate source engine proof","Episode policy integration is checked, not a new exhaustive material/physics proof","Control signals are emitted on actual scene buttons; OS mouse input is not simulated"]}
	var file=FileAccess.open(output+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("RELEASE_INTEGRATION ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty() else 1)
