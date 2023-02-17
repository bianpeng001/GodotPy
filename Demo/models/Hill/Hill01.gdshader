shader_type spatial;
render_mode skip_vertex_transform;

uniform sampler2D heightmap;
uniform sampler2D normalmap;

void vertex() {
	VERTEX.y += texture(heightmap, UV.xy).x;
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
    //NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	COLOR = vec4(0.0, 0.2, 0.0, 1.0);
}
void fragment() {
	NORMAL_MAP = texture(normalmap, UV.xy).xyz;
	ALBEDO = COLOR.xyz;
}
