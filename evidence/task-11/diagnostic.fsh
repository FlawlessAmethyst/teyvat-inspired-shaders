#version 330 compatibility

#include "/lib/color.glsl"
#include "/lib/tonemap.glsl"

uniform sampler2D colortex0;
in vec2 sceneUV;

// Iris reads the format directive from a block comment before GLSL compilation.
/*
const int colortex0Format = RGBA16F;
*/

void main() {
    // Top: neutral SDR ramp. Middle: neutral HDR ramp. Bottom: saturated HDR ramp.
    float x = clamp((gl_FragCoord.x - 0.5) / 2559.0, 0.0, 1.0);
    vec3 sceneColor = vec3(x);
    if (gl_FragCoord.y < 960.0) sceneColor *= 4.0;
    if (gl_FragCoord.y < 480.0) sceneColor *= vec3(0.11, 1.0, 0.22);
    gl_FragColor = vec4(encodeSrgb(gradeSceneColor(sceneColor)), 1.0);
}
