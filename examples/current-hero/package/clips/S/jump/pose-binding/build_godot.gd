extends SceneTree

func _initialize() -> void:
    var manifest_path := "res://clips.json"
    var data = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
    if not data is Dictionary or not data.has("clips"):
        push_error("Missing clip manifest: " + manifest_path)
        quit(1)
        return
    var resources := {}
    var expected := {}
    DirAccess.make_dir_recursive_absolute("res://resources")
    for clip in data["clips"]:
        var actor: String = clip["actor"]
        var clip_name: String = clip["name"]
        if not resources.has(actor):
            resources[actor] = SpriteFrames.new()
            resources[actor].remove_animation("default")
            expected[actor] = {}
        var resource: SpriteFrames = resources[actor]
        if resource.has_animation(clip_name):
            push_error("Duplicate animation: " + actor + "/" + clip_name)
            quit(1)
            return
        var atlas_image := load("res://" + clip["sheet"]) as Texture2D
        if atlas_image == null:
            push_error("Missing sprite sheet: " + clip["sheet"])
            quit(1)
            return
        resource.add_animation(clip_name)
        resource.set_animation_speed(clip_name, float(clip.get("video_fps", data.get("video_fps"))))
        resource.set_animation_loop(clip_name, bool(clip["loop"]))
        var size := Vector2(float(clip["frame_size"][0]), float(clip["frame_size"][1]))
        var columns: int = clip["sheet_columns"]
        for frame in clip["frames"]:
            var index: int = frame["atlas_index"]
            var texture := AtlasTexture.new()
            texture.atlas = atlas_image
            texture.region = Rect2(Vector2(index % columns, index / columns) * size, size)
            texture.filter_clip = true
            var duration := float(frame["duration_video_frames"])
            if duration <= 0.0:
                push_error("Non-positive frame duration")
                quit(1)
                return
            resource.add_frame(clip_name, texture, duration)
        expected[actor][clip_name] = clip
    var verification := {"actors": resources.size(), "animations": 0, "frames": 0, "errors": []}
    for actor in resources:
        var output := "res://resources/" + str(actor) + ".tres"
        var status := ResourceSaver.save(resources[actor], output)
        if status != OK:
            push_error("Cannot save " + output)
            quit(1)
            return
        var saved := ResourceLoader.load(output, "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE) as SpriteFrames
        for name in expected[actor]:
            var clip: Dictionary = expected[actor][name]
            var count := saved.get_frame_count(name)
            if count != clip["frames"].size() or saved.get_animation_loop(name) != clip["loop"] or abs(saved.get_animation_speed(name) - float(clip.get("video_fps", data.get("video_fps")))) > 0.000001:
                push_error("Saved SpriteFrames count mismatch")
                quit(1)
                return
            for index in count:
                var frame: Dictionary = clip["frames"][index]
                var texture := saved.get_frame_texture(name, index) as AtlasTexture
                var size := Vector2(float(clip["frame_size"][0]), float(clip["frame_size"][1]))
                var atlas_index: int = frame["atlas_index"]
                var columns: int = clip["sheet_columns"]
                var region := Rect2(Vector2(atlas_index % columns, atlas_index / columns) * size, size)
                if texture == null or texture.region != region or abs(saved.get_frame_duration(name, index) - float(frame["duration_video_frames"])) > 0.000001:
                    push_error("Saved frame duration or atlas region mismatch")
                    quit(1)
                    return
            verification["animations"] += 1
            verification["frames"] += count
    var report := FileAccess.open("res://godot-validation.json", FileAccess.WRITE)
    report.store_string(JSON.stringify(verification, "  "))
    print("GODOT_CLIP_RESOURCES_OK ", JSON.stringify(verification))
    quit(0)
