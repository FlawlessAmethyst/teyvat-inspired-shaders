# Genshin-inspired Iris shaderpack

See the [developer handoff](../docs/HANDOFF.md) for source loading, replay
and benchmarking or the [known gaps](../docs/KNOWN_GAPS.md) for open work.

Copy the unpacked `shaderpack/` folder to the dedicated instance's `minecraft/shaderpacks/`
directory under a new name, and select it in Iris. Iris expects `shaders/` directly
inside that folder. The retained pack was tested in GenshinShaderDev on
Minecraft 1.21.1 with NeoForge. See the [tested stack and limits](../docs/testing/compatibility_notes.md),
[instance paths](../docs/minecraft-environment.md) and [project status](../docs/STATUS.md).
Enable shaders after selecting the pack and verify `Using shaderpack: <folder name>`
in the instance's `minecraft/logs/latest.log`.

Verify the current development source from the repository root with
`sha256sum --quiet -c evidence/task-25/fog-pack.sha256`.
[Current manifest](../evidence/task-25/fog-pack.sha256),
[per-effect profiling](../docs/testing/effect_costs.md),
[TASK-27 optimization results](../docs/testing/optimization.md).

Terrain combines engine lightmap fill and directional sunlight in linear RGB.
The [terrain lighting module](shaders/lib/terrain_lighting.glsl) warms low sun
and cools outdoor fill. The fill tint follows sun elevation and tapers with
strong direct light, bright block light and low skylight. A bounded neutral
fill lifts dark terrain at night and in caves, fading inside bright light pools.
Selected lamp faces use a lower lightmap scale under low light. Biome tint and
combined vertex AO feed the material color. The pack disables legacy directional
shading so the engine and terrain shader do not both shade the same faces.
Other geometry uses the scaffold's color, textured or lightmapped calculation
through Iris fallback or explicit routes for glass, breaking overlays and
block entities. Iris applies its render-type alpha tests and blend states.

Mapped vanilla leaves and grasses retain their biome tint and vertex AO.
The terrain vertex shader shifts green leaves slightly cooler, softens
bright grass and fern tints, and gives off-sun leaf faces a small
daylight fill gated by the lightmap. [Vegetation captures and timings](../docs/testing/vegetation.md).

The final pass reads the single RGBA16F attachment and uses
[`tonemap.glsl`](shaders/lib/tonemap.glsl) to apply 1.48× exposure,
weather-dependent chroma and a smooth highlight shoulder before encoding
for sRGB display. See the [palette](../docs/testing/palette.md),
[sunlight](../docs/testing/sunlight.md) and [ambient lighting](../docs/testing/ambient.md)
reports for the scene captures and client-loop comparisons.

The final pass uses one color sample per pixel. TASK-23 deferred shader
anti-aliasing after a five-sample trial softened some edges but left foliage
shimmer visible in motion. [AA decision and timings](../docs/testing/anti_aliasing.md).
TASK-24 verified the accepted TASK-22 source and left scene-wide bloom and
separate vertex AO for handoff. The proposed sun halo is an optional trial.
[Baseline and effects triage](../docs/architecture/deferred_effects.md).

The [sky module](shaders/lib/sky.glsl) uses sun elevation to blend a pale
blue daylight horizon, a lavender twilight with a sunward peach glow, and
a dim blue night. The untextured sky program evaluates the gradient in
linear RGB. A [projected cloud layer](shaders/lib/clouds.glsl) adds drifting
shapes, cool undersides and warmer sunlit edges to the same draw. Rain thickens
and desaturates the layer. Cloud coverage dims the stars, and the sun and moon
use their textured draw. [Sky report](../docs/testing/sky.md),
[cloud captures and GPU measurements](../docs/testing/clouds.md).

The [fog module](shaders/lib/fog.glsl) softens distant terrain and
translucent surfaces toward the procedural horizon in scene-linear RGB.
At the tested 12-chunk render distance, haze spans 88–180 blocks in
clear weather and 22–136 blocks in settled rain. The ramp uses each
fragment's own view-space position and preserves the render type's alpha
test and blend state. [Current fog captures](../docs/testing/visual_comparison.md#clear-air-fog-follow-up),
[earlier fog validation and timing data](../docs/testing/fog.md).

The [shadow module](shaders/lib/shadows.glsl) attenuates direct sun on
terrain with a 1024² depth map and one hardware-filtered lookup per eligible
fragment. The receiver uses slope-aware bias and fades to the existing terrain
lighting near the map boundary. The opaque terrain caster writes depth
directly. Cutouts use atlas alpha to retain holes in the silhouette.
[Shadow captures and timings](../docs/testing/shadows.md).

The [water module](shaders/lib/water.glsl) tints shallow water turquoise and
deepens the blue with thickness from Iris's pre-hand depth snapshot. Two
small normal waves vary the analytic sky reflection and sun highlight. Rain
mutes the tint and highlight. A submerged fog ramp preserves nearby bottom
detail. [Water captures and timings](../docs/testing/water.md).

Iris's rain intensity coordinates sunlight, fog, sky, water and scene
saturation. The cloud deck closes over a slate horizon, and reduced direct
sun lowers cast-shadow contrast. [The precipitation program](shaders/gbuffers_weather.fsh)
mutes falling streaks while retaining vanilla motion and alpha. TASK-21
checked live rain onset and clearing at fixed midday. TASK-28 and TASK-30
repeated the cycle with the fog-tuned pack in the valley. [Weather transitions](../docs/testing/weather.md),
[fog tuning](../docs/testing/visual_comparison.md#clear-air-fog-follow-up).

The terrain lighting adjustments require skylight and a dimension without a
ceiling. Nether and End terrain use the engine lightmap through the shared
programs. The pack's procedural air fog is also gated off there. Fixed
Nether and End views and the return to the Overworld were smoke-tested
with the TASK-22 snapshot and repeated in TASK-28 and TASK-30 with the
fog-tuned pack.
[Lighting and dimension report](../docs/testing/lighting_dimensions.md#dimensions),
[runtime regression](../docs/testing/regression_report.md),
[handoff replay verification](../evidence/task-30/verification.txt).
