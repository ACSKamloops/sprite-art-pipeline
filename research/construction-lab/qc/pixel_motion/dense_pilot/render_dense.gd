extends SceneTree
var viewport: SubViewport
var rig: Node2D
var frame_sprite: Sprite2D
var textures := {}
var records: Array = []
var dense: Array = []
func _initialize() -> void:
    Engine.max_fps = 0
    call_deferred("run")
func capture() -> Dictionary:
    await process_frame
    await RenderingServer.frame_post_draw
    var image := viewport.get_texture().get_image()
    var hasher := HashingContext.new()
    hasher.start(HashingContext.HASH_SHA256)
    hasher.update(image.get_data())
    var digest := hasher.finish().hex_encode()
    var path := "renders/" + digest + ".png"
    if not FileAccess.file_exists("res://" + path):
        image.save_png("res://" + path)
    return {"path":path,"rgba_sha256":digest,"width":image.get_width(),"height":image.get_height()}
func texture(path: String) -> Texture2D:
    if not textures.has(path):
        var image := Image.load_from_file("res://"+path)
        textures[path]=ImageTexture.create_from_image(image)
    return textures[path]
func run() -> void:
    DirAccess.make_dir_recursive_absolute("res://renders")
    viewport=SubViewport.new()
    viewport.size=Vector2i(128,160)
    viewport.transparent_bg=true
    viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    root.add_child(viewport)
    rig=load("res://cutout_rig.gd").new()
    viewport.add_child(rig)
    for i in range(60):
        rig.pose("walk",float(i)/60.0)
        for part in rig.sprites.values():part.visible=true
        var row := {"id":"dense_%02d"%i,"index":i,"phase":float(i)/60.0,"snapshot":rig.snapshot().duplicate(true),"composite":await capture(),"layers":{}}
        for name in rig.sprites:
            for part in rig.sprites.values():part.visible=false
            rig.sprites[name].visible=true
            row.layers[name]=await capture()
        dense.append(row)
    viewport.size=Vector2i(256,160)
    frame_sprite=Sprite2D.new()
    frame_sprite.centered=false
    frame_sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
    viewport.add_child(frame_sprite)
    for mode in ["old_12_hold5","dense_60_hold1","continuous_rig"]:
        for tick in range(61):
            for fraction in ([0.0]if tick==60 else[0.0,0.25,0.5,0.75,0.999999]):
                var t: float=float(tick)+fraction
                var index: int=int(floor(t))%60
                var phase: float=t/60.0 if mode=="continuous_rig"else(float(index)/60.0 if mode=="dense_60_hold1"else float(int(t/5.0)%12)/12.0)
                var root_x: float=48.0*t/60.0
                var row := {"mode":mode,"tick":t,"phase":fposmod(phase,1.0),"root_x":root_x,"viewport_origin_x":24,"layers":{}}
                if mode=="continuous_rig":
                    frame_sprite.visible=false
                    rig.visible=true
                    rig.position=Vector2(24+root_x,0)
                    rig.pose("walk",phase)
                    for part in rig.sprites.values():part.visible=true
                    row.composite=await capture()
                    for name in ["front_foot","rear_foot"]:
                        for part in rig.sprites.values():part.visible=false
                        rig.sprites[name].visible=true
                        row.layers[name]=await capture()
                else:
                    rig.visible=false
                    frame_sprite.visible=true
                    frame_sprite.position=Vector2(24+root_x,0)
                    var held: int=int(t)%60 if mode=="dense_60_hold1"else int(t/5.0)%12
                    var path: String=dense[held].composite.path if mode=="dense_60_hold1"else "baseline/walk_%02d-composite.png"%held
                    frame_sprite.texture=texture(path)
                    row.composite=await capture()
                    for name in ["front_foot","rear_foot"]:
                        path=dense[held].layers[name].path if mode=="dense_60_hold1"else "baseline/walk_%02d-%s.png"%[held,name]
                        frame_sprite.texture=texture(path)
                        row.layers[name]=await capture()
                records.append(row)
    var proof := {"schema":"sprite-dense-pilot-gpu-capture/v1","godot":Engine.get_version_info(),"video_adapter":RenderingServer.get_video_adapter_name(),"renderer":"gl_compatibility","dense":dense,"world":records,"world_models":"Actual GPU rendering of cached old/dense PNG frames vs continuously evaluated original rig; continuous root48px/s. Tick60 wraps to phase0. No new anatomy/colors."}
    FileAccess.open("res://gpu-observations.json",FileAccess.WRITE).store_string(JSON.stringify(proof,"  "))
    quit()
