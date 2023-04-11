extends Node3D

var omniLight;

func _ready():
	self.omniLight = self.find_child('OmniLight3D');
	randomize()

func _process(delta):
	var f = sin(Time.get_ticks_msec()*0.003 + randf()*0.05);
	self.omniLight.light_energy = 2.5 + 0.5*f;
	self.omniLight.set_position(Vector3(0, 2.0 + 0.2*f, 0));
