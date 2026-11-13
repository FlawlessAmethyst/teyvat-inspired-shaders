#include "/lib/sky.glsl"

vec2 distanceFogRamp(float renderDistance, float rain) {
    float end = max(1.0, min(renderDistance * 0.94, mix(180.0, 136.0, rain)));
    // Hold clear-air terrain detail farther into the view while keeping the rain ramp.
    float start = min(mix(88.0, 22.0, rain), end * mix(0.5, 0.4, rain));
    return vec2(start * start, 1.0 / (end * end - start * start));
}

vec2 submergedFogRamp() {
    // A negative slope selects the water medium in the shared fog varying.
    return vec2(9.0, -1.0 / (26.0 * 26.0 - 9.0));
}

vec3 applyDistanceFog(vec3 color, vec3 viewPosition, vec2 ramp, vec3 horizon,
                      vec3 sunGlow, vec3 up, vec3 horizontalSun) {
    float distanceSquared = dot(viewPosition, viewPosition);
    if (ramp.y == 0.0 || distanceSquared <= ramp.x) {
        return color;
    }

    // Smoothstep in squared distance keeps the clear region and far end smooth
    // without taking a square root for every shaded fragment.
    float t = clamp((distanceSquared - ramp.x) * abs(ramp.y), 0.0, 1.0);
    float haze = t * t * (3.0 - 2.0 * t);

    if (ramp.y < 0.0) {
        return color * mix(vec3(1.0), vec3(0.16, 0.47, 0.54), haze);
    }

    if (sunGlow.r > 0.0) {
        // Normalize the horizontal view ray only during twilight. Keep the
        // sun projection unnormalized to match skyGradient at zero elevation.
        float vertical = dot(viewPosition, up);
        float horizontalSquared = max(distanceSquared - vertical * vertical, 0.0001);
        float sunFacing = dot(viewPosition, horizontalSun) * inversesqrt(horizontalSquared);
        horizon += sunGlow * skySunwardWeight(sunFacing);
    }

    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    color = mix(color, vec3(luminance), 0.16 * haze);
    return mix(color, horizon, haze);
}
