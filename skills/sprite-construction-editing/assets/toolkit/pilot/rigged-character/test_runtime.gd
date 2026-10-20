extends SceneTree
var checks: Array=[]
var pixels: Array=[]
var negative_cases: Array=[]
func _initialize() -> void:
 Engine.max_fps=240
 call_deferred("run")
func check(ok: bool,label: String) -> void:checks.append({"passed":ok,"label":label})
func pixel_hash(image: Image) -> String:
 image.convert(Image.FORMAT_RGBA8);var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(image.get_data());return h.finish().hex_encode()
func source_phase(c: Dictionary,tick: float) -> float:return tick/float(c.duration_ticks) if c.loop else tick/maxi(1,int(c.duration_ticks)-1)
func automatic_playback(sf: SpriteFrames,binding: String,c: Dictionary) -> void:
 var sprite=AnimatedSprite2D.new();sprite.sprite_frames=sf;root.add_child(sprite);var observed={"frames":[],"loops":0,"finished":0}
 sprite.frame_changed.connect(func():observed.frames.append(sprite.frame));sprite.animation_looped.connect(func():observed.loops+=1);sprite.animation_finished.connect(func():observed.finished+=1)
 sprite.animation=binding;sprite.set_frame_and_progress(0,0.0);observed.frames.clear();sprite.play();await create_timer(float(c.duration_ticks)/60.0+0.04).timeout
 var wanted=[]
 for i in range(1,int(c.duration_ticks)):wanted.append(i)
 check(observed.frames.slice(0,wanted.size())==wanted,binding+" actual automatic SpriteFrames complete order")
 check(observed.loops==1 and observed.finished==0 if c.loop else observed.loops==0 and observed.finished==1,binding+" isolated automatic loop/finish signal")
 sprite.pause();var frame=sprite.frame;var progress=sprite.frame_progress;await create_timer(0.025).timeout;check(sprite.frame==frame and sprite.frame_progress==progress,binding+" automatic pause preserves fraction")
 sprite.stop();sprite.speed_scale=2.0;sprite.play();await create_timer(float(c.duration_ticks)/120.0+0.025).timeout
 check(sprite.is_playing() if c.loop else not sprite.is_playing(),binding+" real automatic double-speed completion")
 sprite.queue_free();await process_frame
func frame_contract(sf: SpriteFrames,binding: String,c: Dictionary,tick: int) -> bool:
 if sf.get_frame_count(binding)!=int(c.duration_ticks)or sf.get_animation_speed(binding)!=60.0 or sf.get_animation_loop(binding)!=bool(c.loop):return false
 var region=sf.get_frame_texture(binding,tick)as AtlasTexture;var r=c.frames[tick].region
 return sf.get_frame_duration(binding,tick)==1.0 and region!=null and region.region==Rect2(r[0],r[1],r[2],r[3])and region.atlas.resource_path=="res://generated/"+c.atlas
func click_button(lab: Control,label: String) -> bool:
 var target: Button=null
 for node in lab.find_children("*","Button",true,false):
  if node.text==label:target=node;break
 if target==null:return false
 var point=target.get_global_rect().get_center();var motion=InputEventMouseMotion.new();motion.position=point;motion.global_position=point;Input.parse_input_event(motion)
 var down=InputEventMouseButton.new();down.button_index=MOUSE_BUTTON_LEFT;down.pressed=true;down.position=point;down.global_position=point;Input.parse_input_event(down);await process_frame
 var up=InputEventMouseButton.new();up.button_index=MOUSE_BUTTON_LEFT;up.pressed=false;up.position=point;up.global_position=point;Input.parse_input_event(up);await process_frame
 return true
