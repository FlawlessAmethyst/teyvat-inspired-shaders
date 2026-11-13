vec3 gradeSceneColor(vec3 sceneColor, float saturationBoost) {
    const float exposure = 1.48;
    const float shoulderStart = 0.52;
    const float shoulderRange = 1.0 - shoulderStart;

    vec3 color = max(sceneColor, 0.0) * exposure;
    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float darkest = min(color.r, min(color.g, color.b));

    // Limit positive expansion to preserve the darkest channel. Negative values
    // move the color toward luminance during overcast weather.
    float boost = min(saturationBoost, 0.70 * darkest / max(luminance - darkest, 1e-6));
    color += (color - luminance) * boost;

    // Compress bright peaks with a common scale to preserve hue and fit the display gamut.
    // The rational shoulder joins the linear region with a slope of one and approaches one.
    float peak = max(color.r, max(color.g, color.b));
    float excess = max(peak - shoulderStart, 0.0);
    float mappedPeak = shoulderStart + shoulderRange * (excess / (shoulderRange + excess));
    return color * (mappedPeak / max(peak, shoulderStart));
}
