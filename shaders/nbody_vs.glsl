#version 430

in vec3 in_position;
//in vec4 in_velocity;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

//out vec4 body_color;
out float body_color_dist;

void main() {
    vec4 model_pos = m_model * vec4(in_position.xyz, 1.0);
	vec4 view_model_pos = m_view * model_pos;
	gl_Position = m_proj * view_model_pos;

	float dist = length(view_model_pos);
	float psize = 50. / dist;
	gl_PointSize = psize;

	//body_color_dist = model_pos.z;
	body_color_dist = view_model_pos.z;

    //body_color_dist = sqrt(dot(in_velocity, in_velocity));
}