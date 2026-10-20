extends SceneTree
func _initialize(): call_deferred("run")
func run():
 for key in ["move_up", "move_down", "move_left", "move_right", "attack", "firebolt", "nova", "dodge", "interact", "heal", "pause"]:
  if not InputMap.has_action(key): InputMap.add_action(key)
 var world = load("res://scenes/main.tscn").instantiate()
 root.add_child(world)
 world._set_mode("play")
 await physics_frame
 await physics_frame
 var shape := CircleShape2D.new()
 shape.radius = 11
 var query := PhysicsShapeQueryParameters2D.new()
 query.shape = shape
 query.collision_mask = 1
 var count := 0
 var blocked := []
 for route in world.ROUTES:
  for i in range(route.size()-1):
   var a: Vector2 = route[i]
   var b: Vector2 = route[i+1]
   var steps := ceili(a.distance_to(b)/12.0)
   for step in range(steps+1):
    var p := a.lerp(b,float(step)/steps)
    var skip := p.distance_to(world.BELL_POSITION) < 65 or (p.x > 1860 and p.y > 620 and p.y < 700)
    for ward in world.WARD_POSITIONS:
     skip = skip or p.distance_to(ward)<65
    if skip: continue
    query.transform = Transform2D(0,p)
    count += 1
    if not world.get_world_2d().direct_space_state.intersect_shape(query).is_empty(): blocked.append(p)
 print("ROUTE SAMPLES: ", count, "; blocked: ",blocked)
 world.queue_free()
 await process_frame
 # main._exit_tree() stops music and clears its stream before this grace;
 # allow the asynchronous Ogg mixer playback to release on fast headless runs.
 await create_timer(.35,true,false,true).timeout
 quit(0 if blocked.is_empty() else 1)
