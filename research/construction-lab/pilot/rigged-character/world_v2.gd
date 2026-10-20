extends Control
# Original authored combat sandbox: physics, raster compensation and event clocks are separate.
var cache_path=""
var cache: Dictionary
var base=""
var source=""
var clips: Dictionary
var frames=SpriteFrames.new()
var textures={}
var boots={}
var rig: Node2D
var body: AnimatedSprite2D
var boot: Sprite2D
var effects: Node2D
var vp: SubViewport
var level: Node2D
var guides: Node2D
var label: Label
var equipment="inspection"
var charge_started=-1.0
var charged_damage=20
var clip="idle"
var view="right"
var scale_factor=1
var clock=0.0
var elapsed=0.0
var epoch=0
var physical_x=120.0
var physical_y=32.0
var camera_y=0.0
var visual_camera_y=0.0
var playback_speed=1.0
var camera=0.0
var visual_camera=0.0
var camera_mode="fixed"
var playing=true
var direction=0
var run_input=false
var health=100
var target_health=40
var target_x=300.0
var physical_target_y=142.0
var target_cleanup=-1.0
var target_visible=true
var projectiles=[]
var hits=[]
var events=[]
var transitions=[]
var state_log=[]
var event_keys={}
var observation={}
var debug_boot=""
var error=""
func hash_bytes(bytes: PackedByteArray) -> String:
 var h=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func configure(path: String) -> bool:
 cache_path=path;base=path.get_base_dir()
 if not FileAccess.file_exists(path):error="Missing measured cache. Run world_v2_cache.gd --output fresh-folder first.";return false
 cache=JSON.parse_string(FileAccess.get_file_as_string(path))
 if not cache is Dictionary or cache.get("schema")!="copper-scout-world-v2-cache/v2":error="Invalid world cache";return false
 source=cache.source
 var required=["rig.gd","rig_side.gd","design.json","clips.json"]
 if cache.source_bindings.keys().size()!=required.size():error="Missing/extra source binding";return false
 for name in required:
  if not cache.source_bindings.has(name):error="Missing source binding: "+name;return false
 for name in cache.source_bindings:
  if FileAccess.get_sha256(source.path_join(name))!=cache.source_bindings[name]:error="Stale source: "+name;return false
 if cache.renderer!=RenderingServer.get_video_adapter_name():error="Cache renderer differs";return false
 clips=JSON.parse_string(FileAccess.get_file_as_string(source.path_join("clips.json")))
 if cache.fps!=60 or clips.fps!=60 or cache.canvas.size()!=2 or cache.canvas[0]!=192 or cache.canvas[1]!=192:error="Source clock/canvas mismatch";return false
 var probe=load(source.path_join("rig.gd")).new();probe.configure(JSON.parse_string(FileAccess.get_file_as_string(source.path_join("design.json"))),clips)
 for binding in cache.clips:
  var c:Dictionary=cache.clips[binding];var name=c.get("base_clip",c.name)
  if not clips.clips.has(name)or not c.view in cache.views:error="Unknown binding";probe.free();return false
  var spec=clips.clips[name]
  if c.duration_ticks!=spec.duration_ticks or c.loop!=spec.loop or c.events!=spec.events:error="Duration/loop/event source mismatch";probe.free();return false
  probe.clear_equipment_selection()
  if c.get("equipment","inspection")!="inspection":probe.set_equipment(c.equipment)
  var first=probe.pose(name,0.0,c.view);var last=probe.pose(name,1.0,c.view)
  if first.has("error")or last.has("error"):error="Unsupported equipment binding";probe.free();return false
  var motion=Vector2(last.world_root[0]-first.world_root[0],last.world_root[1]-first.world_root[1])
  if Vector2(c.root_motion[0],c.root_motion[1]).distance_to(motion)>1e-12:error="Root motion source mismatch";probe.free();return false
 probe.free()
 for binding in cache.clips:
  var c: Dictionary=cache.clips[binding]
  frames.add_animation(binding);frames.set_animation_speed(binding,60);frames.set_animation_loop(binding,c.loop)
  textures[binding]=[];boots[binding]={"front":[],"rear":[]}
  for i in range(c.frames.size()):
   var row=c.frames[i]
   if row.tick!=i or c.frames.size()!=int(c.duration_ticks):error="Cache tick order";return false
   var image=Image.new()
   if image.load(base.path_join(row.file))!=OK or hash_bytes(image.get_data())!=row.pixel_sha256:error="Corrupt frame "+row.file;return false
   var texture=ImageTexture.create_from_image(image);textures[binding].append(texture);frames.add_frame(binding,texture,1.0)
   for side in ["front","rear"]:
    if row.boots.has(side):
     var b=Image.new()
     if b.load(base.path_join(row.boots[side]))!=OK or hash_bytes(b.get_data())!=row.boot_pixel_sha256[side]:error="Corrupt boot cache";return false
     var rect=b.get_used_rect();var measured=null
     if rect.has_area():
      var y=rect.end.y-1
      for x in range(rect.position.x,rect.end.x):
       if b.get_pixel(x,y).a>0:measured=[x,y];break
     if not row.sole_points.has(side):error="Missing sole point";return false
     var point=row.sole_points[side]
     if (measured==null and point!=null)or (measured!=null and (not point is Array or point.size()!=2 or point[0]!=measured[0]or point[1]!=measured[1])):error="Sole point disagrees boot pixels";return false
     boots[binding][side].append(ImageTexture.create_from_image(b))
 return true
