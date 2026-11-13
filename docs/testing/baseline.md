# Sodium and neutral Iris baseline

TASK-10, 2026-11-12. Compare the existing Sodium client with Iris shaders
disabled against the same client running the TASK-09 neutral shaderpack. The
neutral pack already draws geometry, uses one RGBA16F color attachment and runs
a final pass. The difference includes the shader-enabled Iris pipeline and that
scaffold's work together. Use Sodium for the total cost of enabling the pack
and the previous accepted pack for incremental effect costs. TASK-12 used
the [TASK-11 graded baseline](palette.md#performance). TASK-13 used the
[TASK-12 sunlight snapshot](sunlight.md#handoff). TASK-14 used the
[TASK-13 ambient snapshot](ambient.md#handoff). TASK-15 compares the
[TASK-14 sky snapshot](sky.md#handoff) and Sodium against distance fog in
the [new overlook fixture](fog.md#performance). TASK-16 measures shadows
against the [TASK-15 fog snapshot](fog.md#handoff) and Sodium in the
[forest and low-angle fixture](shadows.md#capture-conditions).
The [TASK-17 checkpoint](prototype_checkpoint.md#performance) compares
the integrated pack with a fresh shaders-off control across all seven presets.
TASK-18 uses that prototype as its visual control and measures the added
sky-draw work with an offscreen OpenGL GPU timer. [TASK-18 timing method](clouds.md#gpu-cost).
TASK-19 compares water against TASK-18 and Sodium in clear and settled-rain
basin views. TASK-20 compares vegetation against TASK-19 and Sodium in
daylight and dense canopy. TASK-21 compares clear and settled rain with
TASK-20 and Sodium, and reuses the isolated sky GPU timer. TASK-22 compares
night and cave against TASK-21 and Sodium. All four comparisons use native
CPU client-loop profiles. TASK-23 adds matched forest and open-water CPU
profiles and an isolated GPU timer for the spatial AA trial. The accepted
source retained the TASK-22 shader baseline, which TASK-24 verified again.
TASK-25 compared stills and tuned the clear-air fog. TASK-26 used that
build for matched Sodium, full-pack and effect-ablation client profiles,
plus isolated GPU draws. Those results are the TASK-27 baseline.
[Per-effect report](effect_costs.md).
[Water timings](water.md#performance), [vegetation timings](vegetation.md#performance),
[weather timings](weather.md#performance),
[night and cave timings](lighting_dimensions.md#performance),
[AA trial timings](anti_aliasing.md#performance),
[TASK-24 baseline verification](../architecture/deferred_effects.md#evidence-and-verification),
[TASK-27 optimization handoff](effect_costs.md#task-27-handoff).

## Test matrix

Run four fresh client sessions in this order — Sodium 01, neutral 01, neutral 02
and Sodium 02. Each session captures daylight, forest and cave in that order.
Two captures per mode and scene give a check on run-to-run variation. Bracketing
the neutral sessions with Sodium sessions reduces sensitivity to steady drift
over time.

| TASK-03 preset | Teleport XYZ | Yaw / pitch | Workload |
| --- | --- | --- | --- |
| Daylight | 1000.5, 184, 1036.5 | 180° / 8° | Mixed outdoor view with grass, stone, foliage, water and sky |
| Forest | 1018.5, 184, 1005.5 | 180° / 5° | Leaf cutouts and outdoor geometry |
| Cave | 970.5, 184, 1027.5 | 0° / 3° | Enclosed low-light view with lanterns |
| Sunset, night, rain, open-water | [TASK-03 presets](scenes.md) | Preset values | Outside the TASK-10 timing matrix. Profiled in TASK-17 |

The three measured scenes all use clear weather, time 6000 and the dedicated
TASK-03 Visual Scenes Overworld. Outdoor feet settle to Y183. Use first person
with no camera movement. The scene runner resets the hotbar trigger with slot 8,
waits 3 seconds, selects the preset and checks for a fresh log acknowledgment
after another 3 seconds. It hides the HUD and hand with F1 and waits 20 seconds
while checking focus. Minecraft's F3+L recorder then measures about 10 seconds.
The debug HUD and FPS overlays are off during capture. Window images before and
after each profile preserve the view and HUD state.

## Capture conditions

- Ryzen 9 9950X, GeForce RTX 4080 SUPER, NVIDIA 580.196.07, OpenGL 4.6.0,
  CachyOS kernel 7.3.3-1-cachyos.
- Prism Launcher Flatpak 11.1.1, GenshinShaderDev, Minecraft 1.21.1, NeoForge
  21.1.265, Java 21.0.7, Iris 1.8.14-beta.1+mc1.21.1 and Sodium
  0.8.13+mc1.21.1. Per-run version manifests and mod JAR hashes preserve the
  rest of the installed stack.
- 2560×1440 fullscreen, FOV 70°, 12 chunks render distance, 8 simulation
  distance, GUI scale 3, bobbing off. Fancy graphics and clouds, vanilla and
  loader-provided resources, and the other [TASK-03 client options](scenes.md).
- VSync off and Unlimited FPS (`maxFps:260`, F3 shows `T: inf`). The TASK-03
  visual baseline used a 240 FPS cap. The TASK-10 settings are temporary.
  Keep the window focused and visible to prevent Dynamic FPS throttling.

## Results

Ranges span two captures per scene and mode. Each capture lasted 9.993–10.000 s.
The full matrix contains 335,017 client render-loop samples.

| Scene | Mode | Profiled FPS | Mean loop ms | p50 ms | p95 ms | p99 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Daylight | Sodium | 3,745–3,758 | 0.262–0.263 | 0.171 | 0.642–0.649 | 0.936–0.960 |
| Daylight | Neutral | 1,769–1,779 | 0.557–0.560 | 0.483–0.492 | 0.995–1.079 | 1.264–1.375 |
| Forest | Sodium | 3,708–3,755 | 0.263–0.266 | 0.172–0.173 | 0.653–0.655 | 0.946–0.982 |
| Forest | Neutral | 1,753–1,774 | 0.559–0.566 | 0.461–0.513 | 1.009–1.011 | 1.297–1.318 |
| Cave | Sodium | 3,883–4,040 | 0.244–0.254 | 0.159–0.162 | 0.593–0.662 | 0.793–0.970 |
| Cave | Neutral | 1,750–1,791 | 0.554–0.567 | 0.483–0.485 | 1.026–1.064 | 1.318–1.360 |

Averaging the two throughput readings for each mode, neutral was 52.7% lower
in daylight, 52.7% lower in forest and 55.3% lower in cave. The mean CPU loop
duration rose by about 0.30–0.31 ms across the scenes. The comparison measures
the combined cost of switching to the neutral Iris pipeline. Individual passes
and effects need isolated measurements. [Per-run metrics and hashes](../../evidence/task-10/runs.csv).

## How to repeat

With the client stopped, use [the exact commands](../../evidence/task-10/commands.txt)
to back up the client files, copy the neutral pack, set each mode, open the dedicated
world, profile, and restore the configuration. Inspect the world list before each
selection. The commands verify the TASK-09 source hashes against the retained
snapshot at `artifacts/task-11/variants/neutral/shaders/`. Include this
snapshot when transferring the baseline for replay. Reuse a fresh artifact
root throughout a repeat for the backup, recordings, results and restoration.

For each batch and scene, `recording/` contains the original profiling ZIP,
before/after window images, options and configuration snapshots, version manifest
and mod hashes. `analysis/client-ticking-raw.csv` preserves the original samples
byte-for-byte. `analysis/frametimes.csv` contains the samples in nanoseconds and
milliseconds. Batch logs show the shader mode, preset acknowledgments and normal
world saves. Preserve `artifacts/task-10/` separately when sharing the developer
handoff. [Neutral pack SHA-256 manifest](../../evidence/task-10/pack.sha256).

## Interpreting the measurements

The FPS column is client loop iterations divided by the profiler wall span. p50,
p95 and p99 use nearest rank across every recorded loop in a single capture.
See [harness metric validation](harness.md#what-the-performance-record-means)
for the units and the one-display-update-per-sample check. These are instrumented
CPU render-loop durations, including waits in the loop. GPU pass times and
compositor presentation cadence require separate instrumentation.

Profiler overhead, background load, temperature and clocks were not measured.
Short captures in one synthetic map give a local regression baseline. Chunk
state and animation phases can still vary. The neutral outdoor captures have
a hard horizon boundary and lack the Sodium captures' rendered clouds. Two
runs per mode and scene show repeat spread in these scenes. Native profile
archives also include server level-dump diagnostic noise described in the harness
handoff.
