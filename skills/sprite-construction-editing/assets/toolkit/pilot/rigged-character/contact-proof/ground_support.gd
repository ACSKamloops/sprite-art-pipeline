extends SceneTree
const PARTS=["whole","torso","head","hands","rear_arm"]
var vp: SubViewport
var rigs=[]
var out_dir: String
func presented()->Image:
    await process_frame;await RenderingServer.frame_post_draw
    return vp.get_texture().get_image()
func bounds(image: Image,lane: int)->Dictionary:
    var lo_y=192;var hi_y=-1;var floor_pixels=0;var below=0
    for y in range(192):
        for x in range(192):
            if image.get_pixel(lane*192+x,y).a>0:
                lo_y=mini(lo_y,y);hi_y=maxi(hi_y,y)
                if y==169:floor_pixels+=1
                if y>=170:below+=1
    return {"min_y":lo_y,"max_y":hi_y,"floor_row_pixels":floor_pixels,"below_ground_pixels":below}
func _initialize():
    Engine.max_fps=0;DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED);call_deferred("run")
func run():
    var base=get_script().resource_path.get_base_dir().get_base_dir()
    out_dir=base.path_join("contact-proof/grounded-fall");DirAccess.make_dir_recursive_absolute(out_dir)
    var design=JSON.parse_string(FileAccess.get_file_as_string(base.path_join("design.json")))
    var clips=JSON.parse_string(FileAccess.get_file_as_string(base.path_join("clips.json")))
    var script=load(base.path_join("rig.gd"))
    vp=SubViewport.new();vp.size=Vector2i(192*PARTS.size(),192);vp.transparent_bg=true;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(vp)
    for i in range(PARTS.size()):
        var rig=script.new();vp.add_child(rig);rig.configure(design,clips);rig.position=Vector2(192*i,0)
        if i>0:rig.visible_layers=[PARTS[i]]
        rigs.append(rig)
    var report={"schema":"copper-scout-grounded-fall/v1","source_sha256":{},"renderer":{"godot":Engine.get_version_info().string,"adapter":RenderingServer.get_video_adapter_name(),"method":RenderingServer.get_current_rendering_method()},"ground_boundary":170,"opaque_ground_row":169,"sampling":"5fractional samples/tick plusone-shot endpoint","parts":PARTS,"classification":"Actual named draw layers only; hands is front glove; rear_arm includes its glove. Layer floor support is pixel evidence, not complete anatomy/collision proof.","routes":[],"checks":[],"artistic_approval":false}
    for file in ["rig.gd","design.json","clips.json"]:report.source_sha256[file]=FileAccess.get_sha256(base.path_join(file))
    var rest_image: Image;var rest_landmarks: Dictionary;var neutral_image: Image;var neutral_landmarks: Dictionary
    for clip in ["knockdown","recover"]:
        var ticks=int(clips.clips[clip].duration_ticks);var rows=[];var below=0
        for sample in range(ticks*5+1):
            var phase=float(sample)/(ticks*5)
            var meta: Dictionary
            for rig in rigs:meta=rig.pose(clip,phase,"right")
            var image: Image=await presented()
            var parts={}
            for i in range(PARTS.size()):parts[PARTS[i]]=bounds(image,i)
            below+=parts.whole.below_ground_pixels
            rows.append({"phase":phase,"tick":float(sample)/5,"parts":parts,"landmarks":meta.landmarks,"ik_error":meta.ik_target_error_px})
            if clip=="knockdown"and sample==0:
                neutral_image=image.get_region(Rect2i(0,0,192,192));neutral_landmarks=meta.landmarks
            if clip=="recover"and sample==ticks*5:
                report.checks.append({"name":"Recovery endpoint equals initial neutral RGBA","passed":neutral_image.get_data()==image.get_region(Rect2i(0,0,192,192)).get_data()})
                report.checks.append({"name":"Recovery endpoint equals neutral landmarks","passed":neutral_landmarks==meta.landmarks})
            if clip=="recover"and sample==int(ticks*5*0.4):
                report.checks.append({"name":"Recovery supported push frontglove floor pixels","passed":parts.hands.floor_row_pixels>0})
            if clip=="knockdown"and sample==ticks*5:
                rest_image=image.get_region(Rect2i(0,0,192,192));rest_landmarks=meta.landmarks
                report.checks.append({"name":"Rest actual torso touchesfloor","passed":parts.torso.floor_row_pixels>0})
                report.checks.append({"name":"Rest actual head touchesfloor","passed":parts.head.floor_row_pixels>0})
                report.checks.append({"name":"Rest actual frontglove touchesfloor","passed":parts.hands.floor_row_pixels>0})
            if clip=="recover"and sample==0:
                report.checks.append({"name":"Recovery opening equalsknockdown finalRGBA","passed":rest_image.get_data()==image.get_region(Rect2i(0,0,192,192)).get_data()})
                report.checks.append({"name":"Recovery opening equalrest landmarks","passed":rest_landmarks==meta.landmarks})
            if sample in [0,ticks,ticks*2,ticks*3,ticks*4,ticks*5]:image.save_png(out_dir.path_join(clip+"_sample%03d.png"%sample))
        report.routes.append({"clip":clip,"sample_count":rows.size(),"below_ground_pixels_total":below,"samples":rows})
        report.checks.append({"name":clip+" allsample fullsprite nopenetration","passed":below==0})
        print(clip," below ",below," endpoint ",rows[-1].parts)
        var f=FileAccess.open(out_dir.path_join("report.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "))
    var passed=true
    for check in report.checks:
        if not check.passed:passed=false
    report["passed"]=passed
    var f=FileAccess.open(out_dir.path_join("report.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n")
    print("Ground support guards ",passed);quit(0 if passed else 1)
