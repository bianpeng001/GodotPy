shader_type spatial;
render_mode skip_vertex_transform;


void vertex() {
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	
	UV = vec2(VERTEX.x * 0.3, VERTEX.z*0.13 + TIME*0.1 );
}

uniform sampler2D noise_tex;
uniform vec3 base_color;
uniform float surface_cutoff = 0.65;

void fragment() {
	float noise_sample = texture(noise_tex, UV).x;
	float surface_noise = noise_sample > surface_cutoff ? 1.0 : 0.0;
	ALBEDO = base_color + surface_noise;
}
