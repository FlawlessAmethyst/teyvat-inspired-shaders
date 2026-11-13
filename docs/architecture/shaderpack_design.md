# Iris-only architecture gate — TASK-08

Status: **DONE**, 2026-11-12. The gate cleared TASK-09 implementation.
The gate selected the architecture after TASK-05–07. Later implementation and
runtime checks are noted below. [Current progress](../STATUS.md).

## Decision and evidence boundary

Use forward lighting in geometry programs, one linear HDR color attachment and
one final display pass. TASK-16 adds one bounded shadow geometry pass. No deferred
lighting, composite pass, normal/material G-buffer, history, compute, raymarching,
SSR or companion mod is needed for the selected minimum. Geometry programs are
multiple entry points over Minecraft's existing draws, not one extra full-screen
pass each. Iris may allocate internal buffers/copies beyond those we request.

Preserve [S1–S7 and their qualitative criteria](../research/style_targets.md).
[Official interface findings](../research/iris_feasibility.md) and
[original implementation candidates](../research/implementation_patterns.md) are
the source basis. Their pinned manifests are
[TASK-06](../../evidence/task-06/sources.json) and
[TASK-07](../../evidence/task-07/sources.json). The pack uses original
implementations of the studied shaderpack techniques. TASK-14's spatial dither
uses Jorge Jimenez's published Interleaved Gradient Noise formula.
[Sky shader behavior](../testing/sky.md#shader-behavior),
[provenance](../HANDOFF.md#provenance-and-continuation).

Target only the existing Minecraft 1.21.1 / NeoForge 21.1.265 / Iris
1.8.14-beta.1 / Sodium 0.8.13 instance on CachyOS, RTX 4080 SUPER, OpenGL 4.6.
Keep Java, mods and loader unchanged; exact versions and access instructions are
in [the environment record](../minecraft-environment.md). TASK-09 validated
`#version 330 compatibility` through Iris in this Overworld configuration.
TASK-11 validated the grade, TASK-12 and TASK-13 validated terrain lighting,
TASK-14 validated the sky gradient, TASK-15 validated distance fog, and
TASK-16 validated cast shadows on the same stack. TASK-18 verified projected
clouds, TASK-19 verified bounded water absorption and submerged fog, and
TASK-20 checked vegetation tint and leaf fill in fixed clear-day views.
TASK-21 checked the coordinated rain response in both directions at fixed
midday. TASK-22 checked night and interior readability and smoke-tested the
shared pipeline in the Nether and End.
[Palette evidence](../testing/palette.md), [sunlight evidence](../testing/sunlight.md),
[ambient evidence](../testing/ambient.md), [sky evidence](../testing/sky.md),
[fog evidence](../testing/fog.md), [shadow evidence](../testing/shadows.md),
[cloud evidence](../testing/clouds.md), [water evidence](../testing/water.md),
[vegetation evidence](../testing/vegetation.md), [weather evidence](../testing/weather.md),
[lighting and dimension evidence](../testing/lighting_dimensions.md).

## Pass and resource ownership

Iris draws the shadow map before the main geometry passes. In the main view,
Iris draws the sky before opaque world geometry and runs the final pass after
world rendering. In the inspected Iris source, `beginHand` copies the
no-hand depth snapshot (`depthtex2`) and `beginTranslucents` copies
`depthtex1` after the opaque hand. Some translucent entities and particles
draw before these snapshots. TASK-19 validated thickness sampling in the
stepped Overworld basin. [Depth and pass feasibility](../research/iris_feasibility.md#passes-and-glsl-conventions-affecting-these-targets).

| Stage / entry points | Responsibility | Reads → writes |
| --- | --- | --- |
| `shadow`, `shadow_solid` (TASK-16) | One 1024² orthographic light view, 64-block caster distance. Solid terrain writes depth directly. Cutout geometry tests base-level atlas alpha and vertex alpha | Light-view geometry → shadow depth. The caster programs request no color attachment |
| `gbuffers_basic`, `gbuffers_textured`, `gbuffers_textured_lit` | Explicit untextured, textured-unlit and lightmapped fallback families | Relevant vertex color/texture/lightmap → `colortex0`, normal engine depth |
| `gbuffers_terrain`, `gbuffers_block`, `gbuffers_damagedblock` | Skylit terrain uses shadowed direct light, lightmap fill, a low-light lift, and material adjustments for vegetation and selected lamp faces. Nether and End terrain use engine lightmap illumination. Block entities and breaking overlays use scaffold lighting. Each applies distance fog where enabled | Albedo, tint/AO, lightmap, position and terrain normal → `colortex0` and normal engine depth. Terrain also reads block material ID and samples shadow depth for eligible sunlight receivers |
| `gbuffers_skybasic`, `gbuffers_skytextured` | Analytic sky and one projected cloud layer on Iris's disc and horizon. Cloud opacity dims stars. The void retains its vertex tint, and sun and moon use the textured sky draw | View direction, time palette, camera origin and rain or sky texture → scene-linear color |
| `gbuffers_water` | TASK-19 water ID selects thickness tint, analytic sky reflection and two small normal waves. Other translucent terrain uses the scaffold material. Both use the shared fog path | Water reads lightmap and `depthtex2` above the surface. Other translucency reads atlas and lightmap. Both write straight-alpha color |
| Entity, hand and particle fallbacks | Entity and particle draws use Iris fallback routes. Hand stages bypass distance fog | Texture/light/tint → color with engine alpha and depth handling |
| `gbuffers_weather` | Grades falling precipitation in the existing draw and bypasses distance fog. Splash particles use their existing fallback | Texture, vertex tint and lightmap → scene-linear RGB with engine alpha and blending |
| `final` | Fixed exposure, weather-dependent chroma, hue-preserving shoulder and sRGB encode | One `colortex0` read → backbuffer, opaque output alpha |

The pack ships the three scaffold fallback families, the graded final
pass, and shadowed direct light with ambient fill in `gbuffers_terrain`. Explicit
`gbuffers_block` and `gbuffers_damagedblock` wrappers use the scaffold lightmap
calculation, as does glass in `gbuffers_water`. The pack-wide `oldLighting=false` also applies
when those routes draw. TASK-14 supplies the procedural sky through the
untextured sky program. TASK-15 gives the sun and moon an explicit textured
sky route that bypasses atmospheric fog. TASK-18 composites a single cloud
layer in the untextured sky program and sets `clouds=off` to suppress the
engine's cloud geometry. It derives shape and shade from two samples of an
analytic noise field, with zero texture reads and the existing color target.
[Sky captures](../testing/sky.md#visual-review), [fog report](../testing/fog.md),
[cloud report](../testing/clouds.md).

Thin vertex/fragment wrappers use shared helpers under `shaders/lib/`
for color, lighting, atmosphere, water and shadows. Vegetation tint and
fill share the terrain lighting module. Developer source flags support
controlled ablations and diagnostics.

Explicitly audit fallback behavior for breaking overlays, outlines, sign/name text,
beacons, eyes, armor glint, particles and translucent entities. Give a route its own
wrapper when its alpha, lighting, overlay or fog semantics differ; do not blindly
force every program through terrain lighting. Additional Iris translucent programs
and ordering flags are conditional fixes after a demonstrated ordering defect,
not baseline dependencies or a claim of order-independent transparency.

| Resource | Chosen contract / lifetime |
| --- | --- |
| `colortex0` | Full resolution `RGBA16F`, explicitly selected; clear every frame, no history or feedback. RGB is scene-linear light, alpha is coverage for blending, never a material mask. Roughly 28.1 MiB per 2560×1440 image, excluding Iris duplicates and other allocations |
| `depthtex0` | Engine current depth; never sample live attached depth for water, never reinterpret as distance |
| `depthtex1` / `depthtex2` | Iris snapshots, no custom depth attachment. Water reads the no-hand snapshot `depthtex2` for the thickness ramp. `depthtex1` includes opaque hand |
| `shadowtex0` (TASK-16) | Single comparison sampler. One filtered lookup on eligible fragments blends the four neighboring depth comparisons in hardware. Translucent terrain and ordinary entities are disabled as casters |
| Atlases/lightmap | Vanilla texture and engine lightmap inputs only; no PBR maps, noise texture, LUT or authored replacement assets |

## Color, geometry and lighting contracts

The terrain route multiplies atlas RGB by vertex RGB in their encoded form, then
decodes the product to linear sRGB. With `separateAo=false`, vertex RGB carries
both biome tint and combined vanilla AO. Decoding their product can darken AO.
Alpha remains coverage. Keep baked AO in vertex RGB.
Use `separateAo=false` explicitly. A later isolated AO improvement must first prove
correct alpha/cutout behavior on the installed beta; it is not a required feature.

TASK-09 preserved vanilla lighting as its neutral scaffold. TASK-12 uses
`oldLighting=false` and evaluates the sun term per terrain vertex. It retains
vertex AO, normalizes lightmap coordinates through the texture matrix and reads
the per-surface block and sky levels separately. Low skylight gates the sun
and high block light reduces the amount of fill reserved for it.
Surface skylight approximates occlusion. [TASK-12 report](../testing/sunlight.md).

TASK-13 computes an RGB fill scale per terrain vertex. It combines the existing
sun reservation with a cool tint weighted by skylight. The tint tapers as
block light and direct sun increase, and is zero at zero skylight or maximum
block light. The fragment shader scales one decoded lightmap sample, adds the
interpolated direct RGB term, and multiplies by linear surface color.
[TASK-13 report](../testing/ambient.md).

TASK-20 maps vanilla leaves, grasses and ferns through `block.properties`.
Green-dominant vertex tints drive the color correction while retaining biome
variation and AO. Mapped outdoor leaf faces receive bounded extra fill from
the existing light terms. The material reuses the terrain draw, texture
reads and interpolants. [Vegetation shader behavior](../testing/vegetation.md#shader-behavior).

TASK-22 adds a neutral low-light fill in the existing terrain varying. The
fill fades in full skylight during the day and at high block-light levels.
Mapped light-source faces reduce their lightmap contribution in low light.
Terrain albedo and vertex AO multiply both terms. The Nether and End
bypass these lighting adjustments and use the decoded engine lightmap.
[Lighting and dimensions](../testing/lighting_dimensions.md).

All lit colors, analytic sky colors, fog colors and transparent source RGB must be
linear before blending. Use straight-alpha RGB with standard source-alpha /
one-minus-source-alpha blending for ordinary transparency; preserve distinct
additive/overlay routes rather than globally overriding all blending. Opaque output
alpha is one; cutouts keep texture alpha tests, not fractional opaque coverage.
The final pass alone applies exposure/shoulder/saturation and encodes to sRGB once.
Leave Iris color correction at its default and validate with the existing sRGB
output setting; don't assert wide-gamut/HDR output support. Guard near-zero
luminance, negative RGB and out-of-gamut values before encoding. TASK-11 checked
neutral stone, diagnostic ramps, lanterns and a snow swatch in the
[palette report](../testing/palette.md#visual-review).

Use view-space normals and light vectors consistently for direct light; derive
view-space positions with the appropriate engine transforms. Fog uses distance in
blocks from geometry position, interpolated then measured per fragment; no full-screen
depth reconstruction is needed for S4. Hand paths bypass world-distance fog.
Use camera-relative world coordinates where needed for stable waves; avoid precision
loss from large absolute world coordinates. Share vertex/caster transforms if wind
is eventually added. Fade shadow influence near map/range boundaries toward the
skylight approximation, clamp bias and test contact/grazing surfaces. Transparent
casters initially do not produce colored shadows; record glass/water omissions.

## Selected style methods and fog/water boundary

| Target | Selected method and priority | Acceptance owner / bounded reduction |
| --- | --- | --- |
| S1 | Fixed exposure and channel-peak shoulder with bounded clear-weather chroma expansion and rain-driven compression | [Grade and ramp validation](../testing/palette.md), [overcast grading](../testing/weather.md#shader-behavior) |
| S2 | Warm terrain sunlight, skylight-weighted cool fill, bounded neutral fill in low light, and retained vertex AO | TASK-16 verifies bounded directional shadows. TASK-22 checks night and interior readability and selected lamp faces. [Shadows](../testing/shadows.md#shader-behavior), [low-light validation](../testing/lighting_dimensions.md#visual-review) |
| S3 | Analytic elevation gradient and sunward twilight tint driven by solar elevation, with a projected cloud layer | TASK-14 verified fixed views and live samples through the day wrap. TASK-18 captured fixed cloud views and measured sky-draw cost. [Cloud report](../testing/clouds.md) |
| S4 | Fragment distance ramp, near clear zone, same horizon color as sky | [TASK-15 matched distance landmarks and fog review](../testing/fog.md) |
| S5 | Shared `rainStrength` ramp across direct light, fog, sky, water and saturation | TASK-21 also grades falling precipitation in its existing draw. [Weather report](../testing/weather.md). |
| S6 | Water-specific turquoise tint, view-angle analytic sky reflection, two small normal-only waves and bounded depth absorption | [TASK-19 capture and timing report](../testing/water.md) |
| S7 | Explicit vanilla plant/leaf IDs, retained biome tint/AO, and bounded skylight-weighted fill on off-sun leaf faces | [TASK-20 vegetation capture and timing report](../testing/vegetation.md) |

TASK-15 added atmospheric fog to lit geometry in linear RGB before blending,
including ordinary transparent surfaces. The squared distance ramp follows
the interpolated view-space position and shifts from 88–180 blocks in
clear weather to 22–136 blocks in full rain at 12 chunks.
[TASK-25 fog tuning](../testing/visual_comparison.md#clear-air-fog-follow-up).
Fog evaluates the shared clear/overcast palette at zero view elevation along the
horizontal view direction. Alpha blending differently
fogged layers can retain too much bottom-distance haze under water. The
submerged fog path attenuates scene colors between 3 and 26 blocks, with
stronger attenuation of red. The basin floor and lamps are visible from
the submerged camera.

The water shader uses inverse projection and homogeneous divide to reconstruct
the sampled position. It measures separation from the surface along the
same pixel ray. The absorption ramp saturates at eight blocks.
Clear-sky, invalid projection and foreground depth select fixed absorption. A single scalar opacity
can approximate transmission without a saved scene-color buffer; it cannot express
independent RGB transmission or refract background geometry. Analytic sky reflection
is a surface-color term, not reflected terrain or objects. Glass must never enter
this water branch. Underwater surfaces use a fixed, lightmapped tint and
the submerged fog ramp.

On a configuration with unreliable depth, bounded tint and opacity are the
S6 fallback. Record the reproducible depth failure and mark S6 PARTIAL for
that configuration. Any additional scene-color copy or pass requires a
documented architecture amendment and measured visible benefit.

## Spike decision and unresolved capability gates

**TASK-08-SPIKE: not needed for this gate; not run.** No selected minimum depends
on separate AO, block-entity shadow casting or depth absorption. The essential
water direction uses the validated TASK-19 thickness branch on the tested
Overworld stack. TASK-16 verified the bounded terrain
shadow pass on the installed beta. If runtime evidence invalidates the minimum,
stop at the affected task, record PARTIAL/BLOCKED and revise this gate.

| Runtime check | Evidence or required experiment |
| --- | --- |
| Iris patching / RGBA16F / alpha and fallback coverage | TASK-09 and TASK-11–16 verified the Overworld load and RGBA16F request. TASK-11 checked ramps and materials. TASK-15 reviewed fog across leaf cutouts, water and overlapping glass. Exact blending and specialized draw parity remain open. |
| `oldLighting` and combined AO response | TASK-12 daylight, sunset and cave captures show the custom face response and retained contact darkening. TASK-13 checks the cool fill and cave lantern response. The pack uses combined vertex AO. |
| Analytic sky draw routing and time continuity | TASK-14 checks the clear-sky palette through running dusk and dawn. TASK-18 checks projected clouds at fixed times. TASK-21 samples the animated sky during rain onset and clearing from fixed cameras. TASK-23 captures clear-day camera movement. Cloud-clock wrap remains untested in the client. [Sky validation](../testing/sky.md), [cloud validation](../testing/clouds.md), [weather validation](../testing/weather.md), [motion review](../testing/anti_aliasing.md). |
| Distance fog and rain response | TASK-15 checks the fixed overlook and TASK-19 checks submerged fog in the stepped basin. TASK-21 checks both rain transition directions at fixed time and camera. TASK-28 repeats that cycle in the valley with the tuned fog ramp. [Fog validation](../testing/fog.md), [weather report](../testing/weather.md), [runtime regression](../testing/regression_report.md#runtime-results). |
| Terrain/cutout/chest shadow coverage in beta | TASK-16 matched captures show terrain, oak leaf cutouts, the chest and cutout glass frames casting onto terrain on the installed beta. [Shadow visual review](../testing/shadows.md#visual-review) |
| Snapshot depth, water/glass blending and bottom fog | TASK-19 verified a fixed stepped basin, shoreline, overlapping glass, held items and submerged floor and surface views. TASK-28 checks both directions of a live waterline crossing. [Water report](../testing/water.md), [runtime regression](../testing/regression_report.md#runtime-results). |
| Vegetation tint, cutouts and shadow contact | TASK-20 compared the original daylight/forest views and two dense-canopy views across plains and jungle biomes. [Vegetation report](../testing/vegetation.md) |
| Sun/sky assumptions outside Overworld | Terrain sun and skylight tint, procedural sky, air distance fog and weather grade gate on skylight and ceiling. TASK-22 checks the shared programs in the Nether and End. TASK-28 repeats those views and checks the Overworld pipeline after the return. [Dimension report](../testing/lighting_dimensions.md#dimensions), [runtime regression](../testing/regression_report.md#runtime-results). |

## Implementation sequence and developer continuation

Follow numbered dependencies, not visual rank: TASK-09 loadable neutral skeleton;
TASK-10 matched Sodium and neutral-pack baselines; TASK-11 palette; TASK-12/13 lighting;
TASK-14 sky; TASK-15 distance fog; TASK-16 shadows; TASK-17 checkpoint. Only after
CONTINUE: TASK-18 clouds, TASK-19 water, TASK-20 foliage, TASK-21 weather, TASK-22
night/caves/dimensions, TASK-23 temporal/AA investigation, TASK-24 triage and
TASK-25 comparison. TASK-24 verified the TASK-22 shader baseline for the
original TASK-25 comparison. TASK-26 profiled the later fog-tuned build
with client-loop ablations and offscreen GPU draws. TASK-27 tested a
smaller shadow map and a fog blend rewrite and retained that baseline.
TASK-28 completed the runtime regression pass. TASK-29 recorded the
tested stack and the Iris and Minecraft API differences relevant to the
pack. TASK-30 delivered the handoff and reran the runtime suite.
[TASK-25 comparison](../testing/visual_comparison.md),
[TASK-26 results](../testing/effect_costs.md), [TASK-27 trials](../testing/optimization.md),
[compatibility notes](../testing/compatibility_notes.md),
[developer handoff](../HANDOFF.md).

Reuse [scene presets](../testing/scenes.md), [harness](../testing/harness.md) and
`tools/minecraft.py`; preserve fixed camera/time/weather, 2560×1440, FOV 70 and
render/simulation distances 12/8. TASK-10 measured the Sodium and neutral-pack
client-loop baselines with Unlimited FPS and VSync off. TASK-26 reused
those settings in five TASK-25 views. TASK-27 used three of those views
and the TASK-16 cutout fixture to compare the trials with the fog-tuned
build. Offscreen GPU draws and client-loop deltas cover different
workloads. TASK-28 and TASK-30 verified the accepted build in the runtime suite.
[Baseline report](../testing/baseline.md),
[TASK-27 visual and timing checks](../testing/optimization.md),
[TASK-28 regression report](../testing/regression_report.md).

The [TASK-15 fixture](../testing/fog.md#capture-conditions) adds near, middle
and far landmarks in a separate copy of the visual world. The
[TASK-16 fixture](../testing/shadows.md#capture-conditions) isolates four
casters and adds a range lane in another copy. TASK-19 adds a stepped
basin with shoreline, glass and submerged views. TASK-20 adds paired
plains/jungle oak crowns and overlapping canopies. TASK-21 covers live
weather transitions. TASK-22 adds enclosed lamp and unlit fixtures and
fixed Nether/End views. TASK-23 reviews moving views of stone, foliage, and
the shoreline. TASK-28 adds a live waterline crossing, cave entry and
a dimension return on the retained build. Snow behavior remains a
coverage gap. Record the camera and settings for new comparisons. See the local numbered plan (`task_decomposed.md`).

TASK-16 used the [TASK-15 fog snapshot](../testing/fog.md#handoff) as its incremental
control. The [TASK-17 checkpoint](../testing/prototype_checkpoint.md) compared
the integrated shadow snapshot with Sodium shaders-off in the complete scene
set and recorded CONTINUE. TASK-18 measured its added sky-draw GPU work in an
offscreen harness. TASK-19 used the TASK-18 snapshot as the incremental
control for its 1440p client-loop timings. TASK-20 compares with the accepted
TASK-19 snapshot and Sodium shaders off. TASK-21 uses the TASK-20 snapshot
and Sodium shaders off, and repeats the isolated sky draw timer with the
new palette and cloud response. TASK-22 compares TASK-21 and Sodium shaders
off in the fixed night and cave scenes. TASK-23 uses the TASK-22 control and
Sodium shaders off, profiles forest and open water, and times the spatial
trial in the existing final draw. The accepted final pass still reads one
color sample per pixel.
[Cloud timings](../testing/clouds.md#gpu-cost), [water timings](../testing/water.md#performance),
[vegetation timings](../testing/vegetation.md#performance),
[weather timings](../testing/weather.md#performance),
[night and cave timings](../testing/lighting_dimensions.md#performance),
[AA trial and final-pass cost](../testing/anti_aliasing.md).
The [evidence transfer checklist](../../evidence/README.md#what-to-transfer)
covers the archived fixtures, raw metrics, logs, captures and references.

## Blocked, reduced and deferred features

- **Out of scope / unavailable assets:** Genshin meshes, authored terrain silhouettes,
  painted textures, species/density, UI and interaction rings. Shaders cannot supply
  absent authored assets/state. No resource pack, extraction or mod branch.
- **Reduced:** local mist banks → distance atmosphere; scene reflections → analytic
  sky; multilayer colored transmission/refraction → ordinary alpha tint with
  bounded depth absorption. Invalid background depth selects fixed absorption.
- **Runtime evidence:** TASK-11 covers S1 in fixed Overworld scenes. TASK-12
  covers S2 direct light in those scenes and a stepped dawn/dusk sequence.
  TASK-13 covers the ambient response in fixed forest, cave, night, daylight
  and sunset scenes. TASK-14 covers S3 sky color and sampled time continuity
  in clear Overworld weather. TASK-15 covers S4 in fixed views with clear and
  settled rain conditions. TASK-16 verifies bounded cast shadows from the
  tested casters. TASK-18 verifies one projected cloud layer and measures its
  incremental GPU cost in an offscreen sky draw. TASK-19 verifies water
  thickness, transparency and fixed submerged views in the Overworld fixture.
  TASK-20 verifies static vegetation tint, cutouts and shadow contact in
  four matched clear-day views. TASK-21 exercises both directions of the
  clear/rain ramp from the daylight, open-water and dense-canopy views.
  TASK-22 checks fixed night and interior lighting, plus one Nether and one
  End view and the return to the Overworld. TASK-23 samples motion in three
  clear-day paths and measures the disposable spatial filter in isolation.
  TASK-28 and TASK-30 check the tuned build in motion and through weather,
  waterline, cave and command-teleport transitions.
  Specialized transparency parity and integrated GPU pass timings remain open.
- **Additional effects:** TASK-24 assigns AA, scene-wide bloom, separate
  vertex AO, height-weighted fog and plant motion to handoff. It rejects
  screen-space AO, geometry reflections and screen-space refraction for
  this build. A sun halo in the existing sky draw is the sole optional small
  trial. [AA decision](../testing/anti_aliasing.md), [effects triage](deferred_effects.md).
- **Unverified compatibility:** other hardware/OS/loaders, modded materials,
  Distant Horizons/Voxy, custom dimensions and specialized effects in the Nether
  and End. TASK-29 records the exact runtime and why the optional 26.3 run
  was skipped. [Compatibility limits](../testing/compatibility_notes.md#untested-combinations).

The TASK-08 architecture gate cleared implementation under these reductions.
