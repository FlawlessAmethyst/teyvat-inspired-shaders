# Iris capability constraints — TASK-06

Status: **DONE**, 2026-11-12. Dependency: [TASK-05](style_targets.md).
Scope: source-backed feasibility for S1–S7, not shader implementation, final pass
architecture, runtime acceptance or a performance result. TASK-07 owns upstream
shaderpack study; TASK-08 owns architecture and any necessary scoped spike.

## Evidence and version boundary

The official [Iris site](https://irisshaders.dev/) links its developer documentation
to [Iris Docs](https://shaders.properties/). Inspected documentation and official
1.21.1 source are pinned below, rather than assuming the current docs describe the
installed beta exactly. [sources.json](../../evidence/task-06/sources.json) records
35 inspected/reference files, canonical permalinks, SHA-256 hashes and local copies.

- Iris repository: `https://github.com/IrisShaders/Iris`, branch `1.21.1`, revision
  `12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3` (HEAD subject: restore block entities in
  the shadow pass). This is **not established as the installed beta's build commit**.
- Docs repository: `https://github.com/IrisShaders/DocsPage`, revision
  `98f84cbe456e7e367afe788885869be46681be8c`. Current docs include features newer
  than 1.8; avoid inferring their presence from a current reference page alone.
- Installed JAR metadata re-read: `iris-neoforge-1.8.14-beta.1+mc1.21.1.jar`, SHA-256
  `60d5f8bf52f25e9986440f4a4270a6bd986d9cff994510e1108ac1547063b314`.
  Its metadata specifies Minecraft `[1.21,1.21.1)` and excludes Embeddium.
  The Embeddium exclusion message names Sodium 0.8. TASK-29 records the
  published 1.21.1 release target and the observed runtime despite the
  embedded range. [Compatibility notes](../testing/compatibility_notes.md#tested-development-stack).
- Selected installed class byte strings confirm depth/shadow sampler names,
  pre-translucent copying, weather controls, material/center attributes and dimension
  properties. This is **name-presence evidence only**, not executed behavior.
  Two full matrix-name searches returned false: source constructs these names by
  concatenation (`MatrixUniforms.addMatrix/addShadowMatrix`), so absence of the full
  byte string does not establish an unavailable uniform.
- Environment remains the inherited CachyOS/NeoForge 21.1.265, Minecraft 1.21.1,
  Sodium 0.8.13, RTX 4080 SUPER/OpenGL 4.6 baseline in
  [minecraft-environment.md](../minecraft-environment.md). TASK-06 used source
  and installed metadata. Subsequent client checks are listed below.

**Feasible** means the documented interface supplies the necessary inputs and a
plausible bounded method; quality/cost are unverified. **Uncertain** means a named
version, ordering or visual requirement still needs a spike/test. **Not feasible**
means unavailable under our shader-only/vanilla-assets scope, not a universal GPU
impossibility. These are capability judgments, separate from TASK-05 visual PASS.

## Essential target mapping

All seven retain their reference IDs, scene criteria and priorities from TASK-05.
The table records TASK-06's source-based judgments alongside later runtime
evidence. Other client checks appear in
[the follow-up record](#limits-and-follow-up-gate).

| Target | Outcome and supported minimum | Interface evidence | Remaining check / bounded fallback |
| --- | --- | --- | --- |
| S1 palette / rolloff | **Feasible**: fixed exposure, bounded saturation, highlight shoulder in a color output stage | ColorTex and final [D1]; color-space converter [J4] | Explicit linear/display encoding contract; test neutral stone, snow and lamps for double gamma/clipping. No LUT/history needed. |
| S2 warm sun / cool fill / cast shadows | **Feasible**: normals, separate block/sky light coordinates, celestial direction and bounded shadow map | Lighting attributes [D2], shadow buffers [D3], common/celestial/matrix uniforms [J2] | TASK-16 tested the bounded shadow receiver. TASK-22 checked low-light fill and selected lamp faces in night and interior fixtures. TASK-23 samples clear-day motion in the forest fixture. Shadow-pass GPU timing and other block-entity types remain open. [Shadow report](../testing/shadows.md), [lighting report](../testing/lighting_dimensions.md) |
| S3 sky / coherent time colors | **Feasible**: analytic view-elevation gradient with sunward color, time interpolation and a projected cloud layer in the sky draw | Sky/cloud programs [D4], world uniforms [D5] | TASK-14 checked the gradient and sampled time transitions. TASK-18 checked the cloud layer in the installed Overworld stack and measured the isolated sky-draw cost. [Cloud report](../testing/clouds.md) |
| S4 atmospheric depth | **Feasible**: distance blend; optional analytic height weight | Depth timing [D6], matrices [D7], pipeline [J1] | TASK-15 checked fixed distances, cutouts and translucent surfaces. TASK-21 exercises the shared horizon palette and fog range through both weather transitions. [Fog report](../testing/fog.md), [weather report](../testing/weather.md) |
| S5 overcast response | **Feasible**: share the world rain ramp across light, sky, fog, water and grade. Keep vanilla precipitation geometry and grade falling streaks in their draw | World/biome uniforms [D5], weather program [D4], common uniforms [J2] | TASK-21 sampled rain onset and clearing at fixed midday from three Overworld cameras. Dry biomes, shelter, snow and thunder remain open. [Weather report](../testing/weather.md) |
| S6 clear turquoise water | **Feasible**: water ID, alpha/tint, analytic sky reflection and procedural surface normals | Material mapping [D8], depth [D6], pre-hand copy [J1] | TASK-19 verified bounded depth absorption on the installed beta in the stepped basin with shoreline, glass, held items and fixed submerged views. Flowing and waterlogged edges remain open. [Water report](../testing/water.md) |
| S7 bright grounded vegetation | **Feasible**: explicit vanilla vegetation IDs, biome vertex tint and bounded skylight-weighted fill | Vertex color [D2], block mapping [D8], Sodium attributes [J3] | TASK-20 implements static vertex color and fill for mapped plants and retains the existing cutout and caster paths. Optional anchored wind across plant models remains unverified. [Vegetation report](../testing/vegetation.md). |

## Passes and GLSL conventions affecting these targets

The relevant ordering is shadow rendering, opaque gbuffers, deferred, translucent
gbuffers, composite, final. Deferred is an opportunity between opaque and
translucent drawing, not a mandatory implementation choice. Source explicitly
copies opaque depth before deferred and runs composite/final after world drawing.
Legacy paths have exceptions: weather/water/translucent hand occur after deferred,
but translucent entities/particles may occur earlier unless the corresponding Iris
programs/flags/order are used. Do not describe all transparency as a single clean
layer. [D4, J1]

Geometry programs require `.vsh`/`.fsh`; shared code can use `#include`, whose `/`
root is the pack's `shaders/` directory. Iris patches compatibility GLSL into its
internal rendering paths; official docs recommend compatibility over core for
patcher coverage. TASK-09 verified `#version 330 compatibility` on the installed
Overworld stack, and the current pack uses it. Keep declarations and
varyings consistent and retain normal, UV, vertex tint and alpha behavior across
fallback programs; a standalone compiler cannot validate Iris patching. No compute,
geometry/tessellation stage or newer extension is needed for the essential methods.
[D10]

`gbuffers_water` handles translucent terrain including glass, not water alone.
`gbuffers_skybasic`, `gbuffers_skytextured`, `gbuffers_clouds` and `gbuffers_weather`
provide separate integration points. Missing specific programs fall back; omitted
paths must later be checked for hand, entities, particles, damage overlays and
precipitation, rather than assuming terrain code covers everything correctly. [D4]

## Buffer and color contract

`gtexture` supplies the geometry's color texture; `gl_Color` carries biome tint and
may include vanilla AO/directional shading. Lightmap coordinates provide block
light in x and skylight in y; use the texture matrix normalization, not a guessed
0–1 range. A final-stage pixel has no automatic material ID/normal/lightmap: keep
lighting in geometry or explicitly store needed data. Normal/specular atlas
samplers do not manufacture authored PBR maps for vanilla textures. [D2, D11]

`colortexN` attachments are pack-defined data, despite misleading legacy names such
as `gnormal`. Defaults are normally 8-bit; HDR lighting may need an explicit float
format before tone mapping. Every added attachment costs bandwidth/storage. Docs
state 16 buffers before the 1.10.5 increase to 32; do not rely on the newer limit or
`MAX_COLOR_BUFFERS`. Use only the few attachments justified in TASK-08. In gbuffers,
`colortex0`–`3` are atlas bindings, not readable scene-color buffers. Later post
passes can use flipping; arbitrary same-texture feedback in geometry is not a safe
substitute. [D1]

`final` writes the display backbuffer. Establish an explicit decode → lighting →
tone map → display encode contract when implementing S1; buffer formats alone do
not establish linear light. Iris's inspected converters skip processing for SRGB
and can convert other selected output spaces; therefore do not rely on a hidden
Iris tonemapper or add a second display encoding blindly. TASK-11's
[native ramp and material tests](../testing/palette.md#visual-review) checked
the installed sRGB path. [D1, J4]

`depthtex0` is current scene depth. The inspected pipeline copies `depthtex2`
before rendering the opaque hand and `depthtex1` before translucent terrain.
Use `depthtex2` as the candidate for water thickness and verify the contents
at water pixels in the installed client. To measure distance, map screen
coordinates and depth to clip space, apply the inverse projection and
perform the homogeneous divide. Guard clear-sky depth. The opaque hand has
a separate projection depth scale. [D6, D7, J1]

For S6, comparing the water fragment's reconstructed position with opaque depth at
the same screen pixel can approximate thickness behind the surface. It cannot find
multiple submerged transparent layers or offscreen bottom geometry, and raw depth
subtraction is not thickness in blocks. Clamp missing/background/negative depth
cases, avoid live depth feedback, preserve blending and apply atmospheric fog
consistently to water and land without double fogging the bottom. These are design
inferences from D6/J1, **not a tested water implementation**. Screen-space refraction,
SSR and full layered transparency are unnecessary for this target.

## Lighting, shadows, atmosphere and materials

Per-vertex sky light is a cheap gate for outdoor fill; it is not a guarantee of
occlusion or GI. `eyeBrightnessSmooth` describes the camera and must not replace
per-surface skylight in caves. Preserve block-light pools and existing AO. If custom
normal-based direct light replaces vanilla orientation shading, explicitly account
for `oldLighting` to avoid applying it twice. Current docs warn that `separateAo`
may require an enabled shadow pass due to a bug: treat independent AO control as
**uncertain**, retaining combined vertex tint/AO if a no-shadow stage cannot separate
it. Do not divide baked AO out numerically. [D2, D12, J2]

The shadow pass supplies light-view depth and matching shadow matrices; celestial
positions are in view space, so transform consistently. A finite orthographic map
with a small fixed comparison kernel is feasible. Range/resolution, bias, cutout
alpha testing and sun/moon transitions remain the pack's responsibility. Larger
maps/filter kernels cost geometry work, bandwidth and samples; hardware comparison
is not proof of negligible cost on this machine. Use matching vegetation deformation
in world and shadow passes if optional wind is later added. [D3, D7, J2]

The inspected 1.21.1 HEAD specifically fixes block entities in shadow rendering.
Its relationship to the installed JAR remains unverified. TASK-16's matched
captures show a chest casting onto terrain alongside stone and oak leaves on
the installed beta. Other block-entity types still need their own checks.
[Shadow visual review](../testing/shadows.md#visual-review).

`worldTime` wraps each day; interpolate cyclically. `sunPosition` and
`shadowLightPosition` allow coherent lighting/sky directions. `rainStrength` and
smoothed `wetness` are weather signals, not actual material wetness. Biome uniforms
refer to the player's biome, not a per-pixel classification; retain vertex biome
tint across boundaries. Dimension properties can route programs by namespaced
world ID, and source exposes `hasSkylight`, `hasCeiling`, `ambientLight`. Do not
apply an Overworld sun/blue-sky assumption universally or pass a non-finite cloud
height into calculations. TASK-22 smoke-tests the shared Nether and End
pipelines on the installed beta. Custom dimensions remain untested.
[Dimension report](../testing/lighting_dimensions.md#dimensions). [D5, D13, J2]

Explicit small integer IDs in `block.properties` can separate water, leaves and
plants. TASK-19 passes the water selector as a flat varying. TASK-20 consumes
vegetation IDs at terrain vertices. Docs disagree on historical ID width. The mc_Entity
page and inspected Sodium transform describe the 1.8 integer representation,
whereas the block.properties page retains older 16-bit wording. Small IDs avoid
both range and float precision issues. `at_midBlock.xyz / 64` gives a vertex-to-block
center offset, not botanical topology. Optional wind needs per-model/state base
rules (including tall-plant halves), shadow agreement and motion evidence. [D8, D9, J3]

## Limits and follow-up gate

**Not feasible within scope:** reproducing painted albedo, authored plant meshes,
round terrain silhouettes, vegetation density/species or gameplay interaction rings
from absent assets/state. Available texture/vertex inputs shade the rendered scene;
they do not supply Genshin art or its interaction system. [D8, D9, D11] Analytic fog
cannot reproduce independently authored mist banks; screen depth cannot extend
terrain beyond the rendered world. These narrower methods are deliberate S4/S6
approximations, not claims that all richer shader methods are impossible.

Runtime compatibility evidence comes from the installed development stack.
TASK-22 checked fixed Nether and End views, and TASK-28 repeated the command
teleport sequence on the retained pack and verified the Overworld return.
Windows, macOS, AMD and Intel GPUs, other loaders, Distant Horizons/Voxy,
modded materials and custom dimensions remain unverified.
[Dimension findings](../testing/lighting_dimensions.md#dimensions),
[retained-pack regression](../testing/regression_report.md#runtime-results),
[compatibility notes](../testing/compatibility_notes.md).

TASK-07 completed the [upstream study](implementation_patterns.md). TASK-08
selected the forward architecture. TASK-16 and TASK-19 closed the scoped
shadow and opaque-depth checks on the installed beta. The architecture
tracks the limits on specialized transparency and dimension behavior.
Separate vertex AO remains unverified on that beta and goes to handoff
under TASK-24. [Architecture and runtime gates](../architecture/shaderpack_design.md#spike-decision-and-unresolved-capability-gates),
[effects triage](../architecture/deferred_effects.md).

TASK-09 verified custom GLSL rendering in the development Overworld. TASK-10
measured Sodium and the neutral pack. TASK-11 checked S1 color and the sRGB
output path. TASK-12 exercised surface skylight gating, sun direction and
combined vertex AO. TASK-13 checked skylight-weighted fill in daylight,
sunset, forest, cave and night. TASK-14 uses the untextured sky stage for
S3 and preserves the engine's celestial geometry. TASK-15 checked S4 with
fixed near, middle and far landmarks and an explicit textured sky program.
It reviewed cutouts, glass and water above the surface, with settled rain
strengthening the haze. TASK-16 checked S2 cast shadows on the installed beta
with matched terrain, leaf cutout, chest and glass-frame captures. It measured
the CPU client-loop cost and sampled fixed-angle camera steps. TASK-18
validated projected clouds in fixed clear, rain and night views. Opaque
depth use for water was open at TASK-15. TASK-19 verified the pre-hand
snapshot in the stepped Overworld basin and used it for bounded absorption.
TASK-20 exercised terrain material IDs in matched clear-day views, including
two dense-canopy views across plains and jungle biomes. TASK-21 sampled the
shared weather ramp in both directions and verified precipitation routing
on the installed beta. TASK-22 exercised dimension lighting flags, the
terrain lightmap weights in enclosed and night scenes, and the lamp
material ID. TASK-23 assessed motion and spatial AA and kept the TASK-22
shader source. TASK-24 used that source and prior captures to triage effects.
TASK-25 compared the integrated pack to Sodium and the reference stills.
The fog follow-up exercised the adjusted distance ramp in five fixed views.
TASK-26 measured the integrated build using client ablations and selected
offscreen GPU draws. TASK-27 kept that build after both optimization trials.
TASK-28 exercised motion, live rain, the waterline, cave entry and dimension
transitions on it. In-client GPU pass timings remain open.
[Per-effect report](../testing/effect_costs.md),
[Water report](../testing/water.md),
[vegetation report](../testing/vegetation.md), [weather report](../testing/weather.md),
[lighting and dimensions](../testing/lighting_dimensions.md).
[Baseline timings](../testing/baseline.md), [palette evidence](../testing/palette.md),
[sunlight evidence](../testing/sunlight.md), [ambient evidence](../testing/ambient.md),
[sky evidence](../testing/sky.md), [fog evidence](../testing/fog.md),
[shadow evidence](../testing/shadows.md), [cloud evidence](../testing/clouds.md),
[motion and AA evidence](../testing/anti_aliasing.md),
[integrated visual and fog evidence](../testing/visual_comparison.md),
[current handoff](../STATUS.md).

## Official source index

All document links below refer to the pinned DocsPage revision; all Java links to
the pinned Iris revision. Exact hashes/local paths are in the evidence manifest.

- **D1**: [colortex](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Buffers/colortex.mdx), [final](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Programs/final.mdx).

- **D2**: [gl_Color](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Attributes/gl_Color.mdx), [gl_MultiTexCoord1](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Attributes/gl_MultiTexCoord1.mdx).

- **D3**: [shadow](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Programs/shadow.mdx), [shadowtex](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Buffers/shadowtex.mdx).

- **D4**: [gbuffers](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Programs/gbuffers.mdx), [deferred](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Programs/deferred.mdx), [composite](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Programs/composite.mdx).

- **D5**: [world](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Uniforms/world.mdx), [biome](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Uniforms/biome.mdx).

- **D6**: [depthtex](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Buffers/depthtex.mdx).

- **D7**: [matrices](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Uniforms/matrices.mdx).

- **D8**: [block_properties](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Miscellaneous/block_properties.mdx), [mc_Entity](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Attributes/mc_Entity.mdx).

- **D9**: [at_midBlock](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Attributes/at_midBlock.mdx).

- **D10**: [compatibility_vs_core](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/How%20To/compatibility_vs_core.mdx), [include](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Miscellaneous/include.mdx).

- **D11**: [atlases](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Buffers/atlases.mdx).

- **D12**: [features](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Shaders.Properties/features.mdx).

- **D13**: [dimension_properties](https://github.com/IrisShaders/DocsPage/blob/98f84cbe456e7e367afe788885869be46681be8c/src/content/docs/current/Reference/Miscellaneous/dimension_properties.mdx).

- **J1**: [IrisRenderingPipeline](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pipeline/IrisRenderingPipeline.java), [IrisSamplers](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/samplers/IrisSamplers.java).

- **J2**: [CommonUniforms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/CommonUniforms.java), [CelestialUniforms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/CelestialUniforms.java), [MatrixUniforms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/MatrixUniforms.java), [WorldTimeUniforms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/WorldTimeUniforms.java), [IrisExclusiveUniforms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/IrisExclusiveUniforms.java).

- **J3**: [SodiumPrograms](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pipeline/programs/SodiumPrograms.java), [SodiumTransformer](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pipeline/transform/transformer/SodiumTransformer.java).

- **J4**: [ColorSpaceFragmentConverter](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pathways/colorspace/ColorSpaceFragmentConverter.java), [ColorSpaceComputeConverter](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pathways/colorspace/ColorSpaceComputeConverter.java).
