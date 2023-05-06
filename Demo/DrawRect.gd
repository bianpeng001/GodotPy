extends Node2D


func _ready():
	pass
	
func _process(delta):
	queue_redraw()

func _draw():
	draw_line(Vector2(100.5, 100.5), Vector2(200.5, 200.5), Color.GREEN, 1.0)
	
