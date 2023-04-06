shader_type spatial;
render_mode depth_test_disabled, unshaded, cull_disabled, skip_vertex_transform;

void vertex() {
	POSITION = vec4(VERTEX, 1.0);
}

void fragment() {
	ALBEDO = vec3(0.0, 1.0, 0.0);
	ALPHA = 0.5;
}

