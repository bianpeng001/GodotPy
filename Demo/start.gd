extends Node

var enter_game_button

func _ready():
	enter_game_button = get_node('EnterGame')
	enter_game_button.connect('pressed', self.on_enter_game)

func _process(delta):
	pass

func on_enter_game():
	get_tree().change_scene_to_file('res://main.tscn')
