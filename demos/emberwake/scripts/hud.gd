extends Control
## Painted, keyboard accessible game interface. World logic stays in main.gd.
signal menu_action(action: String)

const INK := Color("101d24")
const PAPER := Color("eae4cf")
const MUTED := Color("a9bcb5")
const GOLD := Color("e5b766")
const TEAL := Color("7cc5b7")
var mode := "title"
var snapshot: Dictionary = {}
var dialogue: Dictionary = {}
var notice := ""
var notice_time := 0.0
var clock_time := 0.0
var font: Font
var title_font: Font
var title_art: Texture2D
var buttons: Array[Button] = []
var hovered := ""
var _character_previews: Dictionary = {}
var _character_page := 0

func overlay_regions() -> Dictionary:
	# The bottom center is reserved for combat HUD. Keep the boss away from the
	# world-facing top of the screen, and give interactions their own row.
	var regions := {"actions": Rect2(243, 478, 474, 47)}
	if mode != "play":
		return regions
	if notice_time > 0.0:
		regions["notice"] = Rect2(24, 354, 265, 99)
	elif not str(snapshot.get("hint", "")).is_empty():
		regions["hint"] = Rect2(24, 366, 254, 81)
	var has_boss := not (snapshot.get("boss", {}) as Dictionary).is_empty()
	if has_boss:
		regions["boss"] = Rect2(306, 427, 348, 38)
	var prompt := str(snapshot.get("prompt", ""))
	if not prompt.is_empty():
		var width := font.get_string_size(prompt, HORIZONTAL_ALIGNMENT_LEFT, -1, 17).x + 60
		if has_boss:
			width = minf(width, 348)
		regions["interaction"] = Rect2((960 - width) / 2, 375 if has_boss else 421, width, 38)
	return regions

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	font = load("res://assets/fonts/body.ttf") if ResourceLoader.exists("res://assets/fonts/body.ttf") else ThemeDB.fallback_font
	title_font = load("res://assets/fonts/title.ttf") if ResourceLoader.exists("res://assets/fonts/title.ttf") else font
	if ResourceLoader.exists("res://assets/world/title-panorama.png"):
		title_art = load("res://assets/world/title-panorama.png")
	set_mode("title")

func update_snapshot(data: Dictionary) -> void:
	snapshot = data
	queue_redraw()

func toast(message: String, duration := 4.0) -> void:
	notice = message
	notice_time = duration
	queue_redraw()

func set_dialogue(speaker: String, line: String, page: int, total: int) -> void:
	dialogue = {"speaker": speaker, "line": line, "page": page, "total": total}
	queue_redraw()

