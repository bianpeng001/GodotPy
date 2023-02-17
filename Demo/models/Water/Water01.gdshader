shader_type spatial;
render_mode skip_vertex_transform;

void vertex() {
	float x = VERTEX.x;
	//float z = VERTEX.z + TIME*3.0;
	x += TIME*3.0;
	//z += VERTEX.z;
	//VERTEX.y += (sin(x) + sin(z));
	VERTEX.y += sin(x);
	
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;

	vec3 x_axis = vec3(1, cos(x), 0);
	vec3 z_axis = vec3(0, 0, -1);
	//vec3 z_axis = vec3(0, cos(z), 1);
	NORMAL = normalize(cross(x_axis, z_axis));
}

void fragment() {
	// Place fragment code here.
}
