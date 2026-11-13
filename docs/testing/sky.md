# Sky gradients and atmospheric color — TASK-14

## Shader behavior

The [sky module](../../shaderpack/shaders/lib/sky.glsl) blends scene-linear
horizon and zenith colors through night, twilight and daylight. The blend
weights follow sun elevation, using the same Iris view-space sun and up
directions as terrain lighting. A broad peach tint peaks in the low sky
toward the sun around dawn and dusk. The sky vertex stage evaluates the
time-dependent palette. Each sky fragment normalizes the interpolated view
ray and evaluates the gradient and sun-facing tint. The sky uses the
existing RGBA16F target and final grade. The gradient adds no pass, render
target, or texture read.

Iris draws its horizon mesh and sky disc through `gbuffers_skybasic`. The
gradient replaces the vanilla sunset fan on skylit, non-ceiling dimensions
when Iris reports `isEyeInWater == 0`. In the TASK-14 snapshot, the stars
and void use vertex tint and the sun and moon use the textured fallback.
TASK-15 gives the sun and moon an explicit textured program, TASK-18 dims
stars by projected cloud coverage, and TASK-21 adds the shared overcast
palette. A small spatial dither in the procedural sky reduces visible
quantization in the display output.
[Cloud report](clouds.md), [weather report](weather.md),
[Iris gbuffers routing](https://shaders.properties/current/reference/programs/gbuffers/),
[Iris render-stage definitions](https://github.com/IrisShaders/docs/blob/main/src/content/docs/current/Reference/Macros/Render_Stages.mdx),
[Jimenez, SIGGRAPH 2014, Interleaved Gradient Noise](https://www.iryoku.com/next-generation-post-processing-in-call-of-duty-in-advanced-warfare/).

The palette follows the light blue horizon and deeper sky of R9, the
peach-to-lavender relationship of R5, and the blue surroundings and points
of light in R6. R6's exact time of day is unknown. The night brightness is
a source choice for this pack.
[Reference comparison](../../artifacts/task-14/reference-strip.jpg),
[reference provenance](../research/style_targets.md#s3--sky-gradients-and-time-coherence).

## Capture conditions

The control is the hash-verified TASK-13 ambient snapshot. Both packs use
the TASK-03 visual world with the same fixed cameras, clear weather, vanilla
textures, hidden HUD, 2560×1440 resolution, FOV 70, render/simulation distances
12/8, Unlimited FPS and VSync off. The time series keeps the west-facing
sunset camera fixed for 20 samples. Separate video passes run the clock at
normal speed with the same camera position, facing west for dusk and east for
dawn. The recording session uses VSync and a 60 FPS cap. It samples native
2560×1440 F2 captures at 3 Hz, with the game clock advancing normally between
captures. The 1280×720 review clips play the samples at their capture cadence.
[Scene presets](scenes.md), [replay commands](../../evidence/task-14/commands.txt).

GenshinShaderDev ran on CachyOS with a Ryzen 9 9950X, RTX 4080 SUPER, OpenGL 4.6.0
and NVIDIA driver 580.196.07. The client uses Minecraft 1.21.1, NeoForge
21.1.265, Iris 1.8.14-beta.1, Sodium 0.8.13 and Java 21.0.7 in Prism Launcher
Flatpak. The timing index checks the runtime, mod hashes, settings and
presets against the TASK-10 baseline. [Baseline methodology](baseline.md).

## Visual review

- At tick 6000 the upper daylight sky measures sRGB `(90, 170, 230)`
  and the low patch measures `(135, 197, 234)`.
  [Daylight comparison](../../artifacts/task-14/daylight-row.jpg).
- At tick 12785 the west-facing low patch is peach `(236, 160, 147)` and
  the upper patch is lavender `(155, 126, 172)`. The sun remains visible at
  the edge of the terrain. At tick 18000 the same patches fall to
  `(33, 55, 98)` and `(22, 39, 80)`, with visible stars. The moon
  is visible from tick 21900 through 23215.
  [Procedural sweep](../../artifacts/task-14/sky-sweep.jpg),
  [ambient control sweep](../../artifacts/task-14/ambient-sweep.jpg).
- The last tick before day wrap and the first tick after it have identical
  median RGB codes in both fixed sky patches. The west-facing sky is
  cooler during dawn, when the sun is behind that camera.
  [Native patch measurements](../../evidence/task-14/pixels.csv).
- The daylight grass, night grass and cave ceiling recess patches match
  the control's median RGB codes. The cave retains the lit floor. The
  central stone landmark has less contrast against the new night sky.
  [Cave comparison](../../artifacts/task-14/cave-row.jpg),
  [night comparison](../../artifacts/task-14/night-row.jpg).

The live clock advanced from 12300 to 13893 for dusk and from 22530 to
243 for dawn. All 486 native frames passed the capture integrity checks.
The largest gap between native samples was 0.334 seconds. The dusk glow
fades as the stars appear, and the east-facing dawn moves from peach to
blue as the sun rises. The two dawn sky patches changed by at most 2.05
8-bit RGB codes between adjacent samples around the day wrap. The sampled
sequences show no visible jump at the wrap.
[Dusk clip](../../artifacts/task-14/sky-video/dusk/transition.mp4),
[dawn clip](../../artifacts/task-14/sky-video/dawn/transition.mp4),
[wrap frames](../../artifacts/task-14/dawn-wrap.jpg),
[sample continuity](../../evidence/task-14/video.csv).

The procedural gradient removes the control's seam between the sky disc
and Iris horizon geometry. The sampled sky has no apparent banding. The
distant terrain edge is sharp in these TASK-14 captures. TASK-15 now softens
that edge with geometry fog and routes the sun and moon through
`gbuffers_skytextured`. These TASK-14 captures cover clear Overworld weather.
TASK-18 adds cloud coverage to the untextured sky draw.
[Distance fog report](fog.md), [cloud report](clouds.md).

The initial X11 recordings had black bands with both uncapped and
VSync-limited settings. The retained clips were rebuilt from native
captures. The 3 Hz cadence leaves shorter transients unresolved.

## Performance

Four fresh sessions ran sky, ambient, ambient, sky. Each captured the fixed
daylight and sunset scenes after a 20-second focused warm-up. The eight native
profiles contain 184,799 CPU client-loop samples over 9.996–10.000 seconds
per run. The delta uses the average of each mode's two per-run mean loop
durations.
[Profile distributions and archive hashes](../../evidence/task-14/runs.csv).

| Preset | Ambient loops/s | Sky loops/s | Mean loop delta | Ambient p95 (ms) | Sky p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Daylight | 2,341–2,349 | 2,335–2,352 | +0.00037 ms (+0.09%) | 0.681–0.700 | 0.644–0.648 |
| Sunset | 2,248–2,268 | 2,293–2,297 | −0.00727 ms (−1.65%) | 0.654–0.671 | 0.645–0.650 |

The daylight mean range overlaps the control. Both sunset repeats have
lower mean client-loop durations. These short profiles show no consistent
CPU regression. The historical TASK-10 Sodium shaders-off daylight runs
recorded 3,745–3,758 loops/s under the matched settings. That comparison
covers the whole Iris pack on a separate run.
[Sodium raw metrics index](../../evidence/task-10/runs.csv).

TASK-26 measured the cloudless gradient and dither against a flat horizon
color. The synthetic sky-draw increment was 0.00007–0.00024 ms.
In-client sky-stage GPU time and display presentation cadence remain
unmeasured. [TASK-26 GPU comparisons](effect_costs.md#offscreen-gpu-draws).

## Handoff

The tested shader snapshot is at `artifacts/task-14/variants/sky/shaders/`.
Run from the repository root to verify it.

```bash
sed 's|shaderpack/shaders/|artifacts/task-14/variants/sky/shaders/|' \
    evidence/task-14/pack.sha256 | sha256sum -c -
```

TASK-15 uses this snapshot as its control. The distance-fog module shares
the sky palette and sun-facing weight at zero view elevation. The spatial
sky dither belongs to the sky draw.
[Distance fog report](fog.md).

Preserve the native captures,
profiles, video and logs under `artifacts/task-14/` for developer handoff.
[Verification record](../../evidence/task-14/verification.txt).
