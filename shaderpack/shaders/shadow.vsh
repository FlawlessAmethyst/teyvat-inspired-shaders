#version 330 compatibility

out vec2 casterUV;
out float casterAlpha;

void main() {
    gl_Position = ftransform();
    casterUV = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    casterAlpha = gl_Color.a;
}
