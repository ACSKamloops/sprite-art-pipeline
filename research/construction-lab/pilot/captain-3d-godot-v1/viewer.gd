extends Node2D
var pack:Dictionary={}
var sprite=AnimatedSprite2D.new()
var status=Label.new()
var clock_seconds=0.0
var playing=true
var half_speed=false
var zoom=1
var mode="continuous"
var grid_enabled=true
var silhouette=false
var silhouette_material=ShaderMaterial.new()
var follow_camera=true
var camera_scroll=Vector2.ZERO
var origin=Vector2(416,80)
var error=""
var chosen=""

func _ready()->void:
    RenderingServer.set_default_clear_color(Color8(35,42,47))
    var args=OS.get_cmdline_user_args()
    for i in range(args.size()-1):
        if args[i]=="--pack":chosen=args[i+1]
    if chosen.is_empty():
        var available=DirAccess.get_directories_at("res://packs")
        if not available.is_empty():chosen=available[0]
    var path="res://packs/"+chosen
    if not FileAccess.file_exists(path+"/pack.json"):
        error="No frozen pack; run prepare_pack.py and build_resources.gd first."
    else:
        pack=JSON.parse_string(FileAccess.get_file_as_string(path+"/pack.json"))
        mode=pack.get("default_visual_root_policy","continuous")
        sprite.sprite_frames=load(path+"/walk.res")
        if sprite.sprite_frames==null:error="Missing imported SpriteFrames"
    sprite.centered=false;sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
    var shader=Shader.new()
    shader.code="shader_type canvas_item; void fragment(){vec4 p=texture(TEXTURE,UV); COLOR=vec4(vec3(0.91),p.a);}"
    silhouette_material.shader=shader
    add_child(sprite);sprite.animation="walk";sprite.pause()
    status.position=Vector2(12,8);status.add_theme_font_size_override("font_size",17);add_child(status)
    present()

func project(vector:Vector3)->Vector2:
    var c=pack.camera
    var right=Vector3(c[0][0],c[1][0],c[2][0]);var up=Vector3(c[0][1],c[1][1],c[2][1])
    return Vector2(right.dot(vector),-up.dot(vector))*float(pack.pixels_per_metre)
func ground(point:Vector3)->Vector2:
    var c=pack.camera;var camera=Vector3(c[0][3],c[1][3],c[2][3])
    return Vector2(pack.canvas[0],pack.canvas[1])*0.5+project(point-camera)
func root_vector(index:int)->Vector3:
    var p=pack.root_samples[index];return Vector3(p[0],p[1],p[2])
func sampled_state(seconds:float)->Dictionary:
    var tick=seconds*60.0
    # Correct tiny float errors exactly at declared integer tick boundaries.
    if absf(tick-round(tick))<1e-10:tick=round(tick)
    var whole=int(floor(tick));var cycle=whole/65;var index=whole%65;var fraction=tick-floor(tick)
    var delta=root_vector(index)
    if mode=="continuous":delta=delta.lerp(root_vector(index+1),fraction)
    delta+=root_vector(65)*cycle
    if mode=="inplace":delta=Vector3.ZERO
    return {"index":index,"fraction":fraction,"cycle":cycle,"root":delta,"screen":project(delta)}
func present()->void:
    if not error.is_empty():status.text=error;return
    var state=sampled_state(clock_seconds)
    sprite.set_frame_and_progress(state.index,state.fraction)
    sprite.scale=Vector2.ONE*zoom
    camera_scroll=state.screen*zoom if follow_camera else Vector2.ZERO
    sprite.position=(origin+state.screen*zoom-camera_scroll).round()
    sprite.material=silhouette_material if silhouette else null
    status.text="UNAPPROVED %s | cel %02d | %s | %dx\nSpace pause · R replay · arrows step · H half speed · M root mode · F follow camera · Z zoom · G grid · V silhouette\nSingle view; root/cel timing and actual appearance need separate acceptance."%[chosen,state.index,mode,zoom]
    queue_redraw()
func advance_seconds(delta:float)->bool:
    if not is_finite(delta)or delta<0:return false
    if playing:clock_seconds+=delta*(0.5 if half_speed else 1.0)
    present();return true
func _process(delta:float)->void:advance_seconds(delta)
func _unhandled_key_input(event:InputEvent)->void:
    if not event is InputEventKey or not event.pressed or event.echo:return
    match event.keycode:
        KEY_SPACE:playing=not playing
        KEY_R:clock_seconds=0;playing=true
        KEY_LEFT:playing=false;clock_seconds=maxf(0,(floor(clock_seconds*60)-1)/60.0)
        KEY_RIGHT:playing=false;clock_seconds=(floor(clock_seconds*60)+1)/60.0
        KEY_H:half_speed=not half_speed
        KEY_Z:zoom=3-zoom
        KEY_G:grid_enabled=not grid_enabled
        KEY_V:silhouette=not silhouette
        KEY_F:follow_camera=not follow_camera
        KEY_M:mode={"continuous":"synchronized","synchronized":"inplace","inplace":"continuous"}[mode]
    present()
func _draw()->void:
    if error.is_empty()and not pack.is_empty()and grid_enabled:
        for n in range(-48,49):
            var value=n*0.25;var color=Color8(79,89,93)if n%4==0 else Color8(52,62,67)
            draw_line(origin+ground(Vector3(value,-12,-1))*zoom-camera_scroll,origin+ground(Vector3(value,12,-1))*zoom-camera_scroll,color)
            draw_line(origin+ground(Vector3(-12,value,-1))*zoom-camera_scroll,origin+ground(Vector3(12,value,-1))*zoom-camera_scroll,color)
