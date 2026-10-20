extends SceneTree
const Pack=preload("res://pack.gd")
var path=""
var out=""
var checks=[]
var observations=[]
func _initialize()->void:
 Engine.max_fps=0
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--manifest":path=args[i+1]
  if args[i]=="--output":out=args[i+1]
 call_deferred("run")
func check(ok:bool,text:String)->void:checks.append({"passed":ok,"description":text})
func rgba_sha(im:Image)->String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(im.get_data());return h.finish().hex_encode()
func render(vp:SubViewport)->Image:
 await process_frame;await RenderingServer.frame_post_draw;return vp.get_texture().get_image()
func composite(source:Image,bg:Color)->Image:
 var im=Image.create(160,160,false,Image.FORMAT_RGBA8)
 for y in range(160):
  for x in range(160):
   var c=source.get_pixel(x,y);im.set_pixel(x,y,Color(c.r*c.a+bg.r*(1-c.a),c.g*c.a+bg.g*(1-c.a),c.b*c.a+bg.b*(1-c.a),1))
 return im
func diff(a:Image,b:Image)->Dictionary:
 var ad=a.get_data();var bd=b.get_data();var maximum=0;var count=0
 for i in range(ad.size()):
  var d=absi(int(ad[i])-int(bd[i]));maximum=maxi(maximum,d)
  if d>1:count+=1
 return {"max_channel_error":maximum,"channels_over_one_lsb":count}
