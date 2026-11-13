#include "/lib/color.glsl"

in vec4 vertexTint;

#ifndef SKIP_DISTANCE_FOG
#include "/lib/fog.glsl"
in vec3 fogViewPosition;
flat in vec2 fogRamp;
flat in vec3 fogHorizon;
flat in vec3 fogSunGlow;
flat in vec3 fogUp;
flat in vec3 fogHorizontalSun;
#endif

#ifdef BASE_TEXTURE
uniform sampler2D gtexture;
in vec2 atlasUV;
#endif
#ifdef LIGHTMAP
uniform sampler2D lightmap;
in vec2 lightmapUV;
#endif
#ifdef STYLIZED_WATER
#include "/lib/water.glsl"
#endif
#ifdef TERRAIN_LIGHTING
#define SHADOW_RECEIVER_FRAGMENT
#include "/lib/shadows.glsl"
in vec3 terrainDirectLight;
in vec4 terrainFill;
#endif

/* RENDERTARGETS: 0 */

void main() {
#ifdef STYLIZED_WATER
    if (waterMaterial == 1) {
        vec4 water = shadeWater();
#ifndef WATER_DEPTH_DEBUG
        water.rgb = applyDistanceFog(water.rgb, fogViewPosition, fogRamp, fogHorizon,
                                     fogSunGlow, fogUp, fogHorizontalSun);
#endif
        gl_FragData[0] = water;
        return;
    }
#endif
    vec4 surface = vertexTint;

#ifdef BASE_TEXTURE
    surface *= texture(gtexture, atlasUV);
#endif
    // The terrain path retains the lightmap as fill and adds direct light in
    // linear space. Other routes retain the scaffold's encoded modulation.
#ifdef TERRAIN_LIGHTING
    vec3 fill = decodeSrgb(texture(lightmap, lightmapUV).rgb);
    float sunVisibility = terrainSunVisibility(fogViewPosition, terrainDirectLight.r);
    vec3 illumination = fill * terrainFill.rgb + terrainDirectLight * sunVisibility + terrainFill.a;
    vec3 linearColor = decodeSrgb(surface.rgb) * illumination;
#else
#ifdef LIGHTMAP
    surface.rgb *= texture(lightmap, lightmapUV).rgb;
#endif
    vec3 linearColor = decodeSrgb(surface.rgb);
#endif
#ifdef WEATHER_COLOR
    // Keep the streaks' alpha and brightness while softening their blue cast.
    float luminance = dot(linearColor, vec3(0.2126, 0.7152, 0.0722));
    linearColor = mix(linearColor, vec3(luminance), 0.72);
#endif
#ifndef SKIP_DISTANCE_FOG
    linearColor = applyDistanceFog(linearColor, fogViewPosition, fogRamp, fogHorizon,
                                   fogSunGlow, fogUp, fogHorizontalSun);
#endif
    // Iris applies the render type's alpha test to this output.
    gl_FragData[0] = vec4(linearColor, surface.a);
}
