#version 330

in vec3 a_position;
in vec2 a_texture;
in vec3 a_normal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 lightprojection;
uniform mat4 lightview;

uniform vec3 angle;
uniform vec3 scale;

out vec2 v_texture;
out vec3 v_normal;
out vec3 FragPos;
out vec4 lightspace;


vec3 rotx(in vec3 pos, in float angle) {
    return mat3(
        1, 0,        0,
        0, cos(angle), -sin(angle),
        0, sin(angle), cos(angle)
    ) * pos;
}

vec3 roty(in vec3 pos, in float angle) {
    return mat3(
        cos(angle),  0, sin(angle),
        0,           1, 0,
        -sin(angle), 0, cos(angle)
    ) * pos;
}

vec3 rotz(in vec3 pos, in float angle) {
    return mat3(
        cos(angle), -sin(angle), 0,
        sin(angle), cos(angle),  0,
        0,          0,           1
    ) * pos;
}


void main() {
    vec3 spos = vec3(a_position.x*scale.x, a_position.y*scale.y, a_position.z*scale.z);
    vec3 pos = rotz(rotx(roty(spos, angle.y), angle.x), angle.z);
    vec3 normal = rotz(rotx(roty(a_normal, angle.y), angle.x), angle.z);
    
    vec4 glpos = projection * view * model * vec4(pos, 1.0);
    v_texture = a_texture;
    v_normal = mat3(transpose(inverse(model))) * normal;
    FragPos = vec3(model * vec4(pos, 1.0));
    lightspace = vec4(FragPos, 1.0) * (lightprojection*lightview);
    gl_Position = glpos;
}