func set_mode(next_mode: String) -> void:
	var previous_mode := mode
	mode = next_mode
	for button in buttons:
		button.queue_free()
	buttons.clear()
	match mode:
		"play":
			_button("Esc  Journal", "pause_open", Vector2(792, 485), Vector2(146, 34), true)
		"dialogue":
			_button("E / Enter  Continue", "dialogue_next", Vector2(613, 430), Vector2(183, 26), true)
		"title":
			if snapshot.get("has_save", false):
				_button("Continue journey", "continue", Vector2(78, 310), Vector2(250, 42))
				_button("New journey", "new", Vector2(78, 360), Vector2(250, 42))
			else:
				_button("Begin journey", "new", Vector2(78, 330), Vector2(250, 44))
			_button("Controls & map", "help", Vector2(78, 416), Vector2(250, 36), true)
			_button("Choose emberkeeper", "characters", Vector2(574, 432), Vector2(272, 38), true)
		"characters":
			var characters: Array = snapshot.get("characters", [])
			if previous_mode != "characters":
				_character_page = 0
				for i in range(characters.size()):
					if characters[i].id == snapshot.get("character_choice", "rowan"):
						_character_page = i / 3
			var page_count := maxi(1, ceili(characters.size() / 3.0))
			_character_page = clampi(_character_page, 0, page_count - 1)
			var start := _character_page * 3
			var count := mini(3, characters.size() - start)
			var left := (960.0 - count * 264 - maxi(0, count - 1) * 24) / 2
			for i in range(count):
				var character: Dictionary = characters[start + i]
				var selected: bool = character.id == snapshot.get("character_choice", "rowan")
				_button("Selected · %s" % character.name if selected else "Select %s" % character.name, "character_select:" + character.id, Vector2(left + i * 288 + 18, 358), Vector2(228, 36), not selected)
			if page_count > 1:
				_button("‹", "character_page:%d" % posmod(_character_page - 1, page_count), Vector2(782, 66), Vector2(42, 34), true)
				_button("›", "character_page:%d" % posmod(_character_page + 1, page_count), Vector2(836, 66), Vector2(42, 34), true)
			_button("Back", "character_cancel", Vector2(68, 459), Vector2(175, 38), true)
			_button("Use character & return" if snapshot.get("character_return", "title") == "pause" else "Choose for new journey", "character_apply", Vector2(590, 459), Vector2(302, 38))
		"confirm":
			_button("Begin and replace save", "new_confirmed", Vector2(330, 290), Vector2(300, 44))
			_button("Keep my journey", "title", Vector2(330, 346), Vector2(300, 40), true)
		"pause", "help":
			_button("Resume" if mode == "pause" else "Back", "resume" if mode == "pause" else "title", Vector2(68, 459), Vector2(165, 38))
			_button("Effects: off" if snapshot.get("muted", false) else "Effects: on", "mute", Vector2(245, 459), Vector2(165, 38), true)
			_button("Music: off" if snapshot.get("music_muted", false) else "Music: on", "music_mute", Vector2(422, 459), Vector2(165, 38), true)
			if mode == "pause":
				_button("Save & title", "save_title", Vector2(599, 459), Vector2(165, 38), true)
				var choice_button := _button("Change emberkeeper", "characters", Vector2(685, 66), Vector2(195, 34), true)
				choice_button.disabled = not str(snapshot.get("character_switch_reason", "")).is_empty()
		"dead":
			_button("Wake at the lantern", "retry", Vector2(330, 314), Vector2(300, 44))
			_button("Return to title", "title", Vector2(330, 370), Vector2(300, 38), true)
		"ending":
			_button("Walk the waking woods", "explore", Vector2(330, 374), Vector2(300, 44))
			_button("Return to title", "title", Vector2(330, 430), Vector2(300, 38), true)
	if not buttons.is_empty() and mode != "play":
		buttons[0].grab_focus()
		if mode == "characters":
			for button in buttons:
				if button.get_meta("action", "") == "character_select:" + str(snapshot.get("character_choice", "rowan")):
					button.grab_focus()
	queue_redraw()

func _button(label: String, action: String, at: Vector2, dimensions: Vector2, subtle := false) -> Button:
	var button := Button.new()
	button.text = label
	button.position = at
	button.size = dimensions
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	# Space is the dodge action during play. A focused Journal button otherwise
	# also accepts it as ui_accept, causing a dodge to immediately pause the game.
	if mode == "play":
		button.focus_mode = Control.FOCUS_NONE
	button.add_theme_font_override("font", font)
	button.add_theme_font_size_override("font_size", 17)
	button.add_theme_color_override("font_color", PAPER)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.add_theme_color_override("font_focus_color", Color.WHITE)
	for state in ["normal", "hover", "pressed", "focus"]:
		var style := StyleBoxFlat.new()
		style.bg_color = Color("1c343b") if subtle else Color("37544e")
		if state == "hover" or state == "focus":
			style.bg_color = Color("496960")
		style.border_color = GOLD if state == "focus" else Color("73897b")
		style.set_border_width_all(1)
		style.set_corner_radius_all(3)
		button.add_theme_stylebox_override(state, style)
	button.set_meta("action", action)
	button.pressed.connect(func():
		if action.begins_with("character_page:"):
			_character_page = int(action.trim_prefix("character_page:"))
			set_mode(mode)
		else:
			menu_action.emit(action)
	)
	add_child(button)
	buttons.append(button)
	return button

func _process(delta: float) -> void:
	clock_time += delta
	if notice_time > 0.0:
		notice_time -= delta
	queue_redraw()