func _ready() -> void:
 if cache_path.is_empty():
  var args=OS.get_cmdline_user_args()
  for i in range(args.size()):if args[i]=="--cache":cache_path=args[i+1]
 if not configure(cache_path):var warning=Label.new();warning.text=error;add_child(warning);return
 texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
 build_ui();reset(false)
 if cache.clips.has("idle_sword/right"):set_equipment("sword")
func add_button(parent: Node,title: String,call: Callable) -> void:
 var b=Button.new();b.text=title;b.pressed.connect(call);parent.add_child(b)
func build_ui() -> void:
 var panel=VBoxContainer.new();panel.position=Vector2(20,20);panel.add_theme_constant_override("separation",10);add_child(panel)
 var title=Label.new();title.text="COPPER SCOUT · ORIGINAL WORLD SANDBOX / source "+cache.source_bindings["clips.json"].left(12);panel.add_child(title)
 var bar=GridContainer.new();bar.columns=6;panel.add_child(bar)
 for item in [["Play / Pause",func():playing=not playing],["Replay",func():reset()],["+1 tick",func():playing=false;advance(1,true)],["Slash [X]",func():act("slash")],["Thrust [T]",func():act("thrust")],["Charge / release [Q]",func():release_charge()if clip=="charge"else act("charge")],["Shoot [Z]",func():act("shoot")],["Celebrate [B]",func():act("celebrate")],["Cast [C]",func():act("cast")],["Take hit [H]",func():take_hit(25)],["Knockdown [K]",func():take_hit(health)],["Recover [V]",func():act("recover",true)],["Respawn target",respawn_target]]:add_button(bar,item[0],item[1])
 var options=HBoxContainer.new();panel.add_child(options)
 var picker=OptionButton.new()
 for value in ["right","left","front","back"]:
  picker.add_item(value);picker.set_item_disabled(picker.item_count-1,not value in cache.views)
 picker.item_selected.connect(func(i):set_view(picker.get_item_text(i)));options.add_child(picker)
 var weapons=OptionButton.new()
 for value in ["sword","blaster","none"]:weapons.add_item(value)
 weapons.item_selected.connect(func(i):
  if not set_equipment(weapons.get_item_text(i)):weapons.select(["sword","blaster","none"].find(equipment)))
 options.add_child(weapons)
 var speeds=OptionButton.new()
 for value in [0.25,0.5,1.0,2.0]:speeds.add_item(str(value)+"× speed")
 speeds.select(2);speeds.item_selected.connect(func(i):set_speed([0.25,0.5,1.0,2.0][i]));options.add_child(speeds)
 var sizes=OptionButton.new()
 for value in [1,2,3]:sizes.add_item(str(value)+"× nearest")
 sizes.item_selected.connect(func(i):set_scale_factor(i+1));options.add_child(sizes)
 var cameras=OptionButton.new()
 for value in ["fixed","follow","scroll"]:cameras.add_item(value)
 cameras.item_selected.connect(func(i):camera_mode=cameras.get_item_text(i));options.add_child(cameras)
 var left=Button.new();left.text="← Walk";left.button_down.connect(func():set_movement(-1,false));left.button_up.connect(func():set_movement(0,false));options.add_child(left)
 var right=Button.new();right.text="Walk →";right.button_down.connect(func():set_movement(1,false));right.button_up.connect(func():set_movement(0,false));options.add_child(right)
 var run=CheckBox.new();run.text="Run [Shift]";run.toggled.connect(func(v):run_input=v;set_planar_movement(heading()*direction,v));options.add_child(run)
 var scroll=ScrollContainer.new();scroll.custom_minimum_size=Vector2(1100,580);panel.add_child(scroll)
 var container=SubViewportContainer.new();container.custom_minimum_size=Vector2(640,320);container.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;scroll.add_child(container)
 vp=SubViewport.new();vp.size=Vector2i(640,320);vp.transparent_bg=true;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;container.add_child(vp)
 level=Node2D.new();vp.add_child(level)
 guides=Node2D.new();guides.z_index=-10;level.add_child(guides);guides.draw.connect(draw_world)
 body=AnimatedSprite2D.new();body.centered=false;body.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;body.sprite_frames=frames;body.pause();level.add_child(body)
 boot=Sprite2D.new();boot.centered=false;boot.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;boot.visible=false;level.add_child(boot)
 rig=load(source.path_join("rig.gd")).new();add_child(rig);rig.configure(JSON.parse_string(FileAccess.get_file_as_string(source.path_join("design.json"))),clips);rig.visible=false
 effects=load("res://world_v2_effects.gd").new();level.add_child(effects)
 label=Label.new();panel.add_child(label)
 var note=Label.new();note.text="A/D or arrows + Shift · authored hitboxes and swept projectile collision · interrupts H/K, recovery V\nHard pose transitions (no deformation blend); physical root stays continuous. Rounded visual camera, per-view measured raster contacts.\nArrow/WASD four-view movement; sword/blaster selection persists through damage/recovery. Stow explicitly for cast/celebrate. This original combat is separate from animation markers and has no Mana gameplay claim.";panel.add_child(note)
