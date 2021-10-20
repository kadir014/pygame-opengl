#version 330

in vec3 a_position;

//uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 v_texture;

void main() {
    vec4 pos = projection * view * vec4(a_position, 1.0);
    gl_Position = pos.xyww;
    v_texture = a_position;
}