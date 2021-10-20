#version 330

in vec3 v_texture;

out vec4 out_color;

uniform samplerCube gCubemapTexture;

void main() {
    out_color = texture(gCubemapTexture, v_texture);
}