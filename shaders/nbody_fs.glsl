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
    fragColor = vec4(1.0, 1.0, 1.0, 1.0);

}
