# Known gaps

These findings apply to the [retained shader source](../evidence/task-25/fog-pack.sha256)
on the [tested development stack](testing/compatibility_notes.md#tested-development-stack).
Use the [runtime replay](HANDOFF.md#repeat-the-runtime-checks) to recreate the
fixtures. The [TASK-28 regression report](testing/regression_report.md#prioritized-open-bugs)
contains the original bug priorities and captures.

## Reproducible defects

| Priority | Reproduce and inspect | Source to investigate |
| --- | --- | --- |
| P2 · Foliage and shoreline aliasing | From the forest preset walk north and inspect the sky-facing leaf holes. From the open-water preset set yaw 150°, pitch 12°, strafe right and watch the diagonal bank. The stone strafe shows moving steps too. Use the native frames and motion clips at 1440p. [Leaf crop and clips](testing/regression_report.md#runtime-results) | [Terrain sampling](../shaderpack/shaders/lib/geometry_fragment.glsl) and [final draw](../shaderpack/shaders/final.fsh). TASK-23's spatial filter softened fine detail and left shimmer at an additional 0.0091–0.0097 ms per isolated final draw. [AA trial](testing/anti_aliasing.md) |
| P3 · Abrupt waterline color switch | In the stepped basin, start at (1027.5, 179, 1037.5), yaw −90°, pitch 5°. Hold jump to rise through the surface, then sneak to descend. Watch the sky and the same basin surfaces through the switch. The replay logs eye block transitions as IN → OUT → IN. [Crossing clip](../artifacts/task-28/clips/waterline.mp4) | [Eye-medium fog selection](../shaderpack/shaders/lib/geometry_vertex.glsl), [water underside](../shaderpack/shaders/lib/water.glsl) and [sky gating](../shaderpack/shaders/gbuffers_skybasic.fsh) |
| P3 · Low distant contrast in the Nether and End | Use the Nether wastes and End main island cameras in the TASK-22 preset file. Inspect far Nether recesses and obsidian pillars. The TASK-28 replay visits both and returns to the Overworld. [Cameras](../evidence/task-22/presets.json), [dimension sheet](../artifacts/task-28/review/dimensions-interiors.jpg) | [Terrain dimension gate and lightmap fallback](../shaderpack/shaders/lib/terrain_lighting.glsl), [shared fog setup](../shaderpack/shaders/lib/geometry_vertex.glsl) |

## Remaining visual and performance work

- **Style.** The clear-air fog follow-up recovered the opposite
  hillside while keeping distant haze. The single cloud layer still
  gives flatter cloud forms than the reference. Overcast values, water
  hue, canopy variation and dark outdoor detail remain the next visual
  comparisons to revisit. Asset shapes, surface textures and scene art
  constrain what the shader can match. [Matched visual review](testing/visual_comparison.md#gaps-found-in-the-original-comparison).
- **Deferred effects.** A compact arithmetic sun halo in the existing
  sky draw is a scoped optional trial. Scene-wide bloom would need
  downsample, blur and composite resources with a measured gain.
  Separate vertex AO would need proof of the Iris AO input contract
  and comparison against the existing combined tint. Temporal AA,
  upscaling and vegetation motion were deferred. Screen-space AO,
  geometry reflections and refraction were rejected in the effects triage.
  [Candidate gates and dispositions](architecture/deferred_effects.md#dispositions-and-expected-gpu-work).
- **Performance.** Whole-client GPU frame time, in-client caster time,
  the water pre-hand depth copy and display presentation intervals
  remain unmeasured. Offscreen query results characterize bounded
  workloads and the CPU profiles characterize the synthetic scenes on
  the tested system. Representative gameplay and lower-end GPU cost are
  open. [Effect timing coverage](testing/effect_costs.md#coverage-and-limits).
- **Runtime and compatibility.** Portal travel and overlays, custom
  dimensions, lava immersion, sustained swimming, flowing and
  waterlogged edges, multiplayer and modded materials remain untested.
  The fixed-camera rain samples can miss short transients. Other
  game/loader/mod combinations and GPUs need separate live validation.
  [Runtime coverage](testing/regression_report.md), [untested combinations](testing/compatibility_notes.md#untested-combinations).

## Starter tasks

The full runtime replay verifies the accepted manifest before staging.
Use it to capture the control. Stage modified shaders separately and
reuse the linked fixture cameras and conditions for trial captures.
[Baseline and replay workflow](HANDOFF.md#repeat-the-runtime-checks).

1. **Compare a bounded dimension fill.** Copy the accepted build and
   adjust the fallback lightmap gain in the dark range for the Nether
   and End. Compare the two fixed dimension views and the Overworld
   daylight return, cave and night controls. Preserve nearby block-light
   separation and require both static daylight return patches to match.
   [Replay and reviewer](../evidence/task-28/README.md).
2. **Isolate the waterline discontinuity.** Record a baseline up/down
   crossing and build temporary one-change variants of the fog and
   underside branches. Compare paired frames around the IN/OUT log
   markers, with the above-water shallows and submerged floor as
   controls. Repeat at the glass/hand overlap before adopting a change
   to the depth path. [Water depth diagnostic](testing/water.md),
   [crossing evidence](../evidence/task-28/README.md).
3. **Profile a restrained sun halo.** Stage a sky-only trial using the
   existing sun-facing, cloud and rain terms. Compare clear daylight,
   dusk, night and rain at fixed cameras. Reuse the paired offscreen
   sky timer to measure the added draw cost before adopting it.
   [Trial scope and acceptance checks](architecture/deferred_effects.md#optional-follow-up--task-24a-sun-halo).

For motion work, keep TASK-23's original and spatial-filter recordings
as controls. Use paired movement at the same resolution and camera,
including a static detail check and a GPU timing. [AA evidence and replay](../evidence/task-23/README.md).
