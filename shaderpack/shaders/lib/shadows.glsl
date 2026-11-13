// One orthographic map. The receiver fades out before the caster cull range.
const int shadowMapResolution = 1024;
const float shadowDistance = 64.0;
const float shadowDistanceRenderMul = 1.0;
const float shadowIntervalSize = 0.0625;
const bool shadowHardwareFiltering = true;
const bool shadowtex0Nearest = false;

#ifdef SHADOW_RECEIVER_VERTEX
uniform mat4 gbufferModelViewInverse;
uniform mat4 shadowModelView;
uniform mat4 shadowProjection;

out vec3 terrainShadowPosition;
flat out vec2 terrainShadowBiasAndWeight;

void vertexShadowReceiver(vec4 viewPosition, float facing, float sunElevation,
                          bool outdoors) {
    vec4 cameraRelative = gbufferModelViewInverse * viewPosition;
    vec4 shadowView = shadowModelView * cameraRelative;
    vec3 clipPosition = (shadowProjection * shadowView).xyz;
    terrainShadowPosition = clipPosition * 0.5 + 0.5;

    // Cover a neighboring texel on a tilted plane. Limit the slope term at
    // grazing angles, where shadow contrast also tapers to protect contact.
    const float texelBlocks = (2.0 * shadowDistance) / float(shadowMapResolution);
    float slope = sqrt(max(0.0, 1.0 - facing * facing)) / max(0.30, facing);
    float biasBlocks = 0.012 + texelBlocks * min(1.65, 1.35 * slope);
    float depthPerBlock = -0.5 * shadowProjection[2][2];
    float weight = outdoors ? smoothstep(0.05, 0.22, sunElevation)
                            * smoothstep(0.12, 0.34, facing) : 0.0;
    terrainShadowBiasAndWeight = vec2(biasBlocks * depthPerBlock, weight);
}
#endif

#ifdef SHADOW_RECEIVER_FRAGMENT
uniform sampler2DShadow shadowtex0;
in vec3 terrainShadowPosition;
flat in vec2 terrainShadowBiasAndWeight;

float terrainSunVisibility(vec3 viewPosition, float directLight) {
    float weight = terrainShadowBiasAndWeight.y;
    if (weight <= 0.0 || directLight <= 0.0) {
        return 1.0;
    }

    const float fadeStart = shadowDistance - 16.0;
    const float fadeEnd = shadowDistance - 4.0;
    float distanceSquared = dot(viewPosition, viewPosition);
    float rangeFade = 1.0 - smoothstep(fadeStart * fadeStart, fadeEnd * fadeEnd,
                                      distanceSquared);
    vec3 coord = terrainShadowPosition;
    vec2 mapEdge = min(coord.xy, 1.0 - coord.xy);
    float edgeFade = smoothstep(0.01, 0.08, min(mapEdge.x, mapEdge.y));
    weight *= rangeFade * edgeFade;
    if (weight <= 0.0 || coord.z <= 0.0 || coord.z >= 1.0) {
        return 1.0;
    }

    // One lookup blends four neighboring depth comparisons in hardware.
    float lit = textureLod(shadowtex0, vec3(coord.xy, coord.z - terrainShadowBiasAndWeight.x), 0.0);
    return mix(1.0, lit, weight);
}
#endif
