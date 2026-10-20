extends SceneTree
## Real physics crowd motion, attack scheduling and action/feedback boundaries.
## No screenshot score is inferred from these behavioral assertions.
const HERO = preload("res://scripts/hero.gd")
const ENEMY = preload("res://scripts/enemy.gd")
const PROJECTILE = preload("res://scripts/projectile.gd")
var world: Node2D
var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func check(value: bool, note: String) -> void:
	checks += 1
	if not value:
		failures.append(note)

func fixture() -> void:
	if is_instance_valid(world):
		world.free()
	world = Node2D.new()
	world.process_mode = Node.PROCESS_MODE_PAUSABLE
	root.add_child(world)

func hero_at(where: Vector2 = Vector2.ZERO) -> CharacterBody2D:
	var hero := HERO.new()
	hero.position = where
	world.add_child(hero)
	hero._invulnerable_left = 100.0
	return hero

func foe_at(where: Vector2, hero: Node2D, kind: String = "scout") -> CharacterBody2D:
	var foe := ENEMY.new()
	foe.setup(kind)
	foe.position = where
	foe.target = hero
	world.add_child(foe)
	return foe

func visual_gap(foes: Array) -> float:
	var smallest := INF
	for i in range(foes.size()):
		for j in range(i + 1, foes.size()):
			var apart: Vector2 = foes[i].position - foes[j].position
			smallest = minf(smallest, Vector2(apart.x, apart.y * 0.72).length())
	return smallest

