extends SceneTree
## Executable actual-GPU sole-contact experiment, not artistic approval.
const MODES = ["live_continuous", "baked_continuous", "baked_draw_floor", "baked_draw_round", "baked_draw_ceil"]
const LANE = 512
const ORIGIN = 80
var source_dir: String
var output_dir: String
var viewport: SubViewport
var rig_script
var design: Dictionary
var clips: Dictionary
var rigs: Array = []
var sprites: Array = []
var report: Dictionary = {}
func sha(path: String) -> String:
    return FileAccess.get_sha256(path)
func _initialize() -> void:
    Engine.max_fps=0
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    source_dir=get_script().resource_path.get_base_dir()
    output_dir=source_dir.path_join("contact-proof")
    call_deferred("run")
func presented() -> Image:
    await process_frame
    await RenderingServer.frame_post_draw
    return viewport.get_texture().get_image()
func sole(image: Image, lane: int) -> Dictionary:
    var xmin=LANE
    var xmax=-1
    var count=0
    for x in range(LANE):
        if image.get_pixel(lane*LANE+x,169).a>0.0:
            xmin=mini(xmin,x);xmax=maxi(xmax,x);count+=1
    var below=0
    for y in range(170,192):
        for x in range(LANE):
            if image.get_pixel(lane*LANE+x,y).a>0.0:below+=1
    return {"xmin":xmin if count else null,"xmax":xmax if count else null,"opaque_count":count,"below_ground_pixels":below}
func run() -> void:
    design=JSON.parse_string(FileAccess.get_file_as_string(source_dir.path_join("design.json")))
    clips=JSON.parse_string(FileAccess.get_file_as_string(source_dir.path_join("clips.json")))
    rig_script=load(source_dir.path_join("rig.gd"))
    DirAccess.make_dir_recursive_absolute(output_dir)
    viewport=SubViewport.new();viewport.size=Vector2i(LANE*MODES.size(),192)
    viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
    root.add_child(viewport)
    var live=rig_script.new();viewport.add_child(live);live.configure(design,clips);rigs.append(live)
    for i in range(1,MODES.size()):
        var sprite=Sprite2D.new();sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
        viewport.add_child(sprite);sprites.append(sprite)
    report={"schema":"copper-scout-rendered-contact/v1","source_sha256":{},"renderer":{"godot":Engine.get_version_info().string,"adapter":RenderingServer.get_video_adapter_name(),"vendor":RenderingServer.get_video_adapter_vendor(),"method":RenderingServer.get_current_rendering_method()},"ground_boundary_y":170,"opaque_sole_row":169,"threshold_px":0.5,"sampling":"Five fractional samples per tick; two complete cycles including loop boundary and endpoint. Right view only; boot layers only.","physical_root":"Unwrapped continuous stride*input_phase, including every snapped draw policy.","cache":"Actual GPU boot-only tick images made from the bound current source; nearest texture filter, no recentering.","modes":MODES,"routes":[],"artistic_approval":false}
    for name in ["rig.gd","design.json","clips.json"]:report.source_sha256[name]=sha(source_dir.path_join(name))
    for clip in ["walk","run"]:
        var spec: Dictionary=clips.clips[clip]
        var ticks=int(spec.duration_ticks)
        var stride=float(spec.gait.root_motion_px_per_cycle)
        for side in ["front","rear"]:
            print("Caching ",clip," ",side)
            live.visible_layers=[side+"_boot"]
            var cache: Array=[]
            var cache_hashes: Array=[]
            for tick in range(ticks):
                live.position=Vector2.ZERO;live.pose(clip,float(tick)/ticks,"right")
                for sprite in sprites:sprite.visible=false
                var img: Image=await presented()
                var tile=img.get_region(Rect2i(0,0,192,192))
                var path=output_dir.path_join(clip+"_"+side+"_tick%03d.png"%tick)
                tile.save_png(path);cache_hashes.append(sha(path));cache.append(ImageTexture.create_from_image(tile))
            for sprite in sprites:sprite.visible=true
            var rows: Array=[]
            var references: Dictionary={}
            var maxima: Dictionary={}
            var failures: Dictionary={}
            var contact_counts: Dictionary={}
            for mode in MODES:maxima[mode]=0.0;failures[mode]=0;contact_counts[mode]=0
            for sample in range(ticks*10+1):
                var time=float(sample)/5.0
                var phase=time/ticks
                var held_tick=int(floor(time))%ticks
                var root_x=stride*phase
                live.position=Vector2(ORIGIN+root_x,0)
                var meta: Dictionary=live.pose(clip,phase,"right")
                var active: bool=meta.contact_flags[side]
                var segment=int(floor(phase+(0.5 if side=="rear"else 0.0)))
                var poses: Array=[]
                for i in range(sprites.size()):
                    var draw_root=root_x
                    if MODES[i+1]=="baked_draw_floor":draw_root=floor(root_x)
                    elif MODES[i+1]=="baked_draw_round":draw_root=round(root_x)
                    elif MODES[i+1]=="baked_draw_ceil":draw_root=ceil(root_x)
                    sprites[i].texture=cache[held_tick]
                    sprites[i].position=Vector2((i+1)*LANE+ORIGIN+draw_root,0)
                    poses.append(draw_root)
                var img: Image=await presented()
                var measured: Dictionary={}
                for i in range(MODES.size()):
                    var mode: String=MODES[i]
                    var observation=sole(img,i)
                    if active:
                        contact_counts[mode]+=1
                        var key=mode+":"+str(segment)
                        if observation.xmin==null:failures[mode]+=1
                        else:
                            if not references.has(key):references[key]=observation.xmin
                            var error=absf(float(observation.xmin)-float(references[key]))
                            observation["error_from_first_stance_pixel_px"]=error
                            maxima[mode]=maxf(maxima[mode],error)
                            if error>0.5 or observation.below_ground_pixels>0:failures[mode]+=1
                    measured[mode]=observation
                var analytic_world_x=float(meta.feet[side][0])+root_x
                rows.append({"tick":time,"phase":phase,"held_tick":held_tick,"contact":active,"stance_segment":segment,"physical_root_x":root_x,"draw_roots":poses,"analytic_target_world_x":analytic_world_x,"ik_target_error_px":meta.ik_target_error_px[side+"_leg"],"measured":measured})
                if sample in [0,ticks*5-1,ticks*5,ticks*5+1,ticks*10]:img.save_png(output_dir.path_join(clip+"_"+side+"_sample%04d.png"%sample))
            var route={"clip":clip,"side":side,"duration_ticks":ticks,"fps":60,"stride_per_cycle":stride,"cache_sha256":cache_hashes,"sample_count":rows.size(),"contact_sample_counts":contact_counts,"max_stance_pixel_error_px":maxima,"failed_contact_samples":failures,"passes_0_5px_gate":{},"samples":rows}
            for mode in MODES:route.passes_0_5px_gate[mode]=failures[mode]==0
            report.routes.append(route)
            print(clip," ",side," max=",maxima," fail=",failures)
            var partial=FileAccess.open(output_dir.path_join("report.json"),FileAccess.WRITE);partial.store_string(JSON.stringify(report,"  "))
    report["source_unchanged_after_run"]=true
    for name in report.source_sha256:
        if sha(source_dir.path_join(name))!=report.source_sha256[name]:report.source_unchanged_after_run=false
    var file=FileAccess.open(output_dir.path_join("report.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  ")+"\n")
    quit(0)
