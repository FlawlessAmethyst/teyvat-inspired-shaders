# Stylized water

TASK-19, 2026-11-12. [Evidence index](../../evidence/task-19/README.md).

## Shader behavior

The translucent terrain program selects vanilla water through pack-local ID
10001. Other translucent terrain continues through the atlas and lightmap
calculation with the engine's blend state. Above water, the shader reads the
lightmap and one texel of Iris's pre-hand depth snapshot. The two reads replace
the previous water material's lightmap and atlas reads. The material runs
in the translucent draw and writes straight alpha to `colortex0`.
[Water module](../../shaderpack/shaders/lib/water.glsl),
[Iris block ID attribute](https://shaders.properties/current/reference/attributes/mc_entity/),
[Iris depth snapshots](https://shaders.properties/current/reference/buffers/depthtex/).

The inverse projection reconstructs the background at the current pixel.
Water uses the separation along the camera ray to blend from shallow turquoise
toward deeper blue and increase straight alpha over the first eight blocks.
Clear or invalid background depth selects a fixed intermediate absorption.
Skylight gates the reflection of the analytic sky gradient. The reflection
grows at a grazing angle and includes a broad sun-facing highlight that fades
in rain. TASK-21 uses the shared overcast sky palette in the analytic
reflection. Two low-amplitude waves perturb the surface normal using world XZ and
Iris's frame clock. The phase repeats across 64-block tiles and closes at the
clock wrap. [Weather transition review](weather.md#visual-review).

When the eye is underwater, the surface uses a lightmapped tint with fixed
opacity. The shared geometry fog builds between 3 and 26 blocks, with the
strongest attenuation in red. Submerged fragments skip thickness sampling.

## Capture conditions

The fixed basin has one, two, four and seven water blocks above pale sandstone,
with two floor lamps and a stained glass panel overlapping the view of the
water. An identical camera looks down its length in daylight, settled rain
and sunset. Additional presets cover the original TASK-03 open-water view,
a close shoreline, the submerged floor and the underside of the surface.
The glass and stone held items are shown with the HUD on in a separate capture.
Each native F2 capture follows 20 focused seconds at the preset. Cloud drift,
waves, and precipitation have independent clocks.
[Fixture source](../../evidence/task-19/fixture.mcfunction),
[recorded camera and weather presets](../../artifacts/task-19/presets.json).

## Visual review

| View | Observation |
| --- | --- |
| [Basin in daylight](../../artifacts/task-19/basin.jpg) | Sandstone texture and the nearest step remain readable through a light turquoise tint. More oblique and deeper rays give the far steps a stronger blue. The purple glass panel stays distinct at the water overlap. |
| [Basin in rain](../../artifacts/task-19/basin-rain.jpg) | Water shifts toward muted blue-gray as the cloud deck darkens. The floor and bank edge remain legible through the precipitation. The existing rain streaks are still saturated blue. |
| [Basin at sunset](../../artifacts/task-19/basin-sunset.jpg) | The floor carries the cooler low-sun terrain lighting while the surface reflects the brighter sky. The east-facing camera samples the sky away from the setting sun. |
| [Open water](../../artifacts/task-19/open-water.jpg) | The original constant-depth basin shows warm sand nearby and a soft turquoise-to-blue transition at a grazing angle. The original high-chroma rim is softened. |
| [Shore](../../artifacts/task-19/shore.jpg) | The boundary stays aligned with the sandstone lip and nearby texture reads through the surface. |
| [Submerged floor](../../artifacts/task-19/underwater.jpg) and [underside](../../artifacts/task-19/underside.jpg) | The nearby lamp and bottom remain visible. The far wall shifts blue-green and the surface has a continuous edge. |

R5 shows turquoise water adjacent to warm sand, R7 preserves the nearby bottom,
and R9 transitions toward blue farther offshore. Those relationships guided the
palette. The stepped fixture makes the depth transitions more abrupt than the
reference shorelines. [Indexed reference stills](../../evidence/task-17/references.csv).

The developer diagnostic encodes thickness as gray, invalid reconstruction as
yellow, clear depth as magenta, and the submerged branch as cyan. The basin
center shows increasing gray with depth. The shoreline edge and glass silhouette
remain distinct. The held stone and stained glass have their own shading when
visible over the diagnostic water. The submerged views show the cyan branch
over the visible underside. [Basin depth](../../artifacts/task-19/depth/basin/native.png),
[held items](../../artifacts/task-19/depth/basin/held-items.png),
[shore depth](../../artifacts/task-19/depth/shore/native.png),
[submerged depth](../../artifacts/task-19/depth/underside/native.png).

Two fixed-camera frames taken about 0.7 seconds apart show small pixel changes
in the wet surface and byte-identical RGB in a dry foreground patch. The
center patch over the deeper step changed by 0.26 of an 8-bit code value per
channel on average. This confirms time variation at the fixed view.
[First wave frame](../../artifacts/task-19/water-01/shore/wave-a.png),
[second wave frame](../../artifacts/task-19/water-01/shore/wave-b.png).

## Performance

Each of the three modes ran in two fresh sessions. Each session recorded
daylight and settled rain from the same camera after a 20-second warm-up.
The client used 2560×1440, 70° FOV, 12 chunks render distance, 8 chunks
simulation distance, unlimited FPS and VSync off. The installed stack was
Minecraft 1.21.1, NeoForge 21.1.265, Iris 1.8.14-beta.1 and Sodium 0.8.13
on CachyOS, with a Ryzen 9 9950X and RTX 4080 SUPER on NVIDIA 580.196.07.
The archive runtime, video options and mod hashes matched the TASK-10
baseline. [Harness metric](harness.md#what-the-performance-record-means),
[raw archive and CSV index](../../evidence/task-19/runs.csv).

| View | Sodium shaders off | TASK-18 control | TASK-19 water | Water increment |
| --- | ---: | ---: | ---: | ---: |
| Daylight basin | 0.2181 ms | 0.5281 ms | 0.5352 ms | +0.0071 ms (+1.3%) |
| Rain basin | 0.2572 ms | 0.5849 ms | 0.5981 ms | +0.0132 ms (+2.3%) |

Each value averages the two session means from Minecraft's native F3+L
CPU client-loop samples. The individual water-control differences were
+0.0060 and +0.0082 ms in daylight, and +0.0100 and +0.0165 ms in rain.
The p95 difference changed sign between pairs in both scenes. The timings
include client work and waits.

TASK-26 measured the integrated build in the stepped basin and on a
synthetic full-viewport water draw. Above water, the full material added
0.0192–0.0195 ms per synthetic draw versus lightmapped translucency. The
depth-sampling and reconstruction comparison against constant absorption
added 0.0113–0.0116 ms per draw. In-client water GPU time, Iris's pre-hand
depth copy and presentation pacing remain unmeasured.
[TASK-26 water comparisons and limits](effect_costs.md#offscreen-gpu-draws).

## Limits and handoff

Validation covers the installed Overworld stack, fixed source-water surfaces,
one overlapping stained-glass arrangement and the tested held items. The
TASK-23 open-water clip adds a moving shoreline and shallow entry with the
camera above the surface. TASK-28 records a live rise above the surface
and resubmersion in the stepped basin, with an abrupt color change at
both crossings. Flowing and waterlogged edges, extended swimming, and
water rendering outside the Overworld remain unverified.
[Runtime regression](regression_report.md#runtime-results). The optical model uses scalar transmission and
a procedural sky reflection. The debug palette exercises measured thickness
and the submerged branch in this fixture. TASK-24 retained analytic sky
reflection as the water reflection method and rejected scene-geometry
reflections and screen-space refraction for this build.
[Effects triage](../architecture/deferred_effects.md#dispositions-and-expected-gpu-work).

TASK-20 used the exact accepted water snapshot as its incremental control.
TASK-21 checks the above-water tint, analytic reflection and haze through
both directions of the weather ramp.
[Vegetation results](vegetation.md#performance), [weather report](weather.md),
[shoreline motion review](anti_aliasing.md#visual-review).
[Accepted source manifest](../../evidence/task-19/pack.sha256),
[replay commands](../../evidence/task-19/commands.txt).
