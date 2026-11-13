# Terrain ambient lighting — TASK-13

**DONE**, 2026-11-12. Validation covers the installed Iris beta in the
GenshinShaderDev Overworld.

## Shader behavior

In the TASK-13 snapshot, the terrain lighting module uses the existing
per-vertex sky and block light levels to tint the lightmap fill. Sun elevation
blends cool daylight shade toward a bluer night response.
The tint fades as direct sun or block light increases. It is zero where the
sky level is zero, so fully enclosed terrain retains the lightmap's local
colors and darkness. The tint scales the existing fill multiplicatively.
TASK-22 later adds a neutral low-light fill and bounds selected lamp faces.
[Current terrain source](../../shaderpack/shaders/lib/terrain_lighting.glsl),
[lighting and dimension report](lighting_dimensions.md).

The fragment calculation is one decoded lightmap sample times the interpolated
RGB fill scale, plus the existing direct RGB term. The effect replaces the
four-component terrain lighting varying with two RGB varyings. The tint math
runs at vertices. The atlas and lightmap reads, combined vertex AO, render
target and final grade serve both lighting terms. Skylight and AO supply the
occlusion cues in this snapshot. TASK-16 later adds cast shadows to the
direct-light term. [Shadow report](shadows.md).

R2's cool crate faces in daylight and R6/R8's blue surroundings beside warm
lamps guided the palette. The cave is an interior regression check.
[Reference samples](../../artifacts/task-13/reference-strip.jpg),
[reference provenance and S2 rubric](../research/style_targets.md#s2--warm-light-cool-fill-and-legible-shadows).

## Capture conditions

The control is a hash-verified snapshot of TASK-12 sunlight. The two packs use
the same fixed TASK-03 cameras, clear weather and vanilla textures. Forest and
cave are at tick 6000 and night is at 18000. The daylight and sunset guards
are at 6000 and 12000. Captures are native 2560×1440 with hidden HUD, FOV 70,
render and simulation distances of 12 and 8 chunks, Unlimited FPS and VSync off.
[Scene presets](scenes.md).

GenshinShaderDev ran on CachyOS with a Ryzen 9 9950X, RTX 4080 SUPER,
OpenGL 4.6.0 and NVIDIA 580.196.07. The client is Minecraft 1.21.1,
NeoForge 21.1.265, Iris 1.8.14-beta.1, Sodium 0.8.13 and Java 21.0.7
in Prism Launcher Flatpak. The profile validator checks its captures against
the TASK-10 runtime, mod hashes, client options and scene presets.
[Sodium baseline and method](baseline.md).

## Visual review

- In the forest, the stone patch shifts from median sRGB `(113, 113, 113)`
  to `(108, 118, 128)`. Oak bark and leaf cutouts stay legible. The sampled
  grass beside the trunk remains slightly darker than the open foreground
  grass. [Forest comparison](../../artifacts/task-13/forest-row.png).
- Daylight grass holds at `(99, 134, 31)` while the stone shifts toward
  blue-gray. At sunset the shaded wall shifts from `(89, 89, 100)` to
  `(84, 93, 112)` and the doorway recess holds at `(40, 33, 29)`.
  [Daylight comparison](../../artifacts/task-13/daylight-row.png),
  [sunset comparison](../../artifacts/task-13/sunset-row.png).
- At night, the brick wall shifts from `(41, 40, 72)` to `(35, 40, 82)`
  and the grass remains dim with visible texture. The same grass crop has a
  median green code of 37 at night and 134 in daylight.
  [Night comparison](../../artifacts/task-13/night-row.png).
- The cave retains the warm lantern pools and dark ceiling recess. The recess
  goes from `(13, 9, 7)` to `(12, 9, 7)`. The floor near the lantern varies
  by six blue codes between the ambient profile's before and after images,
  the same magnitude as the two modes' native-frame difference. The captures
  leave exact lamp-level changes unresolved because flicker is free-running.
  [Cave comparison](../../artifacts/task-13/cave-row.png).

[Paired native-frame contact sheet](../../artifacts/task-13/comparison.jpg),
[all fixed sRGB patches](../../evidence/task-13/pixels.csv).

## Performance

Each fresh session ran forest, cave and night in that order. Sessions ran
sunlight, ambient, ambient, sunlight. Each profile used the same 20-second
focused warm-up and native F3+L CPU profiler. The 12 profiles contain 280,821
valid samples over 9.996–10.000 seconds per run. The delta compares the average
of the two per-run mean loop durations per mode.
[Per-run timing distributions and hashes](../../evidence/task-13/runs.csv).

| Preset | Sunlight loop FPS | Ambient loop FPS | Mean loop delta | Sunlight p95 (ms) | Ambient p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forest | 2,327 | 2,291–2,329 | +0.00308 ms (+0.72%) | 0.697–0.708 | 0.686–0.731 |
| Cave | 2,388–2,395 | 2,339–2,375 | +0.00612 ms (+1.48%) | 0.670–0.703 | 0.681–0.714 |
| Night | 2,313–2,337 | 2,330–2,334 | −0.00132 ms (−0.31%) | 0.706–0.717 | 0.691–0.692 |

Cave mean loop duration rose in both ambient repeats. The forest and night
mean ranges overlap, as do forest and cave p95 ranges. The night p95 was
lower in both ambient repeats. The profiler records CPU client loops
including waits. TASK-26 covers ambient fill in the grouped terrain
comparison. GPU timing for ambient fill alone and display cadence remain
unmeasured. [TASK-26 terrain coverage](effect_costs.md#coverage-and-limits).

The historical TASK-10 Sodium shaders-off runs at the same capture settings
averaged 0.263–0.266 ms in forest and 0.244–0.254 ms in cave. The earlier
TASK-12 sunlight runs also differ from this session's sunlight runs, so
the table uses fresh controls for the ambient delta.
[Sodium runs](../../evidence/task-10/runs.csv),
[earlier sunlight runs](../../evidence/task-12/runs.csv).

## Handoff

All eight expanded GLSL program pairs linked. All four sessions loaded the
expected pack, rendered the fixed scenes and saved the dedicated world
normally. GenshinShaderDev stopped and released the world lock. Five settings
files were restored byte-for-byte, the installed scene datapack matched its
original bytes, and both temporary packs were removed.

Keep the native PNGs, profile ZIPs and converted CSVs, client logs, settings
and tested shader snapshots in `artifacts/task-13/`. The snapshot at
`artifacts/task-13/variants/ambient/shaders/` is the control for TASK-14.
Verify that snapshot from the repository root before staging it.

```bash
sed 's|  shaderpack/shaders/|  artifacts/task-13/variants/ambient/shaders/|' \
    evidence/task-13/pack.sha256 | sha256sum -c -
```

Reproducing the TASK-13 comparison also uses the TASK-10 neutral daylight
reference recording, the TASK-12 sunlight snapshot and world-list capture,
and the TASK-04 frames used for the reference strip.
[Replay commands](../../evidence/task-13/commands.txt),
[shader manifest](../../evidence/task-13/pack.sha256),
[verification](../../evidence/task-13/verification.txt).

The TASK-13 fill captures cover fixed times and plains materials. TASK-20
adds matched clear-day canopy views in plains and jungle biomes. TASK-21
reviews the combined terrain lighting through midday rain onset and
clearing. TASK-22 checks the current fill in midnight and enclosed
interiors, and verifies that the Nether and End render through the shared
lightmap path. Mixed outdoor block lighting and isolated live fill remain
unverified. [Vegetation report](vegetation.md), [weather report](weather.md),
[lighting and dimension report](lighting_dimensions.md).
