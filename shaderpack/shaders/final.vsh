#version 330 compatibility

out vec2 sceneUV;
flat out float saturationBoost;

uniform bool hasSkylight;
uniform bool hasCeiling;
uniform float rainStrength;

void main() {
    gl_Position = ftransform();
    sceneUV = gl_MultiTexCoord0.xy;
    float rain = hasSkylight && !hasCeiling ? rainStrength : 0.0;
    saturationBoost = mix(0.24, -0.12, rain);
}
