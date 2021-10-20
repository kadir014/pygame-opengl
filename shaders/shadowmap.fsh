#version 330

//out float fragmentdepth;

void main() {
    gl_FragDepth = gl_FragCoord.z;
}