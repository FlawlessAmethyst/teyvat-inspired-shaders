# TASK-25 — End-to-end visual comparison

**DONE · 2026-11-13.** The integrated pack improves the outdoor palette,
sunset colors, vegetation contact, water depth cues and cave readability.
The original comparison found excessive clear-air haze over the far valley
hill. The fog follow-up recovered mid-distance contrast in that view.
Low mist banks, cloud form, sunset focus and overcast values remain open.
[Fog follow-up](#clear-air-fog-follow-up),
[comparison index and replay](../../evidence/task-25/README.md).

## Original capture conditions

- Shader-on runs used the 38-file [TASK-22 snapshot](../../evidence/task-22/pack.sha256).
  The shaders-off control used Sodium in the same instance. Both modes
  used native 2560×1440 captures with the HUD hidden, 70° FOV, render
  and simulation distances of 12 and 8 chunks, Fancy graphics, the same
  vanilla and built-in resources, VSync off and Unlimited FPS (`maxFps:260`).
- Prism Launcher Flatpak 11.1.1, Minecraft 1.21.1, NeoForge 21.1.265,
  Iris 1.8.14-beta.1+mc1.21.1, Sodium 0.8.13+mc1.21.1 and Microsoft
  Java 21.0.7. The host used a Ryzen 9 9950X and GeForce RTX 4080 SUPER
  with OpenGL 4.6.0, NVIDIA 580.196.07 and CachyOS kernel 7.3.3-1-cachyos.
- The replay copied the TASK-15 world. A naturally generated river valley
  provides a landscape check with real relief. The constructed ridges, grove,
  basin and cave make specific shader behavior easier to see. The night
  view adds three vanilla lanterns to the copied fixture. A preset sets
  camera, time and weather. Each native F2 capture follows a fresh preset
  acknowledgement and a 20-second focused warm-up. Clouds, water and
  precipitation advance independently. The repeat session reproduced the
  cave framing, light pools and recesses. [Repeat cave](../../artifacts/task-25/pack-repeat/cave/native.png),
  [camera and weather presets](../../evidence/task-25/presets.json),
  [capture commands](../../evidence/task-25/commands.txt).
- Reference matches use scene cues such as lit foreground foliage, distant
  relief, shallow bottom visibility and warm lamps against cool surroundings.
  The games differ in geometry, viewpoint, textures, lighting and exposure.
  The supplied clips have unknown capture settings. Judgments apply to the
  visible relationships in the decoded stills. The labeled sheets are
  previews. The index includes native PNGs, source clips, presentation
  timestamps and frame hashes. [S1–S7 rubric](../research/style_targets.md#repeatable-qualitative-comparison),
  [full-resolution evidence](../../evidence/task-25/comparisons.csv).

## Matched views

| View and reference | Observation |
| --- | --- |
| [Valley](../../artifacts/task-25/comparisons/valley.jpg) · R1, `01.mp4` at 0.000000 s | The foreground gains yellow-green grass and a stronger blue horizon. Near detail stays legible, but the opposite hillside becomes a faint cyan silhouette. R1 retains multiple rock and foliage layers beneath distinct cream and gray cloud masses. The pack's long bright cloud forms have little apparent height. |
| [Rain](../../artifacts/task-25/comparisons/rain.jpg) · R4, `02.mp4` at 45.016650 s | At the valley camera, the pack takes the sky from blue to gray and mutes the greens. Near grass and dirt remain readable. Compared with R4's dark slate sky and faint rain, the pack has a pale horizon, much more visible falling streaks and saturated blue splash pixels. |
| [Ridges](../../artifacts/task-25/comparisons/ridges.jpg) · R3, `03.mp4` at 40.016650 s | The near tree and grass remain distinct while progressively distant stone shapes approach the sky color. R3 has low bands of mist between still-readable cliff tops. The pack's depth cue follows distance across each face, including the tops, and has no localized low bank. |
| [Dusk](../../artifacts/task-25/comparisons/dusk.jpg) · R5, `08.mp4` at 35.016650 s | The peach and lavender sky, blue-gray wall and green foreground establish a coherent dusk palette. R5 has a soft concentrated warm patch behind the ridge and a more turquoise shore. The pack's square sun has a crisp perimeter in a broad warm gradient, and water reflects pale lavender and gray. |
| [Grove](../../artifacts/task-25/comparisons/grove.jpg) · R2, `06.mp4` at 0.000000 s | Tree shadows attach to the trunks, grass texture survives in shade and leaf holes stay open. The leaf masses remain darker and greener than grass but show less teal-versus-yellow separation and less color variation within a crown than R2. Vanilla canopy geometry and the cutout textures account for part of the difference. |
| [Shallows](../../artifacts/task-25/comparisons/shallows.jpg) · R7, `07.mp4` at 40.016650 s | The near sandy bottom remains visible, the deeper steps shift toward blue-green and stained glass stays legible in front of water. R7's shallows carry a greener tint and local wakes. The visible depth progression is the matched cue. The wakes are outside this still comparison. |
| [Night](../../artifacts/task-25/comparisons/night.jpg) · R6, `09.mp4` at 59.399983 s | Blue surroundings and small warm lights are distinct. The masonry and trees stay legible, though the distant tower and tree interiors have less visible tonal separation than the cliffs and structures in R6. The reference's precise game time is unknown. |
| [Cave](../../artifacts/task-25/comparisons/cave.jpg) · Minecraft control | The two lantern pools warm the floor while the recess between them stays dark. The stone wall and ceiling texture remain visible. This guards interior readability alongside the outdoor comparisons. |

### Rubric results

Direction compares the observed cue with the matched shaders-off frame.
Statuses apply to these stills. Motion criteria and special environments
remain unverified here.

| Criterion | Status and direction | Visible basis |
| --- | --- | --- |
| S1 · Palette and highlights | **PASS · improved** | Valley and grove separate grass, leaves, trunks and stone. Dusk grass remains green. Night and cave retain texture next to lamps. Snow is outside these presets. |
| S2 · Lighting and shadows | **PASS · improved** | Grove shadows ground the trunks and keep grass readable. Dusk has cool masonry and a warm sky. Night/cave keep local warm lights and darker recesses. Shadow stability in motion remains unverified here. |
| S3 · Sky and clouds | **PARTIAL · improved** | Day, dusk and night have distinct sky values and hues. Valley and dusk cloud shapes are broad but flat. Dusk has a weaker localized warm focal point than R5. |
| S4 · Atmospheric depth | **PARTIAL · improved in the ridge fixture, regressed for valley ridge readability** | The ridge fixture has near-to-far separation. The natural opposite hillside is substantially more washed out than in the control. R3's low mist banks are absent. |
| S5 · Overcast response | **PARTIAL · improved** | The valley sky and terrain change together and the falling streaks lose blue intensity. The pale overcast horizon and blue splash pixels still differ from R4's dark, restrained rain. |
| S6 · Shallow water | **PARTIAL · improved** | Depth steps keep visible sand near the edge and become blue-green farther in. The deeper water stays bluer than R7, and the dusk shore lacks R5's green separation from the peach sky. |
| S7 · Vegetation | **PARTIAL · improved** | Trunks anchor against the turf, cutouts remain open and leaves are distinct from grass. Canopy color separation and variation lag R2. TASK-23 saw foliage shimmer in motion. [Motion evidence](anti_aliasing.md). |

A fixed 180×90-pixel patch on the valley's opposite hillside (top-left
x=1130, y=640 in both native frames) has a standard deviation of **13.15**
8-bit luma code values in Sodium and **5.73** with the pack. Mean luma rises
from **53.92** to **172.74**. The patch contains no sky. Luma here is
`0.2126 R + 0.7152 G + 0.0722 B` on the encoded PNG channels. This
describes the visible contrast loss for one matched Minecraft region.
The combined change includes lighting, grading and fog. A fresh shader-on
session reproduced both valley patch statistics to the reported precision.
[Repeat capture](../../artifacts/task-25/pack-repeat/valley/native.png),
[pixel probe command](../../evidence/task-25/commands.txt).

## Gaps found in the original comparison

| Priority | Visible gap and acceptance check for future tuning | Affected shader modules |
| --- | --- | --- |
| 1 · Clear-air depth | Keep the far valley ridge recognizable as a textured landform while it recedes relative to the near hill. Cross-check the controlled ridges and rain so that distant boundaries still blend into the sky. The low banks in R3 are a separate limitation of the distance ramp. | [fog.glsl](../../shaderpack/shaders/lib/fog.glsl), [geometry_vertex.glsl](../../shaderpack/shaders/lib/geometry_vertex.glsl), [sky.glsl](../../shaderpack/shaders/lib/sky.glsl) |
| 2 · Cloud shape and sunset focus | Seek clearer bright-to-shaded cloud structure within the existing sky draw. Use the valley and dusk views to check that cloud color and shape read distinctly at the horizon. Dusk also shows the narrow, separately scoped sun-halo candidate from TASK-24. | [clouds.glsl](../../shaderpack/shaders/lib/clouds.glsl), [gbuffers_skybasic.fsh](../../shaderpack/shaders/gbuffers_skybasic.fsh), [sky.glsl](../../shaderpack/shaders/lib/sky.glsl) |
| 3 · Rain values and splash color | Keep near grass and rock readable while darkening the overly pale horizon and reducing the visual prominence of saturated blue splashes. Check clear, rain and both transition directions in the same views. Splash routing uses a fallback particle draw, so isolate that cue before changing the falling-streak program. | [sky.glsl](../../shaderpack/shaders/lib/sky.glsl), [fog.glsl](../../shaderpack/shaders/lib/fog.glsl), [gbuffers_weather.fsh](../../shaderpack/shaders/gbuffers_weather.fsh), [gbuffers_textured_lit.fsh](../../shaderpack/shaders/gbuffers_textured_lit.fsh) |
| 4 · Water hue | Preserve the stepped basin's near-bottom visibility and give mid-depth water a greener cast. Check that dusk water still follows the sky while retaining a shore-to-depth color distinction. | [water.glsl](../../shaderpack/shaders/lib/water.glsl), [gbuffers_water.fsh](../../shaderpack/shaders/gbuffers_water.fsh) |
| 5 · Canopy variation | Look for clearer lit grass, cool leaf shade and readable trunks in the grove and in a natural canopy. Maintain contact and transparent cutouts. The deferred AA trial has separate motion evidence. | [terrain_lighting.glsl](../../shaderpack/shaders/lib/terrain_lighting.glsl), [geometry_vertex.glsl](../../shaderpack/shaders/lib/geometry_vertex.glsl), [shadows.glsl](../../shaderpack/shaders/lib/shadows.glsl) |
| 6 · Dark outdoor detail | Improve separation within night terrain where it can be done without flattening the cave's dark recesses or brightening lamp faces excessively. | [terrain_lighting.glsl](../../shaderpack/shaders/lib/terrain_lighting.glsl), [tonemap.glsl](../../shaderpack/shaders/lib/tonemap.glsl), [fog.glsl](../../shaderpack/shaders/lib/fog.glsl) |

The ranked list reflects visible impact in the original TASK-22 snapshot.
TASK-26 reused the valley, rain, grove, shallows and cave presets to
profile the fog-tuned build. Its matched frames show the visual effect of
each temporary ablation. The TASK-25 evidence here covers fixed views.
[TASK-26 comparisons and timings](effect_costs.md).

## Clear-air fog follow-up

**DONE.** At 12 chunks the clear-weather fog now starts at 88 blocks
and reaches full haze at 180 blocks. The original start was 28 blocks.
The vertex stage interpolates toward the 22–136-block full-rain ramp. Shorter
render distances cap the start relative to the far bound. The change
reuses the existing fragment fog calculation, draw calls and texture
samples. [Fog source](../../shaderpack/shaders/lib/fog.glsl),
[current 38-file shader manifest](../../evidence/task-25/fog-pack.sha256).

| Matched view | Result |
| --- | --- |
| [Valley](../../artifacts/task-25-fog-tuning/comparisons/valley.jpg) | The opposite hill has clearer stepped contours and texture while its far shoulder still fades into the sky. The original luma probe's mean falls from 172.74 to 144.58 and its standard deviation rises from 5.73 to 15.66 code values. The 120×120 grass patch at (1180, 1190) is pixel-identical. |
| [Ridges](../../artifacts/task-25-fog-tuning/comparisons/ridges.jpg) | The middle stone terrace and its tree are clearer. Far stone and glass still pick up sky color. No new hard fog edge is visible in this view. |
| [Settled rain](../../artifacts/task-25-fog-tuning/comparisons/rain.jpg) | The muted foreground and pale distant silhouette retain the same appearance. Streaks, splash pixels, clouds and the nearby sheep vary across captures. |
| [Dusk](../../artifacts/task-25-fog-tuning/comparisons/dusk.jpg) and [night](../../artifacts/task-25-fog-tuning/comparisons/night.jpg) | The clear-air change also applies outside daylight. Distant structures keep their time-of-day color and the dusk shoreline and night lantern pools remain readable. |

All five native 2560×1440 views match their TASK-25 preset and video
settings. The tuned source differs from the original capture source only
in `lib/fog.glsl`. The tuned session saved and exited, the temporary pack
was removed and the five settings files were restored byte for byte.
This change addresses clear-weather hillside readability in the tested
views. Localized mist banks remain open. Intermediate rain strengths now
interpolate from the later clear-air start. Live weather transitions,
other render distances in-client and GPU cost were outside this follow-up.
TASK-26 measured the tuned fog blend in matched client loops and offscreen
draws. TASK-27 kept the original blend. TASK-28 sampled rain onset and
clearing at the same valley camera using the retained source.
[Exact replay and checks](../../evidence/task-25/fog-commands.txt),
[TASK-26 fog measurements](effect_costs.md#coverage-and-limits),
[TASK-27 fog results](optimization.md#offscreen-gpu-results),
[TASK-28 live weather](regression_report.md#runtime-results).
