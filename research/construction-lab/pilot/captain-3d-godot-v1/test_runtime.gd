extends SceneTree
var output=""
var chosen=""
var checks=[]
var observations=[]
func _initialize()->void:
    var args=OS.get_cmdline_user_args()
    for i in range(args.size()-1):
        if args[i]=="--output":output=args[i+1]
        if args[i]=="--pack":chosen=args[i+1]
    call_deferred("run")
func check(ok:bool,message:String)->void:checks.append({"passed":ok,"description":message})
func rgba_sha(image:Image)->String:
    var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(image.get_data());return hash.finish().hex_encode()
func snapshot(viewport:SubViewport)->Image:
    await process_frame;await RenderingServer.frame_post_draw;return viewport.get_texture().get_image()
func run()->void:
    if output.is_empty()or DirAccess.dir_exists_absolute(output):push_error("Fresh output required");quit(2);return
    DirAccess.make_dir_recursive_absolute(output)
    var path="res://packs/"+chosen
    var pack=JSON.parse_string(FileAccess.get_file_as_string(path+"/pack.json"))
    var original=load(path+"/walk.res")
    var resource_path=output.path_join("walk-reloaded.res")
    check(ResourceSaver.save(original,resource_path)==OK,"Save actual SpriteFrames")
    var frames=ResourceLoader.load(resource_path,"SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE)
    check(frames is SpriteFrames and frames.get_frame_count("walk")==65,"Reopen65 real frame textures")
    check(frames.get_animation_speed("walk")==60 and frames.get_animation_loop("walk"),"Native60Hz loop resource")
    var size=Vector2i(pack.canvas[0],pack.canvas[1])
    var viewport=SubViewport.new();viewport.size=size;viewport.disable_3d=true;viewport.transparent_bg=false;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
    var background=Polygon2D.new();background.polygon=PackedVector2Array([Vector2.ZERO,Vector2(size.x,0),Vector2(size.x,size.y),Vector2(0,size.y)]);viewport.add_child(background)
    var sprite=AnimatedSprite2D.new();sprite.sprite_frames=frames;sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;sprite.animation="walk";sprite.pause();viewport.add_child(sprite)
    for i in range(65):
        var source=Image.new();source.load_png_from_buffer(FileAccess.get_file_as_bytes(pack.images[i].resource_path));source.convert(Image.FORMAT_RGBA8)
        var imported=frames.get_frame_texture("walk",i).get_image();imported.convert(Image.FORMAT_RGBA8)
        check(rgba_sha(source)==rgba_sha(imported),"Lossless imported/reopened RGBA cel"+str(i))
        check(frames.get_frame_duration("walk",i)==1,"Exact unit hold cel"+str(i))
        sprite.set_frame_and_progress(i,0)
        for color in [Color8(61,70,82),Color8(196,201,208)]:
            background.color=color;var image=await snapshot(viewport)
            var file="gpu-%03d-bg%d.png"%[i,color.r8];image.save_png(output.path_join(file))
            observations.append({"cel":i,"background":[color.r8,color.g8,color.b8],"file":file,"gpu_rgba_sha256":rgba_sha(image)})
    var world=load("res://viewer.gd").new();world.chosen=chosen;root.add_child(world);world.set_process(false)
    check(world.error.is_empty(),"Actual local viewer loads same imported pack")
    check(world.mode==pack.get("default_visual_root_policy","continuous"),"Viewer obeys declared whole-actor visual clock policy")
    if world.mode=="synchronized":
        var held_a=world.sampled_state(0)
        var held_b=world.sampled_state(1.0/120.0)
        check(held_a.index==held_b.index and held_a.screen==held_b.screen,"Declared60Hz visual snapshot holds root and pose together")
    world.playing=false
    for i in range(65):
        world.clock_seconds=i/60.0;world.present();check(world.sprite.frame==i,"Pose at rational hold boundary"+str(i))
        world.clock_seconds=(i+1)/60.0-1e-7;world.present();check(world.sprite.frame==i,"Pose before boundary"+str(i))
    world.clock_seconds=65.0/60.0;world.present()
    check(world.sprite.frame==0 and world.sampled_state(world.clock_seconds).cycle==1,"65/60seconds wraps pose and accumulates world stride")
    world.mode="continuous";var a=world.sampled_state(0);var b=world.sampled_state(1.0/120.0)
    check(a.index==b.index and a.screen.distance_to(b.screen)>0,"Real root movement during same held cel")
    world.mode="synchronized";check(world.sampled_state(0).screen==world.sampled_state(1.0/120.0).screen,"Separate synchronized root policy")
    world.mode="continuous";world.clock_seconds=0;world.playing=true
    for delta in [.013,.077,.123,.87]:world.advance_seconds(delta)
    check(absf(world.clock_seconds-1.083)<1e-9 and world.sprite.frame==64,"Variable update partitions keep exact source phase")
    world.playing=false;var before=world.clock_seconds;world.advance_seconds(.4);check(world.clock_seconds==before,"Pause preserves fractional phase")
    check(not world.advance_seconds(-1)and not world.advance_seconds(INF)and world.clock_seconds==before,"Invalid clock inputs leave viewer unchanged")
    var key=InputEventKey.new();key.keycode=KEY_R;key.pressed=true;Input.parse_input_event(key);await process_frame
    check(world.clock_seconds==0 and world.playing and world.sprite.frame==0,"Actual key input restarts viewer")
    key.keycode=KEY_SPACE;Input.parse_input_event(key);await process_frame;check(not world.playing,"Actual key input pauses viewer")
    world.clock_seconds=33.0/60;world.mode=pack.get("default_visual_root_policy","continuous");world.follow_camera=false;world.zoom=1;world.present();await process_frame;await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png(output.path_join("viewer-native.png"))
    world.zoom=2;world.follow_camera=true;world.present();await process_frame;await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png(output.path_join("viewer-nearest2x-follow.png"))
    # Native AnimatedSprite2D autoplay remains independently tested, though the
    # viewer pauses it and owns pose/root with one explicit scalar clock.
    world.visible=false;var loops=[];var transitions=[]
    sprite.frame_changed.connect(func():transitions.append(sprite.frame))
    sprite.animation_looped.connect(func():loops.append(Time.get_ticks_usec()))
    var started=Time.get_ticks_usec();sprite.set_frame_and_progress(0,0);sprite.play("walk")
    while loops.size()<2 and Time.get_ticks_usec()-started<4000000:await process_frame
    sprite.pause();check(loops.size()==2,"Actual unforced engine playback completes two loops")
    var monotonic=true
    for i in range(1,transitions.size()):
        if transitions[i]!=(transitions[i-1]+1)%65:monotonic=false
    check(monotonic and transitions.size()>=129,"Actual engine frame changes preserve complete adjacent source order")
    var failures=checks.filter(func(item):return not item.passed)
    var report={"state":"MECHANICAL_RUNTIME_PROOF_NOT_ART_APPROVAL","passed":failures.is_empty(),"checks":checks,"failures":failures,"pack_sha256":FileAccess.get_sha256(path+"/pack.json"),"saved_resource_sha256":FileAccess.get_sha256(resource_path),"godot":Engine.get_version_info(),"renderer":RenderingServer.get_video_adapter_name(),"code_sha256":{"test_runtime.gd":FileAccess.get_sha256("res://test_runtime.gd"),"viewer.gd":FileAccess.get_sha256("res://viewer.gd")},"gpu_observations":observations,"unforced_engine_playback":{"loops_usec":loops,"transitions":transitions},"limits":["Input is a diagnostic candidate, not approved art","GPU PNGs need independent source-alpha comparison","Only one threequarter view","No force/collision or full sole-material proof","Screenshots/frame observations are not continuous video ingestion"]}
    FileAccess.open(output.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("CAPTAIN_RUNTIME ",checks.size()," failures ",failures.size());quit(0 if failures.is_empty()else 2)
