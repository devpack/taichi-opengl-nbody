#version 430

in float body_color_dist;

out vec4 fragColor;

void main() {
	//float col = (body_color_dist + 20 ) / 1.2;
	//if(col < 0.9) {
	//	col = 0.9;
	//}
	//fragColor = vec4(col, col, col, 1.0);

	//fragColor = vec4(body_color_dist, body_color_dist, body_color_dist, 1.0);

    //fragColor = vec4(1.0, 1.0, 1.0, 1.0);

    vec3 v_color = vec3(1.0, 1.0, 1.0);
    vec2 point_uv = 2.0 * gl_PointCoord - 1.0;

    float circle = smoothstep(1.0, 0.7, dot(point_uv, point_uv));
    if (circle < 0.1) discard;

    fragColor = vec4(vec3(circle * v_color), 1);
}