func binding() -> String:
 var variant=clip+"_"+equipment+"/"+view
 return variant if equipment!="inspection"and cache.clips.has(variant)else clip+"/"+view
func set_equipment(value: String)->bool:
 if value not in ["inspection","none","sword","blaster"]or clip not in ["idle","walk","run"]:return false
 var before=binding();var frame=body.frame;equipment=value
 if value=="inspection":rig.clear_equipment_selection()
 else:rig.set_equipment(value)
 present();transitions.append({"tick":clock,"from_binding":before,"from_frame":frame,"to_binding":binding(),"to_frame":body.frame,"equipment":equipment,"policy":"Explicit selection/stow; preserve locomotion phase and physical root"});return true
func set_speed(value: float)->bool:
 if not is_finite(value)or value<=0 or value>4:return false
 playback_speed=value;return true
func release_charge()->bool:
 if clip!="charge":return false
 charged_damage=20+int(clampf(clock-charge_started,0,60)/3)
 return act("slash",true)
func set_scale_factor(value: int) -> bool:
 if not value in [1,2,3]:return false
 scale_factor=value;level.scale=Vector2(value,value);vp.size=Vector2i(640*value,320*value);vp.get_parent().custom_minimum_size=Vector2(640*value,320*value);return true
func set_view(value: String) -> bool:
 if not cache.clips.has(clip+"/"+value):return false
 view=value;present();return true
func set_state(name: String) -> bool:
 if not cache.clips.has(name+"/"+view):return false
 if equipment!="inspection"and not cache.clips.has(name+"_"+equipment+"/"+view)and cache.clips[name+"/"+view].frames[0].pose.get("effective_equipment","none")!=equipment:return false
 var required={"slash":"sword","thrust":"sword","charge":"sword","shoot":"blaster","cast":"none","celebrate":"none"}
 if equipment!="inspection"and required.has(name)and equipment!=required[name]:return false
 var previous=clip;var from_binding=binding();var from_frame=body.frame;clip=name;elapsed=0.0;epoch+=1;event_keys.clear()
 transitions.append({"tick":clock,"from":previous,"to":name,"physical_x":physical_x,"physical_y":physical_y,"from_binding":from_binding,"from_frame":from_frame,"to_binding":binding(),"to_frame":0,"equipment":equipment,"policy":"Hard cut / reset clip phase; no blend or hidden physical displacement"})
 dispatch(-0.0001,0.0,clock-0.0001,Vector2(physical_x,physical_y),Vector2.ZERO);present();return true
func set_movement(value: int,running: bool) -> bool:
 return set_planar_movement(Vector2(value,0),running)
