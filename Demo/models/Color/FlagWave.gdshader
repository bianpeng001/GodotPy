shader_type spatial;
render_mode skip_vertex_transform;

uniform float _width = 0.2;
uniform float _repeat = 2.5;
uniform float _period = 3.0;

void vertex() {
	// 振幅, 越远越大
	// 振动频率, 周期
	VERTEX.x += _width*VERTEX.z*sin(VERTEX.z*_repeat+TIME*_period);
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform vec3 _color : source_color = vec3(1.0, 1.0, 1.0);

void fragment() {
	ALBEDO = _color;
	//ALPHA = 1.0;
}
