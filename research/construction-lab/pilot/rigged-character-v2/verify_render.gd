extends SceneTree
var checks: Array=[]
var comparisons=0
var differences: Array=[]
func check(label: String,value: bool)->void:
    checks.append({"label":label,"passed":value})
func pixel_hash(image: Image)->String:
    image.convert(Image.FORMAT_RGBA8)
    var context=HashingContext.new();context.start(HashingContext.HASH_SHA256);context.update(image.get_data())
    return context.finish().hex_encode()
func _initialize()->void:
    Engine.max_fps=0
    call_deferred("run")
func viewport()->SubViewport:
    var result=SubViewport.new();result.size=Vector2i(192,192);result.transparent_bg=true
    result.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    result.canvas_item_default_texture_filter=Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
    root.add_child(result)
    return result
func run()->void:
    var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://generated/manifest.json"))
    for file in manifest.source_bindings:
        if FileAccess.get_sha256("res://"+file)!=manifest.source_bindings[file]:push_error("Stale source "+file);quit(2);return
    var output="res://generated/gpu-validation/"
    if FileAccess.file_exists(output+"report.json"):push_error("Refuse overwrite previous GPU audit");quit(2);return
    DirAccess.make_dir_recursive_absolute(output)
    var frames=load("res://generated/frames.tres") as SpriteFrames
    if frames==null:push_error("SpriteFrames not loadable");quit(2);return
    check("96 actual SpriteFrames animations",frames.get_animation_names().size()==96)
    check("Actual resource save",ResourceSaver.save(frames,output+"roundtrip.tres")==OK)
    frames=ResourceLoader.load(output+"roundtrip.tres","SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE) as SpriteFrames
    if frames==null:push_error("Saved SpriteFrames cannot reopen");quit(2);return
    var baked_view=viewport();var live_view=viewport()
    var baked=Sprite2D.new();baked.centered=false;baked.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;baked_view.add_child(baked)
    var rig=load("res://rig.gd").new();live_view.add_child(rig)
    rig.configure(JSON.parse_string(FileAccess.get_file_as_string("res://design.json")),JSON.parse_string(FileAccess.get_file_as_string("res://clips.json")))
    for binding in manifest.clips:
        var clip: Dictionary=manifest.clips[binding]
        check(binding+" frame count/FPS/loop",frames.get_frame_count(binding)==int(clip.duration_ticks) and frames.get_animation_speed(binding)==60 and frames.get_animation_loop(binding)==bool(clip.loop))
        rig.clear_equipment_selection()
        if not clip.equipment_selection.is_empty():check(binding+" explicit gear selection",rig.set_equipment(clip.equipment_selection))
        for tick in range(int(clip.duration_ticks)):
            var frame: Dictionary=clip.frames[tick]
            var texture=frames.get_frame_texture(binding,tick) as AtlasTexture
            check(binding+" source region/hold "+str(tick),texture!=null and texture.region==Rect2(frame.region[0],frame.region[1],192,192) and frames.get_frame_duration(binding,tick)==1)
            baked.texture=texture
            var sampled=tick in [0,int(clip.duration_ticks)/4,int(clip.duration_ticks)/2,int(clip.duration_ticks)-1]
            rig.visible=sampled
            if sampled:
                var pose: Dictionary=rig.pose(clip.base_clip,frame.pose.input_phase,clip.view)
                check(binding+" compatible actual source pose "+str(tick),not pose.has("error"))
            await process_frame
            await RenderingServer.frame_post_draw
            var expected=Image.load_from_file("res://generated/"+frame.png);expected.convert(Image.FORMAT_RGBA8)
            var actual=baked_view.get_texture().get_image();actual.convert(Image.FORMAT_RGBA8)
            var same=actual.get_data()==expected.get_data()
            check(binding+" actual GPU atlas pixels "+str(tick),same);comparisons+=1
            if not same:
                actual.save_png(output+binding.replace("/","-")+"-"+str(tick)+"-baked.png")
                differences.append({"binding":binding,"tick":tick,"kind":"atlas_GPU","expected":pixel_hash(expected),"actual":pixel_hash(actual)})
            if sampled:
                actual=live_view.get_texture().get_image();actual.convert(Image.FORMAT_RGBA8)
                same=actual.get_data()==expected.get_data()
                check(binding+" actual GPU source versus baked "+str(tick),same);comparisons+=1
                if not same:
                    actual.save_png(output+binding.replace("/","-")+"-"+str(tick)+"-source.png")
                    differences.append({"binding":binding,"tick":tick,"kind":"source_GPU","expected":pixel_hash(expected),"actual":pixel_hash(actual)})
        print("AUDITED ",binding)
    var failed=0
    for item in checks:
        if not item.passed:failed+=1
    var report={"schema":"copper-scout-v2-GPU-resource-validation/v1","passed":failed==0,"checks":checks,"comparisons":comparisons,"differences":differences,"source_bindings":manifest.source_bindings,"manifest_sha256":FileAccess.get_sha256("res://generated/manifest.json"),"driver":RenderingServer.get_video_adapter_name(),"godot":Engine.get_version_info(),"scope":"All6000 bakedGPU frames plus4live-source samples per96bindings, exactsame192origin, nearestfilter. ActualSpriteFrames save/reopen/regions/holds. Does notapprove artisticquality or moving-worldcontacts."}
    FileAccess.open(output+"report.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
    print("GPU comparisons ",comparisons," failedchecks ",failed)
    quit(0 if failed==0 else 2)
