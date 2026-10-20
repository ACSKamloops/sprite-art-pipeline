extends SceneTree
var errors: Array = []
var events: Array = []
var finished: Array = []
var pixels: Array = []
var started: int
func check(ok: bool, label: String) -> void:
    if not ok: errors.append(label)
func sha(data: PackedByteArray) -> String:
    var hash: HashingContext = HashingContext.new()
    hash.start(HashingContext.HASH_SHA256)
    hash.update(data)
    return hash.finish().hex_encode()
func _initialize() -> void:
    call_deferred("verify")
func verify() -> void:
    var t: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://timeline.json"))
    var original: SpriteFrames = load("res://clip.tres")
    check(ResourceSaver.save(original, "res://reloaded.tres") == OK, "resource save")
    var frames: SpriteFrames = ResourceLoader.load("res://reloaded.tres", "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE)
    check(frames.get_frame_count(&"clip") == t.frames.size(), "ordered frame count")
    check(frames.get_animation_loop(&"clip") == t.loop, "loop flag")
    check(is_equal_approx(frames.get_animation_speed(&"clip"),1.0), "seconds speed1")
    for i in t.frames.size():
        var texture: AtlasTexture = frames.get_frame_texture(&"clip",i)
        var r: Array = t.frames[i].rectangle
        check(texture.region == Rect2(r[0],r[1],r[2],r[3]), "rectangle " + str(i))
        var image: Image = texture.get_image()
        image.convert(Image.FORMAT_RGBA8)
        var actual: String = sha(image.get_data())
        check(actual == t.frames[i].rgba_sha256, "full RGBA " + str(i))
        var d: Array = t.frames[i].duration
        check(abs(frames.get_frame_duration(&"clip",i)-float(d[0])/d[1]) < 0.0000001, "hold " + str(i))
        pixels.append({"frame":i,"rgba_sha256":actual})
    var packed: PackedScene = load("res://clip.tscn")
    var scene: Node2D = packed.instantiate()
    var sprite: AnimatedSprite2D = scene.get_node("AnimatedSprite2D")
    sprite.frame_changed.connect(func(): events.append({"frame":sprite.frame,"seconds":float(Time.get_ticks_usec()-started)/1000000.0}))
    sprite.animation_finished.connect(func(): finished.append(float(Time.get_ticks_usec()-started)/1000000.0))
    started=Time.get_ticks_usec()
    root.add_child(scene)
    var total: float = float(t.total[0])/t.total[1]
    var count: int = int(t.play_count)
    await create_timer(total*(count if count>0 else 1)+0.08).timeout
    check(events.size()>=2 and events[0].frame==1 and events[1].frame==2, "forward order")
    if events.size()>=2:
        var d0: Array = t.frames[0].duration
        var d1: Array = t.frames[1].duration
        check(abs(events[0].seconds-float(d0[0])/d0[1])<0.04, "first hold within40ms")
        check(abs(events[1].seconds-float(d0[0])/d0[1]-float(d1[0])/d1[1])<0.04, "second hold within40ms")
    if count==0:
        check(sprite.is_playing() and finished.is_empty(), "infinite continues without finish")
        var returned: bool = false
        for event in events:
            if event.frame==0: returned=true
        check(returned, "infinite return seam")
    else:
        check(finished.size()==count, "exact completion count")
        check(sprite.frame==t.frames.size()-1 and not sprite.is_playing(), "held final pose")
        for i in finished.size():
            check(abs(finished[i]-total*(i+1))<0.04*(i+1), "bounded completion " + str(i))
        var pivot: Array = t.frames[-1].pivot
        check(sprite.offset == -Vector2(pivot[0],pivot[1]), "held pivot")
        await create_timer(0.05).timeout
        check(sprite.frame==t.frames.size()-1 and not sprite.is_playing(), "additional final hold")
        scene.restart()
        check(sprite.frame==0 and sprite.is_playing(), "restart resets")
    var file: FileAccess = FileAccess.open("res://engine-receipt.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"errors":errors,"engine":Engine.get_version_info(),"events":events,"completion":finished,"pixels":pixels,"play_count":count,"clock_tolerance_ms":40,"scope":"headless texture readback and actual AnimatedSprite2D; no GPU/visual acceptance"},"  "))
    quit(0 if errors.is_empty() else 2)
