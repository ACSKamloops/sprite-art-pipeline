extends Node2D
var config: Dictionary
var manifest: Dictionary
var textures: Array[Texture2D] = []
var holds: Array[float] = []
var cycle := 0.0
var boundaries: Array[float] = []
var phase := 0.0
var frame_index := 0
var rate := 1.0
var paused := false
var toggled_walk := false
var walking := false
var blocked := false
var actor: CharacterBody2D
var sprite: Sprite2D
var idle_texture: Texture2D
var info: Label
var capture_mode := false
var capture_bank := false
var captured_state: Dictionary = {}
var contacts: Array = []
var stance_enabled := false
var stance_episode := ""
var stance_target := Vector2.ZERO
var draw_correction := Vector2.ZERO
var max_draw_correction := 0.0
var distance := 0.0
var physics_steps := 0
var seen: Dictionary = {}
var bank: Dictionary = {}
var bank_enabled := false
var state := "idle"
var idle_variant := ""
var idle_clips: Dictionary = {}
var stop_clips: Dictionary = {}
var start_clips: Dictionary = {}
var active_clip: Dictionary = {}
var active_binding: Dictionary = {}
var transition_phase := 0.0
var visual_bias := Vector2.ZERO
var transition_collided := false
var state_log: Array = []


func read_json(path: String) -> Dictionary:
 return JSON.parse_string(FileAccess.get_file_as_string(path))
func png_texture(path: String) -> Texture2D:
 var image := Image.new()
 var error := image.load_png_from_buffer(FileAccess.get_file_as_bytes(path))
 assert(error == OK)
 return ImageTexture.create_from_image(image)

func _ready() -> void:
 get_viewport().snap_2d_transforms_to_pixel = true
 config = read_json("res://runtime-config.json")
 manifest = read_json(config.manifest)
 if not config.get("contacts", "").is_empty():
  contacts = read_json(config.contacts).frames
  assert(contacts.size() == manifest.frames.size())
 stance_enabled = bool(config.get("stance_lock", false))
 for f in manifest.frames:
  textures.append(png_texture(config.manifest.get_base_dir().path_join(f.file)))
  assert(textures[-1].get_width() == int(manifest.canvas[0]) and textures[-1].get_height() == int(manifest.canvas[1]))
  holds.append(float(f.hold[0])/float(f.hold[1]))
  cycle += holds[-1]
 for rational in manifest.runtime_boundaries:
  boundaries.append(float(rational[0])/float(rational[1]))
 cycle = float(manifest.runtime_duration[0])/float(manifest.runtime_duration[1])
 if not config.get("idle_file", "").is_empty():
  idle_texture = png_texture(config.idle_file)
 if not config.get("bank", "").is_empty():
  load_bank(config.bank)
 actor = CharacterBody2D.new()
 actor.motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
 add_child(actor)
 var shape := CollisionShape2D.new()
 var rect := RectangleShape2D.new()
 rect.size = Vector2(12, 8)
 shape.shape = rect
 actor.add_child(shape)
 sprite = Sprite2D.new()
 sprite.centered = false
 sprite.top_level = true
 sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
 sprite.scale = Vector2.ONE * float(config.scale)
 actor.add_child(sprite)
 # World collision walls. This is a grounded horizontal lane, no invented view.
 for x in [20.0, float(config.lane_end)]:
  var wall := StaticBody2D.new()
  wall.position = Vector2(x, float(config.start_root[1]))
  var cs := CollisionShape2D.new()
  var r := RectangleShape2D.new()
  r.size = Vector2(8, 120)
  cs.shape = r
  wall.add_child(cs)
  add_child(wall)
 var layer := CanvasLayer.new()
 add_child(layer)
 info = Label.new()
 info.position = Vector2(12, 8)
 info.add_theme_font_size_override("font_size", 12)
 layer.add_child(info)
 var row := HBoxContainer.new()
 row.position = Vector2(12, 292)
 layer.add_child(row)
 for label in ["Walk / stop", "Pause", "Step pose", "Reset", "0.5x", "1x", "2x", "Stance lock"]:
  var button := Button.new()
  button.text = label
  button.add_theme_font_size_override("font_size", 12)
  row.add_child(button)
  button.pressed.connect(command.bind(label))
 reset()