func _draw() -> void:
	if not font:
		return
	if mode in ["play", "dialogue", "pause", "dead", "ending"] or (mode == "characters" and snapshot.get("character_return", "title") == "pause"):
		_draw_game()
	match mode:
		"title": _draw_title()
		"characters": _draw_characters()
		"confirm":
			_scrim(0.82)
			_panel(Rect2(260, 135, 440, 280))
			_center("A new ember", 188, 30, GOLD, title_font)
			_wrap("Beginning a new journey replaces your saved checkpoint. Your current journey is safe until you choose below.", Rect2(308, 216, 344, 68), 17, PAPER)
		"pause", "help": _draw_pause()
		"dialogue": _draw_dialogue()
		"dead":
			_scrim(0.67)
			_center("THE EMBER REMAINS", 218, 32, PAPER, title_font)
			_center("The lantern remembers you. Your kindled wards endure.", 261, 17, MUTED)
		"ending":
			_scrim(0.78)
			_center("THE HOLLOW BELL", 143, 17, GOLD)
			_center("A voice returns to the valley", 195, 34, PAPER, title_font)
			_wrap("For a moment the bell sounds like rain. Then the forest exhales, the lanterns brighten, and somewhere below, Aster opens the door.", Rect2(270, 228, 420, 90), 19, PAPER, true)
			_center("Thank you for carrying the ember.", 343, 17, TEAL)
	if notice_time > 0.0 and mode == "play":
		_panel(overlay_regions().notice, 0.96)
		_wrap(notice, Rect2(39, 370, 235, 73), 15, GOLD)

func _draw_game() -> void:
	_panel(Rect2(22, 20, 236, 78), 0.92)
	var live_name := str(_character(str(snapshot.get("live_character", "rowan"))).get("name", "Emberkeeper"))
	_text(live_name.to_upper() + " · EMBERKEEPER", Vector2(38, 41), 12, MUTED)
	var hp := float(snapshot.get("hp", 100))
	var max_hp := maxf(1, float(snapshot.get("max_hp", 100)))
	_bar(Rect2(39, 51, 162, 10), hp / max_hp, Color("c97f6a"))
	_text(str(ceili(hp)), Vector2(212, 61), 13, PAPER)
	var mana := float(snapshot.get("mana", 60))
	_bar(Rect2(39, 72, 162, 5), mana / maxf(1, float(snapshot.get("max_mana", 60))), Color("78adcc"))
	_text("%d" % ceili(mana), Vector2(212, 81), 12, MUTED)
	_panel(Rect2(641, 20, 297, 78), 0.92)
	_text("THE HOLLOW BELL", Vector2(659, 41), 12, GOLD)
	_wrap(str(snapshot.get("objective", "Find Aster by the village lantern.")), Rect2(659, 48, 263, 42), 16, PAPER)
	var complete: Array = snapshot.get("wards", [false, false, false])
	for i in range(3):
		var point := Vector2(901 + i * 12, 34)
		draw_circle(point, 3, GOLD if complete[i] else Color("486269"))
	var zone := str(snapshot.get("zone", "BELLWETHER"))
	_center(zone.to_upper(), 38, 13, Color("e6e1cb"))
	# Compact action belt, with resource costs clear at a glance.
	var regions := overlay_regions()
	_panel(regions.actions, 0.90)
	var skills := [["J", "Strike"], ["K", "Fire · 10"], ["L", "Frost · 24"], ["SPACE", "Dodge"], ["H", "Heal × %d" % int(snapshot.get("heals", 2))]]
	for i in range(skills.size()):
		var x := 258 + i * 92
		_text(skills[i][0], Vector2(x, 495), 11, GOLD)
		_text(skills[i][1], Vector2(x, 514), 13, PAPER)
	var prompt := str(snapshot.get("prompt", ""))
	if not prompt.is_empty() and mode == "play":
		var prompt_rect: Rect2 = regions.interaction
		_panel(prompt_rect, 0.94)
		if regions.has("boss"):
			var prompt_size := 17
			while prompt_size > 11 and font.get_string_size("E  " + prompt, HORIZONTAL_ALIGNMENT_LEFT, -1, prompt_size).x > prompt_rect.size.x - 20:
				prompt_size -= 1
			_center("E  " + prompt, prompt_rect.position.y + 26, prompt_size, PAPER)
		else:
			_center("E  " + prompt, 447, 17, PAPER)
	var boss: Dictionary = snapshot.get("boss", {})
	if not boss.is_empty() and mode == "play":
		var boss_rect: Rect2 = regions.boss
		_panel(boss_rect, 0.94)
		_center("THE ROOTBOUND WARDEN", boss_rect.position.y + 15, 11, GOLD)
		_bar(Rect2(boss_rect.position + Vector2(16, 23), boss_rect.size - Vector2(32, 33)), float(boss.get("hp", 1)) / maxf(1, float(boss.get("max_hp", 1))), Color("bd7660"))
	var hint := str(snapshot.get("hint", ""))
	if not hint.is_empty() and mode == "play" and notice_time <= 0.0:
		_panel(regions.hint, 0.92)
		_wrap(hint, Rect2(39, 381, 224, 58), 15, MUTED)
	_draw_compass()

