#version 330

in vec3 a_position;
in vec2 a_texture;

out vec2 v_texture;

uniform float pos_x;
uniform float pos_y;

void main() {
    gl_Position = vec4(vec3(a_position.x+pos_x, a_position.y+pos_y, 0.0), 1.0);
    v_texture = a_texture;
}