extends SceneTree
## Production pixels only. No synthetic fallback and no art-quality score.
## LP_NUM_THREADS=4 xvfb-run -a godot --path . --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --script tests/eight_directions_render.gd
## Optional -- --eight-render-output=/absolute/fresh/folder
## 24 release PNGs pair plain (.24s) and fire-release engine pixels; 48 further
## pairs compare plain versus charge at two preparation exposures in all views.

const HERO = preload("res://scripts/hero.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
const FX = preload("res://scripts/combat_fx.gd")
const IDS := ["rowan", "lyra", "brann"]
const VIEWS := ["south", "southeast", "east", "northeast", "north", "northwest", "west", "southwest"]
var checks := 0
var failures: Array[String] = []
var receipts: Array[Dictionary] = []
var charge_receipts: Array[Dictionary] = []
var output := "res://output/eight-directions-render"
var fixture: Node2D
var viewport: SubViewport
var actors: Node2D
var label: Label

class Background extends Node2D:
	func _draw() -> void:
		draw_rect(Rect2(0,0,320,280),Color("29382f"))
		draw_line(Vector2(40,220),Vector2(280,220),Color("566552"),1)

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--eight-render-output="):
			output = arg.trim_prefix("--eight-render-output=")
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)
		printerr("EIGHT_RENDER FAIL: " + note)

func _run() -> void:
	fixture = Node2D.new()
	root.add_child(fixture)
	var probe := HERO.new()
	fixture.add_child(probe)
	# Preflight every actor before producing any images: old four-view art must
	# never acquire a misleading eight-way screenshot receipt.
	for id in IDS:
		var loaded: bool = probe.set_character(id)
		check(loaded, id + " actual production bank loads")
		check(loaded and probe._directions == VIEWS, id + " actual production bank explicitly declares all eight directions")
	check(DisplayServer.get_name() != "headless", "a real renderer is required; use xvfb-run instead of --headless")
	if not failures.is_empty():
		await finish(false)
		return
	probe.free()
	viewport = SubViewport.new()
	viewport.size = Vector2i(320,280)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	fixture.add_child(viewport)
	var background := Background.new()
	viewport.add_child(background)
	actors = Node2D.new()
	actors.y_sort_enabled = true
	background.add_child(actors)
	label = Label.new()
	label.position = Vector2(12,12)
	label.add_theme_font_size_override("font_size",14)
	background.add_child(label)
	DirAccess.make_dir_recursive_absolute(output)
	for id in IDS:
		for index in VIEWS.size():
			await render_release(id,index)
	check(receipts.size() == 24, "24 actual actor/view release pairs were rendered")
	for id in IDS:
		for index in VIEWS.size():
			for exposure in [1,2]:
				await render_charge(id,index,exposure)
	check(charge_receipts.size() == 48, "48 actual eight-view preparation charge pairs were rendered")
	await finish(true)

func snapshot() -> Image:
	await process_frame
	await RenderingServer.frame_post_draw
	return viewport.get_texture().get_image()

