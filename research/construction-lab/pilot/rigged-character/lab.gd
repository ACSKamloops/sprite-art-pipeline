extends Control
var design: Dictionary
var clips: Dictionary
var manifest: Dictionary
var rig: Node2D
var baked: AnimatedSprite2D
var live_viewport: SubViewport
var baked_viewport: SubViewport
var current_clip=""
var current_view="right"
var tick_clock=0.0
var playing=false
var speed=1.0
var loop_override=false
var events: Array=[]
var event_keys={}
var load_error=""
var status_label: Label
var event_log: RichTextLabel
var clip_picker: OptionButton
var view_picker: OptionButton
var speed_picker: OptionButton
var anchor_overlay: Node2D
var show_anchors=false
var last_pose: Dictionary={}
var checker=true
var effects: Node2D
var effects_enabled=false
func _ready() -> void:
 texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
 if not configure_sources():return
 build_ui();select_clip("idle"if manifest.clips.has("idle/right")else manifest.clips.values()[0].name);set_process(true)
func configure_sources() -> bool:
 for name in ["design.json","clips.json","generated/manifest.json","generated/frames.tres"]:
  if not FileAccess.file_exists("res://"+name):load_error="Missing "+name+". Run build_exports.py first.";show_error();return false
 design=JSON.parse_string(FileAccess.get_file_as_string("res://design.json"));clips=JSON.parse_string(FileAccess.get_file_as_string("res://clips.json"));manifest=JSON.parse_string(FileAccess.get_file_as_string("res://generated/manifest.json"))
 for name in manifest.source_bindings:
  if not FileAccess.file_exists("res://"+name) or FileAccess.get_sha256("res://"+name)!=manifest.source_bindings[name]:load_error="Stale bake: source changed "+name;show_error();return false
 return true
func source_fresh(bindings: Dictionary) -> bool:
 for name in bindings:
  if not FileAccess.file_exists("res://"+name) or FileAccess.get_sha256("res://"+name)!=bindings[name]:return false
 return true
func show_error() -> void:
 var label=Label.new();label.text=load_error;label.position=Vector2(30,30);add_child(label)
func text(parent: Node,value: String,font_size=16) -> Label:
 var label=Label.new();label.text=value;label.add_theme_font_size_override("font_size",font_size);parent.add_child(label);return label
func button(parent: Node,label: String,callback: Callable) -> Button:
 var b=Button.new();b.text=label;b.pressed.connect(callback);parent.add_child(b);return b
func build_ui() -> void:
 var margin=MarginContainer.new();margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 for side in ["left","right","top","bottom"]:margin.add_theme_constant_override("margin_"+side,24)
 add_child(margin);var column=VBoxContainer.new();column.add_theme_constant_override("separation",12);margin.add_child(column)
 text(column,"COPPER SCOUT  /  RIG → SPRITE",26);text(column,"Original procedural character · 192 px source · authored 60 Hz · right / mirrored left",14)
 var controls=HBoxContainer.new();controls.add_theme_constant_override("separation",8);column.add_child(controls)
 clip_picker=OptionButton.new();var names=[]
 for binding in manifest.clips.values():
  if not binding.name in names:names.append(binding.name)
 names.sort()
 for name in names:clip_picker.add_item(name)
 clip_picker.item_selected.connect(func(i):select_clip(clip_picker.get_item_text(i)));controls.add_child(clip_picker)
 view_picker=OptionButton.new();
 for view in manifest.views:view_picker.add_item("left (mirror)"if view=="left"else"right")
 view_picker.item_selected.connect(func(i):set_view("right"if i==0 else"left"));controls.add_child(view_picker)
 button(controls,"Play",play);button(controls,"Pause",pause);button(controls,"Replay",replay);button(controls,"+1 tick",func():pause();advance_ticks(1.0,true))
 speed_picker=OptionButton.new()
 for v in [0.25,0.5,1.0,2.0]:
  speed_picker.add_item(str(v)+"×");speed_picker.set_item_metadata(speed_picker.item_count-1,v)
 speed_picker.select(2);speed_picker.item_selected.connect(func(i):set_speed(float(speed_picker.get_item_metadata(i))));controls.add_child(speed_picker)
 var loop_box=CheckBox.new();loop_box.text="Force loop";loop_box.toggled.connect(func(v):loop_override=v);controls.add_child(loop_box)
 button(controls,"World motion test",func():get_tree().change_scene_to_file("res://moving_world.tscn"))
 var displays=HBoxContainer.new();displays.add_theme_constant_override("separation",24);column.add_child(displays)
 live_viewport=make_panel(displays,"LIVE RIG · CONTINUOUS JOINTS");baked_viewport=make_panel(displays,"BAKED SPRITE · ONE-TICK HOLDS")
 rig=load("res://rig.gd").new();live_viewport.add_child(rig);rig.configure(design,clips)
 baked=AnimatedSprite2D.new();baked.centered=false;baked.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;baked.sprite_frames=load("res://generated/frames.tres");baked_viewport.add_child(baked);baked.pause()
 effects=load("res://effects.gd").new();baked_viewport.add_child(effects);effects.visible=false
 anchor_overlay=Node2D.new();live_viewport.add_child(anchor_overlay);anchor_overlay.draw.connect(draw_anchors)
 var options=HBoxContainer.new();column.add_child(options)
 var anchors=CheckBox.new();anchors.text="Joint anchors";anchors.toggled.connect(func(v):show_anchors=v;anchor_overlay.queue_redraw());options.add_child(anchors)
 var fx_box=CheckBox.new();fx_box.text="Effects (authored visuals)";fx_box.toggled.connect(set_effects);options.add_child(fx_box)
 var grid=CheckBox.new();grid.text="Checker / ground guides";grid.button_pressed=true;grid.toggled.connect(func(v):checker=v;queue_redraw());options.add_child(grid)
 status_label=text(column,"",14);event_log=RichTextLabel.new();event_log.custom_minimum_size=Vector2(0,120);event_log.size_flags_vertical=Control.SIZE_EXPAND_FILL;column.add_child(event_log)
 text(column,"One-shots hold their authored endpoint through the final tick; Play resumes, Replay resets. Events are authored markers, not combat rules.",13)
