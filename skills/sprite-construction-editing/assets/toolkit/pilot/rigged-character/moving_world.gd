extends Control
# Fixed camera: physical motion and whole-sprite visual compensation remain distinct.
var cache: Dictionary
var manifest: Dictionary
var clips: Dictionary
var rig: Node2D
var sprite: Sprite2D
var viewport: SubViewport
var guide: Node2D
var clip="walk"
var mode="contact-locked visual root"
var clock=0.0
var playing=false
var error=""
var observation: Dictionary={}
var label: Label
const ORIGIN=32.0
func fail(message: String) -> bool:
 error=message;return false
func read_dictionary(path: String) -> Dictionary:
 if not FileAccess.file_exists("res://"+path):error="Missing "+path;return {}
 var parser=JSON.new()
 if parser.parse(FileAccess.get_file_as_string("res://"+path))!=OK or not parser.data is Dictionary:error="Invalid JSON dictionary: "+path;return {}
 return parser.data
func integral(value: Variant,minimum: int,maximum: int) -> bool:
 return (value is int or value is float)and is_finite(float(value))and float(value)==floor(float(value))and value>=minimum and value<=maximum
func configure_sources() -> bool:
 error=""
 cache=read_dictionary("contact-proof/held-sole-cache.json")
 if not error.is_empty():return false
 manifest=read_dictionary("generated/manifest.json")
 if not error.is_empty():return false
 clips=read_dictionary("clips.json")
 if not error.is_empty():return false
 var receipt=read_dictionary("generated/build-receipt.json")
 if not error.is_empty():return false
 if receipt.get("manifest_sha256")!=FileAccess.get_sha256("res://generated/manifest.json"):return fail("Stale build receipt manifest")
 if not FileAccess.file_exists("res://generated/frames.tres")or receipt.get("frames_tres_sha256")!=FileAccess.get_sha256("res://generated/frames.tres"):return fail("Stale SpriteFrames resource")
 if not manifest.get("source_bindings")is Dictionary or receipt.get("source_bindings")!=manifest.source_bindings:return fail("Build receipt source bindings differ")
 if manifest.source_bindings.size()!=5 or not manifest.source_bindings.has_all(["rig.gd","design.json","clips.json","bake.gd","build_exports.py"]):return fail("Incomplete rendered source bindings")
 if not cache.get("source_sha256")is Dictionary or cache.source_sha256.size()!=3 or not cache.source_sha256.has_all(["rig.gd","design.json","clips.json"]):return fail("Missing cache source bindings")
 for bindings in [manifest.source_bindings,cache.source_sha256]:
  for name in bindings:
   if not FileAccess.file_exists("res://"+name)or FileAccess.get_sha256("res://"+name)!=bindings[name]:return fail("Stale source/cache: "+name)
 if FileAccess.get_sha256("res://foot_contact.gd")!=cache.get("policy_sha256"):return fail("Stale contact policy")
 if cache.get("schema")!="copper-scout-held-sole-cache/v1"or cache.get("view")!="right":return fail("Unsupported contact cache")
 if not integral(cache.get("sole_row"),169,169)or not integral(cache.get("ground_boundary"),170,170)or cache.get("sole_offset")!=-9:return fail("Unsupported cache ground geometry")
 if not manifest.get("clips")is Dictionary or not clips.get("clips")is Dictionary or not cache.get("clips")is Dictionary:return fail("Missing clip dictionaries")
 if not integral(manifest.get("fps"),60,60)or not integral(clips.get("fps"),60,60):return fail("World runner requires authored 60 Hz")
 for name in ["walk","run"]:
  if not manifest.clips.has(name+"/right"):return fail("World runner requires full walk/run bake")
  if not clips.clips.has(name)or not cache.clips.has(name):return fail("Missing locomotion source/cache")
  var source=clips.clips[name];var baked=manifest.clips[name+"/right"];var cached=cache.clips[name]
  if not source is Dictionary or not baked is Dictionary or not cached is Dictionary:return fail("Invalid locomotion dictionary")
  var duration=source.get("duration_ticks")
  if not integral(duration,1,441)or baked.get("duration_ticks")!=duration or cached.get("duration_ticks")!=duration or not integral(cached.get("fps"),60,60):return fail("Locomotion timing mismatch")
  if not source.get("gait")is Dictionary or cached.get("root_motion_px_per_cycle")!=source.gait.get("root_motion_px_per_cycle"):return fail("Locomotion gait mismatch")
  if not cached.get("frames")is Array or not baked.get("frames")is Array or cached.frames.size()!=duration or baked.frames.size()!=duration:return fail("Cache count mismatch")
  for index in range(int(duration)):
   var row=cached.frames[index];var frame=baked.frames[index]
   if not row is Dictionary or not frame is Dictionary or not integral(row.get("tick"),index,index)or not integral(frame.get("tick"),index,index):return fail("Cache row order mismatch")
   if row.get("whole_frame_rgba_sha256")!=frame.get("pixel_sha256"):return fail("Cache raster mismatch")
   var soles=row.get("sole_xmin")
   if not soles is Dictionary or not soles.has("front")or not soles.has("rear"):return fail("Missing sole cache entries")
   for side in ["front","rear"]:
    if soles[side]!=null and not integral(soles[side],0,191):return fail("Invalid cached sole coordinate")
 return true
