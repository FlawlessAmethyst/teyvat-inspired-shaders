# TASK-22 — Night, caves, artificial lighting and dimensions

## Shader behavior

The terrain vertex program computes a neutral fill of up to 0.024 in
scene-linear illumination. It fades with the product of the existing daylight
ramp and local skylight, and tapers from about block-light level 1.5 to 11.7.
Surface albedo and combined vertex AO multiply the fill in the fragment
shader. The same terrain varying carries the RGB lightmap scale and the new
scalar. This adds no pass, buffer, texture lookup or shadow lookup.

For terrain material ID 10004, low light reduces the decoded lightmap scale by
up to 32%. The mapping covers selected vanilla torches, lanterns, glow blocks
and lit redstone lamps. The adjustment works on the source model. Adjacent
terrain continues to use the engine's block-light levels. The engine's
lightmap coordinates supply both levels in the established vertex path.
[Iris lightmap matrix](https://shaders.properties/current/reference/uniforms/matrices/#gl_texturematrix1).

Iris reports skylight and ceilings at the dimension level. Overworld caves
therefore get the low-light fill based on their local lightmap levels. The
Nether and End use the engine lightmap with a unit fill scale and bypass the
custom terrain sun, skylight tint, neutral fill and lamp adjustment. The
global display grade still applies. [Iris dimension uniforms](https://shaders.properties/current/reference/uniforms/biome/).

## Capture conditions

GenshinShaderDev, Prism Flatpak 11.1.1, Minecraft 1.21.1, NeoForge 21.1.265,
Iris 1.8.14-beta.1+mc1.21.1 and Sodium 0.8.13+mc1.21.1. CachyOS, AMD Ryzen
9 9950X, NVIDIA RTX 4080 SUPER, OpenGL 4.6.0, NVIDIA 580.196.07 and Java
21.0.7. Native F2 captures use 2560×1440, sRGB, FOV 70°, render distance
12 chunks, simulation distance 8, brightness 0.5, Unlimited FPS
(`maxFps:260`), VSync off and hidden HUD.
[Baseline settings](baseline.md#capture-conditions), [environment](../minecraft-environment.md).

The daylight, night and lantern cave reuse the exact TASK-03 cameras. The
disposable copy adds a sealed lamp room and a separate unlit room with steps
and dark materials. The Nether and End use fixed first-person cameras over
invisible barrier anchors. After the End, the replay returns to the same
Overworld daylight camera. Each of the three modes has eight accepted native
captures, including that return view. [Fixture](../../evidence/task-22/build.mcfunction),
[added presets](../../evidence/task-22/presets.json),
[replay](../../evidence/task-22/commands.txt).

## Visual review

In the clear midnight view, the grass and wall gain definition while the
trees still read as dark silhouettes against the blue sky. The candidate
raises the grass patch from 32.5 to 37.7 and the stone wall from 43.2 to
49.5 in mean display-encoded luma on the 0–255 scale. The same grass and
wall RGB crops match TASK-21 byte for byte in the clear midday view.

In the lantern cave, the ceiling recess rises from 14.2 to 24.5 mean luma.
The floor patch next to the left lantern changes from 125.1 to 126.4. The
two warm pools remain distinct from the cooler foreground and the texture
in the back corner is easier to read.

In the unlit room, the steps and floor joints become distinguishable. Mean
luma on the step faces rises from 8.3 to 22.5. The deepslate wall remains
dark at 6.5 mean luma, up from 1.8, with some brick detail now visible.

In the lamp room, the 99th-percentile peak channel drops from 232 to 219
on the sea lantern, 236 to 226 on glowstone, and 238 to 228 on shroomlight.
The nearby wall changes from 138.9 to 135.9 mean luma and retains its stone
texture. The sea lantern center remains naturally uniform and the soul
lantern still casts a neutral-to-warm pool through the vanilla lightmap.
The light color of adjacent terrain follows that lightmap, so source-specific
colored illumination is outside this implementation. [Pixel patches](../../evidence/task-22/pixels.csv).

[Night](../../artifacts/task-22/night.jpg), [lantern cave](../../artifacts/task-22/cave.jpg),
[unlit steps](../../artifacts/task-22/unlit.jpg), and [lamp room](../../artifacts/task-22/lamps.jpg).

## Dimensions

The candidate opened the Nether, moved to the End and returned to the
Overworld through the normal Iris dimension pipeline rebuilds. The daylight
grass and stone patches match the pre-transition captures byte for byte.

| Condition | Observed in the installed client | Remaining gap |
| --- | --- | --- |
| Nether wastes over a lava basin | Netherrack, fire, glowstone and the lava surface render. The shared lightmap keeps the warm palette and the cavern has dark recesses. Lava flow varies across sessions. | Distant surfaces can be hard to separate. The pack skips its procedural air haze in the Nether. Other Nether biomes, lava immersion and portal overlays remain unverified. |
| End main island | End stone, obsidian pillars, crystals and the purple-black sky render. The island edge remains distinct. | Obsidian is very dark and distant pillars lack the stronger atmospheric fade visible with Sodium shaders off. The dragon fight, gateway travel, beam and portal effects, and outer islands remain unverified. |
| Return to the Overworld | The pipeline rebuilt and the original daylight view rendered after the return. | The replay uses command teleports. Portal travel, reentry while submerged and custom dimensions remain unverified. |

The lamp limiter was visually checked on the fixture's lantern, soul
lantern, glowstone, sea lantern and shroomlight models. The other mapped
sources, the lit/off redstone lamp transition, modded emissives, held
items and block-entity glow need their own checks. Night vision, darkness,
blindness and extreme brightness settings also remain unverified.

[Nether comparison](../../artifacts/task-22/nether.jpg), [End comparison](../../artifacts/task-22/end.jpg).

## Performance

The native F3+L comparison uses two fresh client sessions per mode. Each
session records night followed by cave. The preset and video settings match
across all three modes. The incremental control is the exact
TASK-21 shader tree. Sodium with Iris shaders disabled supplies the
shaders-off baseline. Mean and percentile values describe the instrumented
CPU client loop. [Raw profile index](../../evidence/task-22/runs.csv),
[baseline method](baseline.md).

| Scene | Sodium, shaders off (ms) | TASK-21 mean (ms) | TASK-22 mean (ms) | TASK-22 minus TASK-21 (ms) |
| --- | ---: | ---: | ---: | ---: |
| Night | 0.258974 | 0.629840 | 0.634410 | +0.004569 |
| Cave | 0.241115 | 0.593329 | 0.591082 | −0.002247 |

Means average the two runs in each mode. The individual night differences
were +0.005373 and +0.003765 ms. The cave differences were −0.001631 and
−0.002862 ms. The directions agree across repeats for each scene. With two
sessions per mode, treat the deltas as descriptive measurements for the
fixed fixtures. TASK-22 p95 ranges were 1.059–1.158 ms at night and
1.032–1.112 ms in the cave.

The fixed cameras and peaceful fixture leave moving gameplay and combat
outside this validation. TASK-26 measured the grouped terrain lighting and
tint path with shadows disabled, using a grove camera and a synthetic quad.
It leaves the individual low-light fill and lamp terms, full-client GPU
time and display cadence unmeasured.
[TASK-26 terrain lighting coverage](effect_costs.md#coverage-and-limits).

## Handoff

TASK-23 used `artifacts/task-22/shaders/` as its control for clear-day
motion and retained the same shader source after deferring AA. TASK-28
tested cave entry on foot and repeated the dimension sequence on the
fog-tuned pack. Two static Overworld terrain patches matched after the
return. Portal travel and overlays remain untested.
[Motion report](anti_aliasing.md), [runtime regression](regression_report.md#runtime-results).
Retain the control and candidate source trees, native captures, raw profiles,
client logs, restored-settings proof and disposable world with the
[reviewed evidence](../../evidence/task-22/README.md).
