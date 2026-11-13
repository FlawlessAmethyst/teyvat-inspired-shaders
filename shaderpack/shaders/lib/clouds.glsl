// The lattice repeats every 128 cells, matching the wrapped camera origin.
float cloudLattice(ivec2 cell) {
    uvec2 wrapped = uvec2(cell & 127);
    uint bits = wrapped.x * 1973u + wrapped.y * 9277u + 89173u;
    bits = (bits ^ (bits >> 13u)) * 1274126177u;
    return float((bits ^ (bits >> 16u)) & 65535u) / 65535.0;
}

// Return the interpolated value and its gradient. The detail octave uses
// just the value, so it does not need the derivative arithmetic.
vec3 cloudNoise(vec2 position) {
    ivec2 cell = ivec2(floor(position));
    vec2 f = fract(position);
    vec2 weight = f * f * (3.0 - 2.0 * f);
    float a = cloudLattice(cell);
    float b = cloudLattice(cell + ivec2(1, 0));
    float c = cloudLattice(cell + ivec2(0, 1));
    float d = cloudLattice(cell + 1);
    float lower = mix(a, b, weight.x);
    float upper = mix(c, d, weight.x);
    vec2 gradient = vec2(mix(b - a, d - c, weight.y), upper - lower) * (6.0 * f * (1.0 - f));
    return vec3(mix(lower, upper, weight.y), gradient);
}

// The virtual deck has no depth. Fade near the horizon and as the eye
// approaches its altitude, before the plane projection becomes unstable.
vec2 sampleCloudDeck(vec3 worldRay, float elevation, vec3 plane, vec2 lightDirection,
                     float rain) {
    float visibility = smoothstep(0.045, 0.19, elevation)
                     * smoothstep(20.0, 72.0, plane.y);
    if (visibility <= 0.0) {
        return vec2(0.0);
    }

    vec2 position = (plane.xz + worldRay.xz * (plane.y / worldRay.y)) / 256.0;
    vec3 broad = cloudNoise(position);
    // Rotate the detail lattice without breaking the 128-cell period.
    float detail = cloudNoise(mat2(3, 1, -1, 3) * position + vec2(39.5, 17.25)).x;
    float density = mix(broad.x, detail, 0.34);
    float edge = mix(0.53, 0.32, rain);
    float coverage = mix(smoothstep(edge, edge + 0.065, density), 1.0, 0.72 * rain);
    float thickness = smoothstep(edge, edge + 0.28, density);
    float underside = clamp(0.38 + 0.30 * thickness + 0.45 * dot(broad.yz, lightDirection),
                            0.0, 1.0);
    return vec2(coverage * visibility, underside);
}

vec3 cloudColor(float underside, float sunFacing, vec3 base, vec3 rim, float rain) {
    vec3 color = mix(rim, base, underside);
    return color + rim * (0.18 * sunFacing * (1.0 - underside) * (1.0 - rain));
}