func _draw_compass() -> void:
	if mode != "play" or not snapshot.has("goal_direction"):
		return
	var direction: Vector2 = snapshot.goal_direction
	if direction.length() < 0.1:
		return
	var center := Vector2(907, 144)
	draw_circle(center, 23, Color(0.06, 0.12, 0.15, 0.8))
	draw_arc(center, 23, 0, TAU, 36, Color("667a70"), 1, true)
	var forward := direction.normalized()
	var side := Vector2(-forward.y, forward.x)
	draw_colored_polygon(PackedVector2Array([center + forward * 15, center - forward * 8 + side * 6, center - forward * 5, center - forward * 8 - side * 6]), GOLD)
	_text(str(snapshot.get("goal_label","WARD")), Vector2(891, 185), 10, MUTED)

func _draw_title() -> void:
	if title_art:
		var art_size := title_art.get_size()
		var factor := maxf(960 / art_size.x, 540 / art_size.y)
		var dimensions := art_size * factor
		draw_texture_rect(title_art, Rect2((Vector2(960, 540) - dimensions) / 2, dimensions), false)
	draw_rect(Rect2(0, 0, 460, 540), Color(0.035, 0.075, 0.10, 0.93))
	draw_rect(Rect2(460, 0, 500, 540), Color(0.035, 0.075, 0.10, 0.16))
	draw_line(Vector2(460, 0), Vector2(460, 540), Color(0.8, 0.65, 0.39, 0.36), 1)
	_text("A SMALL ADVENTURE IN A WAKING WORLD", Vector2(79, 101), 11, GOLD)
	_text("Emberwake", Vector2(74, 182), 57, PAPER, title_font)
	_text("THE HOLLOW BELL", Vector2(80, 219), 19, GOLD)
	_wrap("The bell has forgotten its voice.\nCarry one small flame into the forest.", Rect2(80, 251, 320, 57), 18, MUTED)
	_text("Explore · kindle three wards · wake the bell", Vector2(79, 489), 13, MUTED)
	_text("An original adventure in Bellwether Valley", Vector2(79, 510), 12, Color("738b83"))
	var character := _character(str(snapshot.get("selected_character", "rowan")))
	_panel(Rect2(534, 104, 352, 312), 0.89)
	_text("YOUR EMBERKEEPER", Vector2(558, 133), 12, GOLD)
	_draw_character_preview(character, Vector2(710, 328), 1.55)
	var character_name := str(character.get("name", "Rowan"))
	_text(character_name, Vector2(710 - title_font.get_string_size(character_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 29).x / 2, 362), 29, PAPER, title_font)
	_wrap(str(character.get("subtitle", "Bearer of the first ember")), Rect2(553, 373, 314, 32), 15, TEAL, true)
	_text("New journeys use your chosen emberkeeper.", Vector2(553, 492), 13, PAPER)
	_text("Continue restores the character in your save.", Vector2(553, 512), 12, MUTED)

func _draw_characters() -> void:
	_scrim(0.94)
	_text("ONE EMBER, MANY PATHS", Vector2(62, 52), 12, GOLD)
	_text("Choose your emberkeeper", Vector2(58, 97), 34, PAPER, title_font)
	var characters: Array = snapshot.get("characters", [])
	var start := _character_page * 3
	var count := mini(3, characters.size() - start)
	var left := (960.0 - count * 264 - maxi(0, count - 1) * 24) / 2
	for i in range(count):
		var character: Dictionary = characters[start + i]
		var x := left + i * 288
		var selected: bool = character.id == snapshot.get("character_choice", "rowan")
		_panel(Rect2(x, 126, 264, 282), 0.96)
		if selected:
			draw_rect(Rect2(x, 126, 264, 282), GOLD, false, 2)
		_text(str(character.name), Vector2(x + 18, 156), 25, GOLD if selected else PAPER, title_font)
		_text(str(character.get("subtitle", "Emberkeeper")), Vector2(x + 18, 180), 13, TEAL)
		_draw_character_preview(character, Vector2(x + 132, 294), 1.16)
		_wrap(str(character.get("description", "A new way to carry the village's ember.")), Rect2(x + 18, 302, 228, 43), 14, MUTED)
	var error := str(snapshot.get("character_error", ""))
	_text(error if not error.is_empty() else "Every emberkeeper shares the same movement, strikes and spells.", Vector2(68, 435), 14, Color("e7a68f") if not error.is_empty() else MUTED)
	_text("Esc returns without changing your choice.", Vector2(68, 524), 12, MUTED)

