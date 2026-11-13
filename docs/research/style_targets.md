# Visual targets and comparison rubric — TASK-05

Status: **DONE**, 2026-11-12. Dependencies TASK-03 and TASK-04 are complete.
This defines seven essential visual targets for one default style. It does not
implement shaders or certify Iris capabilities. All proposed algorithms below are
original design candidates. TASK-06 has since documented source-backed capabilities
and remaining uncertainties in [iris_feasibility.md](iris_feasibility.md); TASK-08
owns pass architecture. See [STATUS.md](../STATUS.md) for current progress.

## Direction and evidence

Aim for clear, colorful landscapes: warm sunlit surfaces, cooler readable shade,
blue skies, progressively softer distant terrain, restrained turquoise water and
bright foliage that still has depth. Preserve vanilla texture and block identity.
Use green daylight landscapes as the default anchor; sunset, rain and night are
coherent environmental variations, not selectable looks. The purple fantasy scene
is evidence of depth/color separation, not a mandate to tint every biome purple.

**Observed** below means visible in the selected decoded frames reviewed for this
task. **Proposed** means an artistic or algorithmic choice, not an attribution of
Genshin's implementation. Camera, exposure, source settings and exact game time
are unknown. The TASK-04 samples cover starts, interiors and ends of multiple clips;
this review uses ten targeted PNGs from nine clips, not just opening frames.
Still images establish spatial relationships, not motion cadence or stability.

The following example links open original-size decoded PNGs. Source paths and
actual presentation timestamps are explicit; hashes and decoded frame numbers
remain in [frames.json](../../evidence/task-04/frames.json). The
[reference inventory](reference_index.md) and [frame index](frame_index.md) retain
full coverage and limitations. Do not use contact-sheet JPEG colors as calibration.

| ID | Source / actual timestamp | Example frame | Inspect |
| --- | --- | --- | --- |
| R1 | [01.mp4](../../references/video/gameplay/01.mp4), 0.000000 s | [Valley](../../artifacts/task-04/video-01/frame-001.png) | Green foreground, cool shaded cliffs, hazy city; cream cloud tops |
| R2 | [06.mp4](../../references/video/gameplay/06.mp4), 0.000000 s | [Walkway and grass](../../artifacts/task-04/video-06/frame-001.png) | Warm boards, dark but readable crate sides, yellow-green grass and teal canopy |
| R3 | [03.mp4](../../references/video/gameplay/03.mp4), 40.016650 s | [Mountain layers](../../artifacts/task-04/video-03/frame-009.png) | Near rock detail versus pale distant cliffs and dense low mist |
| R4 | [02.mp4](../../references/video/gameplay/02.mp4), 45.016650 s | [Rain sky](../../artifacts/task-04/video-02/frame-010.png) | Slate sky, dim blue-gray rock, faint rain streaks |
| R5 | [08.mp4](../../references/video/gameplay/08.mp4), 35.016650 s | [Warm shoreline](../../artifacts/task-04/video-08/frame-008.png) | Peach horizon to lavender sky, cool rocks, warm sand, turquoise water |
| R6 | [09.mp4](../../references/video/gameplay/09.mp4), 59.399983 s | [Blue settlement](../../artifacts/task-04/video-09/frame-013.png) | Blue ambient environment, readable cliffs and localized warm lamps |
| R7 | [07.mp4](../../references/video/gameplay/07.mp4), 40.016650 s | [Shallow oasis](../../artifacts/task-04/video-07/frame-009.png) | Visible near bottom, greener far water, bounded rock/palm shadows |
| R8 | [11.mp4](../../references/video/gameplay/11.mp4), 15.016650 s | [Snow village](../../artifacts/task-04/video-11/frame-004.png) | Cool snow with visible relief, warm lanterns, dark wood |
| R9 | [02.mp4](../../references/video/gameplay/02.mp4), 0.000000 s | [Clear coast](../../artifacts/task-04/video-02/frame-001.png) | Light blue atmosphere, readable sun/shade, turquoise coast to blue offshore |
| R10 | [10.mp4](../../references/video/gameplay/10.mp4), 50.016650 s | [Purple landscape](../../artifacts/task-04/video-10/frame-011.png) | Saturated foreground versus pale distant silhouettes; authored luminous plants |

## Priority and provisional feasibility

