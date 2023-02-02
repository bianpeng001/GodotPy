extends Node2D

var enter_game_button

# Called when the node enters the scene tree for the first time.
func _ready():
	enter_game_button = get_node('EnterGame')
	enter_game_button.connect('pressed', self.on_enter_game)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func on_enter_game():
	get_tree().change_scene_to_file('res://main.tscn')
	
	