func _character(id: String) -> Dictionary:
	for character in snapshot.get("characters", []):
		if character.id == id:
			return character
	return {}

func _draw_character_preview(character: Dictionary, feet: Vector2, scale_value: float) -> void:
	var atlas_path := str(character.get("atlas", ""))
	var manifest_path := str(character.get("manifest", ""))
	var key := atlas_path + "|" + manifest_path
	if not _character_previews.has(key):
		var preview: Dictionary = {}
		if ResourceLoader.exists(atlas_path) and FileAccess.file_exists(manifest_path):
			var bank: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
			if bank is Dictionary and bank.get("cell") is Array and bank.cell.size() == 2 and bank.get("pivot") is Array and bank.pivot.size() == 2 and bank.get("animations") is Dictionary:
				preview = {"atlas": load(atlas_path), "bank": bank}
		_character_previews[key] = preview
	var preview: Dictionary = _character_previews[key]
	if preview.is_empty():
		return
	var bank: Dictionary = preview.bank
	var idle: Dictionary = bank.animations.get("south_idle", {})
	var frames: Array = idle.get("frames", [])
	if frames.is_empty():
		return
	var cell := Vector2(float(bank.cell[0]), float(bank.cell[1]))
	var pivot := Vector2(float(bank.pivot[0]), float(bank.pivot[1]))
	var columns := maxi(1, int(bank.get("columns", 1)))
	var frame := int(frames[0])
	var region := Rect2(Vector2(frame % columns, frame / columns).floor() * cell, cell)
	draw_set_transform(feet + Vector2(0, 2), 0, Vector2(1, 0.23))
	draw_circle(Vector2.ZERO, 32 * scale_value, Color(0, 0, 0, 0.24))
	draw_set_transform(Vector2.ZERO)
	draw_texture_rect_region(preview.atlas, Rect2(feet - pivot * scale_value, cell * scale_value), region)

func _draw_pause() -> void:
	_scrim(0.86)
	_text("FIELD JOURNAL", Vector2(68, 69), 13, GOLD)
	_text("A light through the leaves", Vector2(66, 112), 30, PAPER, title_font)
	_text("YOUR WAY", Vector2(68, 159), 12, GOLD)
	_wrap(str(snapshot.get("objective", "Speak to Aster, then seek the three forest wards.")), Rect2(68, 172, 337, 58), 18, PAPER)
	var rows := [["WASD / arrows", "Move"], ["J / left mouse", "Unarmed strike"], ["K / right mouse", "Firebolt · 10 mana"], ["L / Q", "Frost nova · 24 mana"], ["Space", "Dodge through danger"], ["E / Enter", "Speak / kindle / continue"], ["H", "Healing flask"], ["Esc / P", "Pause / journal"]]
	for i in range(rows.size()):
		_text(rows[i][0], Vector2(68, 258 + i * 22), 14, MUTED)
		_text(rows[i][1], Vector2(242, 258 + i * 22), 14, PAPER)
	_draw_map(Rect2(458, 150, 422, 270))
	_text("Lanterns restore health, mana and both flasks.", Vector2(458, 439), 13, MUTED)
	if mode == "pause":
		var reason := str(snapshot.get("character_switch_reason", ""))
		if not reason.is_empty():
			_text(reason, Vector2(458, 124), 12, MUTED)

