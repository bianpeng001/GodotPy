shader_type spatial;
void vertex() {
	
}

uniform vec3 _color : source_color;

void fragment() {
	ALBEDO = _color;
}