func run()->void:
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var pack=Pack.read_pack(path)
 if pack.has("error"):push_error(pack.error);quit(2);return
 check(pack.frames.get_animation_speed("front")==9.6,"Real SpriteFrames noninteger 9.6poses/s")
 var filename=out.path_join("walk-frames.res");check(ResourceSaver.save(pack.frames,filename)==OK,"Save actual SpriteFrames resource")
 var reopened=ResourceLoader.load(filename,"SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE)
 check(reopened is SpriteFrames,"Reopen actual SpriteFrames resource")
 for v in ["front","right","back","left"]:
  check(reopened.get_frame_count(v)==12 and reopened.get_animation_loop(v)and reopened.get_animation_speed(v)==9.6,"Reopened exact timing/loop "+v)
  for i in range(12):check(rgba_sha(reopened.get_frame_texture(v,i).get_image())==rgba_sha(pack.images[v][i]),"Reopened160RGBA "+v+str(i))
 var vp=SubViewport.new();vp.size=Vector2i(160,160);vp.disable_3d=true;vp.transparent_bg=false;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(vp)
 var bg=Polygon2D.new();bg.polygon=PackedVector2Array([Vector2.ZERO,Vector2(160,0),Vector2(160,160),Vector2(0,160)]);vp.add_child(bg)
 var body=AnimatedSprite2D.new();body.sprite_frames=reopened;body.centered=false;body.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;vp.add_child(body)
 for background in [Color8(61,70,82),Color8(196,201,208)]:
  bg.color=background
  for v in ["front","right","back","left"]:
   body.animation=v;body.pause()
   for i in range(12):
    body.set_frame_and_progress(i,0);var actual=await render(vp);var expected=composite(pack.images[v][i],background);var result=diff(actual,expected)
    result.view=v;result.pose=i;result.background=[background.r8,background.g8,background.b8];result.gpu_rgba_sha256=rgba_sha(actual);result.reference_rgba_sha256=rgba_sha(expected);observations.append(result)
    check(result.channels_over_one_lsb==0,"GPU softalpha reference composite "+v+str(i)+str(result.background))
    if i in [0,3,6,9]:actual.save_png(out.path_join("neutral-"+str(background.r8)+"-"+v+"-"+str(i)+".png"))
 var world=load("res://audition.gd").new();world.manifest_path=path;root.add_child(world);world.set_process(false)
 check(world.error.is_empty(),"Playable scene loads same final pack")
 world.grid_enabled=false;world.present()
 for v in ["front","right","back","left"]:
  world.view=v;world.clock_seconds=0;world.present()
  for i in range(12):
   world.clock_seconds=i*2.5/24.0;world.present();check(world.sprite.frame==i,"Exact continuous hold start "+v+str(i))
   world.clock_seconds=(i+1)*2.5/24.0-1e-8;world.present();check(world.sprite.frame==i,"True preboundary stays previous "+v+str(i))
  world.clock_seconds=1.25;world.present();check(world.sprite.frame==0,"Exact1.25second loop "+v)
 world.clock_seconds=0;world.playing=true
 for d in [0.031,0.177,0.007,1.033,0.002]:world.advance_seconds(d)
 check(absf(world.clock_seconds-1.25)<1e-12 and world.sprite.frame==0,"Variable-rate update partitions preserve exact loop")
 world.clock_seconds=0.11;world.present();world.playing=false;var before=world.clock_seconds;world.advance_seconds(0.4);check(world.clock_seconds==before and world.sprite.frame==1,"Pause holds scalarclock and pose")
 world.playing=true;world.advance_seconds(0.03);check(absf(world.clock_seconds-0.14)<1e-12 and world.sprite.frame==1,"Resume retains fraction")
 world.clock_seconds=0;world.present();check(world.sprite.frame==0,"Replay phase0")
 world.clock_seconds=0;world.advance_seconds(12.6);check(world.sprite.frame==0 and absf(world.clock_seconds-12.6)<1e-12,"Low-rate many-loop advance preserves noninteger hold")
 before=world.clock_seconds;check(not world.advance_seconds(-1)and not world.advance_seconds(INF)and world.clock_seconds==before,"Invalid dt leavesclock unchanged")
 world.camera_mode="follow";world.physical=Vector2(333,225);world.present();check(world.camera==Vector2(93,55),"Follow camera retains physical/view origin")
 world.playing=false;world.view="front";world.clock_seconds=0;world.physical=Vector2(240,200);world.camera_mode="fixed";world.present();await render(world.vp);root.get_texture().get_image().save_png(out.path_join("audition-ui.png"))
 var display_node:TextureRect
 for child in world.get_children():
  if child is VBoxContainer:
   for control in child.get_children():
    if control is TextureRect:display_node=control
 world.physical=Vector2(240,170);world.camera_mode="fixed"
 # Native and integer zoom use the same complete soft-alpha texture, no per-frame fitting.
 for zoom in [1,2,3]:
  world.scale_factor=zoom;world.scene.scale=Vector2.ONE*zoom;world.vp.size=Vector2i(480*zoom,240*zoom)
  for v in ["front","right","back","left"]:
   world.view=v;world.clock_seconds=3*pack.interval_seconds;world.present()
   var screen=await render(world.vp);var tile=screen.get_region(Rect2i(Vector2i(world.sprite.position*zoom),Vector2i(160,160)*zoom));tile.resize(160,160,Image.INTERPOLATE_NEAREST)
   check(diff(tile,composite(pack.images[v][3],Color8(61,70,82))).channels_over_one_lsb==0,"Actual fixed-origin nearest zoom "+v+str(zoom))
   await render(world.vp)
   var used=pack.images[v][3].get_used_rect();var centered=(display_node.size-Vector2(world.vp.size))*0.5
   var position=display_node.global_position+centered+world.sprite.position*zoom+Vector2(used.position*zoom)
   var ui_tile=root.get_texture().get_image().get_region(Rect2i(Vector2i(position.round()),used.size*zoom))
   var ui_expected=composite(pack.images[v][3],Color8(61,70,82)).get_region(used);ui_expected.resize(used.size.x*zoom,used.size.y*zoom,Image.INTERPOLATE_NEAREST)
   var ui_diff=diff(ui_tile,ui_expected)
   if ui_diff.channels_over_one_lsb>0:
    ui_tile.save_png(out.path_join("ui-actual-"+v+str(zoom)+".png"));ui_expected.save_png(out.path_join("ui-expected-"+v+str(zoom)+".png"));root.get_texture().get_image().save_png(out.path_join("ui-screen-"+v+str(zoom)+".png"));print("UI_DIFF ",v,zoom," ",ui_diff," rect ",position," used ",used," display ",display_node.size)
   check(diff(ui_tile,ui_expected).channels_over_one_lsb==0,"Actual visible UI nearest pixel size "+v+str(zoom))
 # A deliberate texture-order corruption must fail the same GPU oracle used above.
 bg.color=Color8(61,70,82);body.animation="front";body.pause()
 var original=reopened.get_frame_texture("front",0);reopened.set_frame("front",0,reopened.get_frame_texture("front",1),1);body.set_frame_and_progress(0,0)
 var corrupted=await render(vp);check(diff(corrupted,composite(pack.images.front[0],bg.color)).channels_over_one_lsb>0,"Negative swapped actual resource pose detected by GPU reference");reopened.set_frame("front",0,original,1)
 reopened.set_frame("front",0,original,2);check(not Pack.resource_contract(reopened).is_empty(),"Negative mutated resource hold rejects");reopened.set_frame("front",0,original,1);check(Pack.resource_contract(reopened).is_empty(),"Restored exact resource timeline")
 var old_interval=world.pack.interval_seconds;world.pack.interval_seconds=0.1;world.clock_seconds=0.102;world.present();check(world.sprite.frame!=0,"Negative fast clock crosses a genuine early boundary");world.pack.interval_seconds=old_interval
 var wrong=pack.manifest.duplicate(true);wrong.source_fps=30;wrong.cycle_seconds=1.0
 var negative_dir=out.path_join("negative");DirAccess.make_dir_recursive_absolute(negative_dir);var bad_path=negative_dir.path_join("wrong-clock.json");FileAccess.open(bad_path,FileAccess.WRITE).store_string(JSON.stringify(wrong));var rejected=Pack.read_pack(bad_path)
 check(rejected.get("error","")=="Expected corrected24fps,30sourceframes,1.25second cycle","Negative30fps/1second rejects specifically at clock contract")
 # Actual keyboard state travels through Godot Input; movement is independent of pose count.
 world.scale_factor=2;world.scene.scale=Vector2.ONE*2;world.vp.size=Vector2i(960,480);world.clock_seconds=0;world.physical=Vector2(240,200);world.playing=true;world.present()
 var key=InputEventKey.new();key.keycode=KEY_D;key.physical_keycode=KEY_D;key.pressed=true;Input.parse_input_event(key);await process_frame;world._process(0.25)
 check(world.physical==Vector2(252,200)and world.view=="right"and absf(world.clock_seconds-0.25)<1e-12,"Actual WASD keyboard movement, direction and continuous clock")
 key.pressed=false;Input.parse_input_event(key);await process_frame
 var buttons=[]
 for child in world.get_children():
  if child is VBoxContainer:
   for row in child.get_children():
    if row is HBoxContainer:
     for control in row.get_children():
      if control is Button and not control is OptionButton and not control is CheckBox:buttons.append(control)
 check(buttons.size()==3,"Actual local playback controls exist")
 var pause_button=buttons[0];var mouse=InputEventMouseButton.new();mouse.position=pause_button.get_global_rect().get_center();mouse.global_position=mouse.position;mouse.button_index=MOUSE_BUTTON_LEFT;mouse.pressed=true;Input.parse_input_event(mouse);await process_frame
 mouse.pressed=false;Input.parse_input_event(mouse);await process_frame;check(not world.playing,"Actual mouse pause button dispatch")
 buttons[2].emit_signal("pressed");check(not world.playing and absf(world.clock_seconds-3*pack.interval_seconds)<1e-12,"Step advances one source pose while paused")
 buttons[1].emit_signal("pressed");check(world.playing and world.clock_seconds==0 and world.sprite.frame==0,"Replay control clears phase and resumes")
 world.playing=false;world.view="front";world.physical=Vector2(240,170);world.present();await render(world.vp);root.get_texture().get_image().save_png(out.path_join("audition-ui.png"))
 for child in world.get_children():
  if child is VBoxContainer:
   for control in child.get_children():
    if control is TextureRect:check(control.stretch_mode==TextureRect.STRETCH_KEEP_CENTERED and control.clip_contents,"UI does not rescale native integer viewport")
 # Actual four-direction movement snapshots, fixed and follow, preserve source origin.
 for mode in ["fixed","follow"]:
  for v in ["front","right","back","left"]:
   world.playing=true;world.clock_seconds=0;world.physical=Vector2(240,170);world.camera_mode=mode;world.view=v;world.grid_enabled=true;world.present()
   world.sprite.visible=false;var grid_before=rgba_sha(await render(world.vp));world.sprite.visible=true
   var movement_key=InputEventKey.new();movement_key.keycode={"front":KEY_S,"right":KEY_D,"back":KEY_W,"left":KEY_A}[v];movement_key.physical_keycode=movement_key.keycode;movement_key.pressed=true;Input.parse_input_event(movement_key);await process_frame
   for i in range(6):world._process(0.1)
   movement_key.pressed=false;Input.parse_input_event(movement_key);await process_frame
   var delta={"front":Vector2.DOWN,"right":Vector2.RIGHT,"back":Vector2.UP,"left":Vector2.LEFT}[v]*28.8
   check(world.physical.distance_to(Vector2(240,170)+delta)<0.0001 and world.view==v and absf(world.clock_seconds-0.6)<1e-12,"Actual moving keyboard state "+v+mode)
   world.sprite.visible=false;var grid_after=rgba_sha(await render(world.vp));world.sprite.visible=true
   check(grid_before==grid_after if mode=="fixed"else grid_before!=grid_after,"Actual world grid reference under camera "+v+mode)
   await render(world.vp);await render(world.vp);root.get_texture().get_image().save_png(out.path_join("movement-"+mode+"-"+v+".png"))
 var failed=checks.filter(func(c):return not c.passed)
 var report={"schema":"model-sprite-godot-audition-proof/v1","passed":failed.is_empty(),"checks":checks,"failures":failed,"gpu_composites":observations,"manifest_sha256":pack.manifest_sha256,"landmarks_sha256":pack.landmarks_sha256,"resource_sha256":FileAccess.get_sha256(filename),"sourceclock":{"source_fps":24,"source_interval_frames":2.5,"pose_seconds":2.5/24,"simulation_ticks60_per_pose":6.25,"loop_seconds":1.25},"godot":Engine.get_version_info(),"renderer":RenderingServer.get_video_adapter_name(),"code_sha256":{"pack.gd":FileAccess.get_sha256("res://pack.gd"),"audition.gd":FileAccess.get_sha256("res://audition.gd"),"test_runtime.gd":FileAccess.get_sha256("res://test_runtime.gd"),"world_grid.gd":FileAccess.get_sha256("res://world_grid.gd")},"limits":["Neutral opaque compositing tolerance is at most1LSB perchannel; softalpha is not binaryalpha.","Movement speed48px/s is an audition setting, not an evaluated stance/contact/rootmotion contract.","Foot control projections are not presumed toe/sole landmarks or plantedcontact.","Mechanical proof does not approve the final art; no humancontinuous-playback claim."]}
 FileAccess.open(out.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("MODEL_GODOT ",checks.size()," failures ",failed.size());quit(0 if failed.is_empty()else 2)
