# TASK-26 — Per-effect performance profiling

**DONE · 2026-11-13.** The control is the [fog-tuned TASK-25 build](../../evidence/task-25/fog-pack.sha256).
Each trial changes a disposable copy of that tree. The [evidence index](../../evidence/task-26/README.md)
links the exact commands, source edits, raw captures and timing samples.

## Client method

- GenshinShaderDev on CachyOS 7.3.3-1-cachyos, Ryzen 9 9950X and GeForce
  RTX 4080 SUPER. OpenGL 4.6.0, NVIDIA 580.196.07, Prism Flatpak 11.1.1,
  Microsoft Java 21.0.7, Minecraft 1.21.1, NeoForge 21.1.265,
  Iris 1.8.14-beta.1+mc1.21.1 and Sodium 0.8.13+mc1.21.1.
  Each archive records the runtime and video options. Recording directories
  retain settings and hashes for the mod JARs. NVIDIA telemetry records
  clocks, temperature, power and performance state at batch boundaries.
- Native 2560×1440 fullscreen, 70° FOV, 12 chunks render distance, 8
  simulation distance, Fancy graphics, vanilla and loader-provided resources,
  GUI scale 3, view bobbing off, VSync off, Unlimited FPS (`maxFps:260`).
  The HUD and hand are hidden, and the window stays focused.
- The copied TASK-25 world provides the valley, settled rain at the same
  camera, grove, stepped shallows and lantern cave. Each profile follows a
  fresh fixed-position, time and weather acknowledgment and a 20-second
  warm-up. Sodium sessions bracket the two shader sessions. Within each shader
  session the dedicated Iris reload key swaps the build, and the second
  session reverses the order. The first Sodium run built the stepped basin
  during setup, before its 20-second warm-up and recorded interval. Fixed
  positions and weather come from the [preset source](../../evidence/task-25/presets.json).
