// Palette anchors are scene-linear RGB and pass through the existing final grade.
void skyPalette(float sunElevation, float rain, out vec3 horizon, out vec3 zenith,
                out vec3 sunGlow) {
    float twilight = smoothstep(-0.32, -0.065, sunElevation);
    float day = smoothstep(0.035, 0.46, sunElevation);

    horizon = mix(vec3(0.014, 0.027, 0.075), vec3(0.23, 0.195, 0.33), twilight);
    horizon = mix(horizon, vec3(0.34, 0.63, 0.86), day);
    zenith = mix(vec3(0.0045, 0.009, 0.036), vec3(0.125, 0.10, 0.225), twilight);
    zenith = mix(zenith, vec3(0.035, 0.245, 0.61), day);
    sunGlow = vec3(0.68, 0.25, 0.055) * (twilight * (1.0 - day));

    if (rain > 0.0) {
        vec3 overcastHorizon = mix(vec3(0.012, 0.018, 0.033), vec3(0.105, 0.112, 0.15), twilight);
        overcastHorizon = mix(overcastHorizon, vec3(0.21, 0.24, 0.29), day);
        vec3 overcastZenith = mix(vec3(0.005, 0.008, 0.017), vec3(0.045, 0.051, 0.072), twilight);
        overcastZenith = mix(overcastZenith, vec3(0.085, 0.105, 0.14), day);
        horizon = mix(horizon, overcastHorizon, rain);
        zenith = mix(zenith, overcastZenith, rain);
        sunGlow *= 1.0 - rain;
    }
}

float skySunwardWeight(float sunFacing) {
    return smoothstep(0.0, 1.0, sunFacing);
}

vec3 skyGradient(float viewElevation, float sunFacing, vec3 horizon, vec3 zenith,
                 vec3 sunGlow) {
    float elevation = clamp(viewElevation, 0.0, 1.0);
    // Rise quickly out of the pale horizon and ease into the upper sky.
    float heightBlend = elevation * (2.0 - elevation);
    float glowHeight = 1.0 - smoothstep(0.0, 0.58, abs(viewElevation));
    return mix(horizon, zenith, heightBlend) + sunGlow * (skySunwardWeight(sunFacing) * glowHeight);
}
