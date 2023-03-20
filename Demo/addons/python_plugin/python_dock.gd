extends Control

func _ready():
	print('python dock ready')
	get_node('Button').connect("pressed", self.on_button_click)

	
func _process(delta):
	pass

func on_button_click():
	print('11111')
	
	