func set_planar_movement(input: Vector2,running: bool) -> bool:
 var desired=view
 if input.x!=0:desired="left"if input.x<0 else"right"
 elif input.y!=0:desired="back"if input.y<0 else"front"
 if not cache.clips.has(("run"if running else"walk")+"/"+desired):return false
 direction=0 if input==Vector2.ZERO else 1;run_input=running
 if not clip in ["idle","walk","run"]:return false
 if desired!=view:set_view(desired)
 var desired_clip="idle"if direction==0 else("run"if running else"walk")
 if desired_clip!=clip:return set_state(desired_clip)
 return true
func act(name: String,force=false) -> bool:
 if not force and not clip in ["idle","walk","run"]:return false
 var previous_clip=clip
 if not set_state(name):return false
 direction=0
 if name=="charge":charge_started=clock
 elif name in ["slash","thrust"]and previous_clip!="charge":charged_damage=20
 elif name not in ["slash","thrust"]:charged_damage=20
 return true
func take_hit(amount: int) -> void:
 if amount<=0:return
 var before=health;health=maxi(0,health-amount)
 if not set_state("knockdown"if health==0 else"hurt"):health=before;return
 direction=0
func respawn_target() -> void:
 target_health=40;target_visible=true;target_cleanup=-1;var target=Vector2(physical_x+96,physical_y+110)+heading()*(84 if view in ["right","left"]else 48);target_x=target.x;physical_target_y=target.y
func reset(start=true) -> void:
 clock=0.0;elapsed=0.0;physical_x=120.0;camera=0.0;camera_y=0.0;visual_camera=0.0;visual_camera_y=0.0;physical_y=32.0;direction=0;health=100;charge_started=-1;charged_damage=20;epoch=0;events.clear();hits.clear();projectiles.clear();transitions.clear();state_log.clear();effects.reset();clip="idle";playing=start;respawn_target();set_state("idle")
func dispatch(before: float,after: float,global_before: float,physical_before: Vector2,velocity: Vector2) -> void:
 var c: Dictionary=cache.clips[binding()];var n=int(c.duration_ticks)
 for cycle in range(maxi(0,int(floor(before/n))),int(floor(after/n))+1):
  if cycle>0 and not c.loop:break
  for index in range(c.events.size()):
   var event=c.events[index];var at=cycle*n+int(event.tick);var key=str(epoch)+"/"+str(cycle)+"/"+str(index)
   if at<=before or at>after or event_keys.has(key):continue
   event_keys[key]=true;var born=global_before+(at-before);var birth_position=physical_before+velocity*(at-before);var x=birth_position.x;var y=birth_position.y
   var pose: Dictionary=c.frames[mini(int(event.tick),n-1)].pose.duplicate(true)
   for anchor in pose.fx_anchors:pose.fx_anchors[anchor][0]+=x;pose.fx_anchors[anchor][1]+=y
   pose.direction_vector=[heading().x,heading().y]
   effects.receive(key,event.type,born,pose)
   events.append({"token":key,"clip":clip,"view":view,"type":event.type,"tick":born,"physical_x":x,"physical_y":y})
   if event.type=="projectile_emit":projectiles.append({"token":key,"birth":born,"origin":pose.fx_anchors.muzzle,"heading":heading(),"ttl":30.0,"last_tick":born})
   if event.type in ["strike_pose","strike","thrust_pose","thrust"]:
    var center=Vector2(x+96,y+110)+heading()*(70 if view in ["right","left"]else 32)
    if target_visible and target_health>0 and Rect2(center-Vector2(16,21),Vector2(32,42)).intersects(target_rect()):damage_target(charged_damage,key,"slash",born);charged_damage=20
func damage_target(amount: int,token: String,kind: String,tick: float) -> void:
 target_health=maxi(0,target_health-amount);hits.append({"token":token,"kind":kind,"tick":tick,"amount":amount,"remaining_health":target_health})
 if target_health==0:target_cleanup=tick+30.0
func heading() -> Vector2:
 return {"right":Vector2.RIGHT,"left":Vector2.LEFT,"front":Vector2.DOWN,"back":Vector2.UP}[view]
func target_rect() -> Rect2:
 return Rect2(Vector2(target_x,physical_target_y)-Vector2(8,50),Vector2(16,100))if view in ["right","left"]else Rect2(Vector2(target_x,physical_target_y)-Vector2(24,24),Vector2(48,48))
