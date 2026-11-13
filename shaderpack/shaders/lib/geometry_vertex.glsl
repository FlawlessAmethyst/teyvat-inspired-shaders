out vec4 vertexTint;

#ifndef SKIP_DISTANCE_FOG
#include "/lib/fog.glsl"
uniform vec3 sunPosition;
uniform vec3 upPosition;
uniform float far;
uniform float rainStrength;
uniform bool hasSkylight;
uniform bool hasCeiling;
uniform int isEyeInWater;
#ifdef FOG_FALLBACK_STAGE
uniform int renderStage;
#endif

out vec3 fogViewPosition;
flat out vec2 fogRamp;
flat out vec3 fogHorizon;
flat out vec3 fogSunGlow;
flat out vec3 fogUp;
flat out vec3 fogHorizontalSun;
#endif

#ifdef BASE_TEXTURE
out vec2 atlasUV;
#endif
#ifdef LIGHTMAP
out vec2 lightmapUV;
#endif
#ifdef STYLIZED_WATER
in vec2 mc_Entity;
uniform mat4 gbufferModelViewInverse;
uniform ivec3 cameraPositionInt;
uniform vec3 cameraPositionFract;
uniform float frameTimeCounter;
flat out int waterMaterial;
out vec2 waterPhase;
out vec3 waterViewNormal;
flat out vec3 waterSkyZenith;
flat out vec3 waterSun;
#endif
#ifdef TERRAIN_LIGHTING
in vec2 mc_Entity;
#include "/lib/terrain_lighting.glsl"
#define SHADOW_RECEIVER_VERTEX
#include "/lib/shadows.glsl"
out vec3 terrainDirectLight;
out vec4 terrainFill;
#endif

void main() {
#ifdef SKIP_DISTANCE_FOG
    gl_Position = ftransform();
#else
    vec4 viewPosition = gl_ModelViewMatrix * gl_Vertex;
    gl_Position = gl_ProjectionMatrix * viewPosition;
    fogViewPosition = viewPosition.xyz;
    fogUp = normalize(upPosition);
    vec3 sunDirection = normalize(sunPosition);
    float sunElevation = dot(sunDirection, fogUp);
    fogHorizontalSun = sunDirection - fogUp * sunElevation;
    bool outdoors = hasSkylight && !hasCeiling;
    float rain = outdoors ? rainStrength : 0.0;
    vec3 zenith;
    skyPalette(sunElevation, rain, fogHorizon, zenith, fogSunGlow);
    bool worldFog = true;
#ifdef FOG_FALLBACK_STAGE
    // These draws share a fallback with world geometry. Their own effects
    // keep the existing color path.
    worldFog = renderStage != MC_RENDER_STAGE_CLOUDS
                  && renderStage != MC_RENDER_STAGE_RAIN_SNOW
                  && renderStage != MC_RENDER_STAGE_HAND_SOLID
                  && renderStage != MC_RENDER_STAGE_HAND_TRANSLUCENT;
#endif
    fogRamp = vec2(0.0);
    if (worldFog && isEyeInWater == 1) {
        fogRamp = submergedFogRamp();
    } else if (worldFog && outdoors && isEyeInWater == 0) {
        fogRamp = distanceFogRamp(far, rain);
    }
#endif
    vertexTint = gl_Color;

#ifdef BASE_TEXTURE
    atlasUV = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
#endif
#ifdef LIGHTMAP
    lightmapUV = (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy;
#endif
#ifdef STYLIZED_WATER
    waterMaterial = mc_Entity.x == 10001.0 ? 1 : 0;
    if (waterMaterial == 1) {
        // Both wave vectors repeat on a 64-block tile and on Iris's clock wrap.
        vec3 worldOffset = (gbufferModelViewInverse * viewPosition).xyz;
        vec2 position = vec2(cameraPositionInt.xz & 63) + cameraPositionFract.xz
                      + worldOffset.xz;
        const float turn = 6.283185307;
        waterPhase = vec2(dot(position, vec2(9.0, 5.0)),
                          dot(position, vec2(-11.0, 15.0))) * (turn / 64.0);
        waterPhase += frameTimeCounter * (turn / 3600.0) * vec2(-640.0, 880.0);
        waterViewNormal = gl_NormalMatrix * gl_Normal;
        waterSkyZenith = zenith;
        waterSun = sunDirection;
    }
#endif
#ifdef TERRAIN_LIGHTING
    bool leaves = mc_Entity.x == 10002.0;
    if (leaves || mc_Entity.x == 10003.0) {
        vertexTint.rgb = vegetationTint(vertexTint.rgb, leaves);
    }
    vec3 viewNormal = normalize(gl_NormalMatrix * gl_Normal);
    float facing = max(0.0, dot(viewNormal, sunDirection));
    vertexTerrainLighting(lightmapUV, facing, sunElevation, rain, outdoors,
                          leaves, mc_Entity.x == 10004.0, terrainDirectLight, terrainFill);
    vertexShadowReceiver(viewPosition, facing, sunElevation, outdoors);
#endif
}
