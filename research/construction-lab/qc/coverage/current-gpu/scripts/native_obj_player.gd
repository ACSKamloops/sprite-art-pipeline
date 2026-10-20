extends Node2D
## Capture-bound OBJ timeline. Its clock is independent of body pose holds.
## Backgrounds, color math, scanline OBJ limits and priority rotation are excluded.
var route := {}
var frame_index := 0
var elapsed_ticks := 0.0
var playing := false
var finished := false
var nodes := {}
var textures := {}
var shader = preload("res://scripts/indexed_object.gdshader")
var current_palette: Texture2D
const MAX_ROUTE_FRAMES = 10000
const MAX_ADVANCE_TICKS = 10000.0
func integral(value, minimum: int, maximum: int) -> bool:
    return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and float(value) >= minimum and float(value) <= maximum
func relative_asset(value) -> bool:
    if not value is String or value.is_empty() or value.contains(":") or value.contains("\\") or value.begins_with("/"):
        return false
    return value.simplify_path() == value and not value.split("/").has("..")
func validate_texture(path, local_textures: Dictionary, size: Vector2i) -> bool:
    if not relative_asset(path) or not ResourceLoader.exists("res://" + path):
        return false
    if not local_textures.has(path):
        local_textures[path] = load("res://" + path) as Texture2D
    var image = local_textures[path]
    return image != null and Vector2i(image.get_size()) == size
func validate_route(data, local_textures: Dictionary) -> bool:
    if not data is Dictionary or data.get("schema") != "som.native_indexed_obj_route.v1" or not data.get("route_id") is String or data.route_id.is_empty():
        return false
    if not data.get("loop") is bool or data.loop:
        return false
    var fps = data.get("video_fps")
    if not (fps is int or fps is float) or not is_finite(float(fps)) or fps <= 0 or fps > 1000:
        return false
    var frames = data.get("frames")
    if not frames is Array or frames.is_empty() or frames.size() > MAX_ROUTE_FRAMES or not integral(data.get("frame_count"),1,MAX_ROUTE_FRAMES) or int(data.frame_count) != frames.size():
        return false
    var total = 0
    var previous_tick = -1
    var previous_duration = 0
    for frame in frames:
        if not frame is Dictionary or not integral(frame.get("source_tick"),0,2147483647) or not integral(frame.get("duration_ticks"),1,10000):
            return false
        if previous_tick >= 0 and int(frame.source_tick) != previous_tick + previous_duration:
            return false
        previous_tick = int(frame.source_tick)
        previous_duration = int(frame.duration_ticks)
        total += previous_duration
        if total > 10000000 or not validate_texture(frame.get("palette_texture"),local_textures,Vector2i(16,8)):
            return false
        if not frame.get("actor") is Dictionary or not frame.get("palette_state") is Dictionary or not frame.get("source_hashes") is Dictionary:
            return false
        if not integral(frame.get("actor_slot"),0,2560) or int(frame.actor_slot)%512 != 0:
            return false
        for key in ["world_x","world_y","height","jump","action_row","action_mode","effect_mode","generic_index","family","spell_id","spell_variant"]:
            if not integral(frame.actor.get(key),0,65535):
                return false
        if frame.has("expected_texture") and not relative_asset(frame.expected_texture):
            return false
        var objects = frame.get("objects")
        if not objects is Array or objects.size() > 128:
            return false
        var indices = {}
        for obj in objects:
            if not obj is Dictionary or not integral(obj.get("index"),0,127) or indices.has(int(obj.index)):
                return false
            indices[int(obj.index)] = true
            if not integral(obj.get("x"),-256,255) or not integral(obj.get("y"),0,255):
                return false
            if not integral(obj.get("palette"),0,7) or not integral(obj.get("priority"),0,3) or not integral(obj.get("tile"),0,511) or not integral(obj.get("z_index"),0,127) or int(obj.z_index) != 127-int(obj.index):
                return false
            if not integral(obj.get("width"),8,64) or not integral(obj.get("height"),8,64) or int(obj.width)%8 != 0 or int(obj.height)%8 != 0:
                return false
            if not obj.get("flip_x") is bool or not obj.get("flip_y") is bool or not obj.get("semantic_layer") is String or obj.semantic_layer.is_empty():
                return false
            if not validate_texture(obj.get("indexed_texture"),local_textures,Vector2i(int(obj.width),int(obj.height))):
                return false
            var positions = obj.get("positions")
            if not positions is Array or positions.is_empty() or positions.size() > 2:
                return false
            for coordinates in positions:
                if not coordinates is Array or coordinates.size()!=2 or not integral(coordinates[0],-1024,1024) or not integral(coordinates[1],-1024,1024):
                    return false
    return integral(data.get("duration_ticks"),1,10000000) and int(data.duration_ticks) == total
func load_route(path: String) -> bool:
    if not path.begins_with("res://") or not relative_asset(path.substr(6)) or not FileAccess.file_exists(path):
        return false
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    var local_textures = {}
    if not validate_route(parsed,local_textures):
        return false
    # Commit only after every frame and texture validates.
    textures.merge(local_textures,true)
    route = parsed
    frame_index = 0
    elapsed_ticks = 0.0
    playing = false
    finished = false
    show_frame(0)
    return true
func texture(path: String) -> Texture2D:
    if not textures.has(path):
        textures[path] = load("res://" + path) as Texture2D
    return textures[path]
