extends SceneTree
const Lab = preload("res://lab.gd")
var checks: Array = []
var loops := 0
var output := "/tmp/captain-godot-proof"
func check(value: bool, label: String) -> void:
	checks.append({"description":label,"passed":value})
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): output = arg.substr(9)
	call_deferred("run")
func run() -> void:
	DirAccess.make_dir_recursive_absolute(output)
	var resource = Lab.frames_resource()
	check(resource.get_frame_count("experimental_walk")==12, "Twelve real SpriteFrames textures")
	check(ResourceSaver.save(resource,output+"/walk.res")==OK,"Save real resource")
	var reopened = ResourceLoader.load(output+"/walk.res","",ResourceLoader.CACHE_MODE_IGNORE)
	check(reopened != null,"Reload real resource")
	check(reopened.get_animation_speed("experimental_walk")==10 and reopened.get_animation_loop("experimental_walk"),"100ms holds and loop")
	var viewport := SubViewport.new()
	viewport.size=Vector2i(256,256)
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var bg := Sprite2D.new()
	bg.centered=false
	viewport.add_child(bg)
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames=reopened
	sprite.animation="experimental_walk"
	sprite.centered=false
	sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	viewport.add_child(sprite)
	var maximum := 0
	for mode in ["opaque","checker"]:
		bg.texture=ImageTexture.create_from_image(Image.load_from_file("res://assets/background-"+mode+".png"))
		for frame in range(12):
			check(reopened.get_frame_texture("experimental_walk",frame).get_image().get_data()==Image.load_from_file("res://assets/frames/%02d.png"%frame).get_data(),"Reopened exact RGBA %s/%d"%[mode,frame])
			sprite.frame=frame
			await process_frame
			await RenderingServer.frame_post_draw
			var actual=viewport.get_texture().get_image()
			actual.convert(Image.FORMAT_RGBA8)
			var expected=Image.load_from_file("res://assets/%s-%02d.png"%[mode,frame])
			expected.convert(Image.FORMAT_RGBA8)
			var a=actual.get_data();var b=expected.get_data();var error=0
			for i in range(a.size()): error=max(error,abs(int(a[i])-int(b[i])))
			maximum=max(maximum,error)
			check(error<=1,"Actual GPU RGBA %s/%d <=1LSB"%[mode,frame])
			if frame in [0,3,6,9]:actual.save_png(output+"/%s-%02d.png"%[mode,frame])
	var original = reopened.get_frame_texture("experimental_walk",0)
	reopened.set_frame("experimental_walk",0,reopened.get_frame_texture("experimental_walk",1),1.0)
	sprite.frame=0
	await process_frame;await RenderingServer.frame_post_draw
	var wrong=viewport.get_texture().get_image();wrong.convert(Image.FORMAT_RGBA8)
	var correct=Image.load_from_file("res://assets/checker-00.png");correct.convert(Image.FORMAT_RGBA8)
	check(wrong.get_data()!=correct.get_data(),"Negative wrong texture order detected by actual GPU")
	reopened.set_frame("experimental_walk",0,original,2.0)
	check(reopened.get_frame_duration("experimental_walk",0)!=1.0,"Negative wrong hold duration detected")
	reopened.set_frame("experimental_walk",0,original,1.0)
	sprite.animation_looped.connect(func(): loops+=1)
	sprite.play("experimental_walk")
	sprite.frame=0
	var elapsed:=0.0
	while elapsed<2.6:
		await process_frame
		elapsed+=sprite.get_process_delta_time()
		var phase=fposmod(elapsed,1.2)
		if fposmod(phase,.1)>.02 and fposmod(phase,.1)<.08:
			check(sprite.frame==int(floor(phase*10)),"Actual AnimatedSprite2D playback %.4fs"%elapsed)
	check(loops==2,"Two actual loop signals over2.6s")
	sprite.pause();var held=sprite.frame
	await create_timer(.23).timeout
	check(sprite.frame==held,"Actual engine pause holds frame")
	sprite.play();await create_timer(.13).timeout
	check(sprite.frame!=held,"Actual engine resume advances")
	viewport.queue_free()
	var lab=Lab.new();root.add_child(lab)
	await process_frame
	lab.command("Play/Pause");lab.clock=.6;lab.present()
	check(lab.sprite.frame==6,"UI clock exact6 tick hold boundary")
	lab.clock=.59999999;lab.present();check(lab.sprite.frame==5,"True early boundary remains previous frame")
	lab.clock=1.2;lab.present();check(lab.sprite.frame==0,"UI exact72tick loop")
	lab.command("Step");check(lab.sprite.frame==1 and not lab.playing,"Step pauses at next hold")
	lab.command("Restart");check(lab.sprite.frame==0,"Restart resets")
	await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output+"/actual-lab.png")
	lab.command("1× / 2×")
	check(lab.preview.custom_minimum_size==Vector2(256,256),"Native1x256 canvas presentation")
	await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output+"/actual-lab-1x.png")
	var failed=checks.filter(func(c):return not c.passed)
	var report={"schema":"captain-godot-proof/v1","manifest_sha256":FileAccess.get_sha256("res://assets/manifest.json"),"checks":checks,"failures":failed,"passed":failed.is_empty(),"gpu_max_channel_error":maximum,"engine":Engine.get_version_info(),"resource_sha256":FileAccess.get_sha256(output+"/walk.res"),"limitations":["Experimental unapproved art; one view and Walk only","No sole/contact proof","Actual playback samples avoid20ms boundary uncertainty; UI boundaries tested separately"],"code_sha256":{"lab.gd":FileAccess.get_sha256("res://lab.gd"),"test_runtime.gd":FileAccess.get_sha256("res://test_runtime.gd")}}
	var file=FileAccess.open(output+"/report.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("CAPTAIN_CHECKS ",checks.size()," failures ",failed.size())
	quit(0 if failed.is_empty() else 1)
