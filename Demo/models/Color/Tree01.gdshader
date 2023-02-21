shader_type spatial;
render_mode skip_vertex_transform;

// 四元组乘法
vec4 quat_mul(vec4 a, vec4 b) {
	vec4 v;
	v.w = a.w*b.w - dot(a.xyz, b.xyz);
	v.xyz = a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz);
	return v;
}

uniform vec3 axis = vec3(1, 0, 0);
uniform float angle = 0;

void vertex() {
	float half_angle = angle * 0.5;
	vec4 q;
	
	half_angle *= sin(TIME*2.0);
	
	// v1 = qvq'
	// qq' = 1
	q.w = cos(half_angle);
	q.xyz = sin(half_angle)*axis;
	
	vec4 v = quat_mul(q, vec4(VERTEX.xyz, 0));
	q.xyz *= -1.0;
	v = quat_mul(v, q);
	
	VERTEX = (MODELVIEW_MATRIX * vec4(v.xyz, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform sampler2D albedomap;

void fragment() {
	ALBEDO = texture(albedomap, UV).xyz;
}

