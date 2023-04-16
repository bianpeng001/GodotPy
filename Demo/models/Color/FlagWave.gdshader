shader_type spatial;
render_mode skip_vertex_transform;

// 振幅, 越远越大
uniform float _width = 0.2;
// 波浪的数量
uniform float _repeat = 2.5;
// 振动频率
uniform float _period = 3.0;

// random
float random (vec2 uv) {
    return fract(sin(dot(uv.xy,
        vec2(12.9898,78.233))) * 43758.5453123);
}

void vertex() {
	VERTEX.x += _width*VERTEX.z*sin(VERTEX.z*_repeat+TIME*_period);
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform vec3 _color : source_color = vec3(1.0, 1.0, 1.0);

void fragment() {
	ALBEDO = _color;
	//ALPHA = 1.0;
}
