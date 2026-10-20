extends SceneTree
## Actual production Hero/Sprite2D pixels at explicit rational samples.
## Run in the isolated preview project with a real renderer, not --headless.
## Translation is an authored158px/s render fixture, NOT a physics/contact test.
## Optional -- --walk-preview-output=/absolute/fresh/directory

const HERO = preload("res://scripts/hero.gd")
const CLOCK := 320
const LOOPS := 2
const IDS := ["brann"]
const VIEWS := ["northeast", "northwest"]
var output := "res://output/walk-art-preview"
var checks := 0
var failures: Array[String] = []
var records: Array[Dictionary] = []
var viewport: SubViewport
var actors: Node2D
var caption: Label

class Ground extends Node2D:
	func _draw() -> void:
		draw_rect(Rect2(0,0,640,280),Color("27392f"))
		for x in range(0,640,16):
			draw_line(Vector2(x,40),Vector2(x,280),Color("304438"),1)
		for y in range(40,280,16):
			draw_line(Vector2(0,y),Vector2(640,y),Color("304438"),1)
		draw_line(Vector2(320,0),Vector2(320,280),Color("8c9a81"),1)

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--walk-preview-output="):
			output=arg.trim_prefix("--walk-preview-output=")
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks+=1
	if not value:
		failures.append(note)
		printerr("WALK_PREVIEW FAIL: "+note)

func _run() -> void:
	check(DisplayServer.get_name()!="headless","real renderer required")
	check(not DirAccess.dir_exists_absolute(output),"fresh output required")
	if not failures.is_empty():
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	viewport=SubViewport.new()
	viewport.size=Vector2i(640,280)
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ground:=Ground.new()
	viewport.add_child(ground)
	actors=Node2D.new()
	ground.add_child(actors)
	caption=Label.new()
	caption.add_theme_font_size_override("font_size",12)
	caption.position=Vector2(8,8)
	ground.add_child(caption)
	for id in IDS:
		for view in VIEWS:
			await sample_clip(id,view)
	var report:={"passed":failures.is_empty(),"assertions":checks,"failures":failures,"engine":Engine.get_version_info(),"renderer":RenderingServer.get_rendering_device(),"display":DisplayServer.get_name(),"clock_hz":CLOCK,"loops":LOOPS,"clips":records,"scope":"Actual Hero/Sprite2D GPU frames, fixed camera and explicitly sampled clock. Left in-place, right authored158px/s translation. No input/controller/world-contact or human normal-speed approval. Route resets after2loops are transport resets, not animation-loop evidence."}
	var f:=FileAccess.open(output+"/RECEIPT.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  "))
	f.close()
	print("WALK_PREVIEW "+("PASS" if failures.is_empty() else "FAIL")+": "+str(checks)+" assertions; "+str(records.size())+" actual GPU clips")
	quit(0 if failures.is_empty() else 1)

func sample_clip(id: String, view: String) -> void:
	for child in actors.get_children():
		child.free()
	var pair: Array = []
	var aim:=Vector2(-1 if view=="northwest" else 1,-1).normalized()
	for _index in range(2):
		var hero:=HERO.new()
		actors.add_child(hero)
		hero.set_process(false)
		hero.set_physics_process(false)
		check(hero.set_character(id),id+" loads actual catalog bank")
		hero._set_aim(aim)
		hero._set_state("walk")
		hero._update_animation(0)
		check(hero.current_art_clip==view+"_walk",id+" uses declared walk view")
		pair.append(hero)
	var clip: Dictionary=pair[0]._animations[view+"_walk"]
	var schedule: Array[int] = []
	for exposure in clip.frames.size():
		var ticks:=roundi(float(clip.holds[exposure])*CLOCK)
		check(ticks>0 and absf(ticks/float(CLOCK)-float(clip.holds[exposure]))<.0000001,"hold exactly represented at320Hz")
		for _tick in range(ticks):
			schedule.append(exposure)
	check(schedule.size()==144,"declared .45second walk")
	var directory:=output+"/"+id+"-"+view
	DirAccess.make_dir_recursive_absolute(directory)
	var hashes: Dictionary={}
	var rows: Array[Dictionary]=[]
	for tick in range(schedule.size()*LOOPS):
		# Mid-raster-tick sampling avoids mistaking a binary-float boundary for
		# a whole-exposure error. Exact durations stay separately verified.
		var t: float=(tick+.5)/CLOCK
		var expected_exposure: int=schedule[tick%schedule.size()]
		var expected_frame: int=int(clip.frames[expected_exposure])
		pair[0].position=Vector2(160,220)
		var origin:=Vector2(395,155 if view=="southeast" else 235)
		pair[1].position=origin+aim*HERO.MOVE_SPEED*t
		for hero in pair:
			hero._animation_time=t
			hero._update_animation(0)
			check(hero.current_art_frame==expected_frame,id+" "+view+" actual exposure at tick"+str(tick))
		caption.text="%s / %s / %.5fs\nIn place                         Authored world translation"%[id,view,t]
		await process_frame
		await RenderingServer.frame_post_draw
		var image:=viewport.get_texture().get_image()
		check(not image.is_empty(),"actual GPU image available")
		var crop:=image.get_region(Rect2i(112,132,96,104))
		var digest:=crop.get_data().hex_encode().sha256_text()
		if hashes.has(expected_exposure):
			check(hashes[expected_exposure]==digest,"in-place held pose/second-loop pixels remain exact")
		else:
			hashes[expected_exposure]=digest
		var name:="%04d.png"%tick
		check(image.save_png(directory+"/"+name)==OK,"actual GPU frame saved")
		rows.append({"tick":tick,"time":t,"exposure":expected_exposure,"atlas_frame":expected_frame,"in_place_crop_RGBA_hex_text_sha256":digest,"world_root":[pair[1].position.x,pair[1].position.y],"file":id+"-"+view+"/"+name})
	check(hashes.size()==clip.frames.size(),"every declared exposure rendered")
	var unique: Dictionary={}
	for digest in hashes.values():
		unique[digest]=true
	check(unique.size()==clip.frames.size(),"every exposure has distinct actual game-scale body pixels")
	records.append({"actor":id,"view":view,"exposures":clip.frames.size(),"rendered_unique_poses":unique.size(),"ticks":rows.size(),"actual_in_place_crop_hashes":hashes,"samples":rows})
