extends SceneTree
var legs_dir:=""
var actor_dir:=""
var output:="/tmp/captain-material"
var expected_stable:=true
var checks:Array=[]
func check(ok:bool,label:String)->void:checks.append({"passed":ok,"description":label})
func digest(bytes:PackedByteArray)->String:
	var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes);return hash.finish().hex_encode()
func view()->Dictionary:
	var viewport=SubViewport.new();viewport.size=Vector2i(512,288);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
	var sprite=Sprite2D.new();sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;viewport.add_child(sprite)
	return {"viewport":viewport,"sprite":sprite}
func _initialize()->void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--legs="):legs_dir=arg.substr(7)
		if arg.begins_with("--actor="):actor_dir=arg.substr(8)
		if arg.begins_with("--output="):output=arg.substr(9)
		if arg=="--expect-unstable":expected_stable=false
	call_deferred("run")
func run()->void:
	assert(not legs_dir.is_empty());DirAccess.make_dir_recursive_absolute(output)
	var binding=FileAccess.get_sha256(legs_dir+"/manifest.json")
	var m=JSON.parse_string(FileAccess.get_file_as_string(legs_dir+"/manifest.json"))
	var design=m.registered_design.legs
	var body:Array=[];var boots={"right":[],"left":[]};var image_hashes:Dictionary={}
	for i in range(72):
		for side in ["right","left"]:
			var path=legs_dir+"/boot-isolates/%s-%02d.png"%[side,i]
			var image=Image.load_from_file(path);image.convert(Image.FORMAT_RGBA8)
			if m.frames[i].legs[side].has("boot_material_RGBA_sha256"):
				check(digest(image.get_data())==m.frames[i].legs[side].boot_material_RGBA_sha256,"Source attached bootRGBA %s/%d"%[side,i])
			else:
				check(not expected_stable,"Historicalnegative lacks attachedidentity metadata %s/%d"%[side,i])
			image_hashes["%s/%d"%[side,i]]=FileAccess.get_sha256(path)
			boots[side].append(ImageTexture.create_from_image(image))
	var actor_binding=""
	if not actor_dir.is_empty():
		actor_binding=FileAccess.get_sha256(actor_dir+"/manifest.json")
		var actor=JSON.parse_string(FileAccess.get_file_as_string(actor_dir+"/manifest.json"))
		check(actor.leg_source_manifest_sha256==binding,"Fullactor binds exact leg source")
		for f in actor.frames:
			var path=actor_dir+"/"+f.file;check(FileAccess.get_sha256(path)==f.sha256,"Fullactor PNGhash %d"%f.frame)
			body.append(ImageTexture.create_from_image(Image.load_from_file(path)))
	var views={"right":view(),"left":view(),"actor":view()}
	var episodes:Dictionary={};var observations:Array=[]
	var stride=Vector2(m.root_stride[0],m.root_stride[1]);var max_offset:=0.0
	for mode in ["physical","global-contact-lock"]:
		for tick in range(144):
			for fraction in [0.0,.2,.4,.6,.8]:
				var time=tick+fraction;var phase=time/72.0;var index=tick%72;var active:Array=[];var targets:Dictionary={}
				for side in ["right","left"]:
					var d=design[side];var local=fposmod(phase+d.phase_offset,1.0)
					if local<.6-1e-12:
						active.append(side);var episode=floor(phase+d.phase_offset)
						targets[side]=(Vector2(d.rest_sole[0],d.rest_sole[1])+stride*(.3-d.phase_offset+episode)).round()
				var physical=stride*phase;var draw_root=physical
				if mode=="global-contact-lock" and not active.is_empty():
					var chosen=active[0];var sole=m.frames[index].legs[chosen].actual_sole
					draw_root=targets[chosen]-Vector2(sole[0],sole[1])
				max_offset=max(max_offset,draw_root.distance_to(physical))
				for side in ["right","left"]:
					views[side].sprite.texture=boots[side][index];views[side].sprite.position=Vector2(128,0)+draw_root
				if not body.is_empty():views.actor.sprite.texture=body[index];views.actor.sprite.position=Vector2(128,0)+draw_root
				await process_frame;await RenderingServer.frame_post_draw
				var row={"mode":mode,"tick":time,"frame":index,"physical_root":[physical.x,physical.y],"draw_root":[draw_root.x,draw_root.y],"active":active,"gpu":{}}
				for side in ["right","left"]:
					var actual=views[side].viewport.get_texture().get_image();actual.convert(Image.FORMAT_RGBA8)
					var hash=digest(actual.get_data());row.gpu[side]=hash
					if side in active:
						var key="%s/%s/%d"%[mode,side,int(floor(phase+design[side].phase_offset))]
						if not episodes.has(key):episodes[key]={"samples":0,"hashes":{}}
						episodes[key].samples+=1;episodes[key].hashes[hash]=true
				if not body.is_empty():
					var image=views.actor.viewport.get_texture().get_image();image.convert(Image.FORMAT_RGBA8);row.fullactor_rgba_sha256=digest(image.get_data())
					if fraction==0.0 and tick%36==0:image.save_png(output+"/actor-%s-%03d.png"%[mode,tick])
				observations.append(row)
	var metrics:Array=[];var stable:=true;var physical_detected:=false
	for key in episodes:
		var unique=episodes[key].hashes.size();metrics.append({"episode":key,"samples":episodes[key].samples,"unique_actual_GPU_whole_boot_RGBA":unique,"stable":unique==1})
		if key.begins_with("global-contact-lock/") and unique!=1:stable=false
		if key.begins_with("physical/") and unique!=1:physical_detected=true
	check(stable==expected_stable,"Actual wholeboot material gate matches expected stable=%s"%expected_stable)
	check(physical_detected,"Continuous physical drawroot negative exposes material displacement")
	check(FileAccess.get_sha256(legs_dir+"/manifest.json")==binding,"Leg manifest unchanged during GPUrun")
	if not actor_dir.is_empty():check(FileAccess.get_sha256(actor_dir+"/manifest.json")==actor_binding,"Actor manifest unchanged during GPUrun")
	var failures=checks.filter(func(c):return not c.passed)
	var report={"schema":"captain-whole-boot-GPU-material/v1","leg_manifest_sha256":binding,"actor_manifest_sha256":actor_binding,"checks":checks,"failures":failures,"passed":failures.is_empty(),"expected_material_stable":expected_stable,"actual_global_material_stable":stable,"metrics":metrics,"observations":observations,"boot_encoded_hashes":image_hashes,"max_visual_physical_root_offset":max_offset,"engine":Engine.get_version_info(),"code_sha256":FileAccess.get_sha256("res://test_material.gd"),"scope":"Actualtransparent512x288GPUwholebootRGBA,two cycles fivefractions/tick; BOTH boots and fullactor receive ONEsame drawtranslation","limits":["Finite720contexts/mode, not all continuous instants","Isolated boot material identity; actualactor calf/gear occlusion is separate","Policy derives correction from extrema witness but acceptance measures EVERYactual GPU bootmaterialpixel","No artquality, anatomical heel/toe collision or fullphysics approval"]}
	var f=FileAccess.open(output+"/report.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close();print("MATERIAL_GPU ",checks.size()," failures ",failures.size()," actualstable ",stable);quit(0 if failures.is_empty() else 1)
