#version 330

in vec3 a_position;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main() {
    gl_Position = model * projection * view * vec4(a_position, 1.0);
}