extends SceneTree
var world: Node
var count := 0
func _initialize():
 call_deferred("run")
func check(value: bool, description: String):
 count += 1
 if not value:
  push_error("WORLD CHECK FAILED: " + description)
  quit(1)
func finish_dialogue():
 while world.mode == "dialogue":
  world._advance_dialogue()
func run():
 for key in ["move_up", "move_down", "move_left", "move_right", "attack", "firebolt", "nova", "dodge", "interact", "heal", "pause"]:
  if not InputMap.has_action(key): InputMap.add_action(key)
 world = load("res://scenes/main.tscn").instantiate()
 root.add_child(world)
 await process_frame
 check(world.mode == "title", "title opens")
 check(paused and not world.hero.input_enabled, "title pauses combat")
 check(world.hud.buttons.size() >= 2, "title has focusable buttons")
 world._menu_action("new_confirmed")
 check(world.mode == "dialogue", "new game introduction")
 finish_dialogue()
 check(world.mode == "play" and world.hero.input_enabled, "introduction resumes play")
 check(world._read_save().wards == [false,false,false], "fresh save progression")
 world.hero.position = world.NPC_POSITION + Vector2(0,45)
 world._interact()
 check(world.talked_to_aster, "Aster conversation recorded")
 finish_dialogue()
 for i in range(3):
  world.hero.position = world.WARD_POSITIONS[i] + Vector2(0,70)
  world._check_encounters()
  check(world.encounters_started[i], "encounter starts on approach")
  check(world.encounter_foes[i].size() == [3,4,5][i], "encounter composition")
  world._interact()
  check(not world.wards[i], "ward cannot kindle through living enemies")
  for foe in world.encounter_foes[i].duplicate():
   foe.take_damage(9999, world.hero.position)
  check(world.encounter_foes[i].is_empty(), "defeated signals clear encounter")
  world._interact()
  check(world.wards[i] and world.mode == "dialogue", "cleared ward kindles by interaction")
  finish_dialogue()
  check(world.heals == 2 and world.hero.hp == world.hero.max_hp, "kindled ward restores resources")
  check(world.checkpoint == ["moss","tide","crown"][i], "ward checkpoint recorded")
  check(world._read_save().wards[i], "ward progress persisted")
  check(world.gate.collision_layer == (0 if i == 2 else 1), "threeward physical gate")
 check(world.wards.count(true) == 3, "three wards complete")
 world.hero.position = Vector2(1900,520)
 world._check_encounters()
 check(world.boss_started and is_instance_valid(world.boss), "boss starts in shrine")
 check(world.boss.kind == "warden", "actual boss actor")
 check(world.checkpoint == "shrine", "shrine checkpoint")
 world.hero.position = world.BELL_POSITION + Vector2(0,65)
 world._interact()
 check(not world.won and world.mode == "play", "living Warden blocks ending")
 world.boss.take_damage(9999, world.hero.position)
 check(world.boss_defeated, "boss defeat signal updates journey")
 world._interact()
 check(world.mode == "dialogue", "bell ending dialogue")
 finish_dialogue()
 check(world.won and world.mode == "ending", "finite ending")
 var saved: Dictionary = world._read_save()
 check(saved.won and saved.boss_defeated, "ending saved")
 world._menu_action("explore")
 check(world.mode == "play", "postgame exploration")
 world.hero.hp = 20
 world._on_action_used("heal")
 check(world.heals == 1 and world.hero.hp == world.hero.max_hp, "healing consumes one flask")
 world._menu_action("pause_open")
 check(world.mode == "pause" and paused, "journal pauses")
 var elapsed: float = world.elapsed
 await process_frame
 check(world.elapsed == elapsed, "simulation elapsed frozen during pause")
 world._menu_action("mute")
 check(AudioServer.is_bus_mute(AudioServer.get_bus_index("SFX")), "effects mute bus")
 world._menu_action("music_mute")
 check(AudioServer.is_bus_mute(AudioServer.get_bus_index("Music")), "music mute bus")
 world._menu_action("resume")
 world._on_hero_defeated()
 check(world.mode == "dead", "death screen")
 world._menu_action("retry")
 check(world.mode == "play" and world.hero.position == world.CHECKPOINTS.shrine, "retry checkpoint")
 check(world.wards.count(true) == 3 and world.heals == 2, "death preserves wards and refills flasks")
 world._apply_save(saved)
 check(world.won and world.boss_defeated and world.wards.count(true) == 3, "continue restores completed journey")
 check(world.get_debug_state().save_valid, "debug snapshot")
 world._menu_action("title")
 world._menu_action("new")
 check(world.mode == "confirm", "existing save protected by explicit replace choice")
 check(world._read_save().won, "new game confirmation does not overwrite save")
 print("WORLD PASS: %d assertions; title, dialogue, 3 encounters, wards, gate, boss, ending, healing, pause, audio, death, save/continue" % count)
 world.queue_free()
 await process_frame
 await create_timer(.15,true,false,true).timeout
 quit()
