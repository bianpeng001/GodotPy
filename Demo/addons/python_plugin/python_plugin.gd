@tool
extends EditorPlugin

var dock

func _enter_tree():
	print('init python plugin')
	add_tool_menu_item("Exec Python", self.on_exec_python)
	
	dock = preload('res://addons/python_plugin/python_dock.tscn').instantiate()
	add_control_to_dock(DOCK_SLOT_LEFT_UL, dock)
	
	var btn = dock.find_child("Button")
	btn.pressed.connect(click) 

func click():
	FPyObject.call_python_func("game.editor_plugin", "say_hello")
	
func _exit_tree():
	remove_tool_menu_item("Exec Python")
	remove_control_from_docks(dock)
	dock.free()

func on_exec_python():
	print('on_exec_python')