func segment_entry(rectangle: Rect2,a: Array,b: Array)->float:
 var delta=[b[0]-a[0],b[1]-a[1]];var near=0.0;var far=1.0
 for axis in [0,1]:
  var start=a[axis];var motion=delta[axis];var low=rectangle.position[axis];var high=rectangle.end[axis]
  if absf(motion)<1e-15:
   if start<low or start>high:return -1.0
  else:
   var first=(low-start)/motion;var last=(high-start)/motion
   if first>last:var swap=first;first=last;last=swap
   near=maxf(near,first);far=minf(far,last)
   if near>far:return -1.0
 return near
func update_projectiles() -> void:
 var alive=[]
 for p in projectiles:
  var end=minf(clock,p.birth+p.ttl);var previous=[p.origin[0]+p.heading.x*(p.last_tick-p.birth)*2,p.origin[1]+p.heading.y*(p.last_tick-p.birth)*2];var current=[p.origin[0]+p.heading.x*(end-p.birth)*2,p.origin[1]+p.heading.y*(end-p.birth)*2]
  var rectangle=target_rect();var collided=false
  if target_visible and target_health>0:
   var expand=Rect2(rectangle.position-Vector2(2,2),rectangle.size+Vector2(4,4))
   var entry=segment_entry(expand,previous,current)
   if entry>=0:
    damage_target(12,p.token,"projectile",p.last_tick+(end-p.last_tick)*entry);collided=true
  p.last_tick=end
  if collided:effects.items=effects.items.filter(func(item):return not(item.type=="bolt"and item.birth==p.birth));effects.queue_redraw()
  if not collided and clock<p.birth+p.ttl:alive.append(p)
 projectiles=alive
 if target_cleanup>=0 and clock>=target_cleanup:target_visible=false
func advance(ticks: float,force=false) -> bool:
 if not is_finite(ticks)or ticks<0 or ticks>10000:return false
 if not playing and not force:return true
 var remain=ticks
 while remain>0:
  var c: Dictionary=cache.clips[binding()];var terminal_hold=clip=="knockdown"and elapsed>=c.duration_ticks;var slice=remain if c.loop or terminal_hold else minf(remain,float(c.duration_ticks)-elapsed)
  if slice<=0:break
  var velocity=Vector2(c.root_motion[0],c.root_motion[1])/float(c.duration_ticks)if clip in ["walk","run"]and direction!=0 else Vector2.ZERO
  var previous=elapsed;var physical_before=Vector2(physical_x,physical_y);var global_before=clock
  clock+=slice;elapsed=minf(elapsed+slice,float(c.duration_ticks))if terminal_hold else elapsed+slice;physical_x+=float(c.root_motion[0])/float(c.duration_ticks)*slice if clip in ["walk","run"]and direction!=0 else 0;physical_y+=float(c.root_motion[1])/float(c.duration_ticks)*slice if clip in ["walk","run"]and direction!=0 else 0
  for key in ["clock","elapsed"]:
   var value=clock if key=="clock"else elapsed;var rounded=round(value)
   if absf(value-rounded)<=1.0e-12*maxf(1.0,absf(value)):
    if key=="clock":clock=rounded
    else:elapsed=rounded
  if camera_mode=="scroll":camera+=0.37*slice;camera_y+=0.23*slice
  elif camera_mode=="follow":camera+=(physical_x+96-320-camera)*minf(1.0,slice/30.0);camera_y+=(physical_y+96-160-camera_y)*minf(1.0,slice/30.0)
  dispatch(previous,elapsed,global_before,physical_before,velocity);update_projectiles();effects.set_clock(clock);remain-=slice
  if not c.loop and elapsed>=c.duration_ticks:
   if clip=="knockdown":continue
   if clip=="recover":health=100
   set_state("idle")
 present();return true
