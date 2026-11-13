# Integrated prototype checkpoint

TASK-17, 2026-11-12. The candidate is the 33-file TASK-16 shadow snapshot,
covering palette, terrain sunlight and fill, the analytic sky, distance fog
and bounded cast shadows. Both the source tree and staged copy matched the
accepted manifest. [Shader manifest](../../evidence/task-16/pack.sha256),
[checkpoint evidence index](../../evidence/task-17/README.md).

## Decision — CONTINUE

The integrated Overworld pack rendered all seven fixed scenes in two fresh
sessions. Terrain lighting and shadows give visible depth, the cave keeps
readable local light, and the sky and distance haze establish the intended
outdoor palette. At the checkpoint, clouds, water, vegetation and weather
were the largest gaps. The decision opened TASK-18 and the subsequent
numbered finishing work. [Current handoff](../STATUS.md).

The measured CPU loop increment is **0.267–0.304 ms** at 1440p, with a
substantial **124.7–155.2%** increase over the fast shaders-off control. The
prototype's mean loop time was **0.446–0.547 ms** in these synthetic scenes
on the test machine. That supports continuing with small, measured changes
on the current architecture. Broader performance and the brief's
aspirational frame-time goals remain open. TASK-18 used this snapshot as
its visual control. [Cloud report](clouds.md).

## Capture conditions

- GenshinShaderDev in Prism Launcher Flatpak 11.1.1. Minecraft 1.21.1,
  NeoForge 21.1.265, Iris 1.8.14-beta.1+mc1.21.1, Sodium 0.8.13+mc1.21.1
  and Microsoft Java 21.0.7. Ryzen 9 9950X, GeForce RTX 4080 SUPER,
  OpenGL 4.6.0, NVIDIA 580.196.07, CachyOS kernel 7.3.3-1-cachyos.
- The four fresh client sessions ran Sodium 01, prototype 01, prototype 02
  and Sodium 02. All used one copy of the TASK-03 Overworld map and the
  seven existing preset functions. Each preset re-established the camera,
  time and weather. The runner checked for a new acknowledgement, hid the
  HUD and waited 20 focused seconds before recording. Cloud translation,
  water animation, rain particles and light flicker run independently.
