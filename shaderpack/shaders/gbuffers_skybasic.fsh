#version 330 compatibility

#include "/lib/color.glsl"
#include "/lib/sky.glsl"
#include "/lib/clouds.glsl"

uniform int renderStage;
uniform int isEyeInWater;
uniform bool hasSkylight;
uniform bool hasCeiling;
uniform float rainStrength;

in vec3 viewRay;
in vec3 cloudWorldRay;
in vec4 vertexTint;
flat in vec3 skyUp;
flat in vec3 skySun;
flat in vec3 skyHorizon;
flat in vec3 skyZenith;
flat in vec3 skySunGlow;
flat in vec3 cloudPlane;
flat in vec2 cloudLightDirection;
flat in vec3 cloudBase;
flat in vec3 cloudRim;

/* RENDERTARGETS: 0 */

void main() {
    if (hasSkylight && !hasCeiling && isEyeInWater == 0) {
        // The procedural lobe supplies the color of the vanilla sunrise/sunset fan.
        if (renderStage == MC_RENDER_STAGE_SUNSET) {
            discard;
        }
        if (renderStage == MC_RENDER_STAGE_SKY) {
            vec3 ray = normalize(viewRay);
            float elevation = dot(ray, skyUp);
            float sunFacing = dot(ray, skySun);
            vec3 color = skyGradient(elevation, sunFacing,
                                     skyHorizon, skyZenith, skySunGlow);
            vec2 cloud = sampleCloudDeck(cloudWorldRay, elevation, cloudPlane,
                                         cloudLightDirection, rainStrength);
            color = mix(color, cloudColor(cloud.y, skySunwardWeight(sunFacing),
                                         cloudBase, cloudRim, rainStrength), cloud.x);
            // Stable, sub-code noise softens display quantization in clear gradients.
            float noise = fract(52.9829189 * fract(dot(gl_FragCoord.xy,
                                                     vec2(0.06711056, 0.00583715)))) - 0.5;
            color += noise * (0.001 + 0.003 * color);
            gl_FragData[0] = vec4(color, 1.0);
            return;
        }
        if (renderStage == MC_RENDER_STAGE_STARS) {
            float elevation = dot(normalize(viewRay), skyUp);
            float cloudOpacity = sampleCloudDeck(cloudWorldRay, elevation, cloudPlane,
                                                 cloudLightDirection, rainStrength).x;
            gl_FragData[0] = vec4(decodeSrgb(vertexTint.rgb) * (1.0 - cloudOpacity),
                                 vertexTint.a);
            return;
        }
    }

    // Stars, the void plane and other untextured sky draws retain their vertex tint.
    gl_FragData[0] = vec4(decodeSrgb(vertexTint.rgb), vertexTint.a);
}
