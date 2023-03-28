shader_type spatial;
//render_mode unshaded;


uniform sampler2D base_tex;
uniform sampler2D blend_tex;

void fragment() {
	vec3 color1 = texture(base_tex, COLOR.xy).xyz;
	vec3 color2 = texture(base_tex, COLOR.zw).xyz;
	vec3 blend = texture(blend_tex, UV).xyz;
	ALBEDO = color1 * blend + color2 * (vec3(1,1,1) - blend);
	//ALBEDO = color1;
	//ALBEDO= color1*blend;
	ALPHA = 1.0;
	
}

void light() {
    DIFFUSE_LIGHT += clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION * ALBEDO;
}
