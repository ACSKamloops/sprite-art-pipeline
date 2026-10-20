extends Node
var events: Array = []
var player: AnimationPlayer
func record_event(value: Dictionary) -> void:
 events.append({"name":value.name,"source_tick":value.at_tick,"player_position_seconds":player.current_animation_position})