func show_frame(index: int) -> void:
    assert(index >= 0 and index < route.frames.size())
    frame_index = index
    var frame: Dictionary = route.frames[index]
    current_palette = texture(frame.palette_texture)
    for node in nodes.values():
        node.visible = false
    for obj in frame.objects:
        for position_index in obj.positions.size():
            var key = str(obj.index) + "/" + str(position_index)
            if not nodes.has(key):
                var sprite = Sprite2D.new()
                sprite.centered = false
                sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                var material = ShaderMaterial.new()
                material.shader = shader
                sprite.material = material
                nodes[key] = sprite
                add_child(sprite)
            var sprite: Sprite2D = nodes[key]
            sprite.texture = texture(obj.indexed_texture)
            sprite.position = Vector2(float(obj.positions[position_index][0]), float(obj.positions[position_index][1]))
            sprite.z_index = int(obj.z_index)
            sprite.material.set_shader_parameter("palette_texture", current_palette)
            sprite.material.set_shader_parameter("palette_row", float(obj.palette))
            sprite.visible = true
func advance_ticks(ticks: float) -> bool:
    if not is_finite(ticks) or ticks < 0.0 or ticks > MAX_ADVANCE_TICKS:
        return false
    if not playing:
        return true
    elapsed_ticks += ticks
    # Remove only scaled floating-point roundoff at integer native-video ticks.
    # A genuine sub-tick remainder outside this bound keeps its exact phase.
    var integral_ticks: float = roundf(elapsed_ticks)
    var roundoff_bound := 1.0e-12 * maxf(1.0, absf(elapsed_ticks))
    if absf(elapsed_ticks - integral_ticks) <= roundoff_bound:
        elapsed_ticks = integral_ticks
    var budget = route.frames.size() - frame_index
    while elapsed_ticks >= float(route.frames[frame_index].duration_ticks) and budget > 0:
        budget -= 1
        elapsed_ticks -= float(route.frames[frame_index].duration_ticks)
        if frame_index + 1 >= route.frames.size():
            playing = false
            finished = true
            elapsed_ticks = 0.0
            return true
        show_frame(frame_index + 1)
    return true
func _process(delta: float) -> void:
    if not route.is_empty():
        advance_ticks(delta * float(route.video_fps) * playback_speed)

var capture_index := {}
var playback_speed := 1.0
func configure_index(path := "res://capture-index.json") -> bool:
    if not path.begins_with("res://") or not relative_asset(path.substr(6)) or not FileAccess.file_exists(path):
        return false
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not parsed is Dictionary or parsed.get("schema") != "som.native_capture_index.v1" or not parsed.get("routes") is Array:
        return false
    var ids = {}
    for entry in parsed.routes:
        if not entry is Dictionary or not entry.get("id") is String or entry.id.is_empty() or ids.has(entry.id) or not relative_asset(entry.get("path")) or not FileAccess.file_exists("res://"+entry.path):
            return false
        ids[entry.id] = true
    capture_index = parsed
    return true
func select_route(route_id: String) -> bool:
    for entry in capture_index.get("routes", []):
        if entry.id == route_id:
            return load_route("res://" + str(entry.path))
    return false
func play() -> bool:
    if route.is_empty() or finished:
        return false
    playing = true
    return true
func pause() -> void:
    playing = false
func replay() -> bool:
    if route.is_empty():
        return false
    elapsed_ticks = 0.0
    finished = false
    show_frame(0)
    playing = true
    return true
func step_video_ticks(count: int = 1) -> bool:
    if route.is_empty() or finished or count < 1 or count > 10000:
        return false
    var was_playing = playing
    playing = true
    advance_ticks(float(count))
    playing = was_playing and playing
    return true
func set_speed(speed: float) -> bool:
    if not is_finite(speed) or speed <= 0.0 or speed > 16.0:
        return false
    playback_speed = speed
    return true
func read_back() -> Dictionary:
    if route.is_empty():
        return {"loaded":false}
    var frame: Dictionary = route.frames[frame_index]
    return {"loaded":true,"route_id":route.route_id,"frame_index":frame_index,"frame_count":route.frames.size(),"source_tick":frame.source_tick,"elapsed_ticks":elapsed_ticks,"duration_ticks":route.duration_ticks,"playing":playing,"finished":finished,"speed":playback_speed,"object_count":frame.objects.size(),"actor_slot":frame.actor_slot,"actor":frame.actor.duplicate(true),"palette_state":frame.palette_state.duplicate(true),"source_hashes":frame.source_hashes.duplicate(true)}
func command(request: Dictionary) -> Dictionary:
    var rejected = {"accepted":false,"request_id":request.get("request_id"),"state":read_back()}
    var operation = request.get("op")
    if not operation is String:
        return rejected
    var allowed = ["op","request_id"]
    if operation == "select_route":allowed.append("route_id")
    elif operation == "step":allowed.append("ticks")
    elif operation == "speed":allowed.append("value")
    for key in request:
        if not key in allowed:return rejected
    if request.has("request_id"):
        var id = request.request_id
        if id != null and not id is String and not ((id is int or id is float) and is_finite(float(id))):
            return rejected
    var accepted := false
    match operation:
        "select_route":
            if request.get("route_id") is String:
                accepted = select_route(request.route_id)
        "play":accepted = play()
        "pause":
            pause()
            accepted = true
        "replay":accepted = replay()
        "step":
            var value = request.get("ticks",1)
            if integral(value,1,int(MAX_ADVANCE_TICKS)):
                accepted = step_video_ticks(int(value))
        "speed":
            var value = request.get("value")
            if value is int or value is float:
                accepted = set_speed(float(value))
        "read_back":accepted = true
    return {"accepted":accepted,"request_id":request.get("request_id"),"state":read_back()}
