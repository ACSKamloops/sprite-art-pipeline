extends SceneTree
## One GLOBAL visual correction shared by BOTH boots and complete baked sprite.
const LANE=512
const ORIGIN=80
const SOLE_OFFSET=-9.0 # Authored boot outer sole, validated against actual live raster below.
var vp: SubViewport
var bake_vp: SubViewport
var rigs: Array=[]
var sprites: Array=[]
var root_dir: String
var out_dir: String
var report: Dictionary
func frame(viewport: SubViewport) -> Image:
    await process_frame
    await RenderingServer.frame_post_draw
    return viewport.get_texture().get_image()
func sole(image: Image,lane: int) -> Dictionary:
    var lo=LANE;var hi=-1;var below=0
    for x in range(LANE):
        if image.get_pixel(lane*LANE+x,169).a>0:lo=mini(lo,x);hi=maxi(hi,x)
    for y in range(170,192):
        for x in range(LANE):
            if image.get_pixel(lane*LANE+x,y).a>0:below+=1
    return {"xmin":lo if hi>=0 else null,"xmax":hi if hi>=0 else null,"below_ground_pixels":below}
func _initialize() -> void:
    Engine.max_fps=0;DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    root_dir=get_script().resource_path.get_base_dir().get_base_dir()
    out_dir=root_dir.path_join("contact-proof")
    call_deferred("run")
