#version 330 compatibility

#include "/lib/color.glsl"
#include "/lib/tonemap.glsl"

uniform sampler2D colortex0;
in vec2 sceneUV;
flat in float saturationBoost;

// Iris reads the format directive from a block comment before GLSL compilation.
/*
const int colortex0Format = RGBA16F;
*/

void main() {
    vec3 sceneColor = texture(colortex0, sceneUV).rgb;
    gl_FragColor = vec4(encodeSrgb(gradeSceneColor(sceneColor, saturationBoost)), 1.0);
}
