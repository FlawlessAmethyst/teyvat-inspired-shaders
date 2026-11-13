# TASK-27 — Targeted performance optimization

## Trials

The control is the fog-tuned TASK-25 pack used for TASK-26. Shader variants
were built from the verified control in an ignored artifact directory.

| Trial | Change | Expected effect |
| --- | --- | --- |
| Shadow map | 1024² → 768², with the receiver bias derived from the new texel size | 43.75% fewer texels to allocate, clear and copy. The cutout draw covers fewer depth texels at equal projected coverage. The 64-block caster distance, 48–60 block receiver fade, one hardware-filtered lookup and base-level atlas alpha test are the same. |
| Fog arithmetic | Factor the nested desaturation and horizon interpolation into one weighted sum of the original color, its luma and the horizon | Share the grayscale contribution across RGB channels. The two forms are equivalent in real arithmetic. The existing clear-air, rain, twilight and underwater logic is retained in the trial. |

The shadow map has a 0.167-block texel pitch at 768², up from 0.125.
The corresponding risk is broader bias and filtering on close contact and
thin cutout shadows. The fog rewrite can change floating-point rounding
and the GPU compiler's generated instructions.
[Trial patches and baseline manifest](../../evidence/task-27/README.md).

## Measurement method

- The runtime is GenshinShaderDev on CachyOS 7.3.3-1-cachyos with Ryzen 9
  9950X, RTX 4080 SUPER and NVIDIA 580.196.07. The client uses Minecraft 1.21.1,
  NeoForge 21.1.265, Iris 1.8.14-beta.1+mc1.21.1 and Sodium
  0.8.13+mc1.21.1. Fixed views use native 2560×1440, 70° FOV, 12/8
  chunk render/simulation distance, VSync off and Unlimited FPS
  (`maxFps:260`). [Baseline settings](baseline.md#capture-conditions).
- Two fresh Sodium sessions bracket two shader sessions. The first
  shader session runs control, shadow, fog. The second reverses the
  order. Each build uses the original TASK-25 valley, grove and settled
  rain views. Each run follows the camera/time/weather
  acknowledgment and a 20-second focused warm-up. Minecraft's F3+L
  archive gives instrumented CPU client-loop timings in milliseconds
  and loops per second. The TASK-16 pad and range lane were added
  during the first full-pack visual batch, after its three profiles.
  They were already present throughout the reversed shader session.
  The pad lies behind the grove camera and within the caster distance.
  The first-round grove comparison may include a change in shadow
  submission from the fixture.
- Offscreen GPU queries run in independent NVIDIA EGL contexts on
  the same driver. Each test uses 32 paired batches of 64 iterations
  after warm-up, alternating which build goes first. The synthetic
  shadow pass clears a depth-only framebuffer, renders a full-map
  solid floor plus a patterned alpha-cutout card, and copies depth
  with `glCopyImageSubData`. Three depth probes at each resolution
  verify solid depth, a hole and solid cutout coverage in both textures.
  The fog case reuses the TASK-26 RGBA16F geometry timer and its
  near, distant clear, dusk, rain and submerged probes.
- Native contact, sunset and range captures retest the TASK-16
  smooth-stone fixture. Valley, grove and rain have window captures
  at both ends of each profile. The fog trial additionally uses
  native dusk and ridges captures. Free-running cloud motion,
  precipitation and mobs can differ between frames.

## Visual results

The 768² map preserves the pillar's contact with the ground, the chest
silhouette, the near-to-far fade and the grove's tree shadows. The
unoccluded contact pad and far range crop are pixel-identical to the
control. The suspended leaf footprint gains softer edges and different
hole shapes. Its contact crop changes by 6.4 levels per RGB channel on
average, with a 95th-percentile absolute difference of 34 levels. The
glass-frame crop changes by 3.2 levels on average. These differences
are concentrated in the cast footprints. Continuous shadow-edge
motion was outside this fixed-camera check.
[Contact detail](../../artifacts/task-27/comparisons/shadow-contact-detail.jpg),
[cutouts](../../artifacts/task-27/comparisons/shadow-cutouts.jpg),
[range detail](../../artifacts/task-27/comparisons/shadow-fade.jpg),
[grove](../../artifacts/task-27/comparisons/shadow-grove.jpg).

The fog trial preserves the opposite hillside, ridge separation, pale
rain silhouettes and sunward dusk tint in the reviewed frames. In the
dusk crop, the average channel difference was 0.13 8-bit levels. The
valley and rain differences also include cloud, precipitation and
other animation.
[Valley](../../artifacts/task-27/comparisons/fog-valley.jpg),
[ridges](../../artifacts/task-27/comparisons/fog-ridges.jpg),
[rain](../../artifacts/task-27/comparisons/fog-rain.jpg),
[dusk](../../artifacts/task-27/comparisons/fog-dusk.jpg),
[pixel index](../../evidence/task-27/pixels.csv).

## Client-loop results

The two values in each cell are rounds 01 and 02. Deltas are trial
minus the full shader control in the same round, in milliseconds per
instrumented client loop.

| Scene | Full pack mean (ms) | 768² mean (ms) | 768² delta (ms) | Fog mean (ms) | Fog delta (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Valley | 0.61053 / 0.61491 | 0.61245 / 0.60950 | +0.00192 / −0.00541 | 0.61673 / 0.62235 | +0.00620 / +0.00744 |
| Grove | 0.48365 / 0.47800 | 0.47503 / 0.47558 | −0.00862 / −0.00242 | 0.48383 / 0.48273 | +0.00018 / +0.00473 |
| Settled rain | 0.67679 / 0.68246 | 0.67393 / 0.67489 | −0.00286 / −0.00756 | 0.67368 / 0.68541 | −0.00311 / +0.00295 |

The smaller map improved the mean in both grove and rain repeats, by
about 0.4–1.8%. The valley changed sign. Its p95 improved in every
first-round scene and rose in every second-round scene. The fog
trial increased the valley mean in both rounds. The full-pack shadow
CPU profiler section remained present in every shader run. Reordering,
GPU clocks, client waits and free-running effects contribute to
variation. [Raw profile index and tails](../../evidence/task-27/runs.csv).

The 24 profiles contain 549,153 client-loop samples over 9.995–10.000 seconds
per run. Shaders-off Sodium averaged 0.261–0.271 ms in the valley,
0.192–0.194 ms in the grove and 0.308–0.312 ms in rain. The matched
full-pack ranges were 0.611–0.615, 0.478–0.484 and 0.677–0.682 ms.
The accepted pack still carries that incremental Iris and shader cost on
these scenes.

## Offscreen GPU results

| Workload | Control median (ms), rounds 01 / 02 | Trial median (ms), rounds 01 / 02 | Median paired delta (ms), rounds 01 / 02 |
| --- | ---: | ---: | ---: |
| Shadow clear, solid and cutout draw, depth copy | 0.021872 / 0.018976 | 0.013616 / 0.012808 | −0.008280 / −0.006176 |
| Dusk fog draw | 0.028056 / 0.028280 | 0.028168 / 0.028216 | +0.000048 / −0.000112 |

The smaller map reduced the synthetic pass by about one third. Both
textures gave the expected solid, hole and cutout depth at each size.
The fog draw's largest absolute paired median difference was 0.000112 ms.
All sampled linear RGB fog probes matched. The shadow workload uses
two controlled draws and a depth copy. Actual world geometry, submission,
overdraw, receiver workload, in-client GPU frame time and presentation
cadence are outside these GPU measurements. The shadow depth copy here
is distinct from the pre-hand scene depth copy used by the water shader.
[Paired timing index](../../evidence/task-27/gpu-summary.csv),
[raw GPU results](../../artifacts/task-27/gpu/),
[water timing limits](water.md#performance).

## Decision and handoff

**DONE.** Discarded both trials after measurement. The smaller map's
isolated GPU savings and small live mean savings in the grove and rain
came with visibly softer leaf and glass cutout detail and an inconsistent
p95 across repeats. The fog rewrite preserved the tested appearance and
offscreen pixel probes, with no repeatable GPU improvement. The default
source matches the fog-tuned TASK-25 manifest byte for byte and retains
1024² shadows. Both proposed changes and their replay are retained for the
handoff. Projected clouds were outside the selected two hot paths.
[TASK-25 manifest](../../evidence/task-25/fog-pack.sha256),
[replay and raw evidence](../../evidence/task-27/README.md).

All four clients saved and exited. The log contains the known profiler
level-dump diagnostics. The archives completed and shader validation
found no shader compilation, link or pipeline fallback errors. The
five instance settings were restored and both source-world manifests
verified. TASK-28 ran the retained pack through camera motion, weather,
waterline, cave and dimension transitions.
[Verification record](../../evidence/task-27/verification.txt),
[TASK-28 runtime results](regression_report.md).
