extends CharacterBody2D
## Explicit clock for frame events; every crossed frame is processed, including
## large delta ticks. Rendering is paused AnimatedSprite2D driven by this clock.
signal timeline_event(event: Dictionary)
signal state_changed(state_name: String)

var sprite: AnimatedSprite2D
var manifest := {}
var clip_bindings := {}
var actor := "randi"
var weapon := "sword"
var direction := "down"
var state := "idle"
var move_speed := 80.0
var playback_speed := 1.0
var clock := 0.0
var cursor := 0
var loop_number := 0
var events: Array[Dictionary] = []
var current := {}
var stunned_until := 0.0
var simulation_time := 0.0
var input_axis := Vector2.ZERO
var hit_active := false

func configure(data: Dictionary, identity: String, frames: SpriteFrames) -> bool:
    actor = identity
    clip_bindings = data.get("gameplay_bindings", {}).get(actor, {})
    manifest.clear()
    for clip in data["clips"]:
        if clip["actor"] == actor:
            var normalized: Dictionary = clip.duplicate(true)
            normalized["video_fps"] = clip.get("video_fps", data.get("video_fps"))
            normalized["ground_pivot_pixels"] = clip.get("ground_pivot_pixels", clip["pivot_pixels"])
            manifest[clip["name"]] = normalized
    if sprite == null:
        sprite = AnimatedSprite2D.new()
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        add_child(sprite)
    sprite.sprite_frames = frames
    current = {}
    state = "unconfigured"
    return _transition("idle", true)

func _clip_name(next_state: String) -> String:
    var binding = clip_bindings.get(next_state, {}).get(direction, "")
    if binding is Dictionary:
        return str(binding.get(weapon, ""))
    return str(binding)

func _transition(next_state: String, force := false) -> bool:
    var name := _clip_name(next_state)
    if not force and state == next_state and current.get("name", "") == name:
        return true
    if not manifest.has(name):
        push_error("No clip binding for " + name)
        return false
    state = next_state
    current = manifest[name]
    clock = 0.0
    cursor = 0
    loop_number = 0
    hit_active = false
    sprite.animation = name
    sprite.pause()
    sprite.offset = Vector2(float(current["frame_size"][0]) / 2.0, float(current["frame_size"][1]) / 2.0) - Vector2(float(current["ground_pivot_pixels"][0]), float(current["ground_pivot_pixels"][1]))
    sprite.set_frame_and_progress(0, 0.0)
    state_changed.emit(state)
    _emit_frame_events()
    return true

func _emit_frame_events(at_time: float = -1.0) -> void:
    for entry in current.get("timeline_events", []):
        if int(entry["frame"]) == cursor:
            var event: Dictionary = entry.duplicate(true)
            event.merge({"actor": actor, "clip": current["name"], "loop": loop_number, "simulation_time": simulation_time if at_time < 0.0 else at_time}, true)
            if entry["name"] == "hit_start":
                hit_active = true
            elif entry["name"] == "hit_end":
                hit_active = false
            events.append(event)
            timeline_event.emit(event)

func request_attack() -> bool:
    if state == "attack" or simulation_time < stunned_until:
        return false
    return _transition("attack", true)

func interrupt(seconds: float = 0.3) -> void:
    stunned_until = simulation_time + maxf(seconds, 0.0)
    hit_active = false
    _transition("idle", true)

func tick(delta: float, axis: Vector2, attack_pressed := false) -> void:
    assert(is_finite(delta) and delta >= 0.0)
    assert(is_finite(playback_speed) and playback_speed > 0.0)
    input_axis = axis.limit_length(1.0)
    if simulation_time < stunned_until:
        simulation_time += delta
        velocity = Vector2.ZERO
        return
    if state != "attack":
        if input_axis.length_squared() > 0.0:
            if absf(input_axis.x) >= absf(input_axis.y):
                direction = "right" if input_axis.x > 0 else "left"
            else:
                direction = "down" if input_axis.y > 0 else "up"
        if attack_pressed:
            request_attack()
        else:
            _transition("walk" if input_axis.length_squared() > 0.0 else "idle")
    velocity = input_axis * move_speed if state == "walk" else Vector2.ZERO
    if velocity != Vector2.ZERO:
        move_and_collide(velocity * delta)
    simulation_time += delta
    _advance(delta * playback_speed)

func _advance(seconds: float) -> void:
    if current.is_empty():
        return
    clock += seconds
    # Positive holds are checked on import. Bound runaway catch-up explicitly;
    # callers should split exceptional multi-minute deltas into simulation ticks.
    var budget := 10000
    while budget > 0:
        budget -= 1
        var duration := float(current["frames"][cursor]["duration_video_frames"]) / float(current["video_fps"])
        if clock + 0.000000001 < duration:
            sprite.set_frame_and_progress(cursor, clampf(clock / duration, 0.0, 1.0))
            return
        clock -= duration
        cursor += 1
        if cursor >= current["frames"].size():
            if current["loop"]:
                cursor = 0
                loop_number += 1
            else:
                hit_active = false
                _transition("walk" if input_axis.length_squared() > 0.0 else "idle", true)
                return
        sprite.set_frame_and_progress(cursor, 0.0)
        _emit_frame_events(simulation_time - clock / playback_speed)
    push_error("Animation catch-up budget exceeded")

func snapshot() -> Dictionary:
    return {"actor": actor, "state": state, "direction": direction, "clip": current.get("name"),
        "frame": cursor, "loop": loop_number, "clock": clock, "position": [position.x, position.y],
        "hit_active": hit_active, "stunned": simulation_time < stunned_until, "event_count": events.size()}