func render_release(id: String, index: int) -> void:
	for child in actors.get_children():
		child.free()
	var actor := HERO.new()
	actor.position = Vector2(160,220)
	actors.add_child(actor)
	actor.set_physics_process(false)
	actor.set_process(false)
	var loaded: bool = actor.set_character(id)
	check(loaded and actor._directions == VIEWS, id + " stays bound to the actual eight-way bank during rendering")
	if not loaded or actor._directions != VIEWS:
		return
	var view: String = VIEWS[index]
	var aim := Vector2(sin(index*PI/4),cos(index*PI/4)).normalized()
	actor._set_aim(aim)
	actor._action_aim = aim
	actor._set_state("cast",.5)
	actor._state_time = .24
	actor._update_animation(0)
	label.text = "%s / %s / .24 s release" % [id,view]
	var frame: int = actor.current_art_frame
	var point: Array = actor._cast_hands[view]
	var hand: Vector2 = actor.get_cast_hand_global()
	var expected: Vector2 = actor.to_global((Vector2(point[0],point[1])-actor._pivot)*actor._sprite.scale)
	check(hand.is_equal_approx(expected), id + " " + view + " hand uses actual pivot and scale")
	var texture: Image = actor._sprite.texture.get_image()
	var source := Vector2i((frame % actor._columns)*int(actor._cell.x)+int(point[0]),int(frame/actor._columns)*int(actor._cell.y)+int(point[1]))
	var painted := 0
	for y in range(source.y-2,source.y+3):
		for x in range(source.x-2,source.x+3):
			if x >= 0 and y >= 0 and x < texture.get_width() and y < texture.get_height() and texture.get_pixel(x,y).a > .5:
				painted += 1
	check(painted >= 3, id + " " + view + " declared socket is near opaque release-cel paint")
	var plain: Image = await snapshot()
	check(not plain.is_empty(), id + " " + view + " renderer returns actual body pixels")
	if plain.is_empty():
		return
	actor._perform_action_hit("firebolt")
	var bolts := get_nodes_in_group("combat_projectiles")
	check(bolts.size() == 1, id + " " + view + " releases one actual firebolt")
	if bolts.is_empty():
		return
	var bolt: Node2D = bolts[0]
	bolt.set_physics_process(false)
	for child in actors.get_children():
		if child.get_script() == FX:
			child.set_process(false)
			child.elapsed = .01
			child.queue_redraw()
	check(bolt.global_position == actor.global_position and bolt.direction.is_equal_approx(aim), id + " " + view + " physical release remains on the foot plane with committed aim")
	check((bolt.global_position+bolt.visual_offset).is_equal_approx(hand), id + " " + view + " rendered projectile origin matches the measured socket")
	check(actor.current_art_frame == frame, id + " " + view + " release presents the same authored cast cel")
	var release: Image = await snapshot()
	check(not release.is_empty(), id + " " + view + " renderer returns actual release pixels")
	if release.is_empty():
		return
	var warm_change := 0
	for y in range(int(hand.y)-5,int(hand.y)+6):
		for x in range(int(hand.x)-5,int(hand.x)+6):
			if x >= 0 and y >= 0 and x < release.get_width() and y < release.get_height():
				var pixel := release.get_pixel(x,y)
				if pixel != plain.get_pixel(x,y) and pixel.r > pixel.b*1.15:
					warm_change += 1
	check(warm_change > 15, id + " " + view + " warm fire pixels render around the actual hand socket")
	var pair := Image.create(640,280,false,Image.FORMAT_RGBA8)
	pair.blit_rect(plain,Rect2i(0,0,320,280),Vector2i.ZERO)
	pair.blit_rect(release,Rect2i(0,0,320,280),Vector2i(320,0))
	var filename := id + "-" + view + "-plain-left-release-right.png"
	check(pair.save_png(output+"/"+filename) == OK, id + " " + view + " paired engine screenshot saves")
	var entry: Dictionary = actor._character_entry(id)
	receipts.append({"character":id,"view":view,"release_frame":frame,"manifest":entry.manifest,"manifest_sha256":FileAccess.get_sha256(str(entry.manifest)),"atlas":entry.atlas,"atlas_sha256":FileAccess.get_sha256(str(entry.atlas)),"columns":actor._columns,"cell":[actor._cell.x,actor._cell.y],"native_socket":point,"screen_socket":[hand.x,hand.y],"opaque_pixels_near_socket":painted,"warm_changed_pixels_near_socket":warm_change,"screenshot":filename,"screenshot_sha256":FileAccess.get_sha256(output+"/"+filename)})