func _ready() -> void:
 if not configure_sources():
  var failure=Label.new();failure.text=error;failure.position=Vector2(24,24);add_child(failure)
  var back=Button.new();back.text="In-place lab";back.position=Vector2(24,64);back.pressed.connect(func():get_tree().change_scene_to_file("res://main.tscn"));add_child(back);return
 var stack=VBoxContainer.new();stack.position=Vector2(24,24);add_child(stack)
 var title=Label.new();title.text="FIXED-CAMERA WORLD RUNNER · right view · original 60 Hz";stack.add_child(title)
 var bar=HBoxContainer.new();stack.add_child(bar)
 var picker=OptionButton.new()
 for name in ["walk","run"]:picker.add_item(name)
 picker.item_selected.connect(func(i):clip=picker.get_item_text(i);clock=0.0;present());bar.add_child(picker)
 var modes=OptionButton.new()
 for name in ["live physical root","baked physical root","contact-locked visual root"]:modes.add_item(name)
 modes.select(2);modes.item_selected.connect(func(i):mode=modes.get_item_text(i);present());bar.add_child(modes)
 for item in [["Play",func():playing=true],["Pause",func():playing=false],["Replay",func():clock=0.0;playing=true;present()],["+0.2 tick",func():playing=false;advance(0.2)],["In-place lab",func():get_tree().change_scene_to_file("res://main.tscn")]]:
  var button=Button.new();button.text=item[0];button.pressed.connect(item[1]);bar.add_child(button)
 var guides=CheckBox.new();guides.text="Ground / fixed-world ruler";guides.button_pressed=true;guides.toggled.connect(func(value):guide.visible=value);bar.add_child(guides)
 var surface=SubViewportContainer.new();surface.custom_minimum_size=Vector2(1024,384);surface.stretch=true;surface.stretch_shrink=2;surface.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;stack.add_child(surface)
 viewport=SubViewport.new();viewport.size=Vector2i(512,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;surface.add_child(viewport)
 guide=Node2D.new();guide.z_index=-10;viewport.add_child(guide);guide.draw.connect(func():
  guide.draw_line(Vector2(0,170),Vector2(512,170),Color("596d78"),1)
  for x in range(0,512,32):guide.draw_line(Vector2(x,171),Vector2(x,179),Color("596d78"),1)
 )
 rig=load("res://rig.gd").new();viewport.add_child(rig);rig.configure(JSON.parse_string(FileAccess.get_file_as_string("res://design.json")),clips)
 sprite=Sprite2D.new();sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;viewport.add_child(sprite)
 label=Label.new();stack.add_child(label)
 var note=Label.new();note.text="Camera stays fixed. Visual contact correction translates the whole sprite; physics root stays continuous.\nRight walk/run only; replay before leaving the 512 px strip. No collision/gameplay implementation.";stack.add_child(note)
 present()
func advance(ticks: float) -> bool:
 if not is_finite(ticks)or ticks<0 or ticks>10000:return false
 clock+=ticks;present();return true
func _process(dt: float) -> void:
 if playing and error.is_empty():advance(dt*60.0)
func present() -> void:
 if not is_instance_valid(rig):return
 var n=int(clips.clips[clip].duration_ticks);var phase=clock/n;var held=int(floor(clock))%n
 var meta: Dictionary=rig.pose(clip,phase,"right");var physical=float(clips.clips[clip].gait.root_motion_px_per_cycle)*phase
 var soles={}
 for side in ["front","rear"]:
  var value=cache.clips[clip].frames[held].sole_xmin[side];soles[side]=null if value==null else int(value)
 var policy: Dictionary=load("res://foot_contact.gd").contact_draw_root(meta,physical,soles,ORIGIN,float(cache.sole_offset))
 if policy.has("error"):error=policy.error;return
 var draw_root=policy.draw_root if mode=="contact-locked visual root"else physical
 rig.visible=mode=="live physical root";rig.position=Vector2(ORIGIN+physical,0)
 sprite.visible=not rig.visible;sprite.texture=load("res://generated/frames.tres").get_frame_texture(clip+"/right",held);sprite.position=Vector2(ORIGIN+draw_root,0)
 observation={"clip":clip,"clock":clock,"held_tick":held,"mode":mode,"physical_root":physical,"draw_root":draw_root,"policy":policy,"contact_flags":meta.contact_flags}
 label.text="tick %.3f · held %d · physical %.3f px · draw %.3f px · visual offset %.3f px"%[clock,held,physical,draw_root,draw_root-physical]
