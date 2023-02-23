shader_type spatial;
render_mode skip_vertex_transform;

// 这个用来做固定的UV，没有做时间偏移
// 用来做一点点溶解的效果，波浪破碎感
varying vec2 UV0;

void vertex() {
	// tile
	UV0 = vec2(VERTEX.x * 0.3, VERTEX.z * 0.08);
	UV = UV0;
	//# uv move by time
	UV.y += TIME*0.03;
	UV.x += TIME*0.02;
	
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

uniform sampler2D noise_tex;
uniform vec3 base_color = vec3(0.0, 0.576, 0.835);
uniform float surface_cutoff = 0.65;

void fragment() {
	vec2 uv2 = UV;
	uv2.x += texture(noise_tex, UV0).x * 0.05;
	float noise_sample = texture(noise_tex, uv2).x;
	float surface_noise = noise_sample > surface_cutoff ? 1.0 : 0.0;
	
	ALBEDO = base_color + surface_noise;
}
