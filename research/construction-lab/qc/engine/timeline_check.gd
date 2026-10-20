extends SceneTree
var checks: Array = []
var realtime: Array = []
var deterministic: Array = []
var native_routes: Array = []
var negatives: Array = []
func check(ok: bool, label: String) -> void:
 checks.append({"label":label,"passed":ok})
func _initialize() -> void:
 Engine.max_fps=120
 call_deferred("run")
func build_frames(manifest: Dictionary, name: String) -> SpriteFrames:
 var sf=SpriteFrames.new();sf.remove_animation("default")
 var rows={}
 for f in manifest.frames: rows[f.id]=f
 for a in manifest.animations:
  sf.add_animation(a.id);sf.set_animation_speed(a.id,a.fps);sf.set_animation_loop(a.id,a.loop)
  for id in a.frames:
   var texture=AtlasTexture.new();texture.atlas=load("res://fixtures/%s/atlas.png" % name)
   var r=rows[id].region;texture.region=Rect2(r[0],r[1],r[2],r[3]);sf.add_frame(a.id,texture,rows[id].duration_ticks)
 return sf
func oracle(manifest: Dictionary, a: Dictionary) -> Dictionary:
 var rows={};var starts=[];var holds=[];var regions=[];var time=0.0
 for f in manifest.frames:rows[f.id]=f
 for id in a.frames:
  starts.append(time);holds.append(float(rows[id].duration_ticks)/float(a.fps));regions.append(rows[id].region);time+=holds[-1]
 return {"starts":starts,"holds":holds,"regions":regions,"duration":time,"events":a.events}
func isolated_native_playback(sf: SpriteFrames, a: Dictionary, expected: Dictionary, label: String) -> void:
 var sprite=AnimatedSprite2D.new();sprite.sprite_frames=sf;root.add_child(sprite)
 var record={"changes":[],"loops":0,"finished":0,"start_usec":0}
 sprite.frame_changed.connect(func():record.changes.append({"frame":sprite.frame,"seconds":float(Time.get_ticks_usec()-record.start_usec)/1000000.0}))
 sprite.animation_looped.connect(func():record.loops+=1)
 sprite.animation_finished.connect(func():record.finished+=1)
 sprite.animation=a.id;sprite.set_frame_and_progress(0,0.0);record.changes.clear();record.start_usec=Time.get_ticks_usec();sprite.play(a.id)
 await create_timer(expected.duration+0.05).timeout
 var wanted=[]
 for i in range(1,a.frames.size()):wanted.append(i)
 var actual=record.changes.slice(0,wanted.size()).map(func(v):return v.frame)
 check(actual==wanted,label+" real AnimatedSprite complete order")
 var worst=0.0
 for i in range(min(wanted.size(),record.changes.size())):worst=maxf(worst,abs(float(record.changes[i].seconds)-float(expected.starts[i+1])))
 # Native process scheduling tolerance: two120Hz process periods +5ms, not exact wall-time equality.
 check(record.changes.size()>=wanted.size() and worst<0.025,label+" real holds within measured process tolerance")
 if a.loop:check(record.loops==1 and record.finished==0 and sprite.is_playing(),label+" isolated loop signal")
 else:check(record.finished==1 and record.loops==0 and not sprite.is_playing() and sprite.frame==a.frames.size()-1,label+" isolated one-shot signal")
 var first_pass_changes: Array=record.changes.duplicate(true);var first_pass_loops: int=record.loops;var first_pass_finished: int=record.finished
 sprite.play(a.id);sprite.set_frame_and_progress(0,0.2);await process_frame;sprite.pause();var frame=sprite.frame;var progress=sprite.frame_progress;await create_timer(0.06).timeout
 check(sprite.frame==frame and abs(sprite.frame_progress-progress)<0.000001 and not sprite.is_playing(),label+" real pause freezes phase")
 sprite.play();await create_timer(0.025).timeout;check(sprite.is_playing() and (sprite.frame!=frame or sprite.frame_progress>progress),label+" real resume preserves phase")
 sprite.stop();sprite.speed_scale=2.0;record.changes.clear();record.loops=0;record.finished=0;record.start_usec=Time.get_ticks_usec();sprite.play(a.id)
 await create_timer(expected.duration/2.0+0.03).timeout
 if a.loop:check(record.loops==1,label+" double speed exact loop count")
 else:check(record.finished==1 and sprite.frame==a.frames.size()-1,label+" double speed completion")
 realtime.append({"clip":label,"first_pass_changes":first_pass_changes,"double_speed_changes":record.changes,"max_first_pass_timing_error_seconds":worst,"first_pass_loop_signals":first_pass_loops,"first_pass_finish_signals":first_pass_finished,"double_speed_loop_signals":record.loops,"double_speed_finish_signals":record.finished,"signal_scope":"One distinct AnimatedSprite2D per clip; freed after test"})
 sprite.stop();sprite.queue_free();await process_frame
