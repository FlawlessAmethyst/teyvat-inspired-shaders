# TASK-24 — Additional visual effects triage

**DONE · 2026-11-13.** TASK-24 proposed one additional effect, a restrained
sun halo in the existing sky draw. The original TASK-25 comparison used
the TASK-22 shader snapshot. The later fog tuning addressed the loss of
mid-distance terrain detail. TASK-24A remains proposed.
[TASK-25 comparison and fog tuning](../testing/visual_comparison.md).

## What the references show

These timestamps identify decoded frames from the supplied
`references/video/gameplay/` clips. The observations describe the visible
result. Exposure, graphics settings, assets and the rendering method behind
each result are unknown. Settings screenshots
[12](../../references/pictures/settings_screen/12.jpg),
[13](../../references/pictures/settings_screen/13.jpg) and
[15](../../references/pictures/settings_screen/15.jpg) show controls for
volumetric fog, reflections and bloom. Their settings during capture are
unverified. [Full frame index with source paths and timestamps](../research/frame_index.md).

| Cue | Genshin footage | Retained Minecraft evidence |
| --- | --- | --- |
| Sun glow and local highlights | [02 at 20.016650 s](../../artifacts/task-04/video-02/frame-005.png) and [07 at 25.016650 s](../../artifacts/task-04/video-07/frame-006.png) show a broad soft glow centered on the sun, with separate bright flare spots. A warm patch spreads across the sky near the horizon in [08 at 35.016650 s](../../artifacts/task-04/video-08/frame-008.png). In [09 at 59.399983 s](../../artifacts/task-04/video-09/frame-013.png) and [11 at 15.016650 s](../../artifacts/task-04/video-11/frame-004.png), warm lamps and windows punctuate cool surroundings. The blue light around the statue in [10 at 40.016650 s](../../artifacts/task-04/video-10/frame-009.png) is a localized scene effect. | The [sunset capture](../../artifacts/task-18/clouds/sunset/native.png) has a crisp square sun over a broad pink gradient. The [cave capture](../../artifacts/task-22/lighting-01/cave/native.png) already has readable warm light pools and clear lantern faces. |
| Contact and foliage | [06 at 0.000000 s](../../artifacts/task-04/video-06/frame-001.png) shows dark contacts under crates and rocks with directional shadows across the boards. [05 at 25.016650 s](../../artifacts/task-04/video-05/frame-006.png) shows bright color and defined shade under foliage. Texture, occlusion and cast shadow contributions cannot be isolated. | The [forest](../../artifacts/task-23/control-01/forest/native.png) shows tree contact and directional shadows, and the cave shows readable wall and ceiling junctions. TASK-23 motion shows high-contrast leaf gaps shimmering as the camera approaches. |
| Water | In [07 at 40.016650 s](../../artifacts/task-04/video-07/frame-009.png), the oasis has a readable sandy bottom, a green-blue surface and localized wakes. [08 at 50.016650 s](../../artifacts/task-04/video-08/frame-011.png) shows a turquoise shore with soft surface highlights. The reviewed views have no clear, persistent mirror image of nearby terrain. The bright swirl in [05 at 50.016650 s](../../artifacts/task-04/video-05/frame-011.png) is specific to that scene. | The [stepped basin](../../artifacts/task-19/water-01/basin/native.png) and [open-water view](../../artifacts/task-23/control-01/open-water/native.png) already show shallow bottom visibility, a depth-dependent tint and brighter distant water. |
| Atmosphere | [03 at 40.016650 s](../../artifacts/task-04/video-03/frame-009.png) shows pale, low bands separating cliffs at different heights. [02 at 45.016650 s](../../artifacts/task-04/video-02/frame-010.png) shows muted land and sky in rain. | The [rain capture](../../artifacts/task-21/weather-01/rain/native.png) shows a gray horizon and receding geometry. The distance ramp produces depth separation, with no localized valley bank in this fixture. |

Two short strips from the original clips provide sequence context. Each uses
one preview frame per second. In [02 around 19–25 s](../../artifacts/task-24/sun-sequence.jpg)
the glow follows the sun as framing changes, and the separated spots shift.
In [07 around 38–44 s](../../artifacts/task-24/oasis-sequence.jpg) rings trail
the moving character while the shallows remain readable. These previews
support the spatial observations and leave fine motion and effect attribution
unverified. The Minecraft stills are prior fixture captures at different
times and viewpoints from the Genshin footage.

## Dispositions and expected GPU work

