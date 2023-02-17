shader_type spatial;
render_mode skip_vertex_transform;

uniform sampler2D heightmap;
uniform sampler2D normalmap;

void vertex() {
	float h = texture(heightmap, UV.xy).x;
	VERTEX.y += h;
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
    //NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	//COLOR = vec4(0.11, 0.39, 0.24*h, 1.0);
	COLOR = vec4(0.23, 0.48, 0.5*h, 1.0);
}
void fragment() {
	NORMAL_MAP = texture(normalmap, UV.xy).xyz;
	ALBEDO = COLOR.xyz;
}