func make_track(sf: SpriteFrames, a: Dictionary) -> Dictionary:
 var container=Node2D.new();root.add_child(container);var sprite=AnimatedSprite2D.new();sprite.name="Sprite";sprite.sprite_frames=sf;sprite.animation=a.id;sprite.pause();container.add_child(sprite)
 var player=AnimationPlayer.new();player.name="Timeline";player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL;player.callback_mode_method=AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE;container.add_child(player)
 var track=Animation.new();var time=0.0;var index=track.add_track(Animation.TYPE_VALUE);track.track_set_path(index,NodePath("Sprite:frame"));track.value_track_set_update_mode(index,Animation.UPDATE_DISCRETE)
 for i in range(sf.get_frame_count(a.id)):
  track.track_insert_key(index,time,i);time+=sf.get_frame_duration(a.id,i)/sf.get_animation_speed(a.id)
 track.length=time;track.loop_mode=Animation.LOOP_LINEAR if a.loop else Animation.LOOP_NONE
 var probe=load("res://event_probe.gd").new();probe.name="Events";probe.player=player;container.add_child(probe)
 var method=track.add_track(Animation.TYPE_METHOD);track.track_set_path(method,NodePath("Events"))
 for e in a.events:track.track_insert_key(method,float(e.at_tick)/float(a.fps),{"method":&"record_event","args":[e.duplicate(true)]})
 var library=AnimationLibrary.new();library.add_animation("test",track);player.add_animation_library("",library)
 return {"container":container,"sprite":sprite,"player":player,"track":track,"probe":probe}
func exact_track_test(sf: SpriteFrames, a: Dictionary, expected: Dictionary, label: String) -> void:
 var fixture=make_track(sf,a);var player: AnimationPlayer=fixture.player;var sprite: AnimatedSprite2D=fixture.sprite;player.play("test");player.advance(0)
 var last=0.0;var sample_count=0
 for cycle in range(2 if a.loop else 1):
  for i in range(a.frames.size()):
   var begin=float(expected.starts[i])+cycle*expected.duration;var end=begin+float(expected.holds[i])
   for target in [begin+expected.holds[i]*0.4,end-0.0001]:
    player.advance(target-last);last=target;sample_count+=1
    check(sprite.frame==i,label+" deterministic hold %s cycle%s" % [i,cycle])
    var region=(sf.get_frame_texture(a.id,sprite.frame) as AtlasTexture).region;var r=expected.regions[i]
    check(region==Rect2(r[0],r[1],r[2],r[3]),label+" deterministic texture order %s" % i)
   if i+1<a.frames.size() or a.loop:
    var target=end+0.0001;player.advance(target-last);last=target;check(sprite.frame==(i+1)%a.frames.size(),label+" exact boundary %s" % i)
 if not a.loop:
  player.advance(expected.duration+0.0001-last);check(not player.is_playing() and sprite.frame==a.frames.size()-1,label+" deterministic one-shot endpoint")
 check(fixture.probe.events.size()==a.events.size()*(2 if a.loop else 1),label+" complete explicit event count")
 for i in range(fixture.probe.events.size()):
  var e=a.events[i%a.events.size()];check(fixture.probe.events[i].name==e.name and fixture.probe.events[i].source_tick==e.at_tick,label+" source-bound event identity")
 fixture.probe.events.clear()
 player.play("test");player.advance(0);player.advance(expected.duration*0.43);var position=player.current_animation_position;var frame=sprite.frame;player.pause()
 check(not player.is_playing() and sprite.frame==frame,label+" manual player pause retains state");player.play();player.advance(0.0001);check(player.current_animation_position>=position,label+" manual player resumes without restart")
 player.speed_scale=2.0;var prior=player.current_animation_position;player.advance(0.005);check(abs(player.current_animation_position-prior-0.01)<0.00001,label+" mid-play speed change doubles clock delta");player.speed_scale=1.0
 # Low-rate advance crosses multiple frame boundaries using actual AnimationPlayer track evaluation.
 player.stop();player.play("test");player.advance(0);var target=expected.duration*0.83;player.advance(target);var wanted=0
 for i in range(expected.starts.size()):if expected.starts[i]<=target:wanted=i
 check(sprite.frame==wanted,label+" low-rate multi-hold crossing")
 var wanted_events=a.events.filter(func(e):return float(e.at_tick)/float(a.fps)<=target)
 # Clear controls-phase callbacks and test low-rate crossings from a fresh engine clock.
 fixture.probe.events.clear();player.stop();player.play("test");player.advance(0);player.advance(target)
 check(fixture.probe.events.size()==wanted_events.size(),label+" low-rate method event count")
 deterministic.append({"clip":label,"samples":sample_count,"duration_seconds":expected.duration,"scope":"Actual Godot AnimationPlayer discrete frame track derived from saved SpriteFrames holds, compared with independent source manifest"})
 fixture.container.queue_free();await process_frame