func command(label: String) -> void:
 match label:
  "Walk / stop": toggled_walk = not toggled_walk
  "Pause": paused = not paused
  "Step pose": step_pose()
  "Reset": reset()
  "0.5x": rate = 0.5
  "1x": rate = 1.0
  "2x": rate = 2.0
  "Stance lock":
   stance_enabled = not stance_enabled
   stance_episode = ""

func _unhandled_key_input(event: InputEvent) -> void:
 if event is InputEventKey and event.pressed and not event.echo:
  match event.keycode:
   KEY_SPACE: command("Walk / stop")
   KEY_P: command("Pause")
   KEY_N: command("Step pose")
   KEY_R: command("Reset")

func reset() -> void:
 actor.position = Vector2(config.start_root[0], config.start_root[1])
 phase = 0.0
 frame_index = 0
 paused = false
 toggled_walk = false
 walking = false
 blocked = false
 distance = 0.0
 seen.clear()
 stance_episode = ""
 draw_correction = Vector2.ZERO
 max_draw_correction = 0.0
 state = "idle"
 idle_variant = str(bank.get("initial_idle", idle_clips.keys()[0] if not idle_clips.is_empty() else ""))
 active_clip = {}
 active_binding = {}
 transition_phase = 0.0
 visual_bias = Vector2.ZERO
 transition_collided = false
 state_log.clear()

func select_frame(time: float) -> int:
 var t := fposmod(time, cycle)
 for i in boundaries.size():
  if t < boundaries[i]:
   return i
 return 0

func step_pose() -> void:
 paused = true
 if bank_enabled:
  if state == "start" or state == "stop":
   var current := clip_frame(active_clip, transition_phase)
   transition_phase = 0.0
   for i in mini(current+1, active_clip.holds.size()-1): transition_phase += active_clip.holds[i]
   return
  if state == "idle": return
 walking = true
 frame_index = (frame_index + 1) % holds.size()
 phase = 0.0
 if frame_index>0: phase = boundaries[frame_index-1]
 # Inspection only: hold physical root, advance visual source pose.

func _physics_process(delta: float) -> void:
 if capture_mode or paused: return
 physics_steps += 1
 var requested := toggled_walk or Input.is_physical_key_pressed(KEY_RIGHT) or Input.is_physical_key_pressed(KEY_D)
 if bank_enabled:
  bank_tick(delta, requested)
  return
 var before := actor.position
 actor.velocity = Vector2(float(config.stride_pixels) / cycle * rate if requested else 0.0, 0)
 actor.move_and_slide()
 var moved := actor.position.distance_to(before)
 distance += moved
 blocked = requested and moved < 0.00001
 walking = requested and not blocked
 if walking:
  phase = fposmod(advance_clock(phase,delta*rate,boundaries),cycle)
  frame_index = select_frame(phase)
  seen[frame_index] = true
 else:
  # Immediate gameplay stop. No invented transition or foot matching.
  phase = 0.0
  frame_index = int(config.idle_frame)

func update_stance() -> void:
 draw_correction = visual_bias
 if not stance_enabled or not walking or contacts.is_empty():
  stance_episode = ""
  return
 var contact: Dictionary = contacts[frame_index]
 if not contact.get("flat", false):
  stance_episode = ""
  return
 var anchor: Array = contact.anchor
 var source_world := actor.position + (Vector2(anchor[0], anchor[1]) - Vector2(manifest.pivot[0], manifest.pivot[1])) * float(config.scale) + visual_bias
 var episode := str(contact.episode)
 if stance_episode != episode:
  stance_target = source_world
  stance_episode = episode
 draw_correction = visual_bias + stance_target - source_world
 max_draw_correction = max(max_draw_correction, draw_correction.length())

