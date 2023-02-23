// 用vec4 表示一个quaternion(s,V)
// vec4.w => s
// vec4.xyz => V


// 四元组乘法
// q1 = (s, V) q2 = (t, U)
// q1 q2 = (st - dot(V,U), sU + tV + cross(V, U))
vec4 quat_mul(vec4 a, vec4 b) {
	vec4 v;
	v.w = a.w*b.w - dot(a.xyz, b.xyz);
	v.xyz = a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz);
	return v;
}
