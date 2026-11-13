# Basic terrain shadows

TASK-16, 2026-11-12. The shadow candidate adds a bounded directional depth
map to the TASK-15 fog pack. The incremental control is the
[verified TASK-15 fog snapshot](fog.md#handoff). Sodium with shaders off is the
total-cost reference.

## Shader behavior

The [shadow module](../../shaderpack/shaders/lib/shadows.glsl) requests a
1024² orthographic map with a 64-block terrain cull distance. The
[solid program](../../shaderpack/shaders/shadow_solid.fsh) writes depth
without an atlas read. The [base shadow program](../../shaderpack/shaders/shadow.fsh)
tests vertex alpha and samples cutout alpha from the atlas base level. The
caster programs request no shadow color attachment. The pack requests block-entity casting and
disables ordinary entity, player and translucent-terrain casting.
[Iris shadow programs](https://shaders.properties/current/reference/programs/shadow/),
[Iris draw controls](https://shaders.properties/current/reference/shadersproperties/ordering/).

Terrain vertices transform into the same light projection used by Iris.
One bilinear depth comparison lookup covers the four neighboring texels.
The receiver estimates a depth bias from the face-to-sun angle and the
0.125-block map texel footprint. The slope contribution is capped and the
receiver fades at grazing angles and low sun elevations. Shadow influence
tapers over 48–60 blocks in view distance and also fades near the projection's
XY edges. Iris's camera snap interval is 1/16 block. The fragment skips
the lookup where the weight or direct sunlight is zero. Shadow visibility
scales the direct sun term before distance fog. Lightmap fill and ambient
occlusion continue to supply contrast inside the shadow.
[Iris shadow sampler](https://shaders.properties/current/reference/buffers/shadowtex/),
[Iris shadow interval](https://shaders.properties/current/reference/constants/shadowintervalsize/).

## Capture conditions

GenshinShaderDev, Minecraft 1.21.1, NeoForge 21.1.265,
Iris 1.8.14-beta.1 and Sodium 0.8.13 on CachyOS with the Ryzen 9 9950X and
GeForce RTX 4080 SUPER. Use the [TASK-10 settings](baseline.md#capture-conditions)
with 2560×1440, FOV 70°, 12/8 render/simulation distances, Unlimited FPS,
VSync off and the HUD hidden. Each native capture and F3+L profile follows
a 20-second focused warm-up. All three modes use the same copy of the TASK-03
world and locked camera, time and weather.

The developer-only [fixture](../../evidence/task-16/fixture.mcfunction) adds
a smooth-stone pad with a chest, a suspended oak leaf block, a stone pillar
and a glass column. A second lane extends east with pillars at increasing
distances. The fixture and camera functions are installed only in
`TASK-16 Shadow Scenes`, a copy of the original test world.

| View | Teleport XYZ | Yaw / pitch | Game time | Coverage |
| --- | --- | --- | --- | --- |
| Contact | 1009.5, 184, 1033.5 | -90° / 18° | 4900 | Isolated caster and contact bias |
| Sunset | 1026.5, 184, 1033.5 | 90° / 17° | 10900 | Opposite side of the pad, low-angle light |
| Range | 1031.5, 184, 1041.5 | -90° / 4° | 4900 | Range fade over the pillar lane |
| Forest | 1018.5, 184, 1005.5 | 180° / 5° | 6000 | Layered canopy and ground shadows |
| Cave, night, open water | [TASK-03 presets](scenes.md#camera-presets) | | | Receiver scope and low-light regressions |

All views use clear weather. The player settles to the inherited preset
height before capture. Forest and sunset are the fixed profile scenes.

## Visual review

The matched low-angle pad separates the caster footprints from the
existing lightmap and AO. The pillar shadow meets its base, the chest
produces a distinct offset silhouette, and the clear-glass column casts
thin strokes from its opaque frame. The clear panes leave gaps in the
shadow. The forest still has legible grass detail under the canopies.
[Sunset comparison](../../artifacts/task-16/sunset-row.jpg),
[contact comparison](../../artifacts/task-16/contact-row.jpg),
[forest comparison](../../artifacts/task-16/forest-row.jpg).

The trial used the atlas's implicit mip selection. Its isolated oak leaf
produced a nearly filled footprint. Sampling level zero exposes several
holes and a broken outer edge in the matched final capture. The comparison
image amplifies the absolute RGB difference from the fog control by 4×.
Black regions show where the two captures match.
[Leaf alpha comparison](../../artifacts/task-16/leaf-alpha.jpg).

The range lane has a strong near footprint, a weaker footprint in the
fade zone and no added shadow at the far pillar beyond 60 blocks.
The strip stays evenly lit outside the caster footprints. This tests the
combined range and projection-edge fade on a flat lane. The far footprint,
unoccluded foreground grass and night foreground patches match the fog
control pixel-for-pixel. The forest canopy patch darkens by 32.8 levels in
mean 8-bit luma and keeps visible texture. The water comparison preserves
the original material route. Its surface animation is free-running.
[Range comparison](../../artifacts/task-16/range-detail.jpg),
[open-water comparison](../../artifacts/task-16/open-water-row.jpg),
[pixel crops and deltas](../../evidence/task-16/pixels.csv).

The cave retains both lantern pools. Across two captures per mode, the near
floor patch is about four 8-bit luma levels darker with shadows. A patch by
the right lantern varies by about one level across modes. The floor change
is consistent with the map attenuating residual directional light near the
entrance. [Cave comparison](../../artifacts/task-16/cave-row.jpg).

The contact camera moved sideways in ten 1/16-block steps with fixed yaw
and pitch. All 11 frames were distinct. The pillar contact and leaf footprint
stay attached as the camera moves across the map's snap grid. TASK-23's
clear-day ground paths showed no obvious shadow flash. TASK-28 repeated
the forest walk and added a camera turn with the retained pack. Visible
tree shadows stayed attached, with no large flash or dropout apparent
in the clips. Fine shadow-edge jitter remains unquantified.
[Camera steps](../../artifacts/task-16/motion-strip.jpg),
[final camera position](../../artifacts/task-16/shadows-motion/motion-debug.png),
[motion report](anti_aliasing.md#visual-review),
[retained-pack runtime review](regression_report.md#runtime-results).

The sunset overlay reports `BE: 0` in Iris. The offset chest silhouette in
the matched renders establishes casting for this fixture. Other block-entity
types still need their own checks.
[Iris debug capture](../../artifacts/task-16/shadows-motion/shadow-debug.png).

## Performance

Six accepted sessions each recorded forest and sunset with Minecraft's
F3+L profiler. The order was Sodium, fog, shadows, shadows, fog, Sodium.
The first cutout trial and the interrupted fog session are excluded.
The second fog and Sodium sessions ran after work resumed. The fixed
camera, runtime, client settings and static image crops matched.

| Preset | Sodium mean (ms) | Fog mean (ms) | Shadows mean (ms) | Shadow delta | Fog p95 (ms) | Shadows p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Forest | 0.195 | 0.430 | 0.473 | +0.0432 ms (+10.0%) | 0.623–0.705 | 0.700–0.730 |
| Sunset | 0.213 | 0.467 | 0.509 | +0.0426 ms (+9.1%) | 0.684–0.740 | 0.742–0.774 |

Each mean averages the two per-run means. The 12 profiles contain 362,699
CPU client-loop samples over 9.993–10.000 seconds per recording. Forest
throughput was 5,016–5,074 loops/s in Sodium, 2,291–2,313 in fog and
2,084–2,098 with shadows. Sunset throughput was 4,601–4,651, 2,122–2,132 and
1,944–1,953 loops/s respectively. These are instrumented CPU timings.
[Raw archive and timing index](../../evidence/task-16/runs.csv).

TASK-26 disabled the caster pass and receiver together. The full pack
added 0.045–0.093 ms per client loop across the grove and valley repeats.
An offscreen test with a prefilled map measured 0.0050–0.0056 ms of
receiver work per eligible foliage draw. In-client caster and receiver
GPU durations and display presentation cadence remain unmeasured.
[TASK-26 shadow comparisons and limits](effect_costs.md#coverage-and-limits).

TASK-27 compared the 1024² map with a 768² map. The smaller map saved
0.0062–0.0083 ms per synthetic clear, caster draw and shadow depth copy.
The in-client mean improved slightly in the grove and rain, with mixed
valley results. The fixed captures showed softer leaf and glass-frame cast
shadows, so the accepted pack retains 1024². In-client GPU time remains
unmeasured. TASK-28 motion coverage uses the retained map.
[Optimization results and matched crops](optimization.md).

## Handoff

TASK-17 used the tested shadow snapshot as its starting point. Verify
the snapshot from the repository root.

```bash
sed 's|shaderpack/shaders/|artifacts/task-16/variants/shadows/shaders/|' \
    evidence/task-16/pack.sha256 | sha256sum -c -
```

Keep the [replay commands](../../evidence/task-16/commands.txt) and the
native PNGs, copied world, shader snapshots, logs, profiler ZIPs and raw CSVs
under `artifacts/task-16/`. The client stopped after a successful save.
All five settings files were restored byte-for-byte, the temporary packs
were removed and all 75 original world file hashes matched.
[Verification record](../../evidence/task-16/verification.txt).

The [TASK-17 checkpoint](prototype_checkpoint.md) used the verified snapshot
in all seven [TASK-03 presets](scenes.md#camera-presets) with a matched
shaders-off control. The shadow fixture remains the targeted comparison.
