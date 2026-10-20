extends Control
const Pack=preload("res://pack.gd")
var manifest_path=""
var pack={}
var error=""
var vp:SubViewport
var sprite:AnimatedSprite2D
var scene:Node2D
var label:Label
var direction_picker:OptionButton
var zoom_picker:OptionButton
var camera_picker:OptionButton
var grid_checkbox:CheckBox
var world_grid:Node2D
var grid_enabled=true
var clock_seconds=0.0
var playing=true
var view="front"
var scale_factor=2
var physical=Vector2(240,170)
var camera_mode="fixed"
var camera=Vector2.ZERO
var speed_px=48.0
var sample_index=0
func _ready()->void:
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--manifest":manifest_path=args[i+1]
 if manifest_path.is_empty():error="Launch with --manifest /absolute/final-pack/manifest.json";push_error(error);return
 if not configure(manifest_path):push_error(error);return
 build_ui();present()
func configure(path:String)->bool:
 pack=Pack.read_pack(path)
 if pack.has("error"):error=pack.error;return false
 manifest_path=path
 vp=SubViewport.new();vp.size=Vector2i(480*scale_factor,240*scale_factor);vp.disable_3d=true;vp.transparent_bg=false;vp.render_target_update_mode=SubViewport.UPDATE_ALWAYS;add_child(vp)
 scene=Node2D.new();scene.scale=Vector2.ONE*scale_factor;vp.add_child(scene)
 var background=Polygon2D.new();background.polygon=PackedVector2Array([Vector2(-2000,-2000),Vector2(2000,-2000),Vector2(2000,2000),Vector2(-2000,2000)]);background.color=Color8(61,70,82,255);scene.add_child(background)
 world_grid=preload("res://world_grid.gd").new();scene.add_child(world_grid)
 sprite=AnimatedSprite2D.new();sprite.sprite_frames=pack.frames;sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;scene.add_child(sprite)
 return true
func build_ui()->void:
 var panel=VBoxContainer.new();panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);add_child(panel)
 var title=Label.new();title.text="Licensed Ranger walk | 24 sourcefps | 12 poses / 1.25s | local audition";panel.add_child(title)
 var controls=HBoxContainer.new();panel.add_child(controls)
 for text in ["Play/Pause","Replay","Next pose"]:
  var b=Button.new();b.text=text;controls.add_child(b)
  b.pressed.connect(func():
   if text=="Play/Pause":playing=not playing
   elif text=="Replay":clock_seconds=0.0;playing=true;present()
   else:playing=false;clock_seconds=(floor(clock_seconds/pack.interval_seconds)+1)*pack.interval_seconds;present())
 var dirs=OptionButton.new();direction_picker=dirs
 for d in ["front","right","back","left"]:dirs.add_item(d)
 controls.add_child(dirs);dirs.item_selected.connect(func(i):view=dirs.get_item_text(i);present())
 var zoom=OptionButton.new();zoom_picker=zoom
 for n in [1,2,3]:zoom.add_item(str(n)+"x")
 zoom.select(1);controls.add_child(zoom);zoom.item_selected.connect(func(i):scale_factor=i+1;scene.scale=Vector2.ONE*scale_factor;vp.size=Vector2i(480*scale_factor,240*scale_factor);present())
 var cam=OptionButton.new();camera_picker=cam;cam.add_item("fixed camera");cam.add_item("follow camera");controls.add_child(cam);cam.item_selected.connect(func(i):camera_mode="fixed"if i==0 else"follow";present())
 grid_checkbox=CheckBox.new();grid_checkbox.text="World grid";grid_checkbox.button_pressed=true;controls.add_child(grid_checkbox);grid_checkbox.toggled.connect(func(value):grid_enabled=value;present())
 var display=TextureRect.new();display.texture=vp.get_texture();display.custom_minimum_size=Vector2(960,480);display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;display.stretch_mode=TextureRect.STRETCH_KEEP_CENTERED;display.clip_contents=true;display.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;panel.add_child(display)
 label=Label.new();panel.add_child(label)
 var limits=Label.new();limits.text="WASD/arrows move; Space pause; R replay. Translation speed is an audition choice, not measured stance contact.";panel.add_child(limits)
func _unhandled_key_input(event:InputEvent)->void:
 if event is InputEventKey and event.pressed and not event.echo:
  if event.keycode==KEY_SPACE:playing=not playing
  if event.keycode==KEY_R:clock_seconds=0;playing=true;present()
func _process(dt:float)->void:
 if pack.is_empty()or pack.has("error"):return
 var move=Vector2(float(Input.is_key_pressed(KEY_D)or Input.is_key_pressed(KEY_RIGHT))-float(Input.is_key_pressed(KEY_A)or Input.is_key_pressed(KEY_LEFT)),float(Input.is_key_pressed(KEY_S)or Input.is_key_pressed(KEY_DOWN))-float(Input.is_key_pressed(KEY_W)or Input.is_key_pressed(KEY_UP)))
 if playing and move!=Vector2.ZERO:
  physical+=move.normalized()*speed_px*dt
  if absf(move.x)>absf(move.y):view="right"if move.x>0 else"left"
  else:view="front"if move.y>0 else"back"
 advance_seconds(dt)
func advance_seconds(dt:float)->bool:
 if not is_finite(dt)or dt<0 or dt>100:return false
 if playing:clock_seconds+=dt
 present();return true
func present()->void:
 if not is_instance_valid(sprite):return
 var elapsed=clock_seconds/pack.interval_seconds;var near=round(elapsed)
 if absf(elapsed-near)<=1e-12*maxf(1.0,absf(elapsed)):elapsed=near
 sample_index=int(floor(elapsed))%12
 sprite.animation=view;sprite.pause();sprite.set_frame_and_progress(sample_index,elapsed-floor(elapsed))
 camera=physical-Vector2(240,170)if camera_mode=="follow"else Vector2.ZERO
 var origin=pack.origins[view]
 sprite.position=(physical-camera-Vector2(origin[0],origin[1])).round()
 world_grid.visible=grid_enabled;world_grid.position=-camera.round()
 if is_instance_valid(grid_checkbox):grid_checkbox.set_pressed_no_signal(grid_enabled)
 if is_instance_valid(direction_picker):direction_picker.select(["front","right","back","left"].find(view))
 if is_instance_valid(zoom_picker):zoom_picker.select(scale_factor-1)
 if is_instance_valid(camera_picker):camera_picker.select(0 if camera_mode=="fixed"else 1)
 if is_instance_valid(label):label.text="View %s | pose %d | clock %.6fs | physical %s | camera %s"%[view,sample_index,clock_seconds,str(physical),str(camera)]
