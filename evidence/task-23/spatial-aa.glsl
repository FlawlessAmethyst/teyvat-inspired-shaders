// TASK-23 trial. Filter diagonal transitions and isolated details while
// retaining straight horizontal and vertical edges.
vec3 filterSceneEdge(vec2 uv, vec3 center) {
    const vec3 weights = vec3(0.2126, 0.7152, 0.0722);
    vec3 left = textureOffset(colortex0, uv, ivec2(-1, 0)).rgb;
    vec3 right = textureOffset(colortex0, uv, ivec2(1, 0)).rgb;
    vec3 down = textureOffset(colortex0, uv, ivec2(0, -1)).rgb;
    vec3 up = textureOffset(colortex0, uv, ivec2(0, 1)).rgb;

    // Approximate perceptual contrast cheaply in the existing linear buffer.
    float middle = sqrt(max(dot(center, weights), 0.0));
    vec4 sides = sqrt(max(vec4(dot(left, weights), dot(right, weights),
                               dot(down, weights), dot(up, weights)), 0.0));
    vec4 delta = abs(sides - middle);
    float acrossX = max(delta.x, delta.y);
    float acrossY = max(delta.z, delta.w);
    float threshold = max(0.035, 0.12 * middle);
    float strength = 0.55 * smoothstep(threshold, 2.0 * threshold, min(acrossX, acrossY));
    return mix(center, (left + right + down + up) * 0.25, strength);
}
