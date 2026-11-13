# TASK-23 — Anti-aliasing and motion artifacts

**Decision — Defer shader anti-aliasing.** Keep the accepted TASK-22 path.
The spatial trial’s main benefit was smoother diagonal edges in stills.
Foliage shimmer persisted in motion and some fine texture detail softened.
The result gives too little visual benefit for four extra full-resolution
samples per pixel. Temporal accumulation and temporal upscaling stay deferred.

## Capture conditions

The accepted TASK-22 pack, a disposable spatial AA trial, and Sodium with
shaders off ran in the same disposable copy of the TASK-03 fixture. All
views use clear weather, fixed midday at tick 6000, vanilla textures,
2560×1440, FOV 70, four mip levels, render distance 12 and simulation
distance 8. The VSync setting was off and the FPS slider was at Unlimited
(`maxFps:260`). The tested client was Minecraft 1.21.1 with NeoForge
21.1.265, Iris 1.8.14-beta.1 and Sodium 0.8.13 on CachyOS with the NVIDIA
RTX 4080 SUPER, driver 580.196.07, and Ryzen 9 9950X. The camera starts come
from the TASK-03 presets, with the water view rotated toward the near bank.
[Environment](../minecraft-environment.md), [presets and replay](../../evidence/task-23/replay.py).

| Scene | Start `(x, y, z; yaw, pitch)` | Motion | Target |
| --- | --- | --- | --- |
| Daylight | `(1000.5, 184, 1036.5; 180°, 8°)` | Strafe right for 3 s | Stone-brick roofline, mortar and distant terrain silhouettes |
| Forest | `(1018.5, 184, 1005.5; 180°, 5°)` | Walk forward for 3 s | Oak cutouts against sky and shadows on grass |
| Open water | `(974.5, 183, 1020.5; 150°, 12°)` | Strafe right for 3 s | Oblique grass-to-water boundary and animated water |

Each mode has a native F2 still from the preset start and a separate KWin
window recording from that same start. The recordings use continuous player
movement, with the HUD hidden, and contain time before and after the key hold.
The nine 1440p clips contain 244–246 decoded frames each at 39.7–39.9
captured frames per second.
They align by scene and input, with independent camera and animation timing.
[Evidence index](../../evidence/task-23/README.md).

## Trial

The five-sample filter uses the center and four adjacent `colortex0` samples
inside the existing `final` pass. It detects local contrast in both axes and
blends toward the neighbors only at those transitions. That targets
one-pixel diagonal steps and isolated details while preserving long
axis-aligned edges. The filter blends the existing scene-linear color before
grading and sRGB encoding. It adds four color fetches per output pixel and
uses the existing attachment and final draw. Iris documents the final draw as
window-resolution output. The FXAA paper informed the local-contrast idea
only. The trial uses an original filter and a simpler sampling pattern.
[Iris final pass](https://shaders.properties/current/reference/programs/final/),
[NVIDIA FXAA white paper](https://developer.download.nvidia.com/assets/gamedev/files/sdk/11/FXAA_WhitePaper.pdf),
[trial source](../../evidence/task-23/spatial-aa.glsl).

## Visual review

| Scene | TASK-22 control | Five-sample trial |
| --- | --- | --- |
| Daylight | Fine steps on diagonal masonry edges and roof trim move across the pixel grid during the strafe. | Rounded some corners and softened some mortar detail. The roof and distant cutout edges still show moving steps. |
| Forest | Bright holes in the leaf silhouette change as the camera approaches. Leaf edges make the strongest visible shimmer in the three paths. | The native crop shows softer high-contrast holes. Bright gaps still appear and disappear during the walk, and fine foliage loses definition. |
| Open water | The diagonal near bank has visible stair steps. The bottom texture and procedural water response change during travel. | The enlarged still shows a softer shoreline. The change is small at native scale and the underlying surface motion remains visible. |

The sequence review used full-frame contact sheets and near-native crops from
the moving intervals. Sodium also shows moving leaf cutouts and geometric
edge steps. The trial's strongest differences are visible in magnified stills.
The motion comparison shows persistent foliage and shoreline aliasing. No
large shadow flash, full-view discontinuity, or persistent water flash was evident in the
paired clear-day paths. The brief blue squares during the water entry are
splash particles. The evidence supports qualitative comparison because the
recording paths are input-matched and the exact animation phase varies.
[Still and motion evidence](../../evidence/task-23/README.md).

## Performance

Two native F3+L profiles per mode and scene record CPU client-loop timing in
forest and open water. These fixed-camera runs were taken with screen
recording stopped. The profile index preserves the raw sample paths and
hashes. Its p95 column measures client-loop duration.
[Raw profile index](../../evidence/task-23/runs.csv), [harness](harness.md).

| Scene | Sodium mean | TASK-22 mean | Spatial mean | Spatial delta vs TASK-22 |
| --- | ---: | ---: | ---: | ---: |
| Forest | 0.263 ms | 0.642 ms | 0.654 ms | +0.012 ms |
| Open water | 0.279 ms | 0.693 ms | 0.710 ms | +0.018 ms |

Values are means of two run means. The forest trial changed by −0.005 and
+0.029 ms across the two pairs. Open water changed by +0.006 and +0.029 ms.
This run-to-run spread limits what the CPU profiles can establish about the
filter alone.

The isolated final-pass timer compiles the expanded control and trial shader
pairs and draws each fullscreen at 2560×1440. It uploads a linearized native
control screenshot per scene as an RGBA16F source and renders to RGBA8. Two
process runs per scene each record 32 alternating-order pairs of 64 draws
per mode using `GL_TIME_ELAPSED`. Repeated draws to an offscreen framebuffer
characterize the incremental GPU work under that setup. In-client input HDR
values, GPU frame time and presentation pacing remain unmeasured.
[Timer source](../../evidence/task-23/final_timer.c), [GPU summary](../../evidence/task-23/gpu-summary.csv).

| Scene | Median GPU control per draw | Median GPU spatial per draw | Median paired increment |
| --- | ---: | ---: | ---: |
| Daylight | 0.0138–0.0142 ms | 0.0233–0.0235 ms | +0.0091–0.0096 ms |
| Forest | 0.0140–0.0141 ms | 0.0236 ms | +0.0096–0.0097 ms |
| Open water | 0.0138–0.0140 ms | 0.0233 ms | +0.0094–0.0096 ms |

The six increments amount to about 64–70% of the measured control final
draw. That cost bought localized softening and left the most visible shimmer
in place. At the end of TASK-23 the accepted shader tree matched the
TASK-22 manifest. The disposable trial and comparison evidence are retained
for replay.

## Evidence limits

The fixture samples three clear-day paths on one Iris and GPU combination.
The water camera steps off the bank into shallow water while the view stays
above the surface. The clips can show obvious crawling and flashing. The
recording cadence and H.264 compression limit pixel-level temporal analysis.
Cloud and water animation phases can differ between captures. The review
leaves submerged camera transitions, rapid turns, rain, dusk and denser
natural vegetation for later coverage.
