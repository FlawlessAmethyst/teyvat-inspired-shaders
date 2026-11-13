#version 330 compatibility

#include "/lib/sky.glsl"

uniform vec3 sunPosition;
uniform vec3 upPosition;
uniform mat4 gbufferModelViewInverse;
uniform ivec3 cameraPositionInt;
uniform vec3 cameraPositionFract;
uniform float eyeAltitude;
uniform float frameTimeCounter;
uniform float rainStrength;

out vec3 viewRay;
out vec3 cloudWorldRay;
out vec4 vertexTint;
flat out vec3 skyUp;
flat out vec3 skySun;
flat out vec3 skyHorizon;
flat out vec3 skyZenith;
flat out vec3 skySunGlow;
flat out vec3 cloudPlane;
flat out vec2 cloudLightDirection;
flat out vec3 cloudBase;
flat out vec3 cloudRim;

void main() {
    gl_Position = ftransform();
    vertexTint = gl_Color;

    // Interpolate the unnormalized ray so the horizon mesh and sky disc
    // evaluate the same direction at a given screen pixel.
    viewRay = (gl_ModelViewMatrix * gl_Vertex).xyz;
    cloudWorldRay = mat3(gbufferModelViewInverse) * viewRay;
    skyUp = normalize(upPosition);
    skySun = normalize(sunPosition);
    float sunElevation = dot(skySun, skyUp);
    skyPalette(sunElevation, rainStrength, skyHorizon, skyZenith, skySunGlow);

    // Follow absolute world XZ. The slow drift closes when Iris's clock wraps.
    float phase = frameTimeCounter * (6.2831853 / 3600.0);
    vec2 origin = vec2(cameraPositionInt.xz & 32767) + cameraPositionFract.xz;
    cloudPlane.xz = origin + 320.0 * vec2(sin(phase), cos(phase) - 1.0);
    cloudPlane.y = 288.0 - eyeAltitude;
    cloudLightDirection = (mat3(gbufferModelViewInverse) * skySun).xz + vec2(-0.26, 0.19);

    float twilight = smoothstep(-0.32, -0.065, sunElevation);
    float day = smoothstep(0.035, 0.46, sunElevation);
    cloudBase = mix(vec3(0.009, 0.016, 0.047), vec3(0.31, 0.21, 0.30), twilight);
    cloudBase = mix(cloudBase, vec3(0.40, 0.50, 0.63), day);
    cloudRim = mix(vec3(0.022, 0.036, 0.082), vec3(0.79, 0.40, 0.31), twilight);
    cloudRim = mix(cloudRim, vec3(0.90, 0.89, 0.81), day);

    // Keep some structure in the overcast deck while following the sky's time of day.
    cloudBase = mix(cloudBase, skyZenith * 0.85, rainStrength);
    cloudRim = mix(cloudRim, skyHorizon * 1.10, rainStrength);
}