func present() -> void:
 update_stance()
 var pivot: Array = manifest.pivot
 var shown_frame := frame_index
 var shown_count := holds.size()
 var shown_phase := phase
 sprite.texture = textures[frame_index]
 if bank_enabled and (not capture_mode or capture_bank):
  if state == "idle":
   var idle: Dictionary = idle_clips[idle_variant]
   sprite.texture = idle.textures[0]
   pivot = idle.pivot
   shown_frame = 0
   shown_count = idle.textures.size()
   shown_phase = 0.0
  elif state == "start" or state == "stop":
   sprite.texture = active_clip.textures[clip_frame(active_clip, transition_phase)]
   pivot = active_clip.pivot
   shown_frame = clip_frame(active_clip, transition_phase)
   shown_count = active_clip.textures.size()
   shown_phase = transition_phase
 elif not walking and idle_texture:
  sprite.texture = idle_texture
  pivot = config.idle_pivot
 sprite.position = (actor.position - Vector2(pivot[0], pivot[1]) * float(config.scale) + draw_correction).round()
 sprite.flip_h = false
 var status := state.to_upper() if bank_enabled else ("WALK" if walking else ("BLOCKED / IDLE" if blocked else "IDLE"))
 if paused: status = "PAUSED " + status
 info.text = "ONE VIEW · Right/D hold, Space toggle · P pause · N step · R reset\n%s | pose %d/%d | phase %.3fs | rate %.1fx | speed %.1f px/s\n%s\nContinuous physical root; whole-actor stance correction: %s / %.2fpx" % [status, shown_frame + 1, shown_count, shown_phase, rate, float(config.stride_pixels)/cycle*rate, config.idle_status, "ON" if stance_enabled else "OFF", draw_correction.length()]
 queue_redraw()

func _process(_delta: float) -> void:
 # Deterministic movie state is assigned BEFORE CanvasItem rendering.
 if capture_mode and not captured_state.is_empty():
  actor.position = Vector2(captured_state.x, captured_state.y)
  phase = float(captured_state.phase)
  frame_index = select_frame(phase)
  walking = bool(captured_state.get("walking", true))
  if captured_state.has("state"):
   state = str(captured_state.state)
   transition_phase = float(captured_state.get("transition_phase",0.0))
  if captured_state.has("visual_bias"):
   visual_bias = Vector2(captured_state.visual_bias[0],captured_state.visual_bias[1])
 present()

func _draw() -> void:
 draw_rect(Rect2(0, 0, 640, 360), Color("151d2a"))
 draw_rect(Rect2(24, float(config.start_root[1])-16, float(config.lane_end)-28, 40), Color("293646"))
 for x in range(24, int(config.lane_end), 16):
  draw_line(Vector2(x, float(config.start_root[1])-16), Vector2(x, float(config.start_root[1])+24), Color("36485b"))
 draw_line(Vector2(24, config.start_root[1]), Vector2(config.lane_end-4, config.start_root[1]), Color("7f9b9e"))
 for x in [20, config.lane_end]:
  draw_rect(Rect2(x-4, float(config.start_root[1])-30, 8, 60), Color("ac7857"))
 # Physics root witness; fixed camera and no per-pose recentering.
 draw_circle(actor.position, 2, Color("7de6cc"))

func load_clip(path: String) -> Dictionary:
 var source := read_json(path)
 var clip := {"textures":[],"holds":[],"duration":0.0,"boundaries":[],"pivot":source.pivot,"manifest":source,"path":path}
 for f in source.frames:
  clip.textures.append(png_texture(path.get_base_dir().path_join(f.file)))
  var duration := float(f.hold[0])/float(f.hold[1])
  assert(duration>0)
  clip.holds.append(duration)
  clip.duration += duration
 for rational in source.runtime_boundaries:
  clip.boundaries.append(float(rational[0])/float(rational[1]))
 clip.duration = float(source.runtime_duration[0])/float(source.runtime_duration[1])
 assert(not clip.textures.is_empty())
 return clip

func load_bank(path: String) -> void:
 bank = read_json(path)
 assert(bank.schema == "authored-locomotion-bank/v1")
 var base := path.get_base_dir()
 for variant in bank.idle_variants:
  idle_clips[variant] = load_clip(base.path_join(bank.idle_variants[variant].manifest))
 for binding in bank.stop_by_walk_frame:
  var clip := load_clip(base.path_join(binding.manifest))
  assert(not clip.manifest.loop)
  assert(binding.root_curve.size()>=2)
  stop_clips[int(binding.walk_frame)] = {"clip":clip,"binding":binding}
 for variant in bank.start_by_idle:
  var binding: Dictionary = bank.start_by_idle[variant]
  var clip := load_clip(base.path_join(binding.manifest))
  assert(not clip.manifest.loop)
  assert(binding.root_curve.size()>=2)
  start_clips[variant] = {"clip":clip,"binding":binding}
 for i in textures.size(): assert(stop_clips.has(i), "Every selected walk frame needs a matching authored immediate stop")
 bank_enabled = true

