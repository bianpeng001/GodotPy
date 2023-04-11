extends Node

#
# 先直接场景
#
func _ready():
	get_tree().change_scene_to_file('res://campfire_scene.tscn')
