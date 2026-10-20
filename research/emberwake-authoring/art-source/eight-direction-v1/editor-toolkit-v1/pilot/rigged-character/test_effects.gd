extends SceneTree
var checks: Array=[]
var viewport: SubViewport
var effects
var out_dir: String
func check(name: String, value: bool) -> void:
    checks.append({"name":name,"passed":value})
func capture() -> Image:
    await process_frame;await RenderingServer.frame_post_draw
    return viewport.get_texture().get_image()
func _initialize() -> void:
    Engine.max_fps=0;call_deferred("run")
func run() -> void:
    var args=OS.get_cmdline_user_args()
    if args.size()!=1:push_error("Provide one fresh output directory");quit(2);return
    out_dir=args[0]
    if DirAccess.dir_exists_absolute(out_dir):push_error("Preserve earlier effects evidence; output must be fresh");quit(2);return
    DirAccess.make_dir_recursive_absolute(out_dir)
    viewport=SubViewport.new();viewport.size=Vector2i(512,192);viewport.transparent_bg=true;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
    var script_path=get_script().resource_path.get_base_dir().path_join("effects.gd")
    effects=load(script_path).new();viewport.add_child(effects)
    var pose={"mirrored":false,"fx_anchors":{"muzzle":[140,90],"cast":[130,80],"charge":[112,95]}}
    check("projectile_emit_once",effects.receive("shot-0","projectile_emit",18,pose))
    check("duplicate_emit_rejected",not effects.receive("shot-0","projectile_emit",18,pose))
    check("unknown_hook_no_spawn",not effects.receive("ignored","strike_pose",0,pose))
    effects.set_clock(18)
    check("flash_and_bolt_separate",effects.snapshot().live_count==2)
    var first=await capture();first.save_png(out_dir.path_join("emit.png"))
    var paused=await capture();check("paused_pixels_unchanged",first.get_data()==paused.get_data())
    effects.set_clock(24);check("flash_expires_exactly_at_six_ticks",effects.snapshot().live_count==1)
    var moved=await capture();moved.save_png(out_dir.path_join("bolt-after-six-ticks.png"));check("projectile_moves",moved.get_data()!=first.get_data())
    effects.set_clock(48);check("projectile_expires_at_thirty_ticks",effects.snapshot().live_count==0)
    check("backward_clock_requires_reset",not effects.set_clock(10))
    effects.reset();check("replay_clears_tokens_items_and_clock",effects.snapshot().received_count==0 and effects.snapshot().live_count==0 and effects.clock==0)
    check("replay_can_emit_same_token",effects.receive("shot-0","projectile_emit",18,pose));effects.set_clock(18)
    var replayed=await capture();check("replay_pixels_exact",replayed.get_data()==first.get_data())
    effects.reset();effects.receive("late-shot","projectile_emit",18,pose);effects.set_clock(100)
    check("low_rate_late_event_does_not_create_fresh_ghost_projectile",effects.snapshot().live_count==0 and effects.snapshot().received_count==1)
    effects.reset();effects.receive("cast","cast_emit",29,pose);effects.set_clock(40)
    var cast=await capture();cast.save_png(out_dir.path_join("cast-eleven-ticks.png"));check("cast_visible_after_emit",effects.snapshot().live_count==1)
    effects.set_clock(53);check("cast_expires_at_twenty_four_ticks",effects.snapshot().live_count==0)
    effects.reset();effects.receive("charge","charge_begin",0,pose);effects.receive("ready","charge_ready",60,pose);effects.set_clock(60)
    var ready=await capture();ready.save_png(out_dir.path_join("charge-ready.png"));check("charge_then_ready_have_independent_lifetimes",effects.snapshot().live_count==1)
    effects.set_clock(72);check("charge_ready_cleanup",effects.snapshot().live_count==0)
    effects.reset();var left=pose.duplicate(true);left.mirrored=true;effects.receive("left","projectile_emit",0,left);effects.set_clock(6)
    var left_image=await capture();left_image.save_png(out_dir.path_join("mirrored-bolt.png"));check("mirrored_projectile_moves_left",float(effects.snapshot().history[0].direction)==-1.0)
    var passed=true
    for entry in checks:
        if not entry.passed:passed=false
    var report={"schema":"copper-scout-effects-proof/v1","passed":passed,"checks":checks,"effects_source_sha256":FileAccess.get_sha256(script_path),"test_source_sha256":FileAccess.get_sha256(get_script().resource_path),"renderer":RenderingServer.get_video_adapter_name(),"scope":"Actual independent VFX GPU rendering and shared-clock/reset/lifetime contract; no collisions, complete game or body atlas effects claim.","art_approved":false}
    FileAccess.open(out_dir.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
    print("EFFECTS_PROOF ",checks.size()," passed ",passed);quit(0 if passed else 1)
