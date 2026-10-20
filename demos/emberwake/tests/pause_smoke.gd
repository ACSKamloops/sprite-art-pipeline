extends SceneTree
var world: Node
var checks := 0
func _initialize(): call_deferred("run")
func check(value: bool, description: String):
 checks += 1
 if not value:
  push_error("PAUSE CHECK FAILED: " + description)
  quit(1)
func snapshot(enemy: Node, bolt: Node = null, fx: Node = null) -> Dictionary:
 var data := {"hero_state": world.hero.state, "hero_state_time": world.hero._state_time, "hero_state_left": world.hero._state_left, "hero_animation_time": world.hero._animation_time, "hero_cooldowns": world.hero.cooldowns.duplicate(), "hero_pending_hit": world.hero._pending_hit, "hero_invulnerable": world.hero._invulnerable_left, "hero_position": world.hero.position, "enemy_state": enemy.state, "enemy_left": enemy._state_left, "enemy_motion": enemy._motion_time, "enemy_position": enemy.position, "world_elapsed": world.elapsed}
 if bolt != null:
  data.merge({"bolt_position": bolt.position, "bolt_elapsed": bolt._elapsed, "bolt_trail": bolt._trail.duplicate()})
 if fx != null: data["fx_elapsed"] = fx.elapsed
 return data
func run():
 for key in ["move_up", "move_down", "move_left", "move_right", "attack", "firebolt", "nova", "dodge", "interact", "heal", "pause"]:
  if not InputMap.has_action(key): InputMap.add_action(key)
 world = load("res://scenes/main.tscn").instantiate()
 root.add_child(world)
 world._new_game()
 while world.mode == "dialogue": world._advance_dialogue()
 var foe: CharacterBody2D = world._spawn_enemy("brute", world.hero.position + Vector2(58,0), -2)
 world.hero.facing = "north"
 world.hero._aim = Vector2.UP
 world.hero.request_action("firebolt")
 await create_timer(0.10).timeout
 check(world.hero.state == "cast" and world.hero._pending_hit == "firebolt", "actual cast is pending")
 check(foe.state == "windup", "actual enemy enters windup")
 var before := snapshot(foe)
 world._set_mode("pause")
 await create_timer(0.20).timeout
 check(snapshot(foe) == before, "pause freezes complete hero action and enemy windup snapshots")
 check(not world.hero.can_process() and not foe.can_process(), "actors inherit explicit pausable boundary")
 var lines: Array[String] = ["A real modal dialogue."]
 world._show_dialogue("TEST", lines, "")
 await create_timer(0.20).timeout
 check(snapshot(foe) == before, "dialogue preserves hero pending hit, cooldowns, art and enemy windup")
 world._advance_dialogue()
 await create_timer(0.18).timeout
 check(world.hero._state_time > before.hero_state_time, "resumed cast clock advances")
 var projectiles: Array[Node] = get_nodes_in_group("combat_projectiles")
 check(projectiles.size() == 1, "resumed pending cast releases one real projectile")
 var bolt: Node = projectiles[0]
 check(bolt.get_parent() == world.actors, "projectile belongs to paused actor branch")
 var fx: Node = load("res://scripts/combat_fx.gd").spawn(world.actors, world.hero.position, "frost", Vector2.UP, 90)
 await create_timer(0.03).timeout
 check(bolt._elapsed > 0 and bolt._trail.size() > 0, "projectile is actually mid-flight")
 check(fx.elapsed > 0, "effect animation is actually active")
 for modal in ["pause", "dialogue", "title"]:
  before = snapshot(foe, bolt, fx)
  if modal == "dialogue": world._show_dialogue("TEST", lines, "")
  else: world._set_mode(modal)
  await create_timer(0.20).timeout
  check(is_instance_valid(bolt) and is_instance_valid(fx), modal + " retains projectile and FX")
  check(snapshot(foe, bolt, fx) == before, modal + " freezes actual projectile travel/lifetime, FX elapsed, hero action and enemy windup")
  check(world.can_process() and world.hud.can_process(), modal + " leaves camera/ambient and HUD active")
  check(not bolt.can_process() and not fx.can_process(), modal + " pauses projectile and effect branch inheritance")
 world._set_mode("play")
 before = snapshot(foe, bolt, fx)
 await create_timer(0.08).timeout
 check(bolt.position != before.bolt_position and bolt._elapsed > before.bolt_elapsed, "resume restores projectile travel and lifetime")
 check(fx.elapsed > before.fx_elapsed, "resume restores effect animation")
 check(foe._state_left < before.enemy_left, "resume restores enemy windup clock")
 check(world.hero._state_time > before.hero_state_time, "resume restores hero action clock")
 print("PAUSE PASS: %d assertions; actual pending cast, midflight projectile, enemy windup, hero animation/cooldown and FX frozen in pause/dialogue/title; resume preserved" % checks)
 world.queue_free()
 await process_frame
 await create_timer(.15,true,false,true).timeout
 quit()
