shader_type spatial;
render_mode skip_vertex_transform;

uniform float _speed = 0.7;
uniform float _angle = 10;

void vertex() {
	float rad = fract(TIME * _speed);
	rad = abs(rad - 0.5)*2.0 - 0.5;
	rad = radians(rad * _angle);
	
	float x = cos(rad);
	float z = sin(rad);
	
	mat4 mat_rot_y = mat4(1.0);
	mat_rot_y[0][0] = x;
	mat_rot_y[0][2] = z;
	mat_rot_y[2][0] = -z;
	mat_rot_y[2][2] = x;
	
	VERTEX = (MODELVIEW_MATRIX * mat_rot_y * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform vec3 _color : source_color = vec3(1.0, 1.0, 1.0);

void fragment() {
	ALBEDO = _color;
	//ALPHA = 1.0;
}
