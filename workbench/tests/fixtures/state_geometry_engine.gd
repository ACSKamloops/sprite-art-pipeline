extends SceneTree

var errors: Array = []
var finished: Array = []
var frames: Array = []
var began: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var packed = load("res://clip.tscn")
    var clip = packed.instantiate()
    var sprite: AnimatedSprite2D = clip.get_node("AnimatedSprite2D")
    var resources: SpriteFrames = sprite.sprite_frames
    if resources.get_frame_count(&"clip") != 2 or resources.get_animation_loop(&"clip"):
        errors.append("finite two-frame resource domain")
    var weight_values: Array = []
    for index in range(2):
        var weight = resources.get_frame_duration(&"clip", index)
        weight_values.append(weight)
        if abs(weight - [0.1, 0.15][index]) > 0.000001:
            errors.append("duration resource weight")
        var actual: Image = resources.get_frame_texture(&"clip", index).get_image()
        var original: Image = Image.load_from_file("res://frame-%04d.png" % index)
        actual.convert(Image.FORMAT_RGBA8)
        original.convert(Image.FORMAT_RGBA8)
        if actual.get_data() != original.get_data():
            errors.append("decoded fullRGBA atlas crop %d" % index)
    resources = null
    began = Time.get_ticks_usec()
    sprite.frame_changed.connect(func():
        frames.append({"frame": sprite.frame, "seconds": (Time.get_ticks_usec()-began)/1000000.0})
    )
    sprite.animation_finished.connect(func():
        finished.append((Time.get_ticks_usec()-began)/1000000.0)
    )
    root.add_child(clip)
    await process_frame
    var initial_offset = sprite.offset
    if initial_offset != Vector2(-0.25, -0.75):
        errors.append("initial pivot")
    await create_timer(0.65).timeout
    if finished.size() != 2:
        errors.append("exactly two finite completed plays")
    else:
        for index in range(2):
            if abs(finished[index] - (index+1)*0.25) > 0.04:
                errors.append("finite playback clock beyond40ms tolerance")
    if sprite.is_playing() or sprite.frame != 1 or clip.get("completed_plays") != 2:
        errors.append("finite animation holds final frame")
    if sprite.offset != Vector2(-1.25, -1.75):
        errors.append("final per-frame pivot")
    var prior_finished = finished.duplicate()
    clip.restart()
    await process_frame
    if sprite.frame != 0 or sprite.offset != Vector2(-0.25,-0.75) or clip.get("completed_plays") != 0:
        errors.append("explicit restart resets frame/pivot/play counter")
    sprite.stop()
    var receipt = {"scope": "independent headless resource/clock control; no GPU or aesthetic review",
        "errors": errors, "resource_weights": weight_values, "completed_times": prior_finished,
        "frame_events": frames, "timing_tolerance_seconds": 0.04,
        "initial_offset": [initial_offset.x,initial_offset.y], "engine": Engine.get_version_info()}
    var output = FileAccess.open("res://independent-engine-receipt.json", FileAccess.WRITE)
    output.store_string(JSON.stringify(receipt))
    output.close()
    quit(0 if errors.is_empty() else 1)