- Fullscreen 2560×1440, 70° FOV, 12 chunks render distance, 8 simulation
  distance, fancy graphics and clouds, vanilla and built-in resources,
  VSync off and Unlimited FPS. Each F3+L profile retained the fullscreen
  window PNGs from immediately before and after recording. The first
  repeat's pre-profile images are the primary visual comparisons. The
  index checks the presets, runtime, mod hashes and video options against
  the retained TASK-10 baseline. Landmark placement and HUD state matched
  in the before/after grids across both repeats.
  [Camera presets](scenes.md#camera-presets),
  [baseline conditions](baseline.md#capture-conditions),
  [before grid](../../artifacts/task-17/comparisons/repeats-before.jpg),
  [after grid](../../artifacts/task-17/comparisons/repeats-after.jpg),
  [replay commands](../../evidence/task-17/commands.txt).

Both prototype session logs record Iris loading `TASK-17-prototype`.
The temporary pack was removed after testing and the original Iris
configuration was restored with shaders disabled and an empty selection.
[Development load instructions](../../shaderpack/README.md),
[loaded-mode and cleanup verification](../../evidence/task-17/verification.txt).

## Visual review

The captures use identical viewpoints within Minecraft. R1–R10 provide
qualitative targets for color, value and depth. Each reference still has its
source and decoded presentation timestamp in the evidence index.
[Reference sheet](../../artifacts/task-17/reference-review.jpg),
[S1–S7 rubric](../research/style_targets.md),
[reference index](../../evidence/task-17/references.csv).

| Preset | Observed against Sodium and the reference rubric |
| --- | --- |
| [Daylight](../../artifacts/task-17/comparisons/daylight.jpg) | Grass is brighter yellow-green, the wall takes on a cool gray-blue and the far stone tower loses contrast. Grass and masonry keep their textures. The color separation moves toward R1/R2, although the broad grass plane is more uniformly vivid than R1. The cyan horizon resembles R9. Sodium's clouds are absent in the prototype. |
| [Sunset](../../artifacts/task-17/comparisons/sunset.jpg) | The warm low horizon grades into pink and lavender-blue, the yellow sun stays visible and grass stays green. The cool face of the stone wall and warm sky give the color contrast of R5. The basin stays blue-purple, with little of R5's turquoise shore. Cloud silhouettes are missing. |
| [Night](../../artifacts/task-17/comparisons/night.jpg) | The sky and masonry turn cool blue, with visible stars and a clear drop in brightness from daylight. The wall and tree silhouettes remain readable, though deep greens are subdued. R6 supports the cool environmental color. The lantern response is visible in the cave preset. |
| [Rain](../../artifacts/task-17/comparisons/rain.jpg) | Far geometry fades and near silhouettes remain legible. Bright cyan sky and near-daylight grass persist behind prominent blue streaks. The shaders-off scene reads as overcast, closer to R4's muted slate sky and subdued ground. The prototype's rain adjustment is concentrated in the fog range. |
| [Forest](../../artifacts/task-17/comparisons/forest.jpg) | Tree shadows meet trunks and keep grass texture. Dark trunks and shaded canopy faces separate from bright leaves. The cutouts stay visible and the bounded shadows evoke the readable contact in R2/R7. The close grass is strongly yellow-green, and leaf variation is less pronounced than R2. |
| [Open water](../../artifacts/task-17/comparisons/open-water.jpg) | The near sand floor is visible and the basin edge is readable. The checkpoint surface is pale lavender over the floor with a saturated blue rim. R7/R9 show a turquoise-to-blue depth relationship that guided the later water material. |
| [Cave](../../artifacts/task-17/comparisons/cave.jpg) | Lantern pools are warmer and stone texture is easier to see. Dark recesses remain visible between the two pools, and the floor keeps its gray stone detail. This is a regression check for S1/S2 and supports the warm local lights seen in R6/R8. |

**S1 palette and S2 lighting** provide the strongest improvement over
Sodium. The grass and stone stay distinct across day, sunset and night.
The forest and the prior contact fixture show bounded cast shadows.
The cave keeps the separation between warm local lights and dark
recesses. **S3 sky** has coherent time colors and lacks cloud form.
**S4 atmosphere** gives readable near geometry and softer distant stone.
The earlier overlook shows more depth separation across multiple ridges.
Localized mist banks and the layered silhouettes of R3/R10 remain
outside the current distance blend. **S5 overcast** and **S6 water**
are the largest visual gaps. **S7 vegetation** retains distinct
canopy faces and trunks, with the strong grass tint and limited leaf
color variation still to tune.
[Fog overlook](../../artifacts/task-15/daylight-row.jpg),
[shadow contact](../../artifacts/task-16/contact-row.jpg),
[shadow range](../../artifacts/task-16/range-row.jpg).

## Performance

Each profile samples roughly ten seconds of the instrumented CPU render loop.
The mean columns average two per-run means per mode. The percentile columns
show the range of the two per-run nearest-rank percentiles. The throughput
columns divide loop count by wall span and express the repeat range in loops
per second. Minecraft's profiler recorded one display-update call per sample.
GPU execution and compositor presentation need separate instrumentation.
[Metric validation](harness.md#what-the-performance-record-means),
[raw archive and timing index](../../evidence/task-17/runs.csv).

| Preset | Sodium mean (ms) | Prototype mean (ms) | Mean increase | Sodium p95 (ms) | Prototype p95 (ms) | Profiled loops/s (Sodium / prototype) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Daylight | 0.196 | 0.476 | +0.280 ms (+143.3%) | 0.346–0.348 | 0.706–0.771 | 5,003–5,058 / 2,079–2,083 |
| Sunset | 0.193 | 0.476 | +0.282 ms (+145.8%) | 0.338–0.340 | 0.719–0.728 | 5,066–5,131 / 2,076–2,096 |
| Night | 0.194 | 0.480 | +0.285 ms (+146.7%) | 0.339–0.344 | 0.724–0.734 | 5,022–5,122 / 2,069–2,070 |
| Rain | 0.243 | 0.547 | +0.304 ms (+124.7%) | 0.409 | 0.804–0.810 | 4,011–4,107 / 1,811–1,818 |
| Forest | 0.198 | 0.476 | +0.278 ms (+140.6%) | 0.345–0.354 | 0.700–0.703 | 4,939–5,038 / 2,085–2,087 |
| Open water | 0.190 | 0.485 | +0.295 ms (+155.2%) | 0.335–0.340 | 0.717–0.735 | 5,135–5,240 / 2,036–2,055 |
| Cave | 0.179 | 0.446 | +0.267 ms (+148.7%) | 0.315–0.326 | 0.654–0.673 | 5,475–5,518 / 2,219–2,233 |

The 28 profiles contain **986,782 samples** over **9.996–10.000 seconds**
per recording. Rain had the largest absolute mean increase and the highest
prototype p95. The largest prototype p99 was 1.139 ms. The index retains
every run's p50, p95 and p99. Means and differences are rounded independently.

The integrated delta covers enabling the Iris pipeline and all active effects
together. TASK-16 separately measured the marginal CPU loop cost of adding the
bounded shadow pass and lookup to the fog snapshot. It added **0.0432 ms in
forest** and **0.0426 ms in the low-angle pad fixture**. Those were different
session conditions and the pad camera differs from this checkpoint's sunset
preset. The TASK-10 neutral comparison measures the combined cost of
enabling Iris and the neutral scaffold. Use the earlier effect results as local
comparisons and this checkpoint for the total cost in the integrated scene set.
[Shadow timings](shadows.md#performance),
[neutral baseline](baseline.md#results).

## Finishing priorities

1. **TASK-18 — Clouds.** The projected layer adds broad cloud shapes and
   shaded undersides. The report covers sunset, rain and night and records
   the incremental GPU cost of the sky draw. [Cloud report](clouds.md).
2. **TASK-19 — Water.** The depth-based tint softens the blue rim and
   preserves the shallow bottom. The stepped basin verifies thickness,
   shoreline, glass and fixed submerged views. [Water report](water.md).
3. **TASK-20 — Vegetation.** Terrain vertex tint restrains grass intensity,
   and a skylight-weighted fill softens leaf faces. The dense fixture checks
   biome tint, cutouts and cast shadows. [Vegetation report](vegetation.md).
4. **TASK-21 — Weather.** One weather ramp coordinates sunlight, fog, sky,
   water and saturation. Fixed cameras exercise both transition directions
   and precipitation readability. [Weather report](weather.md).
5. **TASK-22 — Readability and dimensions.** The matched night and interior
   views check dark terrain and bright lamp faces. The dimension smoke test
   covers the Nether, End and Overworld return. [Lighting and dimension report](lighting_dimensions.md).
6. **TASK-23 — Motion and anti-aliasing.** Compared the accepted pack and a
   spatial filter in continuous movement and deferred AA. [Motion review](anti_aliasing.md).
7. **TASK-24 — Additional effects.** Reviewed timestamped references and
   prior captures against expected GPU work. The optional sun halo remains
   proposed. [Effects triage](../architecture/deferred_effects.md).
8. **TASK-25 — Visual comparison and fog tune.** Compared the TASK-22 pack
   against Sodium and timestamped Genshin stills. The follow-up recovered
   mid-distance detail in the natural valley. [Visual report](visual_comparison.md).
9. **TASK-26 — Per-effect profiling.** Measured the fog-tuned build against
   Sodium and disposable ablations. Shadows had the largest repeatable
   client-loop cost among the tested effects. [Profiling report](effect_costs.md).

## Limits of the evidence

The seven checkpoint views use a synthetic map with flat ground, a shallow
uniform basin and sparse, block-shaped canopies. The fog overlook, shadow
fixture, stepped basin and dense-canopy fixture extend specific checks. TASK-22
adds fixed dimension views and command-teleport transitions. TASK-23 adds
continuous motion in three clear-day scenes. TASK-28 adds a live
waterline crossing in the stepped basin. Portal travel, natural
terrain with heavy vegetation, integrated GPU timings and presentation
cadence remain open. [Runtime regression](regression_report.md).
The reference scenes have different assets, geometry,
camera and exposure. Comparisons concern visible relationships among colors,
lighting and depth. The [reference index](../../evidence/task-17/references.csv)
preserves the source video and decoded timestamp for each still.
