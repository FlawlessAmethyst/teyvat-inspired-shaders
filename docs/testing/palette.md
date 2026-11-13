# Color grading and tonemapping

TASK-11, 2026-11-12. S1 from the [visual rubric](../research/style_targets.md)
is the target. The default grade brings brighter foliage and clearer material
separation to the TASK-09 scaffold.

## Shader

The [final pass](../../shaderpack/shaders/final.fsh) samples the blended
RGBA16F scene once. [The grade](../../shaderpack/shaders/lib/tonemap.glsl)
lifts scene-linear values by 1.48× (about 0.57 EV). In the TASK-11
snapshot it expands chroma around Rec. 709 luminance by up to 24%.
TASK-21 retains this expansion in clear weather and shifts to 12% chroma
compression at full rain. The gamut bound preserves at least 30% of the
smallest exposed channel during expansion. For a channel peak `p` above
0.52, the shoulder maps it to `0.52 + 0.48 * (p - 0.52) / (0.48 + (p - 0.52))`
and applies the same gain to all three channels. The curve joins the linear
range with slope one.
The result is encoded once to sRGB. [Weather grade](weather.md#shader-behavior).

## Capture conditions

GenshinShaderDev ran Minecraft 1.21.1 / NeoForge 21.1.265 / Iris
1.8.14-beta.1 / Sodium 0.8.13 on the TASK-10 RTX 4080 SUPER and Ryzen 9 9950X
stack. Test captures used the TASK-03 Overworld with vanilla textures,
2560×1440 fullscreen, FOV 70°, 12 render chunks, 8 simulation chunks,
sRGB, VSync off and Unlimited FPS. Each preset fixed camera, time and
weather and ran a 20-second focused warm-up. See [the TASK-10
baseline](baseline.md) for the full setup and limits of the profiler.

The neutral control is the exact TASK-09 shader tree used in TASK-10.
The TASK-11 graded snapshot changes `final.fsh` and adds `lib/tonemap.glsl`.
The separate diagnostic variant inserts synthetic values before grading and
uses the production grade and display encode. Source hashes and exact replay
commands are in [the evidence directory](../../evidence/task-11/).

## Visual review

The [paired overview](../../artifacts/task-11/comparison.jpg) is ordered
neutral then graded. The individual F2 captures are the native-resolution
evidence. Review compares material roles to the references indexed under
[S1](../research/style_targets.md#s1--controlled-vivid-palette).

| Preset | Native captures | S1 result | Observation |
| --- | --- | --- | --- |
| Daylight | [Neutral](../../artifacts/task-11/neutral-01/daylight/native.png) / [graded](../../artifacts/task-11/graded-01/daylight/native.png) | PASS, improved | Foreground grass is brighter and more distinct from the gray brick and stone. The blocks and grass still show surface texture. This moves toward R1 and R2. |
| Forest | [Neutral](../../artifacts/task-11/neutral-01/forest/native.png) / [graded](../../artifacts/task-11/graded-01/forest/native.png) | PASS, improved | Leaves and grass are more vivid while the shaded canopy, bark, and neutral stone remain distinct, moving toward R2. The retained blue-channel detail keeps the foliage from collapsing into two-channel green. |
| Sunset | [Neutral](../../artifacts/task-11/neutral-01/sunset/native.png) / [graded](../../artifacts/task-11/graded-01/sunset/native.png) | PASS, improved | The grass stays green beside the warmer horizon, as in R5. The existing bands inside the square sun resolve from near white into visibly distinct levels. |
| Night | [Neutral](../../artifacts/task-11/neutral-01/night/native.png) / [graded](../../artifacts/task-11/graded-01/night/native.png) | PASS, improved | Dark areas gain some separation while the scene remains dim. |
| Cave | [Neutral](../../artifacts/task-11/neutral-01/cave/native.png) / [graded](../../artifacts/task-11/graded-01/cave/native.png) | PASS, improved | Warm lanterns and the nearby floor read more clearly. Floor and pillar texture remain visible, and recesses stay dark. R8 anchors the warm-light and neutral-surface relationship. |

The palette moves toward the material separation in the selected footage.
The square sun, hard horizon and missing clouds are inherited from the
scaffold. Later tasks cover spatial lighting, atmosphere and time-dependent
sky palettes.

Across the five graded native frames, no channel reached code 255. Daylight,
forest, sunset and cave also had no channels at code zero. Night retained the
same 1,215,668 black pixels as neutral, in the black sky. The first trial
grade had 355,138 blue-channel zeros in the forest profiler frame. The revised
chroma bound eliminated them on the matched frame. Counts are preserved in
`artifacts/task-11/endpoint-counts.txt` with the raw PNGs.

The [snow swatch](../../artifacts/task-11/graded-01/snow/native.png) shows
white surface variation and a legible step. It checks snow material response
under fixed daylight. Snow weather and natural snow terrain remain untested.
The world acknowledged placing and removing all 30 temporary snow blocks.

The [diagnostic frame](../../artifacts/task-11/diagnostic/ramp/native.png)
shows a linear gray ramp to 1.0, a gray ramp to 4.0 and a green HDR ramp.
At native resolution the gradients showed 8-bit quantization in the shallow
highlights, with no obvious coarse bands in the five scene captures. All
2,560 samples across each ramp were monotonic and matched the single sRGB
encode to within one code value per channel. The gray ramps ended at 236 and
251, while the green ramp ended at `(49, 251, 107)`. This tests the final
shader's transfer function with synthetic input. Scene captures exercise the
regular geometry and attachment path.

## Performance

Four fresh sessions ran neutral, graded, graded, neutral. The rejected first
grade is excluded from the timing matrix. Each session recorded daylight, forest
and cave with the same native F3+L profiler as TASK-10. The 12 retained captures
contain 211,181 client-loop samples over 9.996–10.000 seconds each.
[Per-run metrics and archive hashes](../../evidence/task-11/runs.csv).

| Preset | Neutral loop FPS | Graded loop FPS | Mean loop change | Neutral p95 (ms) | Graded p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Daylight | 1,756–1,780 | 1,768–1,770 | −0.0002 ms (−0.03%) | 0.991–1.008 | 1.084–1.126 |
| Forest | 1,735–1,738 | 1,737–1,749 | −0.0020 ms (−0.35%) | 1.028–1.083 | 1.070–1.121 |
| Cave | 1,790–1,795 | 1,712–1,791 | +0.0134 ms (+2.41%) | 0.989–1.005 | 1.115–1.161 |

The mean change compares the average of the two per-run mean loop durations.
Daylight and forest mean changes are small relative to repeat spread. The
cave mean rose in one graded session and returned to the neutral range in
the other. The p95 rose in both daylight and cave repeats. The grade is
retained for the visible palette and highlight improvements with this
measured trade-off. The profiler measures instrumented CPU loop durations,
including waits.

TASK-26 timed grading against a bypass that retains the final pass,
attachment fetch and sRGB encoding. Grading added about 0.0002 ms per
offscreen draw. The valley client-loop comparison changed sign across
repeats. The GPU time of the final pass in the running client and
presented-frame cadence remain unmeasured.
[TASK-26 grading comparisons](effect_costs.md#offscreen-gpu-draws).

The original ZIPs, raw and converted timing CSVs, native images, client logs,
and settings snapshots are in `artifacts/task-11/`. Use the
[replay commands](../../evidence/task-11/commands.txt) with the
[TASK-10 artifacts](baseline.md) to validate the recorded environment and
regenerate the comparison and metrics index. Replay stages the retained neutral
and graded shader snapshots and verifies both against their original hashes.