func run() -> void:
 var lab=load("res://lab.gd").new();lab.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);root.add_child(lab);lab.set_process(false)
 if not lab.load_error.is_empty():push_error(lab.load_error);quit(3);return
 for viewport in [lab.live_viewport,lab.baked_viewport]:viewport.get_meta("guide").visible=false
 lab.anchor_overlay.visible=false
 var manifest: Dictionary=lab.manifest;var sf: SpriteFrames=lab.baked.sprite_frames
 var save_path="res://generated/engine-roundtrip.tres";check(ResourceSaver.save(sf,save_path)==OK,"Actual SpriteFrames resource save");sf=ResourceLoader.load(save_path,"SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE);lab.baked.sprite_frames=sf
 var pixel_folder="res://generated/runtime-pixels";DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(pixel_folder))
 for binding in manifest.clips:
  var c: Dictionary=manifest.clips[binding];lab.select_clip(c.name);lab.set_view(c.view);lab.loop_override=false;lab.replay();var n=int(c.duration_ticks)
  for tick in range(n):
   check(lab.baked.frame==tick,binding+" exact tick frame "+str(tick));check(frame_contract(sf,binding,c,tick),binding+" saved/reloaded frame region/hold/order "+str(tick))
   if tick in [0,n/4,n/2,n-1]:
    await process_frame;await RenderingServer.frame_post_draw
    var baked=lab.baked_viewport.get_texture().get_image();var live=lab.live_viewport.get_texture().get_image();var expected=Image.load_from_file("res://generated/"+c.frames[tick].png)
    var bh=pixel_hash(baked);var lh=pixel_hash(live);var eh=pixel_hash(expected)
    check(bh==eh,binding+" actual GPU baked pixels at tick "+str(tick));check(lh==eh,binding+" actual GPU rig versus bake tick "+str(tick))
    var file=binding.replace("/","-")+"-"+str(tick);baked.save_png(pixel_folder+"/"+file+"-baked.png");live.save_png(pixel_folder+"/"+file+"-rig.png")
    pixels.append({"binding":binding,"tick":tick,"expected_sha256":eh,"baked_sha256":bh,"rig_sha256":lh,"held_png":"runtime-pixels/"+file+"-baked.png"})
   lab.advance_ticks(0.75);check(lab.baked.frame==tick,binding+" sub-tick hold "+str(tick))
   if tick in [0,n/4,n/2,n-1]:
    await process_frame;await RenderingServer.frame_post_draw
    var held=lab.baked_viewport.get_texture().get_image();var expected=Image.load_from_file("res://generated/"+c.frames[tick].png);var bh=pixel_hash(held);var eh=pixel_hash(expected)
    check(bh==eh,binding+" actual GPU held pixels at tick "+str(tick)+" +0.75")
    pixels.append({"binding":binding,"tick":tick,"fraction":0.75,"expected_sha256":eh,"baked_sha256":bh,"scope":"Baked hold only; live rig is deliberately continuous between samples"})
   lab.advance_ticks(0.25)
  var expected_events=c.events.size()
  if c.loop:expected_events+=c.events.filter(func(e):return e.tick==0).size()
  check(lab.events.size()==expected_events,binding+" once per semantic marker across complete duration")
  var seen={};var unique=true
  for e in lab.events:
   var key=str(e.cycle)+"/"+str(e.tick)+"/"+e.type
   if seen.has(key):unique=false
   seen[key]=true
  check(unique,binding+" no duplicate authored events")
  check(lab.playing and lab.baked.frame==0 if c.loop else not lab.playing and lab.baked.frame==n-1,binding+" final hold / loop boundary")
  if not c.loop:check(lab.last_pose.endpoint,binding+" live and baked endpoint policy")
  lab.replay();lab.advance_ticks(3.375);lab.pause();var frozen: Dictionary=lab.read_back();lab.advance_ticks(10);check(lab.read_back()==frozen,binding+" shared clock pause exact")
  lab.play();lab.advance_ticks(0.625);check(lab.tick_clock==4.0 and lab.baked.frame==4,binding+" Play resumes retainedfraction")
  lab.replay();lab.set_speed(2.0);lab._process(4.0/60.0);check(lab.tick_clock==8.0 and lab.baked.frame==8,binding+" process clock integral double speed")
  lab.set_speed(0.5);lab._process(4.0/60.0);check(lab.tick_clock==10.0,binding+" mid-play speed change")
  lab.replay();lab.advance_ticks(8.0-1.0e-9);check(lab.baked.frame==7,binding+" genuine early clock preserves previous frame")
  lab.replay();lab.advance_ticks(n-0.25);var expected=c.events.filter(func(e):return e.tick<=n-0.25).size();check(lab.events.size()==expected,binding+" low-rate skippedframes event completeness")
  var before=lab.events.duplicate(true);lab.advance_ticks(0.0);check(lab.events==before,binding+" zero delta cannot redeliver event")
  var state=lab.read_back();check(not lab.advance_ticks(NAN)and state==lab.read_back(),binding+" invalid delta atomic")
  if not c.loop:
   lab.loop_override=true;lab.replay();lab.advance_ticks(n);check(lab.playing and lab.baked.frame==0 and lab.last_pose.input_phase==0.0,binding+" forced one-shot loop resets live/baked pose together");lab.loop_override=false
  lab.replay(false);check(lab.tick_clock==0 and lab.baked.frame==0 and not lab.playing,binding+" Replay resets intentional clock")
  # Deliberate live engine resource perturbations must fail source contract.
  var bad=sf.duplicate(true);bad.set_frame(binding,0,bad.get_frame_texture(binding,0),2.0);var detected=not frame_contract(bad,binding,c,0);check(detected,binding+" detect wrong duration");negative_cases.append({"binding":binding,"kind":"duration","detected":detected})
  bad=sf.duplicate(true);bad.set_frame(binding,0,bad.get_frame_texture(binding,1),1.0);detected=not frame_contract(bad,binding,c,0);check(detected,binding+" detect wrong order");negative_cases.append({"binding":binding,"kind":"order","detected":detected})
  if not c.events.is_empty():
   var original: Array=lab.clips.clips[c.name].events.duplicate(true);lab.clips.clips[c.name].events.append(original[0].duplicate(true));lab.replay();lab.advance_ticks(n-0.25)
   detected=lab.events.size()!=expected;check(detected,binding+" detect duplicated authored event");negative_cases.append({"binding":binding,"kind":"eventduplicate","detected":detected});lab.clips.clips[c.name].events=original
  await automatic_playback(sf,binding,c)
 var wrong: Dictionary=manifest.source_bindings.duplicate(true);wrong["design.json"]="0".repeat(64);check(not lab.source_fresh(wrong),"Source edit/stale bake rejected without mutating source")
 var manifest_path="res://generated/manifest.json";var original_text=FileAccess.get_file_as_string(manifest_path);var stale=manifest.duplicate(true)
 stale.source_bindings["design.json"]="0".repeat(64)
 FileAccess.open(manifest_path,FileAccess.WRITE).store_string(JSON.stringify(stale))
 var rejected=load("res://lab.gd").new();var accepted: bool=rejected.configure_sources();check(not accepted and rejected.load_error.begins_with("Stale bake:"),"Actual source loader rejects stale source binding");rejected.free()
 FileAccess.open(manifest_path,FileAccess.WRITE).store_string(original_text)
 lab.select_clip("idle"if manifest.clips.has("idle/right")else manifest.clips.values()[0].name);lab.set_view("right");lab.replay(false)
 check(await click_button(lab,"Play")and lab.playing,"Actual mouse Play starts clock")
 check(await click_button(lab,"Pause")and not lab.playing,"Actual mouse Pause stops clock")
 var prior=lab.tick_clock
 check(await click_button(lab,"+1 tick")and lab.tick_clock==prior+1.0,"Actual mouse step advances exact tick")
 check(await click_button(lab,"Replay")and lab.playing and lab.tick_clock==0.0,"Actual mouse Replay resets and plays")
 lab.pause()
 for viewport in [lab.live_viewport,lab.baked_viewport]:viewport.get_meta("guide").visible=true
 await process_frame;await RenderingServer.frame_post_draw;root.get_texture().get_image().save_png("res://generated/lab-screenshot.png")
 var failures=checks.filter(func(c):return not c.passed);var report={"schema":"copper-scout-runtime-proof/v1","passed":failures.is_empty(),"check_count":checks.size(),"failures":failures,"checks":checks,"actual_gpu_samples":pixels,"negative_cases":negative_cases,"source_bindings":manifest.source_bindings,"godot":Engine.get_version_info(),"tester_sha256":FileAccess.get_sha256("res://test_runtime.gd"),"lab_sha256":FileAccess.get_sha256("res://lab.gd"),"scope":"Actual Godot source rig, saved/reloaded SpriteFrames, shared authored event clock and separate automatic AnimatedSprite2D runtime","limits":["Mechanics and exact raster reproduction do not establish art approval.","Continuous live pose intentionally differs from baked pose between source tick samples.","Events are authored markers; no combat/collision/gameplay implementation is inferred.","No cross-renderer pixel or PNG-byte determinism claim; same renderer repeat tested separately."]}
 FileAccess.open("res://generated/runtime-proof.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("RUNTIME_PROOF ",checks.size()," checks failures=",failures.size());quit(0 if failures.is_empty()else 2)
