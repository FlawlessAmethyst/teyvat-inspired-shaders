# Stylized clouds

TASK-18, 2026-11-12. The cloud layer is part of the untextured sky draw.
Fixed Overworld views compare it with the verified TASK-17 prototype.
[Evidence index](../../evidence/task-18/README.md).

## Shader behavior

The sky program projects the view ray onto a virtual horizontal plane at
Y=288. Wrapped absolute camera XZ keeps shapes anchored as the camera moves.
The field repeats every 32,768 blocks. The wind offset traces a slow circle
over Iris's 3,600-second clock period so the clock wrap joins smoothly.
Coverage fades at low elevation into the existing fog-matched horizon and
between eye altitudes 216 and 268. The existing skylight, ceiling and
submersion checks gate the entire custom sky.

Two samples of cubic-interpolated 2D value noise define broad masses and
smaller breaks. The coarse field's gradient shades each form using the
horizontal sun direction and a small fill direction. Thin and lit regions
lean cream or peach. Denser regions read cooler, and both tones fall to dim
blue at night. Rain lowers the density threshold and increases coverage.
TASK-21 derives the rainy cloud colors from the shared sky palette and
fades the sunward rim contribution. The same opacity attenuates
starlight on the stars draw. The sun and moon keep their existing textured
draw over the sky. The pack disables vanilla cloud geometry with
`clouds=off`. The layer adds zero texture fetches, attachments or draw calls.
[Cloud source](../../shaderpack/shaders/lib/clouds.glsl),
[Weather palette](weather.md#shader-behavior),
[Iris cloud directive](https://shaders.properties/current/reference/shadersproperties/features/#clouds),
[Iris render stages](https://shaders.properties/current/reference/macros/render_stages/).

## In-game captures

Both accepted modes ran in fresh GenshinShaderDev sessions using a disposable
copy of the TASK-03 Overworld. The presets reset position, yaw, pitch, time
and weather. Each capture followed its log acknowledgement and 20 focused
seconds with the HUD hidden. F2 produced native 2560×1440 PNGs at 70° FOV,
12 chunks render distance and 8 chunks simulation distance. Rain streaks,
torch flicker, and cloud motion have independent clocks. A 1600×360 daylight
foreground crop matched byte-for-byte between the two variants.
[Presets](scenes.md#camera-presets),
[TASK-17 baseline and runtime](prototype_checkpoint.md#capture-conditions).

| Preset | Observation |
| --- | --- |
| [Daylight](../../artifacts/task-18/daylight.jpg) | Broad cream shapes with blue-gray interiors break up the upper sky. Gaps expose the sky gradient and distant wisps fade above the terrain horizon. This recovers the light and cool cloud color relationship in R1 with simpler silhouettes. |
| [Sunset](../../artifacts/task-18/sunset.jpg) | Peach shapes frame the sun against lavender and blue gaps. The low horizon and sun disk remain readable. The palette follows the warm/cool separation in R5. |
| [Rain](../../artifacts/task-18/rain.jpg) | A fuller slate deck sits behind the rain. Terrain and precipitation remain legible, and the blue strip near the horizon and bright grass still differ from the subdued R4 reference. |
| [Night](../../artifacts/task-18/night.jpg) | Dim blue clouds give the sky shape and leave stars visible in gaps. The distant tower and tree silhouettes remain readable. |
| [Cave](../../artifacts/task-18/cave.jpg) | The lantern-lit floor and recesses retain their contrast. Cloud coverage stays behind the terrain. |

The initial trial used a wider opacity ramp and based its shading mostly on
density. The resulting rings drew attention to the outlines. The accepted
revision narrows the ramp, rotates the detail lattice, and uses directional
shading to break up the rim. The trial images and source are retained with
the accepted captures. [Indexed reference stills](../../evidence/task-17/references.csv),
[reference review](../../artifacts/task-17/reference-review.jpg).

## GPU cost

The OpenGL timer harness draws the expanded TASK-17 and TASK-18 sky pairs to
the same 2560×1440 RGBA16F target on the GeForce RTX 4080 SUPER, OpenGL
4.6.0, NVIDIA 580.196.07. It uses an offscreen compatibility context on the
same GPU and driver as the game. A viewport-covering quad reproduces the
70° vertical FOV, preset pitch and yaw, approximate solar direction, and
settled rain state. The cloud clock is fixed at 60 seconds. The extra upward
rain case pitches 55° above the horizon.

Two independent processes each record 32 pairs per view after warm-up.
Each timer query brackets 64 draws. The first variant alternates by pair.
The table reports the range across the two runs in milliseconds per draw.
The delta columns are computed from paired batches before summarizing.
[Harness source](../../evidence/task-18/sky_timer.c),
[raw batches](../../artifacts/task-18/gpu-01.csv),
[second run](../../artifacts/task-18/gpu-02.csv),
[timing summary](../../evidence/task-18/gpu-summary.csv),
[OpenGL timer query specification](https://registry.khronos.org/OpenGL/specs/gl/glspec46.compatibility.pdf).

| View | Control median (ms) | Clouds median (ms) | Added median (ms) | Added p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| Sunset | 0.02733 | 0.04039–0.04045 | 0.01278–0.01296 | 0.01317–0.01326 |
| Rain | 0.02555–0.02561 | 0.03648–0.03654 | 0.01090–0.01098 | 0.01114–0.01166 |
| Night | 0.02557–0.02564 | 0.03648–0.03670 | 0.01091–0.01101 | 0.01123–0.01128 |
| Upward rain | 0.02597–0.02621 | 0.04839–0.04878 | 0.02245–0.02257 | 0.02301–0.02304 |

The directional revision adds at most about 0.0021 ms to the median
increment compared with the trial's separate run. The small measured
sky-draw increment supports retaining the revision. The benchmark isolates
the cloud contribution to the base sky draw. It excludes the stars draw,
Iris's game-side state and shader transformations, world geometry, and
presentation. Full-client GPU frame time and other GPUs remain unmeasured.

TASK-26 repeated the cloud ablation on the fog-tuned build. It measured
0.0103–0.0121 ms per synthetic sunset, rain or night sky draw and about
0.0213 ms in upward rain. The matched client-loop reductions varied
across repeats. [TASK-26 cloud comparisons](effect_costs.md#offscreen-gpu-draws).

## Limits and handoff

The cloud plane is a sky treatment without depth or cloud shadows. The
textured sun and moon can show through the deck. TASK-21 checks live
weather transitions and coordinates the cloud and horizon colors.
TASK-23 records the sky during clear-day ground movement. Flight through
the cloud altitude and the clock wrap remain untested in the client.
The projected cloud layer is disabled in the Nether and End by
the same dimension checks as the procedural sky. TASK-19 used this accepted
pack as its incremental control. [Water report](water.md),
[weather report](weather.md), [motion report](anti_aliasing.md),
[dimension findings](lighting_dimensions.md#dimensions).