func negative_track_tests(sf: SpriteFrames, a: Dictionary, expected: Dictionary, label: String) -> void:
 for kind in ["duration","clock","order"]:
  var bad=sf.duplicate(true)
  if kind=="duration":bad.set_frame(a.id,0,bad.get_frame_texture(a.id,0),bad.get_frame_duration(a.id,0)+1)
  if kind=="clock":bad.set_animation_speed(a.id,bad.get_animation_speed(a.id)*1.7)
  if kind=="order":bad.set_frame(a.id,0,bad.get_frame_texture(a.id,1),bad.get_frame_duration(a.id,0))
  var fixture=make_track(bad,a);fixture.player.play("test");fixture.player.advance(0)
  var target=expected.holds[0]+0.25/float(a.fps);fixture.player.advance(target);var want=1;var r=expected.regions[want];var actual=(bad.get_frame_texture(a.id,fixture.sprite.frame) as AtlasTexture).region
  var detected=fixture.sprite.frame!=want or actual!=Rect2(r[0],r[1],r[2],r[3])
  if kind=="order":
   fixture.player.stop();fixture.player.play("test");fixture.player.advance(0);var first=expected.regions[0];actual=(bad.get_frame_texture(a.id,fixture.sprite.frame)as AtlasTexture).region;detected=actual!=Rect2(first[0],first[1],first[2],first[3])
  if kind=="clock":
   fixture.player.stop();fixture.player.play("test");fixture.player.advance(0);fixture.player.advance(expected.holds[0]*0.8);detected=fixture.sprite.frame!=0
  check(detected,label+" catches deliberately perturbed "+kind);negatives.append({"clip":label,"perturbation":kind,"detected":detected});fixture.container.queue_free();await process_frame
func negative_event_test(sf: SpriteFrames, a: Dictionary, expected: Dictionary, label: String) -> void:
 if a.events.is_empty():return
 var bad=a.duplicate(true);bad.events[0].at_tick+=1;var fixture=make_track(sf,bad);fixture.player.play("test");fixture.player.advance(0)
 fixture.player.advance(float(a.events[0].at_tick)/float(a.fps)+0.0001)
 var detected=fixture.probe.events.is_empty()
 check(detected,label+" catches shifted explicit event tick");negatives.append({"clip":label,"perturbation":"event_tick","detected":detected})
 fixture.container.queue_free();await process_frame
func check_nodes(player: Node2D, frame: Dictionary) -> bool:
 var expected_count=0
 for obj in frame.objects:
  for i in range(obj.positions.size()):
   expected_count+=1;var key=str(obj.index)+"/"+str(i)
   if not player.nodes.has(key):return false
   var sprite: Sprite2D=player.nodes[key]
   if not sprite.visible or sprite.position!=Vector2(obj.positions[i][0],obj.positions[i][1]) or sprite.z_index!=obj.z_index or sprite.texture.resource_path!="res://"+str(obj.indexed_texture):return false
   if sprite.material.get_shader_parameter("palette_row")!=float(obj.palette) or sprite.material.get_shader_parameter("palette_texture").resource_path!="res://"+str(frame.palette_texture):return false
 var actual_count=0
 for sprite in player.nodes.values():if sprite.visible:actual_count+=1
 return actual_count==expected_count
