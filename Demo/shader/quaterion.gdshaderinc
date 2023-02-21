
// 四元组乘法
vec4 quat_mul(vec4 a, vec4 b) {
	vec4 v;
	v.w = a.w*b.w - dot(a.xyz, b.xyz);
	v.xyz = a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz);
	return v;
}
