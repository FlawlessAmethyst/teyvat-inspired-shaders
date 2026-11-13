# Decision ledger

## D-001 — Scope precedence (2026-11-11, TASK-01)

Preserve the owner-supplied `task.md` locally and resolve
superseded requirements in `docs/SCOPE_OVERRIDES.md`. Keep `task_decomposed.md`
as the single numbered task source; `docs/CODEX_TASKS.md` is its stable entry point.
Reason: preserve artistic context without reinstating excluded work or drifting copies.

## D-002 — Reuse the proven environment (2026-11-11, TASK-01)

Use the existing NeoForge Prism Flatpak instance and `tools/minecraft.py`.
Keep `docs/minecraft-environment.md` as the environment handoff, linked from the
state ledger rather than copied into a second potentially divergent file.
TASK-00 evidence is inherited, not rerun or expanded by TASK-01.

## D-003 — Keep source small and originals untouched (2026-11-11, TASK-01)

Ignore supplied references, runtime artifacts and future evidence by default.
Track only small reviewed TASK-01 integrity/verification text and directory guides.
Do not create release archives, vendor dependencies, choose a source license on the
owner's behalf, or implement shaders in this initialization task.

## D-004 — Native performance recorder (2026-11-12, TASK-02)

Use Minecraft's existing F3+L recorder, with no added mod or overlay. Preserve the
native ZIP and export client render-loop timings from nanoseconds to milliseconds.
Verify units against installed bytecode and match samples to display-update counts.
Do not use server ticks as frames or claim GPU/presentation timing. Initial capped,
profiled recordings establish harness operation only; TASK-03 owns controlled scenes.

## D-005 — Scoped input and graceful stop (2026-11-12, TASK-02)

Extend the existing cwd/PID-verified toolkit and expose it through scripts/harness.py.
Window-targeted held uppercase debug chords worked where lowercase attempts failed;
the underlying cause remains unverified. Record commands reject stale archives and
observed focus loss. Shutdown requests WM_DELETE_WINDOW, waits for exit and never
force-kills Java. In-world save completion was verified in logs. Preserve the
pre-test world backup locally; do not restore over normally saved progress.

## D-006 — Isolated controlled map and vanilla texture baseline (2026-11-12, TASK-03)

Copy the existing creative world to TASK-03 Visual Scenes, preserving New World.
Record its seed and construct explicit vanilla geometry above the terrain for
lighting, grove, water and cave comparisons. A world-local developer datapack is
only test tooling, not a companion mod or deliverable resource/shader pack.
Disable the pre-existing Project Amber resource pack for baseline captures and
preserve original configuration files. Leave baseline settings in the isolated
instance for later testing. No assets/mods are added, removed or updated.

## D-007 — Replay through verified hotbar triggers (2026-11-12, TASK-03)

Typed punctuation was altered by the host/GLFW input path; clipboard experiments
also failed. Use world-local hotbar selection triggers, log acknowledgments and
native F2 captures. Require the dedicated world session lock before input. No
keyboard-layout or display-permission changes. Replay locks camera/time/weather,
waits for chunks and 20 seconds of rendering, and hides/restores HUD. Camera
positions settle on solid ground; the final water view is on shore. Animation
phases remain free-running; assess full-frame visual alignment and report both
whole-frame and static-region pixel differences, never artistic similarity scores.

## D-008 — Traceable still sampling (2026-11-12, TASK-04)

Inventory all 30 supplied sources and sample all 11 clips at five-second marks
plus first/final decoded frames. Record actual source presentation timestamps and
frame indices using FFprobe, avoiding nominal-FPS timestamp inference. Preserve
native-size PNGs and use reduced labeled contact sheets only for navigation.
Visually review every sheet and catalog scene groups without ranking style targets
or attributing algorithms. Source integrity is checked against TASK-01 before/after
extraction. Five-second sampling can miss brief events and does not validate motion;
TASK-05 may revisit targeted originals. Keep generated media local and small indexes
eligible for version control; include ignored media explicitly in the handoff.

## D-009 — Seven evidence-linked style targets (2026-11-12, TASK-05)

