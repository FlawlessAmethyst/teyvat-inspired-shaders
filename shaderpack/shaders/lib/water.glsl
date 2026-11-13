uniform sampler2D depthtex2;
uniform mat4 gbufferProjectionInverse;
uniform mat4 gbufferModelView;
uniform int isEyeInWater;
uniform float rainStrength;
uniform bool hasSkylight;
uniform bool hasCeiling;

flat in int waterMaterial;
in vec2 waterPhase;
in vec3 waterViewNormal;
flat in vec3 waterSkyZenith;
flat in vec3 waterSun;

// Trace the current pixel ray to Iris's pre-hand depth snapshot. Use a
// negative result for missing background and a distinct code for bad depth.
float waterThickness(vec3 viewRay) {
    ivec2 pixel = ivec2(gl_FragCoord.xy);
    float depth = texelFetch(depthtex2, pixel, 0).r;
    if (depth >= 1.0) {
        return -1.0;
    }
    vec2 ndc = gl_FragCoord.xy * (2.0 / vec2(textureSize(depthtex2, 0))) - 1.0;
    vec4 bottom = gbufferProjectionInverse * vec4(ndc, depth * 2.0 - 1.0, 1.0);
    if (!(bottom.w > 0.0)) {
        return -2.0;
    }
    float thickness = dot(bottom.xyz / bottom.w - fogViewPosition, viewRay);
    return thickness >= -0.015 ? max(thickness, 0.0) : -2.0;
}

vec4 shadeWater() {
    vec3 viewRay = normalize(fogViewPosition);
    vec3 illumination = decodeSrgb(texture(lightmap, lightmapUV).rgb);
    if (isEyeInWater == 1) {
#ifdef WATER_DEPTH_DEBUG
        return vec4(0.01, 0.65, 0.75, 1.0);
#endif
        return vec4(vec3(0.035, 0.24, 0.31) * illumination, 0.30);
    }

    float thickness = waterThickness(viewRay);
    float absorption = thickness < 0.0 ? 0.26 : smoothstep(0.0, 8.0, thickness);
#ifdef WATER_DEPTH_DEBUG
    if (thickness < -1.5) {
        return vec4(1.0, 0.65, 0.0, 1.0);
    }
    if (thickness < 0.0) {
        return vec4(0.85, 0.0, 0.65, 1.0);
    }
    return vec4(vec3(clamp(thickness / 12.0, 0.0, 1.0)), 1.0);
#endif

    vec3 normal = normalize(waterViewNormal);
    float top = max(0.0, dot(normal, fogUp));
    vec2 waves = cos(waterPhase);
    vec2 slope = vec2(0.043, 0.024) * waves.x + vec2(-0.019, 0.027) * waves.y;
    vec3 waveNormal = mat3(gbufferModelView) * vec3(slope.x, 0.0, slope.y);
    normal = normalize(normal + waveNormal * top);

    vec3 tint = mix(vec3(0.025, 0.34, 0.30), vec3(0.012, 0.17, 0.27), absorption);
    float rain = hasSkylight && !hasCeiling ? rainStrength : 0.0;
    tint = mix(tint, vec3(0.047, 0.14, 0.18), rain * 0.60);
    vec3 color = tint * illumination;
    float alpha = mix(0.22, 0.64, absorption);

    if (hasSkylight && !hasCeiling) {
        vec3 reflectedRay = reflect(viewRay, normal);
        float grazing = 1.0 - clamp(-dot(viewRay, normal), 0.0, 1.0);
        float reflection = (0.08 + 0.32 * grazing * grazing) * top;
        float sunFacing = dot(reflectedRay, waterSun);
        vec3 sky = skyGradient(dot(reflectedRay, fogUp), sunFacing,
                               fogHorizon, waterSkyZenith, fogSunGlow);
        // A broad crest on the analytic reflection, damped as rain settles.
        float highlight = smoothstep(0.91, 0.995, sunFacing)
                        * smoothstep(-0.03, 0.19, dot(waterSun, fogUp));
        sky += vec3(0.30, 0.25, 0.18) * highlight * (1.0 - rain);
        float exposure = smoothstep(0.32, 0.92, lightmapUV.y);
        color = mix(color, sky, reflection * exposure);
        alpha += reflection * absorption * 0.22 * exposure;
    }
    return vec4(color, alpha);
}
