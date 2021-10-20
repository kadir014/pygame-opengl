#version 330


in vec2 v_texture;
in vec3 v_normal;

out vec4 out_color;

uniform sampler2D shadowMap;


void main() {
    //out_color = vec4(vec3(texture(shadowMap, vec3(v_texture.xy, 1.0))), 1.0);
    //float depthValue = texture(shadowMap, vec3(v_texture, 1.0));
    out_color = vec4(texture(shadowMap, v_texture).rgb, 1.0);
    //out_color = vec4(vec3(depthValue), 1.0);
}