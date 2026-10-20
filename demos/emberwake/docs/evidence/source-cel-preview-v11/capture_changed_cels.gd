extends SceneTree
## Arranged actual Hero/Sprite2D A/B GPU stills. No action/VFX/quality score.
## A substitutes retained v10 atlas/clip table; B uses the v11 catalog normally.
const HERO = preload("res://scripts/hero.gd")
var checks := 0
var failures: Array[String] = []
var records: Array[Dictionary] = []
var output := ""
var viewport: SubViewport
var actors: Node2D
var label: Label

class Ground extends Node2D:
	func _draw() -> void:
		draw_rect(Rect2(0,0,640,280),Color("27392f"))
		draw_line(Vector2(320,0),Vector2(320,280),Color("8c9a81"),1)

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--changed-cel-output="):
			output = arg.trim_prefix("--changed-cel-output=")
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)
		printerr("CHANGED_CEL FAIL: " + note)

func _run() -> void:
	check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output), "fresh absolute output")
	check(DisplayServer.get_name() != "headless", "actual renderer required")
	if not failures.is_empty():
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	viewport = SubViewport.new()
	viewport.size = Vector2i(640,280)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var ground := Ground.new()
	viewport.add_child(ground)
	actors = Node2D.new()
	ground.add_child(actors)
	label = Label.new()
	label.position = Vector2(8,8)
	label.add_theme_font_size_override("font_size",12)
	ground.add_child(label)
	for id in ["rowan", "brann"]:
		for view in ["northeast", "northwest"]:
			await capture(id,view)
	var receipt := {"passed":failures.is_empty(),"assertions":checks,"failures":failures,"cases":records,"engine":Engine.get_version_info(),"display":DisplayServer.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"scope":"Four arranged actual Hero/Sprite2D game-scale paired GPU stills at explicit mid-exposure times. A substitutes retained v10 atlas and clip table; B loads v11 catalog normally. Not ordinary input, continuous motion, physical contact, damage/VFX or a numeric art score."}
	var f := FileAccess.open(output+"/RECEIPT.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(receipt,"  ")+"\n")
	f.close()
	print("CHANGED_CEL "+("PASS" if failures.is_empty() else "FAIL")+": "+str(checks)+" assertions;4 paired GPU PNGs")
	quit(0 if failures.is_empty() else 1)

func capture(id: String, view: String) -> void:
	for child in actors.get_children():
		child.free()
	var action := "walk" if id == "rowan" else "attack"
	var t := .196875 if id == "rowan" else .2125
	var aim := Vector2(1 if view == "northeast" else -1,-1).normalized()
	var old_manifest_path := "res://assets/comparison-v10/"+id+"-animations.json"
	var old_atlas_path := "res://assets/comparison-v10/"+id+"-atlas.png"
	var old_manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(old_manifest_path))
	var pair: Array = []
	for index in range(2):
		var hero := HERO.new()
		actors.add_child(hero)
		hero.set_process(false)
		hero.set_physics_process(false)
		check(hero.set_character(id), "actual catalog hero loads")
		if index == 0:
			hero._animations = old_manifest.animations
			hero._sprite.texture = load(old_atlas_path)
		hero.position = Vector2(160+index*320,220)
		hero._set_aim(aim)
		hero._action_aim = aim
		hero._set_state(action,.41 if action == "attack" else 0)
		hero._update_animation(0)
		hero._animation_time = t
		hero._state_time = t
		hero._update_animation(0)
		check(hero.current_art_clip == view+"_"+action,"requested actual view/action")
		check(hero.current_art_frame == int(hero._animations[view+"_"+action].frames[3]),"changed exposure03 actually selected")
		pair.append(hero)
	label.text = "%s / %s / %s / %.6fs\nRetained v10                          Source-cel v11" % [id,view,action,t]
	await process_frame
	await RenderingServer.frame_post_draw
	var im := viewport.get_texture().get_image()
	check(not im.is_empty(),"actual GPU framebuffer")
	var a := im.get_region(Rect2i(112,132,96,104))
	var b := im.get_region(Rect2i(432,132,96,104))
	var changed := 0
	for y in range(104):
		for x in range(96):
			if a.get_pixel(x,y) != b.get_pixel(x,y):
				changed += 1
	check(changed > 0,"new cel visibly changes actual game-scale pixels")
	var filename := id+"-"+view+"-"+action+".png"
	check(im.save_png(output+"/"+filename) == OK,"paired GPU PNG saved")
	var entry: Dictionary = pair[1]._character_entry(id)
	records.append({"actor":id,"view":view,"action":action,"state_time":t,"exposure":3,"old_frame":pair[0].current_art_frame,"new_frame":pair[1].current_art_frame,"old_atlas_sha256":FileAccess.get_sha256(old_atlas_path),"new_atlas_sha256":FileAccess.get_sha256(str(entry.atlas)),"new_manifest_sha256":FileAccess.get_sha256(str(entry.manifest)),"changed_actual_crop_pixels":changed,"screenshot":filename,"screenshot_sha256":FileAccess.get_sha256(output+"/"+filename)})