Use S1 palette, S2 direct/ambient light and shadows, S3 sky, S4 atmospheric depth,
S5 weather, S6 water and S7 foliage as stable IDs for feasibility and later QA.
Anchor the default in green daylight landscapes, with coherent time/weather
variations; do not universalize the purple regional reference. Prefer arithmetic
and reused lighting inputs; shadow rendering and transparent-depth handling need
explicit feasibility and cost checks. Candidate methods are not claims about
Genshin internals or confirmed Iris support. See [style_targets.md](research/style_targets.md).

Judge qualitative material/value relationships, retaining vanilla textures and
geometry. Use PASS/PARTIAL/FAIL/UNVERIFIED with concrete observations, no aggregate
similarity score. Current scenes are regression anchors, not complete coverage of
layered fog, variable-depth water, snow, dense vegetation or temporal behavior.
Record those gaps for later validation rather than expanding TASK-05 into runtime
scene construction or shader work. No new assets, dependencies or architecture.

## D-010 — Source-backed Iris feasibility, separate from runtime acceptance (2026-11-12, TASK-06)

Map every S1–S7 essential target to official Iris docs and pinned 1.21.1 source.
All have a plausible shader-only minimum; robust water depth, beta-specific shadow
coverage and separate AO remain explicit uncertainties. Preserve the installed
beta and distinguish branch source from its unestablished build revision. Current
docs contain newer APIs and historical ID-width inconsistencies; use conservative
inputs and small explicit material IDs. See [iris_feasibility.md](research/iris_feasibility.md).

Do not infer texture/material data from colortex names, treat all translucent
terrain as water, subtract raw depth as metric thickness, or replace per-surface
skylight with camera brightness. Source/metadata checks are not shader execution,
visual acceptance or benchmarks. TASK-07 studies patterns; TASK-08 decides passes,
buffers and necessary spikes. No source reuse, architecture commitment or runtime
configuration change is made by this research task.

## D-011 — Distinguish historical handoffs from live status (2026-11-12)

After the user requested a documentation-drift fix, label old next-task pointers as
completion-time snapshots and route current progress to STATUS.md. Link TASK-05's
provisional feasibility to the completed TASK-06 report. Preserve dated test-log
results and original integrity hashes; the environment document's authorized Git
wording correction is excluded from the historical original-input hash check,
like the previously extended toolkit. All original reference media remain checked.
Update the reference-index generator as well as its output so regeneration retains
the correction. No numbered task is advanced.

## D-012 — Bounded upstream study, original implementation (2026-11-12, TASK-07)

Study MakeUp Ultra Fast and Complementary Reimagined at pinned revisions for
bounded shadow work, time/weather colors, depth-water costs and material handling.
Two projects suffice; runtime uncertainties do not justify inspecting all six.
Record licenses and file hashes before considering reuse. No code/assets are reused;
Complementary's custom agreement is not treated as a permissive license.

[Implementation patterns](research/implementation_patterns.md) specifies two original
alternatives for every S1–S7 target. Prefer fixed shadow work and analytic sky/fog,
without importing temporal filtering, SSR, voxel lighting or settings systems.
These are architecture inputs, not finalized passes or measured performance.
TASK-08 retains responsibility for the gate and any essential beta-specific spike.

## D-013 — Forward Iris-only minimum and conditional water depth (2026-11-12, TASK-08)

Select [the architecture](architecture/shaderpack_design.md): forward geometry
lighting into one scene-linear RGBA16F color attachment, final-only tone mapping
and display encoding, geometry-owned fog, and one bounded shadow map in TASK-16.
No deferred/composite pass, normal/material attachment, history or external assets.
Use original small helpers and explicit route/fallback semantics. Retain combined
vertex AO; do not depend on the beta's uncertain separate AO behavior.

No TASK-08-SPIKE is necessary for this reduced minimum. This decision assigned
block-entity shadow coverage to TASK-16 and opaque water depth to TASK-19.
Depth-independent water is PARTIAL for depth-dependent S6. Ordinary alpha
blending cannot solve colored transmission
or layered fog. No automatic extra buffer, Iris upgrade or architecture switch.
TASK-09 must validate actual GLSL loading before later effect work. No performance
or compatibility claim follows from this architecture decision.

