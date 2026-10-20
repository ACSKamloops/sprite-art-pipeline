extends Node2D
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
var timeline: Dictionary
var completed_plays: int = 0
func _ready() -> void:
    timeline = JSON.parse_string(FileAccess.get_file_as_string("res://timeline.json"))
    sprite.frame_changed.connect(_apply_pivot)
    sprite.animation_finished.connect(_on_finished)
    _apply_pivot()
    sprite.play(&"clip")
func _apply_pivot() -> void:
    var p = timeline["frames"][sprite.frame]["pivot"]
    sprite.offset = -Vector2(p[0], p[1])
func restart() -> void:
    completed_plays = 0
    sprite.stop()
    _apply_pivot()
    sprite.play(&"clip")
func _on_finished() -> void:
    completed_plays += 1
    var count: int = int(timeline.get("play_count", 1))
    if count > 1 and completed_plays < count:
        sprite.stop()
        sprite.play(&"clip")
