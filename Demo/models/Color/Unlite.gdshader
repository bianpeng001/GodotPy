shader_type spatial;
render_mode skip_vertex_transform;

void vertex() {
	float rad = fract(TIME*0.7);
	rad = abs(rad - 0.5)*2.0 - 0.5;
	rad = 45.0 + rad * sin(radians(10.0));
	
	mat4 mat_rot_y = mat4(1.0);
	mat_rot_y[0][0] = cos(rad);
	mat_rot_y[0][2] = sin(rad);
	mat_rot_y[2][0] = -sin(rad);
	mat_rot_y[2][2] = cos(rad);
	
	VERTEX = (MODELVIEW_MATRIX * mat_rot_y * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform vec3 _color : source_color;

void fragment() {
	ALBEDO = _color;
}
