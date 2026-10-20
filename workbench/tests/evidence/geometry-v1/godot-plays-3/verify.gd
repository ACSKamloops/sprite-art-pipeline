extends SceneTree
var errors: Array[String] = []
var events: Array = []
var finished: Array = []
var started: int
var pixels: Array = []
func sha(data: PackedByteArray) -> String:
    var context: HashingContext = HashingContext.new()
    context.start(HashingContext.HASH_SHA256)
    context.update(data)
    return context.finish().hex_encode()
func check(condition: bool, message: String) -> void:
    if not condition:
        errors.append(message)
func _initialize() -> void:
    call_deferred("run_checks")
func run_checks() -> void:
    var timeline: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://timeline.json"))
    var frames: SpriteFrames = load("res://clip.tres")
    check(frames != null, "SpriteFrames load")
    if frames == null:
        quit(2)
        return
    check(ResourceSaver.save(frames, "res://reloaded.tres") == OK, "Save SpriteFrames")
    var reloaded: SpriteFrames = ResourceLoader.load("res://reloaded.tres", "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE)
    check(reloaded.get_frame_count(&"clip") == timeline.frames.size(), "Reload ordered count")
    check(reloaded.get_animation_loop(&"clip") == timeline.loop, "Reload loop")
    check(is_equal_approx(reloaded.get_animation_speed(&"clip"), 1.0), "Speed1 seconds")
    for i in timeline.frames.size():
        var texture: AtlasTexture = reloaded.get_frame_texture(&"clip", i)
        var rect: Array = timeline.frames[i].rectangle
        check(texture.region == Rect2(rect[0],rect[1],rect[2],rect[3]), "Rectangle " + str(i))
        var expected: Image = Image.load_from_file("res://frame-%04d.png" % i)
        var actual: Image = texture.get_image()
        actual.convert(Image.FORMAT_RGBA8)
        expected.convert(Image.FORMAT_RGBA8)
        check(actual.get_data() == expected.get_data(), "Full RGBA including hiddenRGB " + str(i))
        var d: Array = timeline.frames[i].duration
        check(abs(reloaded.get_frame_duration(&"clip",i) - float(d[0])/d[1]) < 0.0000001, "Duration " + str(i))
        pixels.append({"frame":i,"actual_rgba_sha256":sha(actual.get_data()),
            "expected_rgba_sha256":sha(expected.get_data()),"rectangle":rect,
            "seconds":reloaded.get_frame_duration(&"clip",i)})
    var packed: PackedScene = load("res://clip.tscn")
    var scene: Node2D = packed.instantiate()
    var sprite: AnimatedSprite2D = scene.get_node("AnimatedSprite2D")
    sprite.frame_changed.connect(func(): events.append({"frame":sprite.frame,"seconds":float(Time.get_ticks_usec()-started)/1000000.0}))
    sprite.animation_finished.connect(func(): finished.append(float(Time.get_ticks_usec()-started)/1000000.0))
    started = Time.get_ticks_usec()
    root.add_child(scene)
    var total: float = float(timeline.total[0])/timeline.total[1]
    var count: int = int(timeline.get("play_count",1))
    await create_timer(total * (count if count > 0 else 1) + 0.08).timeout
    check(events.size() >= 2 and events[0].frame == 1 and events[1].frame == 2, "First-cycle frame order")
    if events.size() >= 2:
        var d0: Array = timeline.frames[0].duration
        var d1: Array = timeline.frames[1].duration
        var first_end: float = float(d0[0])/d0[1]
        var second_end: float = first_end + float(d1[0])/d1[1]
        check(abs(events[0].seconds-first_end) < 0.03, "First hold timing within30ms")
        check(abs(events[1].seconds-second_end) < 0.03, "Second hold timing within30ms")
    if timeline.loop:
        check(sprite.is_playing(), "Loop continues")
        check(finished.is_empty(), "Loop has no one-shot finish")
        var saw_return: bool = false
        for event in events:
            if event.frame == 0:
                saw_return = true
        check(saw_return, "Loop return observed")
    else:
        check(sprite.frame == timeline.frames.size()-1, "Final pose held")
        check(not sprite.is_playing(), "One-shot stopped")
        check(finished.size() == count, "Exact finite play count")
        for i in finished.size():
            check(abs(finished[i]-total*(i+1)) < 0.03*(i+1), "Completion within30ms-per-cycle headless clock tolerance")
        var p: Array = timeline.frames[-1].pivot
        check(sprite.offset == -Vector2(p[0],p[1]), "Per-frame final pivot")
        check(events.size() >= 2 and events[0].frame == 1 and events[1].frame == 2, "Ordered real forward transitions")
    var held_frame: int = sprite.frame
    if not timeline.loop:
        await create_timer(0.04).timeout
        check(sprite.frame == held_frame, "Additional final hold")
    var first_pass_events: Array = events.duplicate(true)
    sprite.stop()
    check(sprite.frame == 0 and not sprite.is_playing(), "Stop resets and pauses")
    started = Time.get_ticks_usec()
    scene.restart()
    await create_timer(0.04).timeout
    check(sprite.frame == 0 and sprite.is_playing(), "Explicit restart holds first pose")
    var receipt: Dictionary = {"engine":Engine.get_version_info(),"errors":errors,
        "frame_count":timeline.frames.size(),"loop":timeline.loop,"play_count":count,"events":first_pass_events,"pixels":pixels,
        "completion":finished,"rendering_scope":"headless texture readback and real AnimatedSprite2D clock; no GPU visual acceptance"}
    var file: FileAccess = FileAccess.open("res://engine-receipt.json",FileAccess.WRITE)
    file.store_string(JSON.stringify(receipt,"  "))
    quit(0 if errors.is_empty() else 2)
