# Distance fog and atmospheric perspective — TASK-15

## Shader behavior

The fog module uses the squared length of the interpolated view-space
position. A cubic ramp has zero slope at both ends. At 12 chunks the
TASK-15 captures use 28–180 blocks in clear weather and 24–156 blocks in
settled rain. TASK-21 changed the full-rain bounds to 22–136 blocks and
shared the overcast sky palette with fog. The TASK-25 follow-up raises
the clear-air start to 88 blocks at 12 chunks and keeps the clear far
bound at 180. The far bound respects 94% of Iris's render distance. The
near cap interpolates from 50% of that bound in clear weather to 40%
at full rain. The vertex stage evaluates the range and palette. The fragment
stage normalizes the horizontal ray when the directional glow is present.
[Current fog source](../../shaderpack/shaders/lib/fog.glsl),
[TASK-25 fog tuning](visual_comparison.md#clear-air-fog-follow-up),
[TASK-21 weather report](weather.md),
[Iris rendering uniforms](https://shaders.properties/current/reference/uniforms/rendering/),
[Iris weather uniforms](https://shaders.properties/current/reference/uniforms/world/).

Fog gently reduces the material's chroma and blends the lit surface toward
the same scene-linear horizon color as the sky. The target includes the
sun-facing twilight tint along the horizontal ray. The blend applies before
the existing alpha test and render-type blending. Water and ordinary glass
use their own fragment positions and keep their original alpha. The shader
adds no pass, attachment, texture read or screen-space depth lookup.

Atmospheric fog applies in skylit dimensions without a ceiling when Iris
reports the camera outside water, lava and powder snow. The textured sky
route preserves the sun and moon. Stage checks in fallback programs
bypass fog on held items and cloud draws. Falling precipitation now has
an explicit fog-free program.
[Iris gbuffers routes](https://shaders.properties/current/reference/programs/gbuffers/),
[Iris render stages](https://shaders.properties/current/reference/macros/render_stages/).

## Capture conditions

The fixture is built in a copy of `TASK-03 Visual Scenes`. The four distance
captures face west from the same teleport position `1004.5 184 1100.5`, yaw
90°, pitch 2°. The player's feet settle at Y183. The near oak is about 20
blocks away. The sampled middle stone face is about 82 blocks away, the far
face about 139, and the last ridge about 162. Staggered ridges separate
opaque silhouettes, and the cyan glass panels overlap across depths. A
grass strip leads toward the far ridges. The existing open-water and cave
views check the near field. Daylight and rain use tick 6000, sunset uses
12785 and night uses 18000. The build verifies representative block positions
before any capture. [Fixture source](../../evidence/task-15/build.mcfunction),
[recorded presets](../../artifacts/task-15/presets.json),
[TASK-03 presets](scenes.md).

The controls are Sodium with Iris shaders disabled and the hash-verified
TASK-14 sky pack. All modes use the same 2560×1440 fullscreen resolution,
70° FOV, 12/8 render/simulation distances, vanilla textures, hidden HUD,
Unlimited FPS and VSync off. The runtime is Minecraft 1.21.1, NeoForge
21.1.265, Iris 1.8.14-beta.1, Sodium 0.8.13 and Java 21.0.7 in Prism Launcher
Flatpak on CachyOS. Hardware is a Ryzen 9 9950X and RTX 4080 SUPER with
NVIDIA 580.196.07 and OpenGL 4.6.0. The profile index checks these settings,
the mod hashes and per-run presets against the retained baseline and replay
source. [Baseline conditions](baseline.md#capture-conditions),
[exact commands](../../evidence/task-15/commands.txt).

## Visual review

The reference targets are the readable green foreground and cool distant
layers in R1 and R9, and the depth separation of R3. The fixture tests
distance haze with vanilla materials. R3's localized mist banks require a
different technique.
[Reference strip](../../artifacts/task-15/reference-strip.jpg),
[S4 target and provenance](../research/style_targets.md#s4--atmospheric-depth).

- In daylight the foreground grass, trunk and leaf cutouts stay crisp.
  The middle stone face cools and retains its texture. The far stone and
  small oak blend much closer to the horizon and their outlines remain visible.
  The near shore and glass frames remain legible. The water still shows the
  near shelf edge through its existing alpha blend.
  [Daylight comparison](../../artifacts/task-15/daylight-row.jpg),
  [native translucent detail](../../artifacts/task-15/daylight-translucent.png).
- At sunset the distant surfaces pick up the peach sky glow while the
  foreground retains its dark blue and green separation. The sun remains
  visible through the gap between the ridges.
  [Sunset comparison](../../artifacts/task-15/sunset-row.jpg).
- In settled rain the far ridge becomes faint and the middle terrace,
  foreground oak and shoreline remain visible. [Rain comparison](../../artifacts/task-15/rain-row.jpg).
- The near oak and foreground grass keep their sampled pixels at night.
  Distant silhouettes fade into deep blue and the far ridge is faint.
  [Night comparison](../../artifacts/task-15/night-row.jpg).
- Open water keeps its foreground median sRGB of `(152, 155, 185)` across
  animated frames. The cave keeps its ceiling recess median `(13, 9, 7)`,
  and the floor patch near the lantern differs by up to three codes in
  its median channels. Both views retain their visible material and lighting
  detail. [Water comparison](../../artifacts/task-15/open-water-row.jpg),
  [cave comparison](../../artifacts/task-15/cave-row.jpg).

The daylight cutout edge, near trunk, grass and low sky patches match every
sampled pixel in the TASK-14 control. The middle stone patch moves from
`(108, 118, 127)` to `(117, 140, 157)`. The far stone moves from
`(107, 117, 126)` to `(137, 193, 225)` toward the low sky's
`(131, 195, 234)`. The corresponding last ridge reaches `(137, 198, 233)`.
Inspection passed the halo, hard fog edge and near-field readability checks
for the captured views. Elevated distant silhouettes can appear paler than
the higher blue sky behind them. [Native patch index](../../evidence/task-15/pixels.csv).

The TASK-15 fixture tested settled weather, the stock 12-chunk distance and
a short cave in the installed Overworld. Alpha blending can reveal the haze
of opaque blocks through water. TASK-19 added a submerged fog ramp and
checked bottom contrast from fixed floor and underside cameras. TASK-21
checks the fog horizon through live rain and clearing. The TASK-22 Nether
and End captures show the shared pipeline with procedural air fog gated off.
Long enclosed Overworld sightlines, other render distances and dedicated
Nether and End fog remain open. TASK-24 assigned height-weighted valley fog
to handoff. The TASK-25 valley and ridge comparisons show what the current
distance fog does in those views. They leave localized mist banks as a
separate visual gap. [TASK-25 visual comparison](visual_comparison.md#matched-views).
[Water validation](water.md#visual-review), [weather report](weather.md),
[dimension findings](lighting_dimensions.md#dimensions),
[effects triage](../architecture/deferred_effects.md#dispositions-and-expected-gpu-work).

## Performance

Six fresh sessions ran Sodium, sky, fog, fog, sky, Sodium. Each recorded
daylight and sunset after a 20-second focused warm-up. The 12 native
profiles contain 397,216 CPU client-loop samples over 9.991–10.000 seconds
per run. The before and after crops matched within each profile.
[Raw profile index and hashes](../../evidence/task-15/runs.csv).

| Preset | Sodium loops/s | TASK-14 loops/s | TASK-15 loops/s | Fog mean loop delta | TASK-14 p95 (ms) | TASK-15 p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Daylight | 5,254–5,359 | 2,428–2,442 | 2,421–2,427 | +0.00201 ms (+0.49%) | 0.646–0.650 | 0.624–0.653 |
| Sunset | 5,065–5,149 | 2,306–2,312 | 2,275–2,296 | +0.00440 ms (+1.02%) | 0.654–0.657 | 0.653–0.717 |

The incremental delta uses each mode's average of its two per-run mean
loop durations. The full pack averages 0.409 ms in daylight and 0.434 ms
at sunset, compared with 0.185 and 0.193 ms with shaders off. The higher
sunset p95 occurred in one fog repeat. These profiles measure instrumented
CPU client loops.

TASK-26 bypassed the fog blend in the integrated build. The full pack
added 0.027–0.062 ms per client loop in the clear valley and
0.021–0.050 ms in settled rain. The offscreen fog probe measured
0.0023 ms per distant dusk draw. Clear, rain, submerged and near cases
differed by at most 0.0001 ms per draw. In-client fog GPU duration and
display presentation cadence remain unmeasured.
[TASK-26 fog comparisons and limits](effect_costs.md#coverage-and-limits).

TASK-27 timed a weighted-sum rewrite of the air-fog blend. It preserved
the sampled linear RGB probes and showed no repeatable GPU gain. The
fog-tuned source keeps the original blend. TASK-28 sampled both live
transition directions on that build at the fixed valley camera and clock.
[Optimization results](optimization.md#offscreen-gpu-results),
[tuned weather sequence](regression_report.md#runtime-results).

## Handoff

TASK-16 used the tested snapshot at `artifacts/task-15/variants/fog/shaders/`
as its incremental control. Verify it from the repository root.

```bash
sed 's|shaderpack/shaders/|artifacts/task-15/variants/fog/shaders/|' \
    evidence/task-15/pack.sha256 | sha256sum -c -
```

Retain the copied world, shader snapshots, screenshots, profiles, raw timing
CSVs and client logs under `artifacts/task-15/`. The original TASK-03 world
is the source for a fresh replay. GenshinShaderDev stopped after saving and
released the world lock. All five settings files were restored byte-for-byte,
the temporary packs were removed and 75 original world file hashes matched.
[Verification record](../../evidence/task-15/verification.txt).

The TASK-15 timing rows use the overlook cameras. TASK-16 recorded fresh
fog-control timings at the forest and low-angle shadow fixture cameras and
kept fog on the receiver's shaded color in the forward draw.
[TASK-16 capture conditions and timings](shadows.md#capture-conditions).
