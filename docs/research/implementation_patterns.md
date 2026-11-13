# Targeted implementation patterns — TASK-07

Status: **DONE**, 2026-11-12. Dependency: [TASK-06](iris_feasibility.md).
Current progress is in [STATUS](../STATUS.md). This is a source study and original
algorithm proposal, not shader implementation, a pass architecture decision or a
benchmark. Preserve [TASK-05's S1–S7 targets](style_targets.md).

## Study boundary and provenance

Two projects answer the immediate questions: MakeUp Ultra Fast for bounded work,
and Complementary Reimagined for stylized light/material treatment. TASK-07-A
(MakeUp), TASK-07-B (Complementary), and TASK-07-C (synthesis/checks) are complete.
BSL, Photon, Solas and Mellow were not inspected: no remaining source-pattern
question justifies expanding the study. Installed-beta behavior needs runtime
experiments rather than another repository. Upstream advertised performance and
compatibility are not evidence for our pack.

| Study | Canonical repository and pinned revision | License observed / reuse decision |
| --- | --- | --- |
| A | [MakeUp Ultra Fast](https://github.com/javiergcim/MakeUpUltraFast), `fed6d05f841389fb5981f078e2fcac8dfb9c0080` | Root `LICENSE` and named GLSL headers identify GNU LGPL v3.0. README requests attribution. No code reuse proposed; any later reuse requires file-specific notice and license review. |
| B | [Complementary Reimagined](https://github.com/ComplementaryDevelopment/ComplementaryReimagined), `c09950df0650b27dac260c1b0f69afc11387aa6f` | `License.txt`: Complementary License Agreement 1.7, custom terms. Modified-pack grant includes attribution, retained agreement, naming/visual differences, exclusive agreement and human-written additions; other uses default to reserved rights except file-level exceptions. Study only; no copying or porting. |

[Source manifest](../../evidence/task-07/sources.json) records exact file permalinks
and SHA-256 hashes, including license files. The two unmodified research clones
are ignored under `artifacts/task-07/`; they are not vendored shader source or
redistribution artifacts. No upstream code, constants, palettes, noise textures,
material tables or settings UI were added to `shaderpack/`. Licensing observations
record the upstream text, not a declaration that future reuse is compatible.

## Observed source patterns

Paths below are relative to each repository's pinned revision, not floating HEAD.
The manifest supplies a permalink for every named file. Observations describe
source branches; no upstream shader was launched or benchmarked.

### A — MakeUp Ultra Fast

- `shaders/gbuffers_terrain.fsh` is a thin version/define/include wrapper for shared
  `common` code; root entry selects a generic unknown-dimension route. Do not
  mistake this root file for the Overworld implementation or copy its version as
  our compatibility requirement.
- `shaders/lib/shadow_frag.glsl`, `get_shadow`: pixelated branch uses one shadow
  comparison; soft branch uses four comparisons with dithered offsets. Colored
  shadows add conditional depth/color reads. This demonstrates bounded filter
  work, but dithered softness alone does not establish stable motion without TAA.
- `shaders/lib/tone_maps.glsl`, `custom_sigmoid`: arithmetic highlight compression
  with channel powers; no LUT lookup in this function. Curve constants and channel
  behavior belong to this pack. A cheap function is not proof of correct color
  encoding or preserved hue.
- `shaders/lib/day_blend.glsl` and `shaders/src/{low_sky,hi_sky}.glsl`: shared
  day/sunset/night interpolation supplies horizon and zenith colors; rain blends
  toward alternate colors. `shaders/src/fog_vertex.glsl` computes distance fog in
  the vertex route with time/rain controls and camera/sky factors. Vertex work can
  reduce fragment arithmetic, but nonlinear fog interpolated over large triangles
  may diverge from per-fragment distance. Camera brightness is not surface light.
- `shaders/lib/water.glsl`: `refraction` compares projection-linearized surface
  and opaque `depthtex1` depths, then samples saved scene color (`gaux1`). Wave
  normals use three noise samples; reflection has projected and raymarch branches
  plus sky fallback. `fastRaymarch` loops to `RAYMARCH_STEPS`. Thus this water design
  has buffer ownership and repeated-read costs, not merely a cheap tint. The
  separate `lib/depth.glsl` helper also reinforces that raw depth is nonlinear;
  neither helper should be transplanted without its projection convention.

### B — Complementary Reimagined

- `shaders/world0/gbuffers_terrain.fsh` defines stage/dimension/program and includes
  a shared `program` implementation. Small wrappers and shared math are useful
  organization; the broad option tree is outside this project's scope.
- `shaders/lib/lighting/mainLighting.glsl`, `DoLighting`: distinct light/ambient
  colors, per-surface lightmap channels, material-dependent subsurface treatment,
  shadow range fading and separate block-light shaping. Additional branches use
  voxel lighting and material corrections. Retain the separation of responsibilities,
  not the entire system or its special-case constants.
- `shaders/lib/lighting/shadowSampling.glsl`: four basic comparisons, five calls
  to a potentially multi-read colored sampler for the low filtered path, or paired
  samples in a TAA-conditioned loop. `mainLighting.glsl` changes sample count by
  quality/material/proximity. A sampler call is not necessarily one texture read;
  temporal noise relies on other pipeline machinery. Our minimum needs neither
  colored-shadow textures nor temporal accumulation.
- `shaders/lib/atmospherics/fog/mainFog.glsl`: separates border, atmospheric,
  cave, water and status-effect fog; atmospheric density considers distance,
  altitude and rain, and border fog obtains sky color. Reflection handling reduces
  duplicate fogging. Useful lesson: share sky/fog color and define fog ownership,
  rather than reproduce the many controls or assume all geometry is outdoor air.
- `shaders/block.properties` separates water, leaves (including waterlogged
  states), grounded and upper-half foliage. `shaders/lib/materials/materialMethods/
  wavingBlocks.glsl`, `DoWave`, uses those categories and texture midpoint/position
  heuristics, with shared terrain/shadow branches. These heuristics are model
  dependent, not a general semantic root locator. Its newer block names are not
  our 1.21.1 material list.
- `shaders/program/gbuffers_water.glsl` includes material handling, lighting and
  fog and passes depth into reflections. This supports the need for explicit
  translucent material routing; it does not validate our installed Iris ordering.

## Original implementation candidates

These are independently specified algorithms, not translated upstream functions.
A and B are alternatives for developer evaluation, not player profiles. Suggested
preferences remain inputs to TASK-08; it owns actual pass/buffer selection. All
costs below are structural estimates, with no measured milliseconds or FPS claim.

| Target | Approach A — preferred starting candidate | Approach B — bounded alternative | Cost / deciding evidence |
| --- | --- | --- | --- |
| S1 palette | Decode texture color once; use fixed exposure, luminance-based smooth shoulder and rescale RGB together to retain hue, then modest saturation and one display encode. Guard near-zero luminance. | Apply a smooth channel-wise shoulder with restrained saturation before encoding. Simpler hue handling but highlights can shift chroma; independently tune coefficients from reference relationships. | Arithmetic in an existing output stage; no LUT/history. A needs luminance dot/divide; B can shift bright grass/snow colors. Check neutral ramp, snow relief, lamps and sunset greens; establish buffer encoding first. |
| S2 light | Linear albedo times sum of cool ambient gated by surface skylight, warm direct term gated by normal and shadow visibility, and warm block-light response. Preserve AO and disable duplicate vanilla directional shading only with a verified contract. One finite shadow map, fixed four-tap comparison kernel, slope-aware bounded bias and edge fade. | Same independent ambient/block terms, but a smooth wrapped direct-light response with one comparison lookup; achieve softer appearance mainly through ambient contrast rather than larger filters. | Both need a shadow geometry pass. A: four comparison instructions per eligible fragment; B: one (hardware filtering may perform more internal work). B risks obvious stair steps; A costs bandwidth. Check cutouts/chest/contact, cave leakage, sunset and camera motion. No blocker search, colored shadows or TAA dependency. |
| S3 sky | Analytic horizon-to-zenith gradient using view elevation, a broad sunward lobe, and cyclic interpolation of a small fixed time palette. Retain vanilla clouds initially. | A low-order elevation polynomial with coefficients smoothly driven by sun height; same horizon endpoint as fog, independent dim night term. | No atmosphere LUT/raymarch. A gives direct artistic control; B needs fewer palette anchors but may flatten sunset. Inspect continuous dusk/dawn, banding and clouds, not just three still times. |
| S4 depth | Fragment distance ramp with a near clear zone and smooth bounded blend toward the shared horizon color. Reuse geometry distance where available. | Analytic exponential distance attenuation with a bounded height weight calculated from camera and fragment elevation; no sampled volume. | No extra texture read if position already exists; a later screen-space variant requires depth reconstruction/read. B adds exponential/height work and may veil valleys/caves. Compare near/mid/far landmarks; existing platform is insufficient. No authored mist-bank claim. |
| S5 weather | One smoothly changing rain factor desaturates sky, reduces direct light and increases S4 density together; keep precipitation geometry. | Separate onset/recovery smoothing for atmospheric color and direct light, both derived from existing weather signals, to soften transitions. | Reuse uniforms/math, no new wetness buffers. B can lag actual rainfall and needs transition checks. Inspect shelter/dry biomes/snow; global weather is not local wetness. |
| S6 water | Explicit water ID, bounded turquoise tint and alpha with analytic sky reflection weighted by view angle; two low-amplitude analytic waves perturb normals only. | Reconstruct opaque bottom and surface positions on the same view ray, use clamped nonnegative separation for absorption, then the same sky reflection. No SSR/refraction offset. | A avoids depth/scene-color reads but cannot satisfy depth-dependent shallows: label PARTIAL. B adds at least one opaque-depth read and reconstruction; alpha absorption can avoid scene-color feedback, subject to blend contract. Guard sky/hand/negative cases and underwater separately. Validate sloped basin, glass overlap, shoreline and double fog before accepting B. |
| S7 foliage | Explicit small vanilla leaf/plant categories; preserve biome tint, texture alpha and AO. Bounded wrapped diffuse and skylight-gated backlighting retain canopy contrast without emission. Keep vertices static. | Same lighting with one low-frequency vertex oscillation, amplitude zero at verified plant bases and matching deformation in shadow geometry; leaves use a separate small amplitude. | A adds arithmetic only. B adds vertex trigonometry and mapping/shadow obligations, no fragment texture lookup. Test tall-plant halves, cutouts, dense canopy, waterlogged leaves and motion; omit wind if anchoring fails. |

For S2, out-of-map visibility must fade toward the surface-skylight approximation,
not sample arbitrary border depth. Bias must be evaluated at grazing angles and
kept small enough not to detach shadows. Do not copy upstream shadow distortion
unless both rendering and sampling transforms are independently designed together.
For S6, TASK-19 later used scene-linear straight-alpha blending with the
existing color attachment. Layered translucent volumes remain outside the
verified fixture. [Water report](../testing/water.md#shader-behavior).

## Transfer, exclusions and TASK-08 handoff

Transfer concepts: separate direct/ambient/block light, bounded comparisons,
shared cyclic time/weather colors, explicit material classes, common terrain/shadow
vertex math, and deliberate color/depth ownership. Write small original helpers
and thin entry points only when implementation tasks authorize them.

Exclude upstream settings/profiles/localization, PBR textures, voxel GI, SSR,
volumetric cloud/fog marches, automatic exposure, colored shadows, TAA and imported
assets from the starting candidates. These add costs or scope without evidence
that S1–S7 require them. This is a starting constraint, not a measured ranking.

TASK-08 should choose minimum passes and formats, and decide whether a scoped
spike is essential for opaque-depth access/blending, beta block-entity shadows,
and separate AO. None of these uncertainties was closed by source study. Retain
TASK-06's installed-beta/source-revision distinction; do not upgrade the client.
Plan later near/mid/far terrain, variable-depth water, snow and temporal QA.
Measure matched Sodium baseline, empty-pack overhead, shadow pass/filter cost and
water/foliage increments using the existing harness at fixed scene/settings;
CPU render-loop recordings are not isolated GPU timings.

No blocker remains for this research task. No client launch, GLSL compilation,
visual acceptance, benchmark, source reuse or compatibility claim occurred.
Next task at completion: **TASK-08**, not started.
