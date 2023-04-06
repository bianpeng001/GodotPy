//THIS SHADER MUST BE APPLIED TO A QUAD (MeshInstance) WITH A SIZE OF (2, 2)
//Extra Cull Margin on the quad should be turned up all the way!

shader_type spatial;
render_mode depth_test_disabled, unshaded, cull_disabled, skip_vertex_transform;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D DEPTH_TEXTURE : hint_depth_texture, filter_linear_mipmap;

uniform int outline_mode : hint_range(1, 3, 1) = 3;
uniform float outline_intensity : hint_range(0, 5) = 1;
uniform bool _round = false;
uniform float outline_bias : hint_range(-10, 10) = 0;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);

void vertex() {
	POSITION = vec4(VERTEX, 1.0);
}
float get_depth0(in sampler2D depth_texture, in vec2 screen_uv) {
	return texture(depth_texture, screen_uv).x;
}

//
// 由于深度图里面采样出来的, 不是线性值, 直接相减作为边界, 是有问题的
// 最大的问题就是对描边的敏感度不一致, 远近的物体的描边看起来不一致. 所以v1
// 里面才有对深度差值的 *1000, *5000 的一个经验值修正
//
// 详见, https://godotshaders.com/shader/depth-modulated-pixel-outline-in-screen-space/
// 应该更加有追求一些
// 所以需要加点算量, 把采样出来的深度, 还原成view空间的深度值
//
float get_linear_depth(in sampler2D depth_texture,
		in vec2 screen_uv,
		in mat4 inv_projection_matrix
		) {
	float depth0 = get_depth0(depth_texture, screen_uv);
	vec3 normalized_device_coordinates = vec3(screen_uv*2.0 - 1.0, depth0);
	vec4 view_space = inv_projection_matrix * vec4(normalized_device_coordinates, 1.0);
	vec3 pos = view_space.xyz / view_space.w;
	return -pos.z;
}



void fragment() {
	ALBEDO = outline_color.rgb;
	
	vec2 screen_size = vec2(textureSize(SCREEN_TEXTURE, 1));
	
	float px = 0.5/screen_size.x;
	float py = 0.5/screen_size.y;
	
	/*
	float d = texture(DEPTH_TEXTURE, SCREEN_UV).x;
	float du = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, py)).x;
	float dd = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, -py)).x;
	float dr = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(px, 0.0)).x;
	float dl = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(-px, 0.0)).x;
	*/
	float d = get_linear_depth(DEPTH_TEXTURE, SCREEN_UV, INV_PROJECTION_MATRIX);
	float du = get_linear_depth(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, py), INV_PROJECTION_MATRIX);
	float dd = get_linear_depth(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, -py), INV_PROJECTION_MATRIX);
	float dr = get_linear_depth(DEPTH_TEXTURE, SCREEN_UV+vec2(px, 0.0), INV_PROJECTION_MATRIX);
	float dl = get_linear_depth(DEPTH_TEXTURE, SCREEN_UV+vec2(-px, 0.0), INV_PROJECTION_MATRIX);
	
	if (outline_mode == 1){
		ALPHA = 0.0 + abs(abs(d)-abs(du)) + abs(abs(d)-abs(dd)) + abs(abs(d)-abs(dl)) + abs(abs(d)-abs(dr));
			
		ALPHA *= 1.0*outline_intensity;
	} else if (outline_mode == 2) {
		ALPHA = 0.0 + abs(abs(abs(d)-abs(du)) - abs(abs(d)-abs(dd))) + abs(abs(abs(d)-abs(dl)) - abs(abs(d)-abs(dr)));
		
		ALPHA *= 3.0*50000.0*outline_intensity;
	} else if (outline_mode == 3) {
		float dq = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(-px, py)).x;
		float de = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(px, py)).x;
		float dz = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(-px, -py)).x;
		float dc = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(px, -py)).x;
		
		ALPHA = 0.0 + abs(abs(abs(d)-abs(du)) - abs(abs(d)-abs(dd))) + abs(abs(abs(d)-abs(dl)) - abs(abs(d)-abs(dr))) + abs(abs(abs(d)-abs(dq)) - abs(abs(d)-abs(dc))) + abs(abs(abs(d)-abs(dz)) - abs(abs(d)-abs(de)));

		ALPHA *= 50000.0*outline_intensity;
	}
	
	ALPHA += outline_bias;
	
	if (_round) {
		ALPHA = round(ALPHA);
	}
	
	ALPHA *= outline_color.a;
}
