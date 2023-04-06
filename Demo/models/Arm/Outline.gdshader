//THIS SHADER MUST BE APPLIED TO A QUAD (MeshInstance) WITH A SIZE OF (2, 2)
//Extra Cull Margin on the quad should be turned up all the way!

shader_type spatial;
render_mode unshaded;

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

void fragment() {
	ALBEDO = outline_color.rgb;
	
	vec2 screen_size = vec2(textureSize(SCREEN_TEXTURE, 1));
	
	float px = 0.5/screen_size.x;
	float py = 0.5/screen_size.y;
	
	float d = texture(DEPTH_TEXTURE, SCREEN_UV).x;
	float du = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, py)).x;
	float dd = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(0.0, -py)).x;
	float dr = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(px, 0.0)).x;
	float dl = texture(DEPTH_TEXTURE, SCREEN_UV+vec2(-px, 0.0)).x;
	
	if (outline_mode == 1){
		ALPHA = 0.0 + abs(abs(d)-abs(du)) + abs(abs(d)-abs(dd)) + abs(abs(d)-abs(dl)) + abs(abs(d)-abs(dr));
			
		ALPHA *= 1000.0*outline_intensity;
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