func clip_frame(clip: Dictionary, time: float) -> int:
 for i in clip.boundaries.size():
  if time < float(clip.boundaries[i]): return i
 return clip.holds.size()-1

func curve_offset(curve: Array, time: float) -> Vector2:
 var first: Array = curve[0].offset
 if time <= float(curve[0].time[0])/float(curve[0].time[1]): return Vector2(first[0],first[1])*float(config.scale)
 for i in range(1,curve.size()):
  var previous: Dictionary = curve[i-1]
  var current: Dictionary = curve[i]
  var a := float(previous.time[0])/float(previous.time[1])
  var b := float(current.time[0])/float(current.time[1])
  assert(b>a)
  if time <= b:
   var start := Vector2(previous.offset[0],previous.offset[1])
   var finish := Vector2(current.offset[0],current.offset[1])
   return start.lerp(finish, (time-a)/(b-a))*float(config.scale)
 var last: Array = curve[-1].offset
 return Vector2(last[0],last[1])*float(config.scale)

func log_state() -> void:
 state_log.append({"state":state,"physics_tick":physics_steps,"walk_frame":frame_index,"transition_phase":transition_phase,"root":[actor.position.x,actor.position.y],"bias":[visual_bias.x,visual_bias.y],"idle":idle_variant})

func begin_transition(kind: String, record: Dictionary) -> void:
 # Freeze the whole actor's current correction, never reset its visual origin.
 update_stance()
 visual_bias = draw_correction
 stance_episode = ""
 state = kind
 walking = false
 active_clip = record.clip
 active_binding = record.binding
 transition_phase = 0.0
 transition_collided = false
 log_state()

func bank_tick(delta: float, requested: bool) -> void:
 if not requested: blocked = false
 if state == "idle":
  walking = false
  if requested and not blocked:
   begin_transition("start", start_clips[idle_variant])
  return
 if state == "start" or state == "stop":
  var old_time := transition_phase
  transition_phase = min(advance_clock(transition_phase,delta*rate,active_clip.boundaries),float(active_clip.duration))
  var desired := curve_offset(active_binding.root_curve,transition_phase)-curve_offset(active_binding.root_curve,old_time)
  var before := actor.position
  var collision := actor.move_and_collide(desired)
  distance += actor.position.distance_to(before)
  if collision:
   transition_collided = true
   blocked = true
  if transition_phase >= float(active_clip.duration):
   if state == "stop":
    idle_variant = str(active_binding.to_idle)
    state = "idle"
    walking = false
   else:
    frame_index = int(active_binding.walk_entry_frame)
    phase = 0.0
    if frame_index>0: phase = boundaries[frame_index-1]
    state = "walk"
    walking = true
    stance_episode = ""
   log_state()
  return
 if not requested or blocked:
  begin_transition("stop",stop_clips[frame_index])
  return
 var before := actor.position
 actor.velocity = Vector2(float(config.stride_pixels)/cycle*rate,0)
 actor.move_and_slide()
 var moved := actor.position.distance_to(before)
 distance += moved
 blocked = moved<0.00001
 if blocked:
  begin_transition("stop",stop_clips[frame_index])
  return
 walking = true
 phase = fposmod(advance_clock(phase,delta*rate,boundaries),cycle)
 frame_index = select_frame(phase)
 seen[frame_index] = true
 update_stance()

func advance_clock(time: float, delta: float, source_boundaries: Array) -> float:
 var value := time+delta
 # Normalize only floating arithmetic noise accumulated by engine clocks.
 # Explicit select_frame/clip_frame probes remain strict on either side.
 for boundary in source_boundaries:
  var tolerance: float = 8.0*2.220446049250313e-16*max(1.0,max(abs(value),abs(float(boundary))))
  if abs(value-float(boundary))<=tolerance:return float(boundary)
 return value