Rank combines screen coverage/visual impact with expected implementation cost.
It is an artistic prioritization, not a benchmark or replacement for the numbered
implementation order. All seven core targets are essential. The table preserves
TASK-05’s provisional hypotheses. For later runtime findings and remaining
capability checks, use [Iris feasibility](iris_feasibility.md#limits-and-follow-up-gate).

| Rank / ID | Essential signature | Impact | Provisional feasibility / cost reason |
| --- | --- | --- | --- |
| 1 / S1 | Controlled vivid palette and highlight rolloff | Very high, whole image | Favorable: arithmetic in an existing color stage; no LUT required |
| 2 / S2 | Warm direct light, cool ambient fill and legible shadows | Very high, terrain form | Mixed: simple lighting favorable; cast shadows require a shadow render and filtering |
| 3 / S3 | Broad sky gradients with coherent time colors | High, large background | Favorable for analytic gradient; shaped clouds remain uncertain |
| 4 / S4 | Atmospheric depth without a foreground veil | High, landscape depth | Favorable if distance/depth is available; true local mist is more costly |
| 5 / S5 | Overcast weather changes lighting as well as sky | Medium–high in rain | Favorable if weather controls are available; reuse S2–S4, no wetness pass |
| 6 / S6 | Clear shallows and restrained turquoise water | High locally | Uncertain: transparent material/depth ordering and reflection inputs need checking |
| 7 / S7 | Luminous-looking but grounded vegetation | Medium locally | Static tint and leaf lighting are cheap if vanilla plant and leaf IDs are available. Wind adds model anchoring and shadow checks. |

### S1 — Controlled vivid palette

**Observed:** R1/R2 separate green plants, neutral/cool rock and warm wood. R5 keeps
warm sand distinct from violet-blue rock; R8 retains snow relief beside bright
lamps. R10 has a different regional palette, so a single sampled RGB or global
saturation boost cannot describe all footage.

**Proposed cheap first choice:** fixed exposure with a smooth highlight shoulder,
modest luminance-aware saturation and restrained warm-light/cool-shade tinting.
Keep neutral materials recognizable; derive variation from lighting and existing
biome colors. Fold arithmetic into an already needed color output stage. No extra
blur, LUT texture, auto-exposure history or color-quantization pass initially.

**Scenes / pass:** in **daylight** and **forest**, distinguish grass, leaves, trunk,
stone and brick at a glance; retain texture in both bright tops and shaded faces.
In **sunset**, grass must remain identifiable as green rather than uniformly orange.
In **night** and **cave**, lights may be bright but nearby stone must not become a
featureless white patch. Pass when these relationships resemble R1/R2/R5/R8 and
none of these regressions appear. TASK-11 checked snow highlight response with a
[temporary daylight swatch](../testing/palette.md#visual-review). Natural snowy
terrain and snow weather remain untested.

### S2 — Warm light, cool fill and legible shadows

**Observed:** R2 has warm board tops and cool/dark crate and rock faces with retained
detail. R7's rock and palm shadows are bounded and fairly crisp; the style is not
uniformly blurry. R1 has broad readable shade. R6/R8 contrast cool surroundings
with warm local lights. Soft overall appearance is partly color/value balance;
stills do not prove global illumination, subsurface scattering or a penumbra method.

**Proposed cheap first choice:** separate sky/ambient and directional terms, smoothly
vary sun tint with time, and retain existing block-light information for warm local
light. Gate outdoor fill by available skylight so caves do not acquire outdoor blue
illumination. For cast shadows, investigate one bounded shadow map and a small fixed
filter kernel; reserve its extra geometry pass and samples for measured benefit.
Use ambient fill to soften contrast before widening shadow filters. No GI, contact
ray tracing, SSAO pass or large variable filter as the starting point.

**Scenes / pass:** **daylight/forest** tree shadows anchor trunks and retain grass
texture; lit areas remain brighter than shaded ones. No detached shadows, acne or
obvious blocky stair steps at normal viewing scale. **sunset** gives coherent light
direction without bleaching stone; **night** is visibly dimmer than day while
landmarks remain readable. **cave** preserves warm lantern pools and darker recesses,
without sky tint leaking through the ceiling. R2/R7 anchor outdoor judgment; R6/R8
anchor warm/cool separation only. Cave is a regression guard, not a source-matched
Genshin interior target. Later motion QA must check shadow shimmer separately.

### S3 — Sky gradients and time coherence

**Observed:** R9 has a light blue horizon and blue upper sky; R1 has broad bright
cloud masses with cream tops and cooler undersides. R5 has peach near the low sun
and lavender higher sky. R6 has blue sky and visible star-like points; its precise
time is unknown. Do not interpret blue lighting alone as a night-time calibration.

**Implemented approach:** analytic horizon/zenith color interpolation based
on view elevation, with a broad sunward tint and smooth time interpolation.
TASK-18 adds one projected procedural cloud layer to that draw.
[Sky report](../testing/sky.md), [cloud report](../testing/clouds.md).

**Scenes / pass:** **daylight**, **sunset**, **night** show distinct, coherent blue,
peach/lavender and dim cool states respectively; horizon merges with S4's atmosphere.
Sky gradients must have no obvious bands, seams or clipped white dome. Cloud bases
must remain distinct from bright tops/background where visible. R9/R5/R6 are color
relationship anchors; exact cloud shape matching is excluded. Three still presets
cannot pass continuous transitions: later capture intervening times and inspect
for popping before declaring temporal acceptance.

### S4 — Atmospheric depth

**Observed:** R1/R9 lose contrast and shift toward sky color with distance. R3 has
strong pale low banks separating mountain layers, and R10 separates dark nearby
forms from pale silhouettes. Local mist banks are visibly richer than uniform fog.

**Proposed cheap first choice:** one smooth distance-based blend toward the horizon
color, with restrained saturation reduction. Investigate a cheap analytic height
weight only if needed and supported. Apply consistently to terrain and water while
preserving sky treatment. Do not start with raymarched volumes, light shafts,
multiple noise samples or a full-screen blur. A distance blend approximates depth;
it cannot reproduce R3's individually shaped mist banks.

**Scenes / pass:** **daylight** and **open-water** should keep foreground grass,
shore and stone crisp while farther visible geometry approaches sky color without
a hard fog wall or halos. **rain** can increase this effect without hiding the near
trees. References are R1/R3/R9. The TASK-03 map supports near-field checks.
TASK-15 adds a separate fixed overlook with foreground foliage, water and
glass, and staggered stone ridges. [Fog report](../testing/fog.md).

### S5 — Coherent overcast response

**Observed:** R4 has a dark slate sky, dim cool foreground and visible rain streaks,
contrasting with the clear blue coast in R9. These are different camera views from
one clip, not a controlled weather A/B. They do not isolate rain's exposure change
or establish animation/droplet density. R8 provides a separate cold, snowy palette;
its bright points do not by themselves establish snowfall behavior.

**Proposed cheap first choice:** blend S2 direct light downward, S3 toward a muted
slate palette, and S4 toward denser cooler atmosphere using a shared weather factor.
Retain vanilla precipitation initially. No new rain particles, puddles, material
wetness maps, screen droplets or full-scene reflective coating are essential.

**Scenes / pass:** compare **rain** against **daylight** (same camera/time): reduced
sun/shadow contrast and muted sky must read as overcast, while stone and tree shapes
remain legible and the near field is not uniformly black. Rain streaks remain
visible without a bright blue curtain overwhelming the landscape. R4/R9
guide the relative palette and readability. TASK-21 sampled both transition
directions in fixed midday gameplay views and reduced falling-streak
chroma. Snow weather remains untested. [Weather review](../testing/weather.md#visual-review).

### S6 — Clear shallow water with restrained surface detail

**Observed:** R7 shows the bottom near the player, blue-green farther water and
small surface rings. R9 shifts from turquoise shoreline toward bluer offshore;
R5 retains turquoise water beside warm sand. Bottom material, depth, lighting and
regional art all contribute; these frames cannot isolate a reflection algorithm.

**Proposed cheap first choice:** water-specific tint with bounded depth absorption
if reliable scene/water depth is available, a view-angle blend toward analytic sky
color, and a low-amplitude procedural normal perturbation. Prefer a few analytic
wave terms without new texture assets. If depth is unavailable, document a simpler
tint/transparency fallback and its missing depth cue. No SSR, refraction tracing,
caustics, physical waves or character-interaction rings as essentials.

**Scenes / pass:** **open-water** must retain the visible near bottom, a coherent
shoreline and a blue-green surface; distant/grazing water may reflect more sky but
must not become a flat mirror or neon opaque slab. **sunset** must keep water and
sky lighting consistent. R7/R9/R5 anchor these relationships. The shallow,
constant-depth basin checks transparency and angle response. Use a fixed
sloped/deeper basin to evaluate absorption, and include daylight and rain
for TASK-19 acceptance.
TASK-19 verified bounded absorption in the stepped basin and captured daylight,
settled rain, sunset and fixed submerged views. TASK-23 records the moving
shoreline during a shallow entry with the camera above the surface. TASK-28
records a rise above the surface and resubmersion. Extended swimming remains
untested. [Water report](../testing/water.md),
[runtime regression](../testing/regression_report.md#runtime-results).

### S7 — Bright vegetation with retained volume

**Observed:** R2 has bright yellow-green grass and cyan-green canopy tops contrasted
with dark canopy interiors; R1 also has darker green masses and yellow accents.
R5 retains vivid grass beside cool rock under warm light. Fine blades, rounded
canopies and flower density are authored assets, not evidence of a shader effect.

**Proposed cheap first choice:** retain vanilla biome tint; use modest wrapped
lighting or a bounded backlight term on reliably identified vegetation. Avoid
lifting all faces equally or making leaves emissive. Investigate small vertex sway
only later, with base anchoring and consistent shadow displacement; it is an
optional motion enhancement, not a still-evidence-derived requirement. No new grass
geometry, leaf textures, flowers or simulated subsurface scattering pass.

**Scenes / pass:** **forest** canopy tops and shaded interiors retain distinct
values; alpha cutouts remain clean, trunks stay solid/darker, and ground grass does
not become fluorescent. **daylight** preserves green versus stone separation; R2,
R1 and R5 anchor judgment. The nine block-canopy trees provide a repeatable
leaf response check. TASK-20 adds dense views from below and above mixed
canopies and checks the plains/jungle tint boundary and plant cutouts.
[Vegetation report](../testing/vegetation.md).

## Repeatable qualitative comparison

Use the existing [TASK-03 scene definitions and capture workflow](../testing/scenes.md).
Approved baselines are [daylight](../../artifacts/task-03/daylight-01/native.png),
[forest](../../artifacts/task-03/forest-01/native.png),
[rain](../../artifacts/task-03/rain-01/native.png),
[night](../../artifacts/task-03/night-01/native.png),
[cave](../../artifacts/task-03/cave-01/native.png),
[sunset-02](../../artifacts/task-03/sunset-02/native.png) and
[open-water-02](../../artifacts/task-03/open-water-02/native.png).
The earlier sunset/water `-01` images in contact sheets are superseded.

1. Record shader revision, environment/config snapshot and target IDs. Keep the
   same world, camera, time/weather, vanilla textures, 2560×1440 resolution, FOV 70,
   render/simulation distances 12/8 and documented warm-up. Preserve original PNGs.
   Re-capture a Sodium baseline if environment or geometry has changed.
2. Compare Sodium and candidate at the same scale and crop. Look at full-frame
   value/color structure first, then native-resolution texture, edges, shadows and
   transparency. Compare reference regions by role (lit grass, shaded rock, horizon,
   shallow bottom), not pixel registration between different games. Exclude HUD,
   watermark, character art and gameplay effects from aesthetic judgment.
3. For every applicable S1–S7 criterion record **PASS**, **PARTIAL**, **FAIL** or
   **UNVERIFIED**, and a plain-language observation with both image paths. PASS means
   all listed checks for the tested scope are met. PARTIAL means visible progress
   with named unmet checks. FAIL means a named check regressed or is absent.
   UNVERIFIED means missing evidence/coverage; never silently count it as a pass.
4. Record directional change separately: **improved / unchanged / regressed** versus
   baseline, with the specific reference ID and material/region. A target can improve
   and still fail. Do not average statuses, assign weights or invent similarity
   percentages. A convincing day frame cannot compensate for broken cave lighting.
5. Repeat static scenes after intervening views to check reproducibility. Free-running
   clouds, precipitation and water need visual review, not whole-image pixel equality.
   For animation/transition claims, preserve moving captures and inspect flicker,
   seams, popping and shadow stability; stills alone stay UNVERIFIED for motion.
6. Keep performance acceptance separate. Use TASK-10's baseline methodology and later
   per-effect raw timings under matched conditions; TASK-02's capped CPU profiler
   smoke data cannot establish GPU cost. No extra pass or higher sample budget is
   justified solely by a pretty still. Record visible benefit, measured cost and
   retained/removed decision when implementation work reaches that effect.

Suggested review record (not a result):

| Target / scene | Reference | Baseline / candidate paths and revision | Status / direction | Concrete observation, gap and next check | Performance evidence |
| --- | --- | --- | --- | --- | --- |
| S2 / forest | R2 | Fill in captured evidence | UNVERIFIED / not assessed | Check trunk contact, leaf interior and shaded grass | Pending matched effect test |

**Implementation evidence:** TASK-11 records S1 observations and matched
performance measurements in the [palette report](../testing/palette.md).
TASK-12 validates the S2 direct-light component in the fixed daylight, sunset,
forest, night and cave views. TASK-13 checks the ambient response in the same
presets. TASK-16 checks caster contact, cutout shape, range fade and small
fixed-angle camera steps. TASK-23 found no obvious shadow flash on its
clear-day ground paths. Fine shadow-edge stability remains unmeasured.
[Sunlight report](../testing/sunlight.md), [ambient report](../testing/ambient.md),
[shadow report](../testing/shadows.md), [motion review](../testing/anti_aliasing.md#visual-review).
TASK-14 covers the S3 clear-sky palette, fixed time sweep and sampled live
dusk and dawn. TASK-15 covers S4's distance blend. TASK-18 adds a single
projected cloud layer and checks fixed sunset, settled rain and night
captures. [Sky report](../testing/sky.md), [fog report](../testing/fog.md),
[cloud report](../testing/clouds.md).

TASK-19 checks S6 water depth, tint and transparency in the stepped basin.
TASK-20 checks S7 biome tint, canopy contrast, cutouts and shadow contact in
four matched views. TASK-21 coordinates S5's overcast response and checks
both live weather transition directions. [Water report](../testing/water.md),
[vegetation report](../testing/vegetation.md),
[weather report](../testing/weather.md).

TASK-22 checks S1 highlight control and S2 readability in fixed midnight,
lantern cave, mixed-lamp and unlit views. The sampled light sources retain
bright faces and nearby stone texture. The neutral fill reveals the unlit
steps while preserving darker recesses in the cave. The Nether and End
views are smoke tests outside the reference-matching rubric.
[Lighting and dimension report](../testing/lighting_dimensions.md).

TASK-23 checked stone edges, leaf cutouts and the shoreline in continuous
clear-day movement. The spatial filter softened some edges in stills, and
leaf shimmer persisted in motion. The accepted pack keeps its single-sample
final pass. [AA decision and measurements](../testing/anti_aliasing.md).

TASK-25 applies the S1–S7 rubric to eight matched Overworld views. Its fog
follow-up improves mid-distance contrast in the natural valley. The
live weather sequences above used the earlier fog ramp.
[Integrated comparison and follow-up](../testing/visual_comparison.md).

## Scope limits and next handoff

Out of scope: matching painted albedo textures, round rock/tree silhouettes,
vegetation density/species, terrain composition, custom architecture, characters,
anime face shading, authored luminous plants, waterfalls/foam geometry, gameplay
particles and interactive splash rings. Shader-only light/color can suggest the
mood but cannot supply those missing assets. Do not enable Project Amber to hide
these differences, extract proprietary assets or introduce a resource pack/mod.

TASK-24 proposed a compact sun halo as an optional trial. Scene-wide
bloom, height-weighted fog and foliage wind are
handoff items. Screen-space refraction and geometry reflections are outside
the planned build. Settings screenshots identify controls. The recorded
settings and algorithms remain unknown.
[Effects triage](../architecture/deferred_effects.md#dispositions-and-expected-gpu-work).

The TASK-05 handoff requested TASK-06 investigation of each S1–S7: color-space/output behavior; lightmap and
sun/shadow access; sky/time and weather inputs; distance and transparent depth;
water/vegetation identification; and cloud/vertex integration limits. The completed
[TASK-06 report](iris_feasibility.md) supplies official sources and records remaining
runtime uncertainties. TASK-07 owns upstream technique/license study and TASK-08 owns
architecture decisions. Preserve these target IDs so feasibility outcomes can link
back directly. Scene extensions and motion QA are later validation needs, not
changes made by TASK-05. At TASK-05 completion, the next task was TASK-06;
use [STATUS.md](../STATUS.md) for the current task boundary.
