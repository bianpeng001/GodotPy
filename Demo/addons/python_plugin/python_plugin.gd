@tool
extends EditorPlugin


func _enter_tree():
	print('hello python plugin')
	pass


func _exit_tree():
	# Clean-up of the plugin goes here.
	pass
