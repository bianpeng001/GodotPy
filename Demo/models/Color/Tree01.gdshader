shader_type spatial;
render_mode skip_vertex_transform;

vec4 quat_mul(vec4 a, vec4 b) {
	vec4 result;
	result.w = a.w*b.w - dot(a.xyz, b.xyz);
	result.xyz = a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz);
	return result;
}

uniform vec3 axis = vec3(1, 0, 0);
uniform float angle = 0;

void vertex() {
	float half_angle = angle * 0.5;
	vec4 quat;
	
	half_angle *= sin(TIME*2.0);
	
	quat.w = cos(half_angle);
	quat.xyz = sin(half_angle)*axis;
	
	vec4 qv = quat_mul(quat, vec4(VERTEX.xyz, 0));
	quat.xyz *= -1.0;
	qv = quat_mul(qv, quat);
	
	VERTEX = (MODELVIEW_MATRIX * vec4(qv.xyz, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform sampler2D albedomap;

void fragment() {
	ALBEDO = texture(albedomap, UV).xyz;
}

