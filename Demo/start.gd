extends Node

var timer = Timer.new()

#
# 先直接场景
#
func _ready():
	timer.connect("timeout", self.enter_game)
	timer.wait_time = 1
	timer.one_shot = true
	self.add_child(timer)
	timer.start()
	
	
func enter_game():
	get_tree().change_scene_to_file.bind('res://campfire_scene.tscn').call_deferred()
	
	