func render_charge(id: String, index: int, exposure: int) -> void:
	for child in actors.get_children():
		child.free()
	var actor := HERO.new()
	actor.position = Vector2(160,220)
	actors.add_child(actor)
	actor.set_physics_process(false)
	actor.set_process(false)
	check(actor.set_character(id), id + " charge fixture loads actual bank")
	var view: String = VIEWS[index]
	if not actor._cast_hand_tracks.has(view):
		check(false,id + " " + view + " actual preparation track is required")
		return
	var aim := Vector2(sin(index*PI/4),cos(index*PI/4)).normalized()
	actor._set_aim(aim)
	actor._action_aim = aim
	actor._set_state("cast",.5)
	actor._pending_hit = "firebolt"
	actor._state_time = .10 if exposure == 1 else .19
	actor._update_animation(0)
	var clip: Dictionary = actor._animations[view + "_cast"]
	check(actor.current_art_frame == int(clip.frames[exposure]),id + " " + view + " actual preparation cel selected")
	var point: Array = actor._cast_hand_tracks[view][exposure]
	var hand: Vector2 = actor.get_cast_charge_hand_global()
	var expected: Vector2 = actor.to_global((Vector2(point[0],point[1])-actor._pivot)*actor._sprite.scale)
	check(hand.is_equal_approx(expected),id + " " + view + " charge uses displayed preparation palm")
	check(hand.distance_to(actor.get_cast_hand_global()) > 3,id + " " + view + " preparation is distinct from the release socket")
	label.text = "%s / %s / preparation %d" % [id,view,exposure]
	var plain: Image = await snapshot()
	var charge := FX.spawn(actors,actor.global_position,"cast_charge",aim,12.0,Color("ffbc65"))
	charge.tracking_actor = actor
	charge.elapsed = .17
	charge._process(0)
	charge.set_process(false)
	check((charge.global_position+charge.visual_offset).is_equal_approx(hand),id + " " + view + " actual FX follows preparation palm")
	var charged: Image = await snapshot()
	var changed := 0
	for y in range(int(hand.y)-6,int(hand.y)+7):
		for x in range(int(hand.x)-6,int(hand.x)+7):
			if x >= 0 and y >= 0 and x < charged.get_width() and y < charged.get_height():
				var pixel := charged.get_pixel(x,y)
				if pixel != plain.get_pixel(x,y) and pixel.r > pixel.b*1.15:
					changed += 1
	check(changed > 8,id + " " + view + " charge pixels render around the moving glove")
	check(get_nodes_in_group("combat_projectiles").is_empty(),id + " " + view + " charge has not released a projectile")
	var pair := Image.create(640,280,false,Image.FORMAT_RGBA8)
	pair.blit_rect(plain,Rect2i(0,0,320,280),Vector2i.ZERO)
	pair.blit_rect(charged,Rect2i(0,0,320,280),Vector2i(320,0))
	var filename := id + "-" + view + "-prep" + str(exposure) + "-plain-left-charge-right.png"
	check(pair.save_png(output+"/"+filename) == OK,id + " " + view + " charge comparison saves")
	var entry: Dictionary = actor._character_entry(id)
	charge_receipts.append({"character":id,"view":view,"exposure":exposure,"frame":actor.current_art_frame,"state_time":actor._state_time,"native_hand":point,"screen_hand":[hand.x,hand.y],"warm_changed_pixels_near_hand":changed,"manifest_sha256":FileAccess.get_sha256(str(entry.manifest)),"atlas_sha256":FileAccess.get_sha256(str(entry.atlas)),"screenshot":filename,"screenshot_sha256":FileAccess.get_sha256(output+"/"+filename)})

func finish(rendered: bool) -> void:
	DirAccess.make_dir_recursive_absolute(output)
	var file := FileAccess.open(output+"/RESULTS.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"failures":failures,"production_only":true,"rendered":rendered,"receipts":receipts,"charge_receipts":charge_receipts,"display_server":DisplayServer.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"qualification":"Frozen engine fixture using actual production assets. Release pairs show plain left and fire right at .24 s; charge pairs show the two actual preparation cels with their moving palm points. Colored pixel differences check binding; visual glove anatomy/alignment and motion quality need separate review. No ordinary-play or numeric art-score claim."},"\t")+"\n")
	file.close()
	fixture.queue_free()
	await process_frame
	await create_timer(.35,true,false,true).timeout
	if failures.is_empty():
		print("EIGHT_RENDER PASS: %d assertions; 24 release pairs; 48 preparation pairs; no art score" % checks)
		quit(0)
	else:
		quit(1)