func present() -> void:
 if not is_instance_valid(body):return
 var c: Dictionary=cache.clips[binding()];var n=int(c.duration_ticks);var local=fmod(elapsed,n)if c.loop else minf(elapsed,n-1);var held=int(floor(local))
 var phase=elapsed/n if c.loop else local/maxi(1,n-1);var meta: Dictionary=rig.pose(clip,phase,view)
 visual_camera=round(camera);visual_camera_y=round(camera_y);var physical=Vector2(physical_x,physical_y);var visual_cam=Vector2(visual_camera,visual_camera_y);var draw_position=physical.round()-visual_cam;var residuals={};var chosen=""
 if binding() in cache.offset_derivation:
  for side in ["front","rear"]:
   if meta.contact_flags[side]and c.frames[held].sole_points[side]!=null:
    chosen=side;var offset=cache.offset_derivation[binding()][side].offset;var foot=meta.feet[side];var desired=(physical+Vector2(foot[0],foot[1])+Vector2(offset[0],offset[1])+Vector2(0.0001,0.0001)).floor();var point=c.frames[held].sole_points[side]
    draw_position=desired-visual_cam-Vector2(point[0],point[1]);break
  for side in ["front","rear"]:
   if meta.contact_flags[side]and c.frames[held].sole_points[side]!=null:
    var offset=cache.offset_derivation[binding()][side].offset;var foot=meta.feet[side];var goal=(physical+Vector2(foot[0],foot[1])+Vector2(offset[0],offset[1])+Vector2(0.0001,0.0001)).floor();var point=c.frames[held].sole_points[side];var residual=draw_position+visual_cam+Vector2(point[0],point[1])-goal
    residuals[side]=[residual.x,residual.y]
 body.animation=binding();body.set_frame_and_progress(held,local-floor(local));body.pause();body.position=draw_position
 boot.visible=not debug_boot.is_empty();body.visible=not boot.visible
 if boot.visible:boot.texture=boots[binding()][debug_boot][held];boot.position=body.position
 effects.position=-visual_cam;guides.queue_redraw()
 observation={"clock":clock,"clip":clip,"view":view,"elapsed":elapsed,"held":held,"physical_x":physical_x,"physical_y":physical_y,"physical_camera":[camera,camera_y],"visual_camera":[visual_camera,visual_camera_y],"draw_x":draw_position.x,"draw_y":draw_position.y,"visual_child_offset":[draw_position.x+visual_camera-physical_x,draw_position.y+visual_camera_y-physical_y],"contact_flags":meta.contact_flags,"residuals":residuals,"health":health,"target_health":target_health,"projectile_count":projectiles.size(),"equipment":equipment,"binding":binding(),"charge_damage":charged_damage,"source_hash":cache.source_bindings["clips.json"]}
 label.text="%s / %s / %s · clock %.3f pose %.3f · physical XY (%.2f,%.2f) · draw XY (%.0f,%.0f) · HP %d / target %d"%[clip,view,equipment,clock,elapsed,physical_x,physical_y,draw_position.x,draw_position.y,health,target_health]
func draw_world() -> void:
 guides.draw_rect(Rect2(0,0,640,320),Color("25303a"))
 for x in range(-600,1600,32):guides.draw_line(Vector2(x-visual_camera,0),Vector2(x-visual_camera,320),Color("344650"),1)
 for y in range(-600,1600,32):guides.draw_line(Vector2(0,y-visual_camera_y),Vector2(640,y-visual_camera_y),Color("344650"),1)
 if view in ["right","left"]:
  var boundary=physical_y+170-visual_camera_y
  guides.draw_line(Vector2(0,boundary),Vector2(640,boundary),Color("829695"),1)
 if target_visible:guides.draw_rect(Rect2(target_rect().position-Vector2(visual_camera,visual_camera_y),target_rect().size),Color("cb7953")if target_health>0 else Color("54545a"))
func _process(dt: float) -> void:
 if error.is_empty()and is_instance_valid(body):advance(dt*60*playback_speed)
func _unhandled_key_input(event: InputEvent) -> void:
 if not event is InputEventKey or event.echo:return
 if event.pressed:
  match event.keycode:
   KEY_X:act("slash")
   KEY_T:act("thrust")
   KEY_Q:act("charge")
   KEY_B:act("celebrate")
   KEY_Z:act("shoot")
   KEY_C:act("cast")
   KEY_H:take_hit(25)
   KEY_K:take_hit(health)
   KEY_V:act("recover",true)
   KEY_R:reset()
   KEY_SPACE:playing=not playing
 if not event.pressed and event.keycode==KEY_Q:release_charge()
 if event.keycode in [KEY_LEFT,KEY_RIGHT,KEY_UP,KEY_DOWN,KEY_A,KEY_D,KEY_W,KEY_S,KEY_SHIFT]:
  var move=int(Input.is_key_pressed(KEY_RIGHT)or Input.is_key_pressed(KEY_D))-int(Input.is_key_pressed(KEY_LEFT)or Input.is_key_pressed(KEY_A));var depth=int(Input.is_key_pressed(KEY_DOWN)or Input.is_key_pressed(KEY_S))-int(Input.is_key_pressed(KEY_UP)or Input.is_key_pressed(KEY_W));set_planar_movement(Vector2(move,depth),Input.is_key_pressed(KEY_SHIFT))
