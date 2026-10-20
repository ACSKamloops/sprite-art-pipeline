extends SceneTree
## Optional arranged visual fixture, not ordinary-player or independent review evidence.
## Run via xvfb-run -a godot --path . --script tests/capture_combat.gd -- --test-mode
var world: Node
func _initialize() -> void: run.call_deferred()
func run() -> void:
	if "--test-mode" not in OS.get_cmdline_user_args():
		printerr("Capture requires --test-mode to protect the ordinary player save.")
		quit(1)
		return
	world=load("res://scenes/main.tscn").instantiate()
	root.add_child(world)
	world._new_game()
	while world.mode == "dialogue": world._advance_dialogue()
	world.hero.position=Vector2(1220,555)
	world.hero._invulnerable_left=100.0
	world.camera.position=world.hero.position
	world.hud.notice_time=0
	DisplayServer.window_set_size(Vector2i(1280,720))
	DirAccess.make_dir_recursive_absolute("res://output/combat-polish")
	for step in range(4):
		await create_timer(1.5,false,true).timeout
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://output/combat-polish/arranged-crown-%s.png"%step)
		print("CROWN SNAPSHOT: "+JSON.stringify(world.get_debug_state()))
	world.queue_free()
	await process_frame
	await create_timer(.25,true,false,true).timeout
	quit()