func run() -> void:
    var design: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(root_dir.path_join("design.json")))
    var clips: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(root_dir.path_join("clips.json")))
    var baseline: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(out_dir.path_join("report.json")))
    for file in baseline.source_sha256:
        if FileAccess.get_sha256(root_dir.path_join(file))!=baseline.source_sha256[file]:push_error("Stale cache source "+file);quit(2);return
    var script=load(root_dir.path_join("rig.gd"))
    vp=SubViewport.new();vp.size=Vector2i(LANE*6,192);vp.transparent_bg=true;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(vp)
    for i in range(3):
        var rig=script.new();vp.add_child(rig);rig.configure(design,clips)
        if i<2:rig.visible_layers=[("front"if i==0 else "rear")+"_boot"]
        rigs.append(rig)
    for i in range(3):
        var sprite=Sprite2D.new();sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;vp.add_child(sprite);sprites.append(sprite)
    bake_vp=SubViewport.new();bake_vp.size=Vector2i(192,192);bake_vp.transparent_bg=true;bake_vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(bake_vp)
    var bake_rig=script.new();bake_vp.add_child(bake_rig);bake_rig.configure(design,clips)
    report={"schema":"copper-scout-global-contact-lock/v1","source_sha256":baseline.source_sha256,"baseline_raw_sha256":FileAccess.get_sha256(out_dir.path_join("report.json")),"runner_sha256":FileAccess.get_sha256(get_script().resource_path),"renderer":baseline.renderer,"policy":"Single shared whole-sprite integer visual translation: fixed-camera live analytic sole world xmin quantized to actual raster, minus actual held-cache sole xmin. Front preferred if both contacts; rear otherwise; round physical root in flight. Physics stays continuous. Actual rendered both boots and full body share the SAME correction.","sole_offset":SOLE_OFFSET,"threshold_px":0.5,"ground_boundary":170,"opaque_row":169,"scope":"Right, fixed camera, native resolution, nearest texture filtering; visual correction is not physical root movement or collision displacement.","artistic_approval":false,"routes":[]}
    for clip in ["walk","run"]:
        var spec: Dictionary=clips.clips[clip]
        var ticks=int(spec.duration_ticks);var stride=float(spec.gait.root_motion_px_per_cycle)
        var textures={"front":[],"rear":[],"body":[]};var cache_min={"front":[],"rear":[]};var body_hashes=[]
        for side in ["front","rear"]:
            var route: Dictionary={}
            for candidate in baseline.routes:
                if candidate.clip==clip and candidate.side==side:route=candidate
            for tick in range(ticks):
                var path=out_dir.path_join(clip+"_"+side+"_tick%03d.png"%tick)
                if FileAccess.get_sha256(path)!=route.cache_sha256[tick]:push_error("Corrupt boot cache "+path);quit(3);return
                var image=Image.load_from_file(path);textures[side].append(ImageTexture.create_from_image(image))
                var min_x=192
                for x in range(192):
                    if image.get_pixel(x,169).a>0:min_x=mini(min_x,x)
                cache_min[side].append(min_x if min_x<192 else null)
        for tick in range(ticks):
            bake_rig.pose(clip,float(tick)/ticks,"right")
            var image: Image=await frame(bake_vp)
            var path=out_dir.path_join(clip+"_body_tick%03d.png"%tick)
            image.save_png(path);body_hashes.append(FileAccess.get_sha256(path));textures.body.append(ImageTexture.create_from_image(image))
        var rows=[];var episodes={};var max_offset=0.0;var max_jump=0.0;var last_draw=null;var last_physical=null;var simultaneous=0;var formula_mismatch=0;var missing_cache=0
        for sample in range(ticks*10+1):
            var time=float(sample)/5.0;var phase=time/ticks;var held=int(floor(time))%ticks;var physical=stride*phase
            var meta: Dictionary={}
            for i in range(3):
                rigs[i].position=Vector2(i*LANE+ORIGIN+physical,0)
                meta=rigs[i].pose(clip,phase,"right")
            var selected="front"if meta.contact_flags.front else ("rear"if meta.contact_flags.rear else "")
            if meta.contact_flags.front and meta.contact_flags.rear:simultaneous+=1
            var draw_root=round(physical)
            var desired=null
            if selected!="":
                desired=floor(ORIGIN+float(meta.feet[selected][0])+physical+SOLE_OFFSET)
                if cache_min[selected][held]==null:missing_cache+=1
                else:draw_root=float(desired)-ORIGIN-float(cache_min[selected][held])
            for i in range(3):
                var side=["front","rear","body"][i]
                sprites[i].texture=textures[side][held]
                sprites[i].position=Vector2((i+3)*LANE+ORIGIN+draw_root,0)
            var image: Image=await frame(vp)
            var observed={}
            for i in range(2):
                var side="front"if i==0 else "rear"
                var live=sole(image,i);var baked=sole(image,i+3)
                observed[side]={"live":live,"baked":baked,"contact":meta.contact_flags[side]}
                if meta.contact_flags[side]:
                    var seg=int(floor(phase+(0.5 if side=="rear"else 0.0)))
                    var key=side+":"+str(seg)
                    if not episodes.has(key):episodes[key]=[]
                    episodes[key].append(baked)
                    if selected==side and live.xmin!=desired:formula_mismatch+=1
            max_offset=maxf(max_offset,absf(draw_root-physical))
            if last_draw!=null:max_jump=maxf(max_jump,absf(draw_root-last_draw))
            rows.append({"tick":time,"phase":phase,"held_tick":held,"physical_root":physical,"draw_root":draw_root,"visual_child_offset":draw_root-physical,"draw_root_step":draw_root-last_draw if last_draw!=null else 0,"physical_root_step":physical-last_physical if last_physical!=null else 0,"selected_contact":selected,"desired_xmin":desired,"contacts":meta.contact_flags,"observations":observed,"same_translation_for_both_feet_and_body":true})
            last_draw=draw_root;last_physical=physical
            if sample in [0,5,7,ticks*5-1,ticks*5,ticks*5+1,ticks*10]:image.save_png(out_dir.path_join(clip+"_locked_sample%04d.png"%sample))
        var metrics={};var passed=true
        for key in episodes:
            var lo=10000;var hi=-10000;var missing=0;var below=0
            for observation in episodes[key]:
                if observation.xmin==null:missing+=1
                else:lo=mini(lo,observation.xmin);hi=maxi(hi,observation.xmin)
                below+=observation.below_ground_pixels
            var span=hi-lo if missing==0 else null
            var ok=span!=null and span<=0.5 and below==0
            if not ok:passed=false
            metrics[key]={"sample_count":episodes[key].size(),"xmin_range":[lo,hi],"peak_to_peak_px":span,"missing":missing,"below_ground_pixels":below,"passes":ok}
        if formula_mismatch or missing_cache:passed=false
        report.routes.append({"clip":clip,"sample_count":rows.size(),"episodes":metrics,"passes_0_5px_gate":passed,"max_physical_visual_offset_px":max_offset,"max_draw_root_step_px":max_jump,"simultaneous_contact_samples":simultaneous,"sole_formula_vs_actual_live_mismatches":formula_mismatch,"missing_selected_cache_soles":missing_cache,"body_cache_sha256":body_hashes,"samples":rows})
        var file=FileAccess.open(out_dir.path_join("contact-lock-report.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
        print(clip," contact lock ",passed," offset ",max_offset," jump ",max_jump," formula ",formula_mismatch)
    quit()
