#version 330

in vec3 a_position;
in vec2 a_texture;
in vec3 a_normal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;
out vec3 v_normal;


void main() {
    vec4 glpos = projection * view * model * vec4(a_position, 1.0);
    gl_Position = glpos;
    v_texture = a_texture;
    v_normal = mat3(transpose(inverse(model))) * a_normal;
}