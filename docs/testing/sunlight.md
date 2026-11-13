# Terrain sunlight — TASK-12

**DONE**, 2026-11-12. Validation covers the development instance's Overworld.

## Shader behavior

The terrain vertex shader evaluates sunlight from Iris's view-space
`sunPosition` and `upPosition` and the transformed terrain normal. The light
fades smoothly at the horizon and shifts from pale warm daylight to amber at low
elevation. The daylight weight is a function of elevation, so it follows the
engine sun through both dawn and dusk. Terrain interpolates the directional
result. The fragment shader combines it with the existing lightmap sample in
linear RGB and sends the result through the TASK-11 grade.
R2's warm boards and darker crate faces and R5's warm shoreline against cool
rock guided the color choices. [Reference frames and S2 rubric](../research/style_targets.md#s2--warm-light-cool-fill-and-legible-shadows).

The vertex shader reads block light and skylight separately from the engine
lightmap coordinates. Low skylight gates direct sun and bright block light
reduces the portion of fill reserved for it. The lightmap still supplies local
lamp color, interior light and nighttime illumination. The terrain draw keeps
atlas color, biome tint and combined vertex AO, with `oldLighting=false`
disabling the engine's legacy face shading. Water, block entities and breaking
overlays have explicit routes back to the scaffold lightmap calculation because
Iris would otherwise send them through the new terrain program.

The effect adds vertex arithmetic and one interpolated vector. Terrain does
one additional RGB decode, one multiply for the lightmap fill and one add for
the direct term. The existing atlas and lightmap reads, render target, and final
pass still serve the whole effect. TASK-12's skylight gate supplies approximate
occlusion. TASK-13 adds the ambient response and TASK-16 adds a depth map
for cast shadow silhouettes.
[Ambient report](ambient.md), [shadow report](shadows.md).

The pinned Iris source describes the celestial uniforms, Sodium's lightmap
coordinate patch, the matrix's texel-center offset, and the program fallback
chain. The four TASK-12 client sessions establish the behavior observed on the
installed beta. [TASK-06 source record](../../evidence/task-06/sources.json),
[lightmap matrix](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/uniforms/builtin/BuiltinReplacementUniforms.java),
[program fallbacks](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/shaderpack/loading/ProgramId.java).

## Capture conditions and visual review

The control is a hash-verified snapshot of the TASK-11 graded pack. Both modes
use the same GenshinShaderDev Overworld on CachyOS, Minecraft 1.21.1, NeoForge
21.1.265, Iris 1.8.14-beta.1, Sodium 0.8.13 and Java 21.0.7. The machine has a
Ryzen 9 9950X and RTX 4080 SUPER with OpenGL 4.6 and NVIDIA driver 580.196.07.
The captures use the TASK-03 world, 2560×1440 fullscreen,
FOV 70, render and simulation distances of 12 and 8 chunks, clear weather,
vanilla textures, hidden HUD, VSync off and Unlimited FPS.
[Scene presets](scenes.md).

The time-sweep runner uses temporary slot triggers. Install them through the
TASK-12 staging steps before running the sweep, and restore the datapack after
capture. In the stock scene datapack, slot 9 rebuilds the test map.
[Replay commands](../../evidence/task-12/commands.txt).

The [native scene comparison](../../artifacts/task-12/comparison.jpg) shows
slightly warmer, brighter open grass against shaded stone in daylight. Grass,
oak leaves, bark and stone remain distinct in the plains test map. At the
sunset camera, grass has less blue and the wall facing away from the sun
remains shaded. The shapes and translucency of the water basin look consistent
in the fixed captures. The original hard horizon is visible in both modes.

The [stone-face pair](../../artifacts/task-12/stone-faces.jpg) uses a second
camera at tick 12000. The sun-facing west stone changes from median sRGB
`(73, 73, 80)` in the control to `(144, 125, 116)` with sunlight. The adjacent
south face stays cool at `(89, 89, 100)`. Both faces retain their stone texture.
The [temporary scene trigger](../../evidence/task-12/facing.mcfunction) records
the teleport and camera angles.

Both modes sampled 15 fixed times plus a repeat at tick 12000, keeping the
sunset camera stationary. The sunlight foreground darkens across the sampled
dusk frames and recovers through the sampled dawn and day-wrap frames. The grass
patch's green channel drops from 85 at tick 12000 to 75, 61, 46 and 37 at the next
four samples, then stays at 37 at midnight. The still sequence leaves
frame-to-frame motion untested.
[Control sequence](../../artifacts/task-12/graded-transition.jpg),
[sunlight sequence](../../artifacts/task-12/sunlight-transition.jpg),
[fixed pixel patches](../../evidence/task-12/pixels.csv).

The cave keeps warm lantern pools and a darker ceiling recess. The sampled
floor near the right lantern has the same median sRGB codes, `(141, 139, 134)`,
in both frames. Several sidewalls brighten with legacy face shading disabled.
The dark ceiling patch drops from `(16, 14, 13)` to `(13, 9, 7)` under the
linear lightmap calculation. The night scene keeps visible landmarks, with
darker grass and a brighter brick side compared with the graded control.
These changes are included in the measured pack delta.

## Performance

Four fresh sessions ran graded, sunlight, sunlight, graded. Each session
profiled daylight, sunset, forest and cave after the fixed 20-second warm-up.
The native F3+L profiles contain 281,008 valid CPU render-loop samples over
9.995–10.001 seconds per run. The mean delta compares the average of the two
per-run mean durations per mode. [Per-run timings and hashes](../../evidence/task-12/runs.csv).

| Preset | Graded loop FPS | Sunlight loop FPS | Mean loop change | Graded p95 (ms) | Sunlight p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Daylight | 1,779–1,780 | 1,768–1,775 | +0.00243 ms (+0.44%) | 1.048–1.090 | 0.990–1.076 |
| Sunset | 1,659–1,682 | 1,683–1,694 | −0.00627 ms (−1.06%) | 1.113–1.137 | 1.109–1.122 |
| Forest | 1,772–1,780 | 1,763–1,765 | +0.00377 ms (+0.67%) | 1.005–1.135 | 1.033–1.102 |
| Cave | 1,807–1,811 | 1,791–1,793 | +0.00521 ms (+0.95%) | 1.016–1.045 | 1.005–1.057 |

Mean duration rose slightly in daylight, forest and cave and fell in sunset.
The p95 repeat ranges overlap in all four scenes. This is the full pack delta
with the native CPU profiler active, including waits and the legacy shading
change. TASK-26 covers directional sunlight in the grouped terrain
comparison. GPU timing for sunlight alone and display cadence remain
unmeasured. [TASK-26 terrain coverage](effect_costs.md#coverage-and-limits).

## Handoff

All eight expanded shader pairs linked in glslangValidator. The tested Iris beta
loaded the expected pack and RGBA16F Overworld pipeline in every session.
GenshinShaderDev stopped after all four world saves. Its world lock was released,
five original settings files and the installed scene datapack matched their
original bytes, and both temporary shaderpacks were removed.

Raw native frames, profile ZIPs, CSVs, client logs, settings and tested shader
snapshots are under `artifacts/task-12/`. The TASK-13 control is
`artifacts/task-12/variants/sunlight/shaders/`. Preserve this directory with the
developer handoff. [Replay commands](../../evidence/task-12/commands.txt),
[validation results](../../evidence/task-12/verification.txt),
[shader manifest](../../evidence/task-12/pack.sha256).

The TASK-12 sunlight checks cover fixed views of plains materials and a
stepped time sweep. TASK-22 later smoke-tested the shared terrain pipeline
in the Nether and End. TASK-23 recorded clear-day motion in the integrated
pack. Neither comparison isolates the TASK-12 sunlight term. Specialized
draw parity remains open. [Lighting and dimensions](lighting_dimensions.md),
[motion report](anti_aliasing.md), [current handoff](../STATUS.md).