- F3+L captures about ten seconds of instrumented client render loops,
  including CPU work and waits. The harness verifies one display update per
  sample. FPS denotes loops per second over the recorded interval. The
  retained `client/metrics/gpu.csv` contains a utilization ratio. In this
  Minecraft build, the GPU query can complete asynchronously, and the CSV
  can repeat a previous value. Its denominator is the client's
  `savedCpuDuration`. Multiplying this column by same-row CPU loop time
  cannot recover per-frame GPU nanoseconds.
  [Timing harness](harness.md#what-the-performance-record-means).
- Pipeline reload, GPU clocks, world rendering, engine particles and the
  native profiler can affect the deltas. Two repeats give a local check
  on repeatability. Full-frame GPU duration and display presentation
  intervals are unavailable in the retained client records.

## Client results

The 44 native profiles contain 805,413 loop samples. Recorded intervals
span 9.996–10.002 seconds. The ranges below span two runs per scene and
mode. The delta averages the two full-minus-Sodium mean loop differences.
[Per-run distributions and archive hashes](../../evidence/task-26/runs.csv).

| Scene | Sodium loops/s | Full pack loops/s | Mean loop delta |
| --- | ---: | ---: | ---: |
| Valley | 2,637–2,788 | 1,225–1,258 | +0.436 ms |
| Settled rain | 2,330–2,409 | 1,115–1,134 | +0.466 ms |
| Grove | 3,793–3,821 | 1,579–1,584 | +0.369 ms |
| Shallows | 3,506–3,531 | 1,451–1,452 | +0.404 ms |
| Cave | 4,012–4,049 | 1,653–1,660 | +0.354 ms |

Each delta subtracts the ablation's mean client loop from the matched
reference's mean. Positive values indicate more time with the effect
enabled. The terrain lighting reference is the shadowless build. All
other ablations use the full pack as the reference.
[Paired means and repeat spread](../../evidence/task-26/effect-deltas.csv).

| Effect or group | Camera | Round 01 (ms) | Round 02 (ms) |
| --- | --- | ---: | ---: |
| Shadows, caster and receiver | Valley | +0.060 | +0.093 |
| Shadows, caster and receiver | Grove | +0.045 | +0.061 |
| Distance fog | Valley | +0.027 | +0.062 |
| Distance fog | Settled rain | +0.021 | +0.050 |
| Projected clouds | Valley | +0.011 | +0.041 |
| Projected clouds | Settled rain | +0.005 | +0.039 |
| Water material | Shallows | +0.008 | +0.013 |
| Water depth and absorption | Shallows | +0.004 | +0.025 |
| Final grading arithmetic | Valley | −0.011 | +0.012 |
| Final grading arithmetic | Cave | −0.002 | −0.001 |
| Terrain lighting and tint | Grove | +0.029 | +0.008 |
| Shader rain response | Settled rain | −0.020 | +0.008 |

The shadow ablation gave the largest repeatable reduction. It removes both
the render-side work for the extra geometry pass and the main-view
sampling path. The full pack's `shadows` CPU profiler section accounts
for 5.55–6.89% of the profiled root time across the ten full-pack runs
and disappears in the shadowless and lightmap-only variants. Fog also
reduced mean loop time in both views and rounds.
Cloud and water deltas varied across repeats. The valley grade and
coordinated rain comparisons changed sign. The cave grade deltas were
below 0.002 ms in both rounds. Each delta includes changes in client
scheduling and waits. The ablations overlap, so their sum cannot explain
the whole-pack cost.

## Matched visual checks

The [comparison sheets](../../artifacts/task-26/comparisons/) put both
repeats of the full and ablated builds side by side. The grove loses
projected tree shadows when the caster and receiver are disabled. The
cloudless valley keeps the sky gradient, and removing fog exposes the
full hillside and the terrain cutoff. The stepped basin loses the depth
progression with constant absorption and returns to a blue atlas texture
with the lightmapped fallback. Glass stays visible in front of the basin.
The grade brightens the cave floor and lantern pools. The lightmap-only
grove loses the custom foliage tint and the cooler wall. Rain-neutral
keeps falling streaks over the clear-air palette, with the bluer
precipitation texture visible. Clouds, water animation, precipitation,
mobs and lightmap flicker can vary at a fixed camera.

## Offscreen GPU draws

The offscreen tests use the expanded GLSL from the variant trees on the
same NVIDIA driver. The flat-sky control is derived from the cloudless
fragment shader for this timer. Each comparison has two independent
EGL runs. In each run, 32 paired `GL_TIME_ELAPSED` queries per case time
64 draws per build after warm-up, alternating which build goes first.
The per-draw delta is the median of the paired differences divided by
64. Sky and geometry tests write to RGBA16F. Grade
reads RGBA16F and writes RGBA8, using a valley capture decoded to linear
RGB as the input texture. The water and fog tests fill the viewport with a
single synthetic quad. Water blends the result and uses a synthetic depth
texture with a background ramp and a no-hit strip. The shadow receiver
uses a prefilled 1024² comparison texture, with a mid-range leaf draw,
a leaf draw spanning the fade, and a night early-out. The terrain-lighting
test compares the same geometry with shadows disabled in both builds.
Four pixel probes per geometry case verify draw coverage and the expected
color change or early-out. The tests omit client geometry counts, occlusion and
overdraw, texture traffic from other passes, Minecraft's world submission
and display presentation. [Paired GPU results](../../evidence/task-26/gpu-summary.csv).

| Effect and synthetic draw | Full minus ablation, median per draw |
| --- | ---: |
| Projected clouds, sunset/rain/night sky | +0.0103 to +0.0121 ms |
| Projected clouds, upward-looking rain sky | About +0.0213 ms |
| Sky gradient and dither over a flat horizon color | +0.00007 to +0.00024 ms |
| Full above-water material versus scaffold translucency, clear/rain | +0.0192 to +0.0195 ms |
| Water depth sample and reconstruction versus constant absorption, clear/rain | +0.0113 to +0.0116 ms |
| Water, submerged branch | Within 0.0002 ms in both comparisons |
| Terrain shadow receiver, eligible foliage and range fade | +0.0050 to +0.0056 ms |
| Terrain shadow receiver, night early-out | Within 0.0001 ms |
| Terrain lighting and tint on a single quad | Within 0.0002 ms |
| Geometry fog, distant dusk | +0.0023 ms |
| Geometry fog, clear, rain, submerged and near early-out cases | Within 0.0001 ms |
| Exposure, chroma and highlight shoulder within the final draw | About +0.0002 ms |

The `water-depthless` variant retains waves, analytic reflection, blending,
and a constant absorption equal to the missing-background fallback. The
depth delta includes downstream arithmetic the compiler can fold with
that constant. Both water tests omit the in-client pre-hand depth copy.
Iris calls that copy from `beginHand` even when the shader stops sampling
`depthtex2`. The GPU cost of the copy and the contribution of the water
draw at its actual screen coverage remain unmeasured. The water results are
overlapping deltas. The grade comparison keeps the fullscreen pass,
`colortex0` fetch, RGBA16F attachment and sRGB encode in both builds.

## Coverage and limits

| Implemented work | Measurement and missing data |
| --- | --- |
| Bounded terrain shadow map and receiver | `shadowless` disables caster rendering via `shadow.enabled=false` and removes the terrain lookup and receiver vertex work. The live client delta covers both, plus downstream changes in scheduling and waits. The offscreen receiver probe isolates its shading against a prefilled map. GPU time for the in-client shadow pass and receiver remains open. |
| Analytic sky gradient and dithering | The GPU comparison uses a cloudless sky draw against the same draw with flat horizon color. The earlier [TASK-14 client ablation](sky.md#performance) measures the original gradient against its parent build. The current in-client sky stage is unmeasured. |
| Projected clouds and star attenuation | `cloudless` removes cloud shading and cloud attenuation of stars while keeping the vanilla clouds disabled in both builds. The GPU test uses the sky stage. Star draws and the integrated GPU cost are unmeasured. |
| Distance and submerged fog | `fogless` bypasses the color blend while retaining shared view-space inputs used by water and shadows. The live matrix covers the valley and rain. Synthetic GPU draws exercise near, distant clear, dusk, rain and submerged shading. The ablation measures the full fog blend, leaving the incremental cost of the TASK-25 ramp change, in-client GPU pass timing and submerged gameplay open. |
| Water waves, reflection and depth absorption | `water-vanilla` uses the pack's lightmapped translucent fallback. `water-depthless` keeps the rest of the material. The stepped basin covers both comparisons. The offscreen draws give paired GPU deltas with the pre-hand copy gap described above. |
| Terrain sun, skylight fill, vegetation and low-light terms | Compare `shadowless` with `terrain-vanilla` for a lightmap-only group ablation in the grove. Both disable shadows and retain fog. The group combines vertex tint, direct sun, ambient fill and low-light arithmetic. The four-vertex GPU quad gives little evidence about real terrain vertex throughput. Per-component GPU costs remain unmeasured. [Low-light CPU evidence](lighting_dimensions.md#performance). |
| Coordinated overcast response and precipitation grading | `rain-neutral` preserves engine precipitation while suppressing shader rain inputs and streak desaturation. The settled-rain client delta measures the group. Individual GPU contributions and transitions are unmeasured in this matrix. [Transition evidence](weather.md). |
| Scene-linear attachment, resolve/blit and final pass | The shaders-off comparison measures the combined Iris pipeline change. The offscreen grade ablation isolates grading arithmetic. GPU time for the rest of the final draw, attachment traffic and Iris copies is unmeasured in-client. |

## TASK-27 handoff

The shadow ablation showed the largest repeatable client-loop reduction.
TASK-27 followed up with a smaller shadow map, keeping the caster range and
receiver fade. The fog ablation also reduced mean client-loop time in both
rounds, and distant dusk gave the largest measured offscreen fog cost.
TASK-27 tested a fog blend rewrite against that baseline. It retained
the full fog-tuned source after both trials. Projected clouds were measured
in TASK-26. [Baseline manifest](../../evidence/task-25/fog-pack.sha256),
[TASK-27 results](optimization.md).