func _draw_map(rect: Rect2) -> void:
	_panel(rect, 0.86)
	_text("BELLWETHER VALLEY", rect.position + Vector2(16, 25), 12, GOLD)
	var origin := rect.position + Vector2(16, 35)
	var factor := Vector2((rect.size.x - 32) / 2304, (rect.size.y - 53) / 1728)
	var routes := [[Vector2(390, 1370), Vector2(700, 1260), Vector2(850, 1070), Vector2(930, 790), Vector2(1220, 470)], [Vector2(850, 1070), Vector2(470, 850)], [Vector2(850, 1070), Vector2(1330, 1170), Vector2(1690, 1120)], [Vector2(1220, 470), Vector2(1450, 750), Vector2(1730, 770), Vector2(1900, 730), Vector2(1900, 370)]]
	for route in routes:
		var points := PackedVector2Array()
		for p in route:
			points.append(origin + p * factor)
		draw_polyline(points, Color("6e8273"), 3, true)
	var sites := [[Vector2(390, 1370), "Village"], [Vector2(470, 850), "Moss ward"], [Vector2(1690, 1120), "Tide ward"], [Vector2(1220, 470), "Crown ward"], [Vector2(1900, 370), "Hollow bell"]]
	var wards: Array = snapshot.get("wards", [false, false, false])
	for i in range(sites.size()):
		var p: Vector2 = origin + sites[i][0] * factor
		var lit: bool = i == 0 or (i < 4 and wards[i - 1]) or (i == 4 and snapshot.get("won", false))
		draw_circle(p, 5, GOLD if lit else Color("8baca6"))
		_text(sites[i][1], p + Vector2(9, -7), 11, PAPER)
	var player: Vector2 = snapshot.get("position", Vector2(390, 1370))
	draw_circle(origin + player * factor, 4, Color("e9f6ef"))
	_text("N", rect.position + Vector2(rect.size.x - 24, 25), 11, MUTED)

func _draw_dialogue() -> void:
	_panel(Rect2(144, 275, 672, 190), 0.98)
	draw_rect(Rect2(144, 275, 4, 190), GOLD)
	_text(str(dialogue.get("speaker", "ASTER")), Vector2(169, 306), 13, GOLD)
	_wrap(str(dialogue.get("line", "")), Rect2(169, 319, 618, 101), 19, PAPER)
	_text("%d / %d" % [int(dialogue.get("page", 1)), int(dialogue.get("total", 1))], Vector2(170, 449), 12, MUTED)

func _bar(rect: Rect2, ratio: float, tint: Color) -> void:
	draw_rect(rect, Color("2b4147"))
	draw_rect(Rect2(rect.position, Vector2(rect.size.x * clampf(ratio, 0, 1), rect.size.y)), tint)

func _panel(rect: Rect2, opacity := 0.95) -> void:
	draw_style_box(_panel_style(opacity), rect)

func _panel_style(opacity: float) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.055, 0.105, 0.13, opacity)
	style.border_color = Color(0.57, 0.65, 0.56, 0.45)
	style.set_border_width_all(1)
	style.set_corner_radius_all(3)
	return style

func _scrim(alpha: float) -> void:
	draw_rect(Rect2(0, 0, 960, 540), Color(0.025, 0.06, 0.085, alpha))

func _text(value: String, at: Vector2, size_px: int, tint: Color, face: Font = null) -> void:
	draw_string(face if face else font, at, value, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px, tint)

func _center(value: String, y: float, size_px: int, tint: Color, face: Font = null) -> void:
	var used_font := face if face else font
	var width := used_font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px).x
	_text(value, Vector2((960 - width) * 0.5, y), size_px, tint, used_font)

func _wrap(value: String, rect: Rect2, size_px: int, tint: Color, centered := false) -> void:
	var y := rect.position.y + size_px
	for paragraph in value.split("\n"):
		var line := ""
		for word in paragraph.split(" "):
			var next := line + (" " if not line.is_empty() else "") + word
			if font.get_string_size(next, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px).x > rect.size.x and not line.is_empty():
				var x := rect.position.x + (rect.size.x - font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px).x) / 2 if centered else rect.position.x
				_text(line, Vector2(x, y), size_px, tint)
				y += size_px * 1.38
				line = word
			else:
				line = next
		var x := rect.position.x + (rect.size.x - font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, size_px).x) / 2 if centered else rect.position.x
		_text(line, Vector2(x, y), size_px, tint)
		y += size_px * 1.38
