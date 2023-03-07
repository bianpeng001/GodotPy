@tool
extends EditorPlugin

func _enter_tree():
	print('init python plugin')
	add_tool_menu_item("Exec Python", self.on_exec_python)

func on_exec_python():
	print('exec python')

func _exit_tree():
	# Clean-up of the plugin goes here.
	remove_tool_menu_item("Exec Python")
	pass
