extends SceneTree
const Lab = preload("res://lab.gd")
var checks: Array=[]
var output:="/tmp/captain72-proof"
var loops:=0
func check(ok:bool,label:String)->void:
	checks.append({"passed":ok,"description":label})
func _initialize()->void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--source="):Lab.source_dir=arg.substr(9)
		if arg.begins_with("--output="):output=arg.substr(9)
	call_deferred("run")
func run()->void:
	assert(not Lab.source_dir.is_empty())
	DirAccess.make_dir_recursive_absolute(output)
	var frozen_manifest_sha=FileAccess.get_sha256(Lab.source_dir+"/manifest.json")
	var resource=Lab.frames_resource()
	check(ResourceSaver.save(resource,output+"/frames.res")==OK,"Save72 real textures")
	var reloaded=ResourceLoader.load(output+"/frames.res","",ResourceLoader.CACHE_MODE_IGNORE)
	check(reloaded.get_frame_count("experimental_walk")==72 and reloaded.get_animation_speed("experimental_walk")==60,"Reload72 frame60fps resource")
	var viewport:=SubViewport.new();viewport.size=Vector2i(256,256);viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
	var bg:=ColorRect.new();bg.size=Vector2(256,256);viewport.add_child(bg)
	var sprite:=AnimatedSprite2D.new();sprite.sprite_frames=reloaded;sprite.animation="experimental_walk";sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;viewport.add_child(sprite)
	var gpu_max:=0
	for value in [61,196]:
		bg.color=Color8(value,value,value)
		for i in range(72):
			sprite.frame=i
			var original=Image.load_from_file(Lab.source_dir+"/"+Lab.source_manifest.frames[i].file);original.convert(Image.FORMAT_RGBA8)
			var saved=reloaded.get_frame_texture("experimental_walk",i).get_image();saved.convert(Image.FORMAT_RGBA8)
			check(saved.get_data()==original.get_data(),"ReopenedRGBA%d/%d"%[value,i])
			await process_frame;await RenderingServer.frame_post_draw
			var image=viewport.get_texture().get_image();image.convert(Image.FORMAT_RGBA8)
			var a=image.get_data();var b=original.get_data();var error:=0
			for k in range(0,a.size(),4):
				for channel in range(3):
					var expected=int(round(float(b[k+channel])*b[k+3]/255.0+value*(1.0-b[k+3]/255.0)))
					error=max(error,abs(int(a[k+channel])-expected))
				error=max(error,abs(int(a[k+3])-255))
			gpu_max=max(gpu_max,error);check(error<=1,"ActualGPU%d/%d"%[value,i])
			if i%18==0:image.save_png(output+"/gpu-%d-%d.png"%[value,i])
	sprite.animation_looped.connect(func():loops+=1)
	sprite.play();sprite.frame=0
	var elapsed:=0.0
	while elapsed<2.45:
		await process_frame
		await RenderingServer.frame_post_draw
		elapsed+=sprite.get_process_delta_time()
		var phase=fposmod(elapsed,1.2)*60.0
		if fposmod(phase,1.0)>.25 and fposmod(phase,1.0)<.75:check(sprite.frame==int(floor(phase)),"Actual engine60fps%.6f"%elapsed)
	check(loops==2,"Actual72frame two loops")
	sprite.pause();var held=sprite.frame;await create_timer(.08).timeout;check(sprite.frame==held,"Actual pause")
	viewport.size=Vector2i(512,384);bg.size=Vector2(512,384);bg.color=Color8(61,61,61)
	var world_observations:Array=[]
	for tick in [0,18,36,54,72,90,108,126]:
		var index=tick%72
		var declared=Lab.source_manifest.frames[index].physical_root
		var physical=Vector2(declared[0],declared[1])+Vector2(-36,14)*floor(tick/72.0)
		var draw_position=(Vector2(128,64)+physical).round()
		sprite.position=draw_position;sprite.frame=index
		await process_frame;await RenderingServer.frame_post_draw
		var world_image=viewport.get_texture().get_image();world_image.convert(Image.FORMAT_RGBA8)
		var body=reloaded.get_frame_texture("experimental_walk",index).get_image();body.convert(Image.FORMAT_RGBA8)
		var bad:=0
		for y in range(256):
			for x in range(256):
				var pixel=body.get_pixel(x,y)
				var expected=pixel if pixel.a==1.0 else Color8(61,61,61)
				if world_image.get_pixel(x+int(draw_position.x),y+int(draw_position.y))!=expected:bad+=1
		check(bad==0,"Actual fullactor translatedRGBA tick%d"%tick)
		world_image.save_png(output+"/world-%03d.png"%tick)
		world_observations.append({"tick":tick,"frame":index,"physical_root":[physical.x,physical.y],"draw_origin":[draw_position.x,draw_position.y],"material_contact_validated":false})
	viewport.queue_free()
	var lab=Lab.new();root.add_child(lab);await process_frame;lab.playing=false;lab.set_process(false)
	for speed in [.5,1.0,2.0]:
		lab.speed=speed
		for i in range(145):
			lab.clock=i/60.0;lab.present();check(lab.sprite.frame==i%72,"Clock boundary%d speed%.1f"%[i,speed])
			if i>0:lab.clock=i/60.0-1e-8;lab.present();check(lab.sprite.frame==(i-1)%72,"True early%d speed%.1f"%[i,speed])
		lab.clock=0;lab.playing=true
		for i in range(72):lab._process(1.0/60.0/speed)
		check(lab.sprite.frame==0 and abs(lab.clock-1.2)<1e-12,"Accumulated72ticks scaled speed%.1f"%speed)
	lab.playing=false;lab.clock=.5;lab.present();lab._process(.2);check(abs(lab.clock-.5)<1e-12,"Pause clock remains fixed")
	lab.command("Step");check(lab.sprite.frame==31,"Step one60Hzhold")
	lab.command("Restart");check(lab.sprite.frame==0,"Restart")
	await process_frame;await RenderingServer.frame_post_draw;root.get_texture().get_image().save_png(output+"/actual-lab.png")
	check(FileAccess.get_sha256(Lab.source_dir+"/manifest.json")==frozen_manifest_sha,"Source manifest unchanged during engine run")
	var failures=checks.filter(func(c):return not c.passed)
	var file=FileAccess.open(output+"/report.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":"captain72-engine-proof/v1","manifest_sha256":frozen_manifest_sha,"checks":checks,"failures":failures,"passed":failures.is_empty(),"gpu_max_error":gpu_max,"world_observations":world_observations,"engine":Engine.get_version_info(),"code_sha256":{"lab.gd":FileAccess.get_sha256("res://lab.gd"),"test_runtime.gd":FileAccess.get_sha256("res://test_runtime.gd")},"material_contact":"NOT_VALIDATED by this clock/pixel runner; use separate exact-source test_material.gd wholeboot proof","art_status":"Source-bound art verdict is separate; rendering/clock passes do not award art points"},"\t"));file.close()
	print("CAPTAIN72 ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty() else 1)