func make_panel(parent: Node,title: String) -> SubViewport:
 var stack=VBoxContainer.new();parent.add_child(stack);text(stack,title,15)
 var frame=SubViewportContainer.new();frame.custom_minimum_size=Vector2(384,384);frame.stretch=true;frame.stretch_shrink=2;frame.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;stack.add_child(frame)
 var viewport=SubViewport.new();viewport.size=Vector2i(192,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;viewport.canvas_item_default_texture_filter=Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST;frame.add_child(viewport)
 # Render a separate guide behind each transparent character surface.
 var guide=Node2D.new();guide.z_index=-10;viewport.add_child(guide);guide.draw.connect(func():
  if checker:
   for y in range(0,192,12):
    for x in range(0,192,12):guide.draw_rect(Rect2(x,y,12,12),Color("27303b")if (x/12+y/12)%2==0 else Color("222a34"))
   guide.draw_line(Vector2(0,170),Vector2(192,170),Color("596d78"),1)
 );viewport.set_meta("guide",guide);return viewport
func _draw() -> void:
 for viewport in [live_viewport,baked_viewport]:
  if is_instance_valid(viewport):viewport.get_meta("guide").queue_redraw()
func draw_anchors() -> void:
 if not show_anchors:return
 var landmarks=last_pose.get("landmarks",{})
 if landmarks is Dictionary:
  for value in landmarks.values():
   if value is Array and value.size()==2:anchor_overlay.draw_circle(Vector2(value[0],value[1]),2,Color("f5e08b"))
 for key in ["feet","hands","hips","knees","elbows"]:
  var group=last_pose.get(key,{})
  if group is Dictionary:
   for value in group.values():
    if value is Array and value.size()==2:anchor_overlay.draw_circle(Vector2(value[0],value[1]),2,Color("f5e08b"))
func select_clip(name: String) -> bool:
 if not clips.clips.has(name)or not manifest.clips.has(name+"/"+current_view):return false
 current_clip=name;playing=false;replay(false)
 if is_instance_valid(clip_picker):
  for i in range(clip_picker.item_count):if clip_picker.get_item_text(i)==name:clip_picker.select(i)
 return true
func set_view(view: String) -> bool:
 if not view in ["right","left"]or not manifest.clips.has(current_clip+"/"+view):return false
 current_view=view
 if is_instance_valid(effects):rebuild_effects()
 if is_instance_valid(view_picker):view_picker.select(manifest.views.find(view))
 show_pose();return true
func set_speed(value: float) -> bool:
 if not is_finite(value)or value<=0 or value>8:return false
 speed=value
 if is_instance_valid(speed_picker):
  var found=false
  for i in range(speed_picker.item_count):
   if float(speed_picker.get_item_metadata(i))==value:speed_picker.select(i);found=true;break
  if not found:speed_picker.add_item(str(value)+"×");speed_picker.set_item_metadata(speed_picker.item_count-1,value);speed_picker.select(speed_picker.item_count-1)
 show_pose();return true
func replay(start=true) -> void:
 tick_clock=0.0;events.clear();event_keys.clear();playing=start;
 if is_instance_valid(effects):effects.reset()
 dispatch_events(-0.0001,0.0);show_pose()
func play() -> void:
 if current_clip.is_empty():return
 if not clips.clips[current_clip].loop and not loop_override and tick_clock>=clips.clips[current_clip].duration_ticks:return
 playing=true;show_pose()
func pause() -> void:playing=false;show_pose()
func advance_ticks(delta: float,force=false) -> bool:
 if not is_finite(delta)or delta<0 or delta>10000:return false
 if not playing and not force:return true
 var before=tick_clock;var c: Dictionary=clips.clips[current_clip]
 tick_clock+=delta
 var rounded=roundf(tick_clock)
 if absf(tick_clock-rounded)<=1.0e-12*maxf(1.0,absf(tick_clock)):tick_clock=rounded
 if not c.loop and not loop_override:
  tick_clock=minf(tick_clock,float(c.duration_ticks))
  if tick_clock>=float(c.duration_ticks):playing=false
 dispatch_events(before,tick_clock);show_pose();return true
func dispatch_events(before: float,after: float) -> void:
 var c: Dictionary=clips.clips[current_clip];var n=int(c.duration_ticks)
 for cycle in range(maxi(0,int(floor(before/n))),int(floor(after/n))+1):
  if cycle>0 and not c.loop and not loop_override:break
  for i in range(c.events.size()):
   var event: Dictionary=c.events[i];var absolute=cycle*n+int(event.tick);var key=str(cycle)+"/"+str(i)
   if absolute>before and absolute<=after and not event_keys.has(key):
    event_keys[key]=true;var delivered={"clip":current_clip,"view":current_view,"cycle":cycle,"tick":absolute,"type":event.type};events.append(delivered)
    if effects_enabled:deliver_effect(delivered)
func show_pose() -> void:
 if not is_instance_valid(rig)or current_clip.is_empty():return
 var c: Dictionary=clips.clips[current_clip];var n=int(c.duration_ticks);var loop=bool(c.loop)or loop_override;var local=fmod(tick_clock,n)if loop else minf(tick_clock,n-1)
 var phase=tick_clock/n if c.loop else local/maxi(1,n-1)
 if effects_enabled:effects.set_clock(tick_clock)
 last_pose=rig.pose(current_clip,phase,current_view)
 baked.animation=current_clip+"/"+current_view;baked.set_frame_and_progress(int(floor(local)),local-floor(local));baked.pause()
 if is_instance_valid(anchor_overlay):anchor_overlay.queue_redraw()
 if is_instance_valid(status_label):status_label.text="%s / %s   ·   tick %.3f / %d   ·   sprite frame %d   ·   %s   ·   %s×"%[current_clip,current_view,tick_clock,n,baked.frame,"playing"if playing else"paused / endpoint",speed]
 if is_instance_valid(event_log):
  event_log.text="AUTHORED EVENT LEDGER  (one delivery per clip cycle)\n"
  for e in events.slice(maxi(0,events.size()-6)):event_log.text+="tick %d · %s · cycle %d\n"%[e.tick,e.type,e.cycle]
func _process(delta: float) -> void:
 if playing:advance_ticks(delta*float(clips.fps)*speed)
func read_back() -> Dictionary:
 return {"clip":current_clip,"view":current_view,"tick":tick_clock,"frame":baked.frame if is_instance_valid(baked)else-1,"playing":playing,"speed":speed,"loop_override":loop_override,"events":events.duplicate(true),"pose":last_pose.duplicate(true),"completion_policy":"hold_final_until_replay_or_clip_change","clock":"authored60Hz; shared rig/real SpriteFrames consumer"}

func deliver_effect(event: Dictionary) -> void:
 var c: Dictionary=clips.clips[event.clip];var local=fmod(float(event.tick),float(c.duration_ticks))
 var phase=float(event.tick)/float(c.duration_ticks)if c.loop else local/maxi(1,int(c.duration_ticks)-1)
 var event_pose: Dictionary=rig.pose(event.clip,phase,current_view)
 effects.receive(event.clip+"/"+current_view+"/"+str(event.cycle)+"/"+str(event.tick)+"/"+event.type,event.type,float(event.tick),event_pose)
func rebuild_effects() -> void:
 effects.reset()
 if effects_enabled:
  for event in events:deliver_effect(event)
  effects.set_clock(tick_clock)
func set_effects(enabled: bool) -> void:
 effects_enabled=enabled;effects.visible=enabled;rebuild_effects();show_pose()
