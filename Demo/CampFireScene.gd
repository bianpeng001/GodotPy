extends Node3D

var omniLight;

func _ready():
	self.omniLight = self.find_child('OmniLight3D');
	randomize()

func _process(delta):
	self.omniLight.light_energy = 2.5 + 0.5*sin(
			Time.get_ticks_msec()*0.005 + randf()*0.05);