func _run() -> void:
	fixture()
	var hero := hero_at()
	var foes: Array = [foe_at(Vector2(65, 0), hero), foe_at(Vector2(55, 30), hero), foe_at(Vector2(55, -30), hero)]
	var start_gap := visual_gap(foes)
	var peak_reservations := 0
	var moving_waiter := false
	var starts: Array[Vector2] = []
	for foe in foes:
		starts.append(foe.position)
	var after_gap := 0.0
	for tick in range(600):
		await physics_frame
		var reserved := 0
		for i in range(foes.size()):
			var foe: Node2D = foes[i]
			if foe.state in ["windup", "strike", "phase"] or (foe.state == "recover" and foe._state_total - foe._state_left < 0.20):
				reserved += 1
			elif foe.position.distance_to(starts[i]) > 12.0:
				moving_waiter = true
		peak_reservations = maxi(peak_reservations, reserved)
		if tick == 180:
			after_gap = visual_gap(foes)
	check(peak_reservations == 1, "actual three-foe encounter never overlaps committed windups, strikes or early recovery")
	check(moving_waiter, "waiting foes actively reposition instead of standing in a queue")
	check(after_gap > start_gap + 8.0 and after_gap > 30.0, "crowded same-side starts separate their visual bodies under real collision/motion")
	var all_attacked := true
	for foe in foes:
		all_attacked = all_attacked and foe._commit_count > 0
	check(all_attacked, "each of three foes gets a real committed attack within ten seconds")
	check(is_equal_approx(hero.hp, 100.0), "guarded attacks do not damage an invulnerable hero")
	var total_attacks := 0
	for foe in foes:
		total_attacks += foe._commit_count
	check(total_attacks >= 7, "coordination retains repeated group pressure rather than indefinite waiting")
	print("COMBAT CROWD: start gap %.2f, 3s gap %.2f, max reservations %d, attacks %d" % [start_gap, after_gap, peak_reservations, total_attacks])

	# The actual Crown mix includes two slower, longer-reach brutes and three
	# scouts. Fair scheduling must not starve either kind behind the nearest foe.
	fixture()
	hero = hero_at()
	foes = [foe_at(Vector2(-95,-35),hero,"brute"),foe_at(Vector2(105,35),hero,"brute"),foe_at(Vector2(-110,120),hero),foe_at(Vector2(115,145),hero),foe_at(Vector2(0,-125),hero)]
	peak_reservations = 0
	for tick in range(600):
		await physics_frame
		var reserved_count := 0
		for foe in foes:
			if foe.state in ["windup", "strike", "phase"] or (foe.state == "recover" and foe._state_total - foe._state_left < 0.20): reserved_count += 1
		peak_reservations = maxi(peak_reservations, reserved_count)
	all_attacked = true
	total_attacks = 0
	for foe in foes:
		all_attacked = all_attacked and foe._commit_count > 0
		total_attacks += foe._commit_count
	check(peak_reservations == 1, "actual Crown mix preserves one clear committed threat at once")
	check(all_attacked, "Crown scouts and both slower brutes all receive a commitment within ten seconds")
	check(total_attacks >= 7, "mixed encounter continues applying pressure after all foes have participated")
	print("COMBAT CROWN: max reservations %d, attacks %d, final visual gap %.2f" % [peak_reservations,total_attacks,visual_gap(foes)])

	fixture()
	hero = hero_at(Vector2(65, 0))
	var first := foe_at(Vector2.ZERO, hero)
	var second := foe_at(Vector2(65, 65), hero)
	first.set_physics_process(false)
	second.set_physics_process(false)
	first._start_attack(Vector2.RIGHT)
	check(not second._can_commit_attack(), "another live windup reserves the local attack slot")
	first.take_damage(1.0, Vector2(-10, 0))
	check(first.state == "hurt" and second._can_commit_attack(), "scout interruption releases the slot immediately")
	second._start_attack(Vector2.UP)
	check(not first._can_commit_attack(), "new threat owns the slot after interruption")
	second.take_damage(1000.0)
	check(first._can_commit_attack(), "death removes a reservation without waiting for the fade")
	first._start_attack(Vector2.RIGHT)
	first.activated = false
	check(not first._reserves_attack(), "deactivation releases the reservation")
	first.activated = true
	first._change_state("recover", first._recovery)
	check(first._reserves_attack(), "early recovery retains a short visual separation between attacks")
	first._state_left = first._recovery - 0.22
	check(not first._reserves_attack(), "late recovery allows the next warning instead of holding an entire queue")
	var other_hero := hero_at(Vector2(1000, 0))
	var remote := foe_at(Vector2(940, 0), other_hero)
	remote.set_physics_process(false)
	remote._start_attack(Vector2.RIGHT)
	check(first._can_commit_attack(), "unrelated target/encounter does not globally block attacks")

	fixture()
	hero = hero_at(Vector2(65, 0))
	hero._invulnerable_left = 0.0
	first = foe_at(Vector2.ZERO, hero)
	await create_timer(0.25, false, true).timeout
	check(first.state == "windup" and hero.hp == 100.0, "visible live windup does no early damage")
	var aim: Vector2 = first._aim
	hero.position = Vector2(0, 65)
	await create_timer(0.36, false, true).timeout
	check(first._aim == aim and hero.hp == 100.0, "enemy cannot swivel its locked arc onto a player who sidesteps during warning")
	check(first.last_strike_result == "miss", "evaded arc records a miss rather than false damage contact")
	var whiff_count := 0
	var release_count := 0
	for child in world.get_children():
		if child.get("style") == "whiff": whiff_count += 1
		if child.get("style") == "melee_release": release_count += 1
	check(whiff_count == 1 and release_count == 1, "miss emits one restrained release trace and hollow whiff cue")
	await create_timer(0.40, false, true).timeout
	check(first.state == "recover" and first.current_art_pose in ["neutral", "back_neutral"], "late recovery visibly returns to neutral before chasing")

	fixture()
	hero = hero_at(Vector2(65, 0))
	hero._invulnerable_left = 0.0
	first = foe_at(Vector2.ZERO, hero)
	await create_timer(0.64, false, true).timeout
	check(hero.hp == 88.0 and first.last_strike_result == "hit", "actual strike damages once at release and records an accepted contact")
	await create_timer(0.18, false, true).timeout
	check(hero.hp == 88.0, "release presentation never reapplies a damage hit on later frames")
	check(not hero.take_damage(20.0), "hero damage API reports a rejected invulnerable hit")
	check(first.take_damage(1.0), "enemy damage API reports an accepted impact")

	fixture()
	hero = hero_at(Vector2(65, 0))
	first = foe_at(Vector2.ZERO, hero)
	second = foe_at(Vector2(65, 60), hero)
	await create_timer(0.1, false, true).timeout
	var reserved: Node2D = first if first._reserves_attack() else second
	var reserved_left: float = reserved._state_left
	var reserved_count: int = reserved._commit_count
	var snap: Array = [first.state, first._state_left, first._attack_wait, first._commit_count, first.position, second.state, second._state_left, second._attack_wait, second._commit_count, second.position]
	paused = true
	await create_timer(0.18, true).timeout
	check([first.state, first._state_left, first._attack_wait, first._commit_count, first.position, second.state, second._state_left, second._attack_wait, second._commit_count, second.position] == snap, "real pause freezes reservations, wait fairness, staged action clocks and spacing")
	paused = false
	await create_timer(0.05, false, true).timeout
	check(reserved._state_left < reserved_left and reserved._commit_count == reserved_count, "resume continues the same reserved attack rather than restarting it")
	hero.set_input_enabled(false)
	await create_timer(0.05, false, true).timeout
	check(not first._reserves_attack() and not second._reserves_attack(), "dialogue-disabled target clears all live committing threats")

	# A projectile contacts one actor once. The victim supplies the painted hit;
	# the projectile must not add another full-size burst over its action pose.
	fixture()
	hero = hero_at(Vector2(-200, 0))
	first = foe_at(Vector2(60, 0), hero)
	first.set_physics_process(false)
	var bolt := PROJECTILE.new()
	bolt.direction = Vector2.RIGHT
	bolt.damage = 1.0
	world.add_child(bolt)
	await create_timer(0.13, false, true).timeout
	var impact_count := 0
	for child in world.get_children():
		if child.get("style") == "impact": impact_count += 1
	check(first.hp == 41.0 and impact_count == 1, "one projectile hit produces one painted impact instead of doubled contact bursts")

	world.queue_free()
	await process_frame
	await create_timer(0.2, true, false, true).timeout
	if failures.is_empty():
		print("COMBAT_READABILITY PASS: %d assertions" % checks)
		quit(0)
	else:
		for failure in failures: printerr("FAIL: " + failure)
		quit(1)