The [current architecture](shaderpack_design.md#pass-and-resource-ownership)
writes scene-linear RGBA16F to `colortex0`, uses a one-sample final grade,
and has combined terrain vertex AO, a shadow-depth pass and an analytic
water reflection term. It has no post-process history, material/normal
attachment or saved opaque scene color for water. The table estimates work
from the required samples, draws and buffers. TASK-24 has no GPU timings of
its own. For scale, TASK-23's four added full-resolution color samples cost
0.0091–0.0097 ms per isolated 1440p final draw on the RTX 4080 SUPER.
That measurement covers the AA trial only. Integrated GPU and presentation
costs remain open. [TASK-23 timing method and limits](../testing/anti_aliasing.md#performance).

| Candidate | Disposition | Visual value and expected GPU work |
| --- | --- | --- |
| Analytic sun halo | `IMPLEMENT_SMALL_NEXT` | A compact glow around the sun addresses the gap in the sunset fixture and recurs in clear-day footage. Reuse the current sky ray, sun dot product and cloud opacity. A bounded falloff, RGB add and weather/elevation weighting need only arithmetic in the existing sky draw. |
| Scene-wide bloom | `HANDOFF` | Can spread light around bright lamps or emissive objects. The footage shows localized highlights with preserved dark detail, and the current lamps already read clearly. A plausible trial uses one quarter-width and quarter-height HDR buffer, one composite extraction/filter draw and one extra final-pass sample. At 1440p the 640×360 RGBA16F buffer is about 1.76 MiB per image before any duplicate. Four source fetches per reduced pixel would add about 0.92 million shader sample calls for extraction, plus 3.69 million final lookups. Cache and filtering determine actual traffic. Verify usable pre-grade highlight separation against snow, sky, held items and lamps before accepting that cost. [Iris composite](https://shaders.properties/current/reference/programs/composite/), [buffer sizing](https://shaders.properties/current/reference/shadersproperties/rendering/#sizebuffer). |
| Separate control of vanilla vertex AO | `HANDOFF` | Existing crate-like, tree and cave contacts support keeping the current combined AO. The TASK-25 grove and cave retain grounded contacts and readable shade. Separate AO could give more control over a specific defect by moving the factor into an independent vertex component with a small arithmetic cost and no added draw. The installed beta still needs alpha/cutout validation for `separateAo`. [Visual review](../testing/visual_comparison.md#matched-views), [Iris feasibility](../research/iris_feasibility.md#lighting-shadows-atmosphere-and-materials). |
| Screen-space ambient occlusion | `REJECT` | Could add broader contact shading, but the reviewed footage gives no clear gap worth several depth reads and reconstructed geometry per evaluated pixel. Reduced-resolution evaluation would still require edge-aware reconstruction or risk halos near leaves, silhouettes and hands. Retain baked AO, skylight and directional shadows. |
| Water reflections of scene geometry | `REJECT` | The recurring cues are readable shallows, turquoise tint and moving highlights. Screen-space tracing adds repeated depth reads and hit-color lookup per covered water pixel, plus a readable scene-color stage and handling for missing or off-screen geometry. A planar view would redraw terrain. Keep analytic sky reflection and the existing water highlight. [Water implementation](../testing/water.md#shader-behavior). |
| Screen-space refraction | `REJECT` | The oasis shows readable bottom and surface movement. Distorting the bottom would add an opaque color copy or an equivalent staged composite, displaced color reads and edge handling. The thickness ramp already delivers the stronger depth cue. |
| Shoreline foam or shallow-water caustics | `HANDOFF` | The oasis has narrow edge accents and moving bright streaks. TASK-25 confirms bottom visibility and identifies a water hue gap. A weak shallow-water highlight could reuse the thickness estimate and wave inputs, adding arithmetic per visible water fragment. The stills leave shoreline motion and player wakes outside their coverage. The footage gives little reason to fund a separate projected caustic pass. [Visual review](../testing/visual_comparison.md#matched-views). |
| Height-weighted valley fog | `HANDOFF` | The mountain footage has low mist between cliffs. The later clear-air tune restores contrast in the natural valley using distance alone. Low mist banks remain open. A height term could reuse the existing geometry fog path with no new texture reads. A trial would need continuity checks across sky, solid terrain, water and glass. [Fog follow-up](../testing/visual_comparison.md#clear-air-fog-follow-up). |
| Volumetric clouds, fog and light shafts | `REJECT` | Layering in the mountain footage motivates the bounded height-fog option. A volumetric approach would integrate multiple samples along each view ray, with shadow or density sampling and often a separate buffer and resolve. The projected cloud layer and distance ramp cover the core style at lower expected cost. |
| Foliage wind and additional leaf scattering | `HANDOFF` | The footage's bright plants and shaded canopies are already addressed by TASK-20 tint and fill. If a later motion comparison identifies a clear need, anchored grass movement adds per-vertex math and requires consistent displacement in the camera and applicable shadow paths. A bounded light-through-leaves term could reuse the current sun/leaf inputs if the color gap warrants it. Dense-canopy cutout shimmer and shadow alignment are the first checks. [Vegetation report](../testing/vegetation.md). |
| Shader AA and temporal accumulation | `HANDOFF` | TASK-23's spatial filter softened detail with limited motion benefit. TASK-28 reproduced foliage shimmer and shoreline aliasing on the retained build. Temporal accumulation would require reprojection, history storage and motion/disocclusion handling, especially on water and cutouts. [AA decision](../testing/anti_aliasing.md), [regression observations](../testing/regression_report.md#prioritized-open-bugs). |
| Lens flare, motion blur and depth of field | `REJECT` | Bright flare spots appear in sun-facing footage, but the soft sun glow carries the recurring sky cue. Flare adds visibility testing and overlay work. Blur and focus effects add color samples and may require depth or motion information. They can obscure texture and silhouettes used for gameplay. |

## Optional follow-up — TASK-24A Sun halo

- **Scope.** A separately requested trial sized for one implementation and
  validation session. Use the existing
  `gbuffers_skybasic` sky branch and a small original helper in `lib/sky.glsl`
  only if needed. Add a compact scene-linear glow using existing view/sun
  alignment, fade it with solar elevation and rain, and let the projected
  cloud blend attenuate it. Keep the existing textured sun and moon. Use the
  sky draw only so the narrower lobe cannot leak into the shared fog and water
  palettes.
- **Review.** Compare against the [fog-tuned control](../../evidence/task-25/fog-pack.sha256)
  at 2560×1440 from matched
  clear midday and sunset views facing toward and away from the sun. Check
  a horizon sweep, a cloud or terrain occluder, rain onset and clearing, and
  negative controls at night and underwater. Look for a soft localized
  highlight with readable cloud edges, no visible sky discontinuity and a
  smooth fade. Inspect client shader logs.
- **Cost and decision.** Keep the trial to arithmetic in the existing sky
  draw with zero new texture reads, passes or attachments. Use the TASK-18
  paired offscreen sky timer for a matched control/trial comparison and report
  the incremental draw cost. Keep the change only if the improvement is
  visible at native scale and the measured cost is proportionate. If the
  simple trial fails either check or needs a separate pass, restore the
  control and retain the open gap in the handoff. [Sky timing method](../testing/clouds.md#gpu-cost).

The [TASK-25 dusk comparison](../testing/visual_comparison.md#matched-views)
records the remaining localized sunset glow gap. Its camera is available
as a matched review preset.

## Evidence and verification

From the repository root, regenerate the two supplemental review strips and
check the original inputs and the retained shader tree used for triage.

```bash
mkdir -p artifacts/task-24
ffmpeg -hide_banner -loglevel error -ss 19 -i references/video/gameplay/02.mp4 \
  -t 6 -an -vf 'fps=1,scale=480:-2,tile=3x2' -frames:v 1 -y artifacts/task-24/sun-sequence.jpg
ffmpeg -hide_banner -loglevel error -ss 38 -i references/video/gameplay/07.mp4 \
  -t 6 -an -vf 'fps=1,scale=480:-2,tile=3x2' -frames:v 1 -y artifacts/task-24/oasis-sequence.jpg
python3 scripts/verify_references.py
sed 's|  shaderpack/shaders/|  artifacts/task-22/shaders/|' evidence/task-22/pack.sha256 |
  sha256sum --quiet -c -
diff -qr artifacts/task-22/shaders artifacts/task-23/shaders
```

Transfer the linked local footage, decoded frames and fixture captures with
the handoff. The reviewed architecture is grounded in the tested pack and
the [pinned Iris feasibility record](../research/iris_feasibility.md#evidence-and-version-boundary).
The reduced-buffer bloom route is a design estimate pending installed-client
verification. [Iris 1.21.1 target sizing source](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/shaderpack/properties/ShaderProperties.java#L265-L273).
