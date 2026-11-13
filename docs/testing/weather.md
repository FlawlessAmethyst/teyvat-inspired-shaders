# Weather transitions

TASK-21, 2026-11-13. [Evidence index](../../evidence/task-21/README.md).

## Shader behavior

Iris provides a rain intensity that moves between zero and one as Minecraft
changes weather. The shaderpack uses this one ramp across the terrain, sky,
distance fog, water and final grade. The outdoor geometry and final pass
gate the response on skylight and the absence of a dimension ceiling.
[Iris weather uniforms](https://shaders.properties/current/reference/uniforms/world/#rainstrength).

At full rain, the terrain shader retains 10% of its clear direct-sun term.
It also reserves less lightmap intensity for direct sun, preserving diffuse
fill as cast-shadow contrast falls. The skylight and block-light
weights still bound the fill and leaf response. The sky shifts to a muted
slate palette with separate day, twilight and night anchors. The procedural
sun glow fades out as the cloud deck closes and its bright rims soften.
[Terrain lighting](../../shaderpack/shaders/lib/terrain_lighting.glsl),
[sky palette](../../shaderpack/shaders/lib/sky.glsl).

Distance fog uses the same horizon palette as the sky. At 12 chunks the
TASK-21 captures use 28–180 blocks in clear weather and 22–136 in full rain.
The TASK-25 follow-up raises the clear start to 88 blocks. The full-rain
endpoints stay at 22 and 136 blocks. The live sequences below used the
TASK-21 ramp. TASK-28 sampled rain onset and clearing with the tuned ramp
at the fixed valley camera. The distant ridge faded as rain built and
reappeared as it cleared. [Fog tuning](visual_comparison.md#clear-air-fog-follow-up),
[tuned weather sequence](regression_report.md#runtime-results).
Water reuses the sky palette in its analytic reflection, blends the surface
tint toward blue-gray and fades the broad sun highlight. The final grade
shifts from bounded chroma expansion to 12% compression toward luminance.
The existing precipitation draw uses a dedicated shader pair that reduces
falling streak chroma by 72% in scene-linear RGB and retains vanilla motion,
lightmap, alpha and blending. Splash particles continue through their
existing path and receive the final grade. The effect adds no render pass,
texture read, render target or history buffer.
[Fog](../../shaderpack/shaders/lib/fog.glsl),
[water](../../shaderpack/shaders/lib/water.glsl),
[grade](../../shaderpack/shaders/final.vsh),
[precipitation shader](../../shaderpack/shaders/gbuffers_weather.fsh),
[precipitation draw](https://shaders.properties/current/reference/programs/gbuffers/).

## Capture conditions

The fixture is a disposable copy of the saved TASK-20 vegetation world.
The stock daylight/rain camera frames grass, stone, trees and the shallow
basin. Two more camera pairs isolate the open-water surface and the
plains/jungle understory. Every view uses tick 6000, 2560×1440, 70° FOV,
12 chunks render distance, eight chunks simulation distance, and vanilla
textures. Settled views use native F2 PNGs after a 20-second warm-up.
During transition capture the camera and game clock stay fixed. Test
datapack hotkeys change weather and log the clock tick without teleporting.
Each series records 44 native F2 screenshots in an 11-second capture at a
nominal four screenshots per second. The trigger fires about two seconds
after capture starts. The replay keeps
the full-resolution frames and their actual capture times.
[Replay and checks](../../evidence/task-21/commands.txt).

## Visual review

| View | Observed change in rain |
| --- | --- |
| [Daylight](../../artifacts/task-21/daylight.jpg) | The pale blue horizon becomes slate and the distant tower loses contrast. Grass texture, the near wall and tree silhouettes remain readable. Falling streaks are still visible. Splash particles retain some blue. |
| [Open water](../../artifacts/task-21/open-water.jpg) | The reflection and surface tint cool with the sky. The sand pattern and shoreline remain visible while the far end recedes into haze. |
| [Dense canopy](../../artifacts/task-21/dense.jpg) | The lit path dims and its contrast with shaded stone narrows. The plains and jungle oaks retain different greens. Trunks, leaf gaps and cutouts stay readable. |

In the matched clear daylight captures, the foreground grass and near wall
patches match TASK-20 byte for byte. In rain the near wall is brighter than
TASK-20 in the selected patch. The retained diffuse fill helps separate it
from the cooler, dimmer distant tower.
[Settled RGB patches](../../evidence/task-21/pixels.csv).

Both directions were reviewed across 264 native frames. The horizon and water
changed together. Canopy shadow contrast fell and recovered at the same
shadow positions. No severe jump or color flash was observed at the
sampled cadence. Across the selected median RGB patches, the largest
adjacent-sample change was 8 of 255 codes in sky, 5 in water, 3.5 in path or
stone and 10 in foliage. These measurements include moving precipitation
and use local display RGB medians. In the sampled path patches, the
lit-to-shaded luma difference narrowed from about 61 codes in clear weather
to 35 in rain. [Transition samples](../../evidence/task-21/transitions.csv).

| Fixed camera | Clear to rain | Rain to clear |
| --- | --- | --- |
| Daylight | [Preview](../../artifacts/task-21/weather-live/transitions/daylight/to-rain/preview.mp4) | [Preview](../../artifacts/task-21/weather-live/transitions/daylight/to-clear/preview.mp4) |
| Open water | [Preview](../../artifacts/task-21/weather-live/transitions/open-water/to-rain/preview.mp4) | [Preview](../../artifacts/task-21/weather-live/transitions/open-water/to-clear/preview.mp4) |
| Dense canopy | [Preview](../../artifacts/task-21/weather-live/transitions/dense/to-rain/preview.mp4) | [Preview](../../artifacts/task-21/weather-live/transitions/dense/to-clear/preview.mp4) |

The first window-capture trial introduced black bands. It was excluded
from the visual evidence and the series was recaptured with Minecraft's
native screenshot path. Samples averaged 0.25 seconds apart, with a
0.49-second gap across the weather hotkey. Shorter events can fall between
captures.

## Performance

The comparison uses two fresh sessions per mode in daylight and settled
rain, with Sodium shaders off as the whole-pack baseline and the exact
TASK-20 shaders as the incremental control. The client runs at 2560×1440
with unlimited FPS and VSync off. Minecraft's F3+L profiler records
instrumented CPU client-loop duration. The system is a Ryzen 9 9950X with
an RTX 4080 SUPER on CachyOS and NVIDIA driver 580.196.07. The client runs
Minecraft 1.21.1, NeoForge 21.1.265, Iris 1.8.14-beta.1 and Sodium 0.8.13.
[Baseline method](baseline.md), [metric definition](harness.md#what-the-performance-record-means).

| View | Sodium shaders off | TASK-20 | TASK-21 | TASK-21 change |
| --- | ---: | ---: | ---: | ---: |
| Daylight | 0.1990 ms | 0.4950 ms | 0.4922 ms | −0.0028 ms (−0.56%) |
| Settled rain | 0.2469 ms | 0.5642 ms | 0.5629 ms | −0.0013 ms (−0.23%) |

Each entry averages two session means. The daylight change reversed sign
between repeats. Rain was 0.0004–0.0022 ms lower in the paired CPU loop
measurements. [Archive and raw sample index](../../evidence/task-21/runs.csv).

The TASK-18 OpenGL timer repeated 32 paired batches of 64 sky draws per
scene in two offscreen 1440p runs. The median paired candidate-minus-control
time was −0.00046 to −0.00059 ms per draw across the settled-rain, clear
sunset and clear night cases, and −0.00120 to −0.00122 ms in the upward
rain stress view. The measured sky draw incurred no added GPU cost on
this device. The test isolates the sky draw. It leaves the GPU cost of
terrain, precipitation, water and the final grade, full-client GPU time
and presentation cadence open.
[GPU timings](../../evidence/task-21/gpu-summary.csv),
[timer method](clouds.md#gpu-cost).

TASK-26 kept engine rain active while disabling the pack's coordinated
rain response. The settled-rain client-loop delta changed sign across
the two rounds. That grouped comparison leaves the individual in-client
GPU costs open.
[TASK-26 rain comparison](effect_costs.md#client-results).

## Limits and handoff

Live coverage is clear-to-rain and rain-to-clear at fixed midday and
fixed cameras in the installed Overworld stack. The tuned ramp has one
valley sequence at about two native captures per second. Shorter
artifacts between samples can go unseen. Snow, thunder and lightning,
rainy twilight and night, shelter and non-precipitating biomes, weather
changes while submerged, and weather changes during camera movement
remain unverified. The ramp describes world weather. Vanilla controls
where precipitation appears.
The instance saved and exited. Five settings files were restored byte for
byte, both temporary packs were removed and the source worlds matched
their hashes. TASK-22 used this shader tree as its control and separately
smoke-tested the Nether and End.
[Verification record](../../evidence/task-21/verification.txt),
[exact replay](../../evidence/task-21/commands.txt),
[lighting and dimension report](lighting_dimensions.md).