TASK-16 later verified the test chest casting onto terrain. TASK-19 verified
pre-hand depth sampling in the stepped Overworld basin.
[Shadow evidence](testing/shadows.md#visual-review),
[water evidence](testing/water.md#visual-review).

## D-014 — Neutral GLSL scaffold and Iris fallbacks (2026-11-12, TASK-09)

Use three geometry families for vertex color, textured color and lightmapped
texture. Let Iris resolve terrain and other programs through those fallbacks
and supply its render-type alpha and blend behavior. Keep combined vertex AO
and legacy directional lighting. Preserve the encoded vanilla texture, tint
and lightmap product before converting it to linear sRGB for the single
RGBA16F color attachment. Use one final pass for sRGB encoding. This keeps
the initial lightmap behavior independent of assumptions about its encoding
and leaves custom lighting to TASK-12/13.

Write the buffer format directive in a multiline GLSL comment. The installed
Iris beta reads the declaration for allocation, and GLSL compilation ignores
it. The initial bare declaration reached the driver and failed. The corrected
runtime debug log confirms Iris requested RGBA16F. TASK-09 relies on the
existing fallback routing and has smoke coverage only. Dedicated paths for
specialized draws can follow a demonstrated need in their owning tasks.
[Iris framebuffer format directive](https://shaders.properties/current/guides/your-first-shaderpack/3_deferred_lighting/#gamma-correction).

## D-015 — Uncapped paired baseline on fixed scenes (2026-11-12, TASK-10)

Use daylight, forest and cave as the core performance matrix, with the other
four TASK-03 presets available for visual and targeted effect checks. Use two
fresh sessions per mode with Sodium sessions bracketing neutral sessions.
Keep the TASK-03 scene, render settings and warm-up policy. Run with Unlimited
FPS and VSync off to expose headroom that the old 240 FPS ceiling concealed.

Use the installed native profiler and retain every valid client loop sample.
Report profiled throughput and frame-loop duration quantiles per scene. The
mode difference combines Iris pipeline changes and neutral-pack work. It gives
a baseline for later measurements on this machine. GPU pass duration and
display presentation cadence need separate instrumentation.

## D-016 — Fixed exposure and peak-based highlight shoulder (2026-11-12, TASK-11)

Apply 1.48× exposure in the final pass. Expand RGB chroma around Rec. 709
luminance by up to 24%. The gamut bound preserves at least 30% of the smallest
exposed channel during chroma expansion. Then apply a shared RGB scale from the
channel peak.
The shoulder starts at 0.52 in exposed linear RGB, joins the linear range with
equal slope and approaches the display ceiling asymptotically. A peak-based
shoulder preserves ratios in bright saturated colors and bounds them using the
same curve as neutral highlights. Encode to sRGB after grading.

This is a single default. The existing geometry, lightmap and blending feed
the same final-pass read. The work adds scalar/vector arithmetic to that pass.
Scene-dependent sun and ambient tints belong to TASK-12 and TASK-13. The
diagnostic ramp variant is replay evidence outside the shipped shader tree.
TASK-21 makes chroma weather-dependent. [Current grade](testing/weather.md#shader-behavior).

## D-017 — Terrain sunlight with engine lightmap fill (2026-11-12, TASK-12)

Use Iris's view-space sun and up directions with transformed terrain normals.
Evaluate the warm daylight and amber low-sun response in the vertex shader and
interpolate it into the existing terrain pass. Reserve a portion of the engine
lightmap contribution for direct light based on sun elevation, per-surface
skylight and block light. Combine both contributions in linear RGB and retain
the TASK-11 grade. The slope response and sky gate use arithmetic with the
existing inputs, atlas and lightmap samples.

Disable legacy directional shading and retain combined vertex AO. Explicit
lightmapped routes keep water, block entities and breaking overlays out of the
terrain shader. Low-skylight terrain keeps its engine lightmap fill, with
sidewall differences from the global directional setting and dark values
affected by the separate color decodes. Use the graded snapshot as the
performance control. TASK-13 owns ambient balance and TASK-16 owns cast shadow
coverage. [Captures and measured delta](testing/sunlight.md).

## D-018 — Skylight-weighted ambient fill (2026-11-12, TASK-13)

Scale the existing terrain lightmap in linear RGB. Keep the direct term from
TASK-12 and combine its fill reservation with a tint that shifts from cool
daylight shade toward blue at night. Per-surface skylight determines where the
tint can appear. Bright block light and strong direct sun taper its influence.
Use no additive ambient floor so enclosed terrain keeps the engine's dark
recesses and local lamp response.

Interpolate the direct RGB and fill scale from the vertex stage. Retain one
lightmap sample, the existing pass layout and combined vertex AO. This is a
terrain-only approximation of ambient color and soft contrast. TASK-16 owns
cast shadows. Use the verified TASK-12 snapshot for the incremental comparison.
[Ambient report](testing/ambient.md).

## D-019 — Sky palette driven by solar elevation (2026-11-12, TASK-14)

Evaluate horizon and zenith colors at sky vertices from the same continuous
view-space sun and up directions used by terrain. Blend the colors with view
elevation and add a warm sun-facing tint in twilight. Reuse Iris's horizon
geometry and the existing scene target and grade. Add a small spatial dither
to the procedural sky draw.

Use Iris's sky stage to cover the disc and horizon with one directional
function. Skip the vanilla sunrise/sunset fan when that function is active.
Retain the engine tint for stars and the void plane and the textured
fallback for the sun and moon. Fog can evaluate the palette at zero view
elevation in TASK-15. [Sky report](testing/sky.md).

## D-020 — Forward distance fog toward the procedural horizon (2026-11-12, TASK-15)

Use a cubic ramp on squared view-space distance. At 12 chunks keep the
first 28 blocks clear and converge to the horizon by 180 blocks in clear
weather. TASK-15 used 24–156 blocks in settled rain. TASK-21 tightened
those bounds to 22–136 blocks and shared the overcast sky palette.
Limit both bounds for short render distances. Use the TASK-14 sky palette
and the horizontal ray to match the sunward twilight tint. Ease material
chroma down as the fog contribution grows.

Apply fog to scene-linear surface RGB in the existing forward draws.
Preserve source alpha for water, glass and cutouts. Keep the textured sky
on a separate fog-free route and gate the hand, precipitation and clouds
by Iris render stage. Add no depth texture lookup, color attachment or pass.
The fog fixture covered distance and draw order. TASK-19 later verified
bottom contrast in fixed submerged views.
[Fog report](testing/fog.md), [water report](testing/water.md#visual-review),
[weather report](testing/weather.md#shader-behavior).

## D-021 — Bounded directional shadow map (2026-11-12, TASK-16)

Request one 1024² orthographic shadow map with a 64-block caster distance.
Use a depth-only route for opaque terrain and an atlas alpha test for cutouts.
Sample cutout alpha at level zero to retain the gaps observed in the oak leaf
shadow. Implicit mip selection filled most of those gaps in the trial.
Enable block-entity casters and exclude ordinary entities, the player and
translucent terrain. Clear glass on the cutout route can cast thin frame
shadows. The installed Iris beta is the compatibility target.

Sample one bilinear depth comparison on terrain fragments with direct sun.
Use a capped slope-aware bias and blend the result back to the existing sun
term over 48–60 blocks and at the map edge. Fade influence for grazing faces
and near the horizon. Apply visibility to direct sunlight before fog so the
existing ambient fill, block light and AO can carry shaded detail. Use a 1/16
block Iris snap interval to limit screen-visible shifts across camera steps.
[Shadow report](testing/shadows.md).

## D-022 — Continue from the integrated prototype (2026-11-12, TASK-17)

Record **CONTINUE** after comparing all seven repeatable scenes with Sodium
shaders off and ten indexed Genshin stills. Terrain shading, shadow contact,
cave lighting and distance haze support the existing forward pipeline. Use
the TASK-17 snapshot as the incremental control for lightweight clouds in
TASK-18. TASK-19 subsequently addressed water color in the stepped basin.
TASK-21 coordinated overcast lighting and haze with the sky and water.
[Water report](testing/water.md), [weather report](testing/weather.md).

The integrated pack added 0.267–0.304 ms to the mean instrumented CPU loop
on the tested 1440p setup. The relative increase makes incremental measurement
important for later effects. GPU pass costs and real-world scaling remain open.
[Checkpoint report](testing/prototype_checkpoint.md),
[evidence index](../evidence/task-17/README.md).

## D-023 — Single projected cloud layer in the sky draw (2026-11-12, TASK-18)

Project the existing sky ray onto a virtual horizontal plane. Use two
analytic noise samples and the broad field's gradient for cloud shape and
directional shading. Keep the layer in the existing RGBA16F sky draw with
zero texture reads. Override the engine's cloud geometry through
`clouds=off`. The first trial's wide opacity ramp and density shading
produced bright rings. The accepted layer uses a narrower ramp, rotated
detail and directional shading.

Use the existing solar elevation for daylight, sunset and night colors.
Increase coverage and cool the deck in rain. Fade the layer into the
existing horizon and attenuate stars by coverage. TASK-21 ties the cloud
colors to the overcast palette. In TASK-18 the isolated 1440p sky draw
added 0.011–0.013 ms in the three preset-like views and about 0.023 ms in
the upward rain stress view on the tested GPU. [Cloud report](testing/clouds.md),
[timing summary](../evidence/task-18/gpu-summary.csv), [weather report](testing/weather.md).

## D-024 — Depth-based water tint in the translucent draw (2026-11-12, TASK-19)

Map vanilla water to pack-local material ID 10001. Use the pre-hand depth
snapshot and the surface view position to estimate thickness along the same
ray. Increase tint and opacity over eight blocks. Use intermediate absorption
for clear or invalid depth. Retain the ordinary atlas and lightmap material
for stained glass and other translucent terrain.

Use two world-anchored normal waves and a skylight-gated analytic sky
reflection. Dampen the sun highlight and shift the color toward blue-gray in
rain. When submerged, use a fixed surface tint and attenuate far geometry
with a water-specific fog ramp. The tested route uses the existing translucent
draw, straight-alpha blending and two texture reads above water.
[Water report](testing/water.md), [fixture and timings](../evidence/task-19/README.md).

## D-025 — Static vegetation tint and leaf fill (2026-11-13, TASK-20)

Use terrain block IDs 10002 for leaves and 10003 for grass blocks, grasses
and ferns. Derive a bounded correction from the existing green tint to
preserve biome differences and vertex AO. Use the existing daylight,
skylight and block-light weights to add a little fill on off-sun leaf faces.
Keep the direct-light shadow factor and cutout silhouettes through the
existing receiver and caster paths.

Keep geometry static. S7's reference stills establish the vegetation palette
and canopy contrast. Wind would require model-specific anchoring and
matching camera/shadow displacement. The material reuses the terrain draw
and existing vertex outputs. [Vegetation report](testing/vegetation.md).

## D-026 — One ramp for overcast weather (2026-11-13, TASK-21)

Use Iris's interpolated `rainStrength` for the direct-light attenuation,
lightmap reserve, distance fog, sky and cloud palette, water reflection and
grade. Use the sky palette at the fog horizon and in water reflections so
those colors move together. Keep the existing scene-linear attachment and
render sequence. The precipitation shader grades falling streaks in their
existing draw, preserving the engine's geometry, animation and alpha.
[Weather report](testing/weather.md).

## D-027 — Bounded low-light terrain fill (2026-11-13, TASK-22)

Use a small additive neutral illumination term for dark Overworld terrain.
Fade it with daylight multiplied by local skylight and across the
block-light ramp. Apply it before multiplication by the surface albedo and
combined vertex AO so recesses retain shape. In low light, reduce lightmap
scale on selected lamp faces using a terrain material ID. Adjacent blocks
still receive the engine's lightmap contribution. Evaluate both weights at
vertices and pack the neutral term in the fourth component of the terrain
fill varying.

Gate the custom sun and skylight tint on the existing skylight and ceiling
checks. In the Nether and End, use the engine lightmap through the shared
terrain program. [Lighting and dimension report](testing/lighting_dimensions.md).

## D-028 — Defer shader anti-aliasing (2026-11-13, TASK-23)

Keep the accepted TASK-22 rendering path. The five-sample spatial trial
softened selected diagonal edges and foliage holes, with limited improvement
on the three moving clear-day paths. Foliage shimmer persisted and some fine
texture detail softened. Four extra full-resolution samples per pixel give
an insufficient return for the performance budget. Retain the trial and GPU
measurements for replay. Temporal accumulation and upscaling remain deferred.
[Motion and AA report](testing/anti_aliasing.md).

## D-029 — Limit additional effects before comparison (2026-11-13, TASK-24)

The footage supports an optional compact sun halo in the existing sky draw.
The halo can reuse view/sun alignment, rain and cloud inputs with arithmetic
only. Scene-wide bloom and separate vertex AO are handoff items. The current
pack already shows grounded contact shadows, visible shallows and a sky
reflection term. Screen-space AO, geometry reflections and refraction would
add GPU work for cues that were secondary in the reviewed footage. The
optional halo trial is separately scoped and has a matched visual and
isolated GPU-cost gate. TASK-25 used the retained TASK-22 shaders for the
original comparison. [Full effects triage](architecture/deferred_effects.md),
[visual comparison](testing/visual_comparison.md).

## D-030 — Use the TASK-25 scene set as visual guards (2026-11-13, TASK-25)

Keep the accepted rendering path for per-effect profiling. Use the natural
river valley alongside the constructed ridge fixture when evaluating fog:
the shader-on fixture separates the planes, while the opposite hillside in
the valley loses too much detail. Preserve the matched rain, dusk, grove,
shallows, night and cave views to catch visual changes while isolating costs.
[Visual comparison and ranked gaps](testing/visual_comparison.md).

## D-031 — Delay clear-air haze (TASK-25 follow-up)

Raise the 12-chunk clear-air fog start from 28 to 88 blocks. Keep the far
cutoff and settled-rain curve. The natural valley gains mid-distance
detail and the controlled ridges still recede toward the sky. Use the
fog-tuned snapshot as the TASK-26 profiling control.
[Matched captures and verification](testing/visual_comparison.md#clear-air-fog-follow-up).

## D-032 — Profile one ablation at a time against the fog-tuned build (TASK-26)

Use the TASK-25 manifest as the full control. Stage the developer variants
outside the accepted source. Compare the whole pack against Sodium and
compare each major effect against its nearest matching shader build.
Disable both caster rendering and receiver work for the shadow trial.
Compare the terrain lighting group against the shadowless build to keep
shadow work out of that comparison. Measure a fixed-absorption water
variant separately from the lightmapped fallback.

Use client-loop timings for the integrated trials and paired GPU queries
for individual synthetic draws. Keep the two measurements in their own
units. The Minecraft profiler's utilization field cannot recover GPU
nanoseconds for each recorded client loop. Retain the raw timing records
and record the unmeasured in-client GPU costs in the report.
[Per-effect method and results](testing/effect_costs.md).

## D-033 — Keep the full-resolution shadow map and original fog blend (TASK-27)

Keep the fog-tuned default pack. A 768² shadow map reduced a synthetic
caster-and-depth-copy pass by 0.0062–0.0083 ms. The live grove and rain
mean gains were 0.4–1.8%, with mixed valley and p95 results. Matched
captures show softer leaf and glass cutout shadows. The fog blend
rewrite matched the offscreen color probes and showed no repeatable
GPU savings. Retain both patches and their measurements as developer
evidence. [Optimization report](testing/optimization.md).

## D-034 — Carry nonblocking runtime defects into handoff (TASK-28)

Keep the fog-tuned pack after the runtime smoke pass. The live replay
shows existing foliage and shoreline aliasing, an abrupt air/submerged
color switch and dark distant features in the Nether and End. The
tested paths render through each transition and the client saves and
exits normally. Retain the clips and log markers so the issues can be
reproduced on the tested stack.
[Runtime regression and bug priorities](testing/regression_report.md#prioritized-open-bugs).

## D-035 — Carry one tested client into handoff (2026-11-13, TASK-29)

Use the TASK-28 runtime regression on the installed 1.21.1 NeoForge
stack as the compatibility baseline for the retained shader source.
Skip the optional 26.3 run because the cached client requires a separate
loader and Iris/Sodium setup. Upstream API differences identify what to
verify in a future client run. [Compatibility notes](testing/compatibility_notes.md).

## D-036 — Hand off the verified source and replay inputs (2026-11-13, TASK-30)

Use the 38-file TASK-25 fog-tuned manifest to identify the development
baseline. The TASK-30 replay passed the same runtime checks as TASK-28,
and the offline reviewers regenerated the TASK-26 and TASK-27 summaries.
Preserve the TASK-03 fixture copy with the ignored runtime artifacts so
the successor can recreate the fixed scenes from the handed-off inputs.
[Developer handoff](HANDOFF.md), [evidence index](../evidence/README.md).
