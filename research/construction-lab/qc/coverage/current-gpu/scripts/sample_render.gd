extends SceneTree
var Player = preload("res://scripts/native_obj_player.gd")
var player
func _initialize():
    root.transparent_bg = true
    Engine.max_fps=0
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    call_deferred("run")
func run():
    player = Player.new()
    root.add_child(player)
    assert(player.configure_index())
    var report = {"routes":[],"errors":[],"rendered_frames":0,"unchanged_previous_routes":[]}
    var prior={}
    for argument in OS.get_cmdline_user_args():
        if argument.begins_with("--only-new-from="):
            var previous=JSON.parse_string(FileAccess.get_file_as_string(argument.substr(16)))
            for entry in previous.routes:prior[entry.id]=entry.route_sha256
    DirAccess.make_dir_recursive_absolute("res://evidence/rendered")
    for entry in player.capture_index.routes:
        if prior.get(entry.id)==entry.route_sha256:
            report.unchanged_previous_routes.append({"id":entry.id,"route_sha256":entry.route_sha256})
            continue
        assert(player.select_route(entry.id))
        var case = {"id":entry.id,"frames":0,"pixel_differences":0}
        for index in [0, int(player.route.frames.size()/2), player.route.frames.size()-1]:
            player.show_frame(index)
            await RenderingServer.frame_post_draw
            var actual = root.get_texture().get_image()
            actual.convert(Image.FORMAT_RGBA8)
            var expected = Image.load_from_file("res://" + player.route.frames[index].expected_texture)
            expected.convert(Image.FORMAT_RGBA8)
            var a = actual.get_data()
            var b = expected.get_data()
            var differences = 0
            if actual.get_size() != expected.get_size():
                differences = -1
            elif a != b:
                for pixel in range(a.size()/4):
                    if a[pixel*4+3] != b[pixel*4+3] or (a[pixel*4+3] > 0 and (a[pixel*4] != b[pixel*4] or a[pixel*4+1] != b[pixel*4+1] or a[pixel*4+2] != b[pixel*4+2])):
                        differences += 1
            if differences != 0:
                report.errors.append({"route":entry.id,"frame":index,"pixel_differences":differences})
            case.pixel_differences += differences
            case.frames += 1
            case.get_or_add("sample_indices", []).append(index)
            report.rendered_frames += 1
            actual.save_png("res://evidence/rendered/" + entry.id + "-%04d.png" % index)
        report.routes.append(case)
    report["passed"] = report.errors.is_empty()
    FileAccess.open("res://evidence/rendered-route-validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
    print("NATIVE_OBJ_RENDER ",JSON.stringify(report))
    quit(0 if report.passed else 1)
