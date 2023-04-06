//
// 这是一个加的屏幕特效, 后处理, 就是把整个屏幕颜色改一下
// 实测这几个render_mode是必要的
// 在可视范围内, 放了一个2x2的Quad, 用来把几何坐标[-1,1], 直接当做投影的屏幕坐标
//
shader_type spatial;
render_mode depth_test_disabled, unshaded, cull_disabled, skip_vertex_transform;

void vertex() {
	POSITION = vec4(VERTEX, 1.0);
}

void fragment() {
	ALBEDO = vec3(0.0, 1.0, 0.0);
	ALPHA = 0.5;
}

