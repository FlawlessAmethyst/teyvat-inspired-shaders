vec3 vegetationTint(vec3 tint, bool leaves) {
    // Scale the correction with the original tint so vertex AO and biome
    // variation carry through. Neutral faces include the dirt on grass blocks.
    float green = max(0.0, tint.g - max(tint.r, tint.b));
    vec3 shift = leaves ? vec3(0.0, -0.025, 0.20) : vec3(0.10, -0.19, 0.06);
    return tint + green * shift;
}

// Iris supplies both directions in view space. Resolve the lightmap scale
// and direct sun at vertices so each fragment only combines the two terms.
void vertexTerrainLighting(vec2 lightmapUV, float facing, float elevation, float rain,
                           bool outdoors, bool leafFill, bool lightSource,
                           out vec3 direct, out vec4 fill) {
    if (!outdoors) {
        direct = vec3(0.0);
        fill = vec4(1.0, 1.0, 1.0, 0.0);
        return;
    }

    float daylight = smoothstep(-0.025, 0.24, elevation);
    float goldenHour = 1.0 - smoothstep(0.16, 0.65, elevation);
    vec3 sunColor = mix(vec3(1.0, 0.92, 0.78), vec3(1.0, 0.63, 0.34), goldenHour);

    // Recover levels 0 through 15 from the centers of the 16 lightmap texels.
    vec2 lightLevel = clamp((lightmapUV * 16.0 - 0.5) / 15.0, 0.0, 1.0);
    float skyExposure = smoothstep(0.35, 1.0, lightLevel.y);
    float sunWeight = daylight * skyExposure * (1.0 - 0.6 * lightLevel.x);
    float directWeight = sunWeight * facing * (1.0 - 0.90 * rain);

    direct = sunColor * (0.56 * directWeight);

    // The lightmap supplies the base intensity and local block-light color.
    // Fade the tint where there is little skylight, bright block light or strong sun.
    float skyFillWeight = lightLevel.y * (1.0 - lightLevel.x) * (1.0 - directWeight);
    vec3 tintOffset = mix(vec3(-0.16, 0.02, 0.28), vec3(-0.06, 0.09, 0.25), daylight);
    // Reserve less lightmap intensity for direct light as the sky closes in.
    fill.rgb = (1.0 - mix(0.45, 0.23, rain) * sunWeight) * (1.0 + skyFillWeight * tintOffset);

    // Suggest transmitted daylight on off-sun leaf faces using the existing
    // skylight and block-light gates. Direct sunlight keeps its shadow term.
    if (leafFill) {
        fill.rgb *= 1.0 + 0.28 * sunWeight * (1.0 - facing);
    }

    // Lift dark terrain in open night and under cover. Fade the lift out
    // across the light pool so the engine's block light still shapes it.
    float lowLight = 1.0 - daylight * lightLevel.y;
    float lift = 1.0 - smoothstep(0.10, 0.78, lightLevel.x);
    fill.a = 0.024 * lowLight * lift;
    if (lightSource) {
        fill.rgb *= 1.0 - 0.32 * lowLight;
    }
}