func native_route_test(entry: Dictionary) -> void:
 var player=load("res://scripts/native_obj_player.gd").new();root.add_child(player);player.set_process(false)
 var loaded: bool=player.load_route("res://"+entry.path);check(loaded,entry.id+" validates captured native route");if not loaded:player.queue_free();return
 var oracle_route: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+entry.path));var ticks=0;var samples=[];player.replay()
 for i in range(oracle_route.frames.size()):
  var frame: Dictionary=oracle_route.frames[i];var state: Dictionary=player.read_back()
  check(state.frame_index==i and state.source_tick==frame.source_tick and state.actor==frame.actor and state.palette_state==frame.palette_state,entry.id+" capture state order %s" % i)
  check(check_nodes(player,frame),entry.id+" real Sprite2D textures/palette/coords %s" % i)
  var hold=float(frame.duration_ticks);player.advance_ticks(hold-0.25);check(player.frame_index==i,entry.id+" hold before boundary %s" % i);player.advance_ticks(0.25);ticks+=int(hold)
  if i<3 or i==oracle_route.frames.size()-1:samples.append(state)
 check(player.finished and not player.playing and player.frame_index==oracle_route.frames.size()-1,entry.id+" exact native terminal tick")
 check(ticks==int(oracle_route.duration_ticks),entry.id+" entire native duration")
 player.replay();player.advance_ticks(2.25);player.pause();var before=player.read_back();player.advance_ticks(12);check(player.read_back()==before,entry.id+" pause freezes tick and nodes");player.play();player.advance_ticks(0.75);check(player.frame_index==3,entry.id+" resume keeps fraction")
 player.replay();player.set_speed(2.0);player._process(4.0/float(oracle_route.video_fps));check(player.frame_index==8,entry.id+" real controller speed scaling")
 player.replay();player.advance_ticks(float(oracle_route.duration_ticks));check(player.finished,entry.id+" low-rate whole-route crossing")
 player.replay();player.advance_ticks(0.5);var unchanged=player.read_back();check(not player.advance_ticks(NAN) and player.read_back()==unchanged,entry.id+" invalid delta atomic")
 native_routes.append({"route_id":entry.id,"source_frames":oracle_route.frames.size(),"verified_video_ticks":ticks,"samples":samples,"scope":"Unmodified copied native OBJ runtime controller; complete captured clock/state/real Sprite2D property timeline, not new gameplay input or whole-screen BG effects"})
 player.queue_free();await process_frame
func run() -> void:
 for name in ["authored","native_walk","native_sword"]:
  var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://fixtures/%s/manifest.json" % name));var sf=build_frames(manifest,name);var path="res://fixtures/%s/checked.tres" % name
  check(ResourceSaver.save(sf,path)==OK,name+" resource save");sf=ResourceLoader.load(path,"SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE)
  for a in manifest.animations:
   var expected=oracle(manifest,a);var label=name+"/"+a.id
   await isolated_native_playback(sf,a,expected,label);await exact_track_test(sf,a,expected,label);await negative_track_tests(sf,a,expected,label);await negative_event_test(sf,a,expected,label)
 var index: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://capture-index.json"))
 for entry in index.routes:await native_route_test(entry)
 var failures=checks.filter(func(c):return not c.passed)
 var report={"passed":failures.is_empty(),"check_count":checks.size(),"failures":failures,"realtime_spriteframes":realtime,"deterministic_animationplayer":deterministic,"native_routes":native_routes,"negative_perturbations":negatives,"checks":checks,"limits":["AnimationPlayer track tests are named synthetic playback fixtures, not newly discovered native gameplay events.","Native capture actors/palettes/effect state are replayed as observed; no hit windows inferred from SpriteFrames.","No full-screen BG/color-math or all spell variants are newly rendered here."]}
 FileAccess.open("res://engine-timeline-report.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("ENGINE_TIMELINE_RESULT ",checks.size()," checks, failures=",failures.size());quit(0 if failures.is_empty()else 2)
