# Genshin reference inventory — TASK-04

Status: **DONE**, 2026-11-12. This is an inventory and sampled scene catalog.
Visual target selection, technique attribution and comparison criteria belong to TASK-05 onward.

## Inputs and sampling method

All 30 supplied sources are accounted for: 19 settings JPEGs and 11 gameplay MP4s.
Source bytes and SHA-256 hashes match the TASK-01 input manifest before and after
extraction. Originals were never rewritten. Metadata: [sources.json](../../evidence/task-04/sources.json).

FFprobe enumerates decoded video frame presentation timestamps. FFmpeg selects
frame zero, the first frame at or after each five-second mark, and the final frame.
Timestamps below are actual source presentation times in seconds, not requested
seek times or inferred frame-number/FPS values. Variable frame pacing is preserved
in the index. Full-resolution 1920×1080 PNGs are decoded from compressed video;
PNG storage adds no further lossy compression, but cannot restore source detail.
Contact sheets are reduced JPEG navigation previews, not color-measurement masters.
No grading, cropping, sharpening or HUD/watermark removal was applied to PNGs.

Every video contact sheet and all 19 settings thumbnails were visually reviewed.
Descriptions identify content visible at sampled times; ranges group samples and
are not frame-exact cut boundaries. Sampling does not certify every intervening
frame or short-lived event. No additional samples were needed to represent the
scene categories visible in these sheets. No full-motion/temporal-effect analysis
was performed. Review the original clips if later tasks need animation evidence.

## Settings screenshots

These Russian-language menus document available controls, not implementation
proof, measured costs, or authorization to build a player-facing settings system.
Their relationship to the settings used during gameplay recording is unverified.

[Settings contact sheet](../../artifacts/task-04/settings-contact.jpg).

| Source | Dimensions | Observed screen |
| --- | --- | --- |
| [01.jpg](../../references/pictures/settings_screen/01.jpg) | 1920×1080 | Graphics-quality preset menu |
| [02.jpg](../../references/pictures/settings_screen/02.jpg) | 1920×1080 | Resolution/window mode menu |
| [03.jpg](../../references/pictures/settings_screen/03.jpg) | 1920×1080 | Brightness calibration with town/interior previews |
| [04.jpg](../../references/pictures/settings_screen/04.jpg) | 1920×1080 | Frame-rate menu |
| [05.jpg](../../references/pictures/settings_screen/05.jpg) | 1920×1080 | Vertical-sync menu |
| [06.jpg](../../references/pictures/settings_screen/06.jpg) | 1920×1080 | Render-scale menu |
| [07.jpg](../../references/pictures/settings_screen/07.jpg) | 1920×1080 | Shadow-quality menu |
| [08.jpg](../../references/pictures/settings_screen/08.jpg) | 1920×1080 | Post-processing-quality menu |
| [09.jpg](../../references/pictures/settings_screen/09.jpg) | 1920×1080 | Effects-quality menu |
| [10.jpg](../../references/pictures/settings_screen/10.jpg) | 1920×1080 | Environment-detail menu |
| [11.jpg](../../references/pictures/settings_screen/11.jpg) | 1920×1080 | Anti-aliasing menu |
| [12.jpg](../../references/pictures/settings_screen/12.jpg) | 1920×1080 | Volumetric-fog toggle |
| [13.jpg](../../references/pictures/settings_screen/13.jpg) | 1920×1080 | Reflections toggle |
| [14.jpg](../../references/pictures/settings_screen/14.jpg) | 1920×1080 | Motion-blur menu |
| [15.jpg](../../references/pictures/settings_screen/15.jpg) | 1920×1080 | Bloom toggle |
| [16.jpg](../../references/pictures/settings_screen/16.jpg) | 1920×1080 | Crowd-density menu |
| [17.jpg](../../references/pictures/settings_screen/17.jpg) | 1920×1080 | Co-op teammate effects menu |
| [18.jpg](../../references/pictures/settings_screen/18.jpg) | 1920×1080 | Subsurface-scattering menu |
| [19.jpg](../../references/pictures/settings_screen/19.jpg) | 1920×1080 | Anisotropic-filtering menu |

## Gameplay inventory and per-video subtasks

All subtasks below are **DONE**: metadata, extraction, visual sheet review and scene indexing.

| Subtask / source | Duration (s) | Samples | Contact sheet |
| --- | ---: | ---: | --- |
| TASK-04-VID-001 / [01.mp4](../../references/video/gameplay/01.mp4) | 58.833000 | 13 | [view](../../artifacts/task-04/video-01/contact.jpg) |
| TASK-04-VID-002 / [02.mp4](../../references/video/gameplay/02.mp4) | 58.349983 | 13 | [view](../../artifacts/task-04/video-02/contact.jpg) |
| TASK-04-VID-003 / [03.mp4](../../references/video/gameplay/03.mp4) | 59.433000 | 13 | [view](../../artifacts/task-04/video-03/contact.jpg) |
| TASK-04-VID-004 / [04.mp4](../../references/video/gameplay/04.mp4) | 58.283000 | 13 | [view](../../artifacts/task-04/video-04/contact.jpg) |
| TASK-04-VID-005 / [05.mp4](../../references/video/gameplay/05.mp4) | 58.616650 | 13 | [view](../../artifacts/task-04/video-05/contact.jpg) |
| TASK-04-VID-006 / [06.mp4](../../references/video/gameplay/06.mp4) | 59.083000 | 13 | [view](../../artifacts/task-04/video-06/contact.jpg) |
| TASK-04-VID-007 / [07.mp4](../../references/video/gameplay/07.mp4) | 59.483000 | 13 | [view](../../artifacts/task-04/video-07/contact.jpg) |
| TASK-04-VID-008 / [08.mp4](../../references/video/gameplay/08.mp4) | 59.616650 | 13 | [view](../../artifacts/task-04/video-08/contact.jpg) |
| TASK-04-VID-009 / [09.mp4](../../references/video/gameplay/09.mp4) | 59.416650 | 13 | [view](../../artifacts/task-04/video-09/contact.jpg) |
| TASK-04-VID-010 / [10.mp4](../../references/video/gameplay/10.mp4) | 58.966650 | 13 | [view](../../artifacts/task-04/video-10/contact.jpg) |
| TASK-04-VID-011 / [11.mp4](../../references/video/gameplay/11.mp4) | 60.916650 | 14 | [view](../../artifacts/task-04/video-11/contact.jpg) |

## Observed scene groups

Each row links one representative PNG; the [complete frame index](frame_index.md)
links every sampled frame with its exact source timestamp and decoded frame number.

| Source | Sample group (seconds, approximate) | Observed content | Representative (actual time) |
| --- | --- | --- | --- |
| [01.mp4](../../references/video/gameplay/01.mp4) | 0–5 | Grassy overlook across green valley, distant city and layered cliffs | [0.000 s](../../artifacts/task-04/video-01/frame-001.png) |
| [01.mp4](../../references/video/gameplay/01.mp4) | 10–20 | Orbit toward shaded rock walls, nearby trees and sky | [15.017 s](../../artifacts/task-04/video-01/frame-004.png) |
| [01.mp4](../../references/video/gameplay/01.mp4) | 25–35 | Valley panorama and downward view over grass, trees and terraces | [30.033 s](../../artifacts/task-04/video-01/frame-007.png) |
| [01.mp4](../../references/video/gameplay/01.mp4) | 40–50 | Cliff-facing orbit with sunward bright cloud edges | [45.017 s](../../artifacts/task-04/video-01/frame-010.png) |
| [01.mp4](../../references/video/gameplay/01.mp4) | 55–60 | Return to distant valley panorama | [58.817 s](../../artifacts/task-04/video-01/frame-013.png) |
| [02.mp4](../../references/video/gameplay/02.mp4) | 0–5 | Daylight coastal plateau and distant landscape | [0.000 s](../../artifacts/task-04/video-02/frame-001.png) |
| [02.mp4](../../references/video/gameplay/02.mp4) | 10–25 | Upward camera orbit: blue sky, clouds, sun glare | [15.017 s](../../artifacts/task-04/video-02/frame-004.png) |
| [02.mp4](../../references/video/gameplay/02.mp4) | 30–30 | Cloud cover builds over coast | [30.017 s](../../artifacts/task-04/video-02/frame-007.png) |
| [02.mp4](../../references/video/gameplay/02.mp4) | 35–60 | Dark overcast panorama; rain streaks visible in sampled frames | [45.017 s](../../artifacts/task-04/video-02/frame-010.png) |
| [03.mp4](../../references/video/gameplay/03.mp4) | 0–10 | Bright mountaintop platform above mist-filled stone pillars | [5.017 s](../../artifacts/task-04/video-03/frame-002.png) |
| [03.mp4](../../references/video/gameplay/03.mp4) | 15–30 | Skyward orbit with sun glare, clouds and floating structures | [20.017 s](../../artifacts/task-04/video-03/frame-005.png) |
| [03.mp4](../../references/video/gameplay/03.mp4) | 35–50 | Layered mountains, autumn-colored trees and low cloud/fog banks | [40.017 s](../../artifacts/task-04/video-03/frame-009.png) |
| [03.mp4](../../references/video/gameplay/03.mp4) | 55–60 | Downward view into fog-filled valley and nearer slopes | [59.417 s](../../artifacts/task-04/video-03/frame-013.png) |
| [04.mp4](../../references/video/gameplay/04.mp4) | 0–5 | High grassy island overlook, pink trees and turquoise coast | [0.000 s](../../artifacts/task-04/video-04/frame-001.png) |
| [04.mp4](../../references/video/gameplay/04.mp4) | 10–20 | Skyward orbit and nearby flowering trees | [15.017 s](../../artifacts/task-04/video-04/frame-004.png) |
| [04.mp4](../../references/video/gameplay/04.mp4) | 25–35 | Descent/glide from overlook toward lower terrain; darker blue views | [30.017 s](../../artifacts/task-04/video-04/frame-007.png) |
| [04.mp4](../../references/video/gameplay/04.mp4) | 40–45 | Low grassy clearing with trees and flowers | [40.017 s](../../artifacts/task-04/video-04/frame-009.png) |
| [04.mp4](../../references/video/gameplay/04.mp4) | 50–60 | Blue-lit grove, luminous plants and distant terrain | [55.033 s](../../artifacts/task-04/video-04/frame-012.png) |
| [05.mp4](../../references/video/gameplay/05.mp4) | 0–15 | Pink rock ledge over blue-purple basin, waterfalls and layered mist | [5.000 s](../../artifacts/task-04/video-05/frame-002.png) |
| [05.mp4](../../references/video/gameplay/05.mp4) | 20–35 | Orbit past wooden bridge, terraces, tree shadows and waterfall walls | [25.017 s](../../artifacts/task-04/video-05/frame-006.png) |
| [05.mp4](../../references/video/gameplay/05.mp4) | 40–40 | Skyward view of clouds and airborne particles | [40.017 s](../../artifacts/task-04/video-05/frame-009.png) |
| [05.mp4](../../references/video/gameplay/05.mp4) | 45–50 | Downward view of vegetation and luminous swirling water | [50.017 s](../../artifacts/task-04/video-05/frame-011.png) |
| [05.mp4](../../references/video/gameplay/05.mp4) | 55–60 | Return to broad waterfall-basin panorama | [58.600 s](../../artifacts/task-04/video-05/frame-013.png) |
| [06.mp4](../../references/video/gameplay/06.mp4) | 0–5 | Wooden walkway and small shelter amid bright grass and shaded trees | [0.000 s](../../artifacts/task-04/video-06/frame-001.png) |
| [06.mp4](../../references/video/gameplay/06.mp4) | 10–30 | Traversal across flowered grass hills, shrubs and broad tree canopies | [20.017 s](../../artifacts/task-04/video-06/frame-005.png) |
| [06.mp4](../../references/video/gameplay/06.mp4) | 35–40 | Skyward view with bright clouds and a luminous gameplay marker | [35.017 s](../../artifacts/task-04/video-06/frame-008.png) |
| [06.mp4](../../references/video/gameplay/06.mp4) | 45–60 | Grassy overlook toward densely wooded hills and giant distant tree | [50.033 s](../../artifacts/task-04/video-06/frame-011.png) |
| [07.mp4](../../references/video/gameplay/07.mp4) | 0–15 | Warm desert dunes, palms, red rock formations and monumental structures | [5.033 s](../../artifacts/task-04/video-07/frame-002.png) |
| [07.mp4](../../references/video/gameplay/07.mp4) | 20–25 | Sunward view with strong glare and long character shadow | [20.017 s](../../artifacts/task-04/video-07/frame-005.png) |
| [07.mp4](../../references/video/gameplay/07.mp4) | 30–35 | Descent toward palm-lined oasis | [30.033 s](../../artifacts/task-04/video-07/frame-007.png) |
| [07.mp4](../../references/video/gameplay/07.mp4) | 40–45 | Wading in shallow oasis water; visible bottom and surface rings | [40.017 s](../../artifacts/task-04/video-07/frame-009.png) |
| [07.mp4](../../references/video/gameplay/07.mp4) | 50–60 | Return over sand toward large stone structure | [55.017 s](../../artifacts/task-04/video-07/frame-012.png) |
| [08.mp4](../../references/video/gameplay/08.mp4) | 0–15 | Grassy lakeshore, mountains, elevated bridge and low sun | [5.000 s](../../artifacts/task-04/video-08/frame-002.png) |
| [08.mp4](../../references/video/gameplay/08.mp4) | 20–30 | Flowered slope and glide toward turquoise shoreline | [25.017 s](../../artifacts/task-04/video-08/frame-006.png) |
| [08.mp4](../../references/video/gameplay/08.mp4) | 35–40 | Beach and shallow water under warm pink-purple sky | [35.017 s](../../artifacts/task-04/video-08/frame-008.png) |
| [08.mp4](../../references/video/gameplay/08.mp4) | 45–60 | Shoreline orbit, flowers and water with progressively warmer horizon | [50.017 s](../../artifacts/task-04/video-08/frame-011.png) |
| [09.mp4](../../references/video/gameplay/09.mp4) | 0–15 | Rocky canyon settlement; orbit between orange sunward clouds and blue sky | [5.017 s](../../artifacts/task-04/video-09/frame-002.png) |
| [09.mp4](../../references/video/gameplay/09.mp4) | 20–35 | Similar overlook as warm horizon light fades toward dusk | [25.033 s](../../artifacts/task-04/video-09/frame-006.png) |
| [09.mp4](../../references/video/gameplay/09.mp4) | 40–50 | Darker blue canyon, sky and nearby cliffs | [45.017 s](../../artifacts/task-04/video-09/frame-010.png) |
| [09.mp4](../../references/video/gameplay/09.mp4) | 55–60 | Settlement panorama with blue ambient light and warm lamps | [59.400 s](../../artifacts/task-04/video-09/frame-013.png) |
| [10.mp4](../../references/video/gameplay/10.mp4) | 0–10 | Blue-purple rocky landscape, ruins, overhanging forms and luminous statue | [10.033 s](../../artifacts/task-04/video-10/frame-003.png) |
| [10.mp4](../../references/video/gameplay/10.mp4) | 15–25 | Star-like sky points, distant structures and pink horizon haze | [20.017 s](../../artifacts/task-04/video-10/frame-005.png) |
| [10.mp4](../../references/video/gameplay/10.mp4) | 30–40 | Orbit toward rocks and glowing statue/vertical light effect | [40.017 s](../../artifacts/task-04/video-10/frame-009.png) |
| [10.mp4](../../references/video/gameplay/10.mp4) | 45–60 | Broad purple-blue landscape with ruins, luminous plants and layered haze | [50.017 s](../../artifacts/task-04/video-10/frame-011.png) |
| [11.mp4](../../references/video/gameplay/11.mp4) | 0–5 | Snowy path, snow-covered conifers and nearby warm lantern | [0.000 s](../../artifacts/task-04/video-11/frame-001.png) |
| [11.mp4](../../references/video/gameplay/11.mp4) | 10–25 | Snowbound wooden village with warm windows and lamps | [15.017 s](../../artifacts/task-04/video-11/frame-004.png) |
| [11.mp4](../../references/video/gameplay/11.mp4) | 30–35 | Open snow/ice basin beneath tall cliff walls | [30.033 s](../../artifacts/task-04/video-11/frame-007.png) |
| [11.mp4](../../references/video/gameplay/11.mp4) | 40–61 | Skyward views of moon, stars, luminous sky bands and snow-covered surroundings | [45.017 s](../../artifacts/task-04/video-11/frame-010.png) |

## Coverage and limits

Observed sample coverage includes green daylight valleys and cliffs (01–03),
coasts/islands and distant water (02, 04), rain/overcast (02), mist-filled mountains
(03), pink/purple vegetation and blue-lit landscapes (04–05), lush grassland (06), desert/oasis shallows (07), warm lakeshore light (08),
a sunset-to-dusk canyon sequence (09), luminous purple-blue ruins (10), and a
moonlit snowy village with warm lamps (11). This is a navigation catalog, not a ranking of visual signatures.

- Settings screenshot 03 includes a small dark-interior preview; that is not a
  full-resolution gameplay cave/interior sequence.
- No controlled fixed-camera full day/sunset/night comparison, isolated graphics-option
  A/B pair, known exposure calibration, or performance recording is supplied.
- Time of day, geographic names and rendering algorithms are not inferred solely
  from color. Blue lighting can be environmental; darkness alone does not prove night.
- Characters, authored geometry/textures, HUD text, watermark and particles appear
  in the footage. These remain in the references and do not expand shaderpack scope.
- Five-second still sampling cannot characterize temporal stability, wind cadence,
  cloud motion, rain density or water animation. Compression and unknown recording
  settings limit fine-detail/color judgments. Brief events between samples may be missed.
- Original media and generated images remain local/ignored. Include both
  `references/` and `artifacts/task-04/` in the developer handoff alongside the small
  checked-in-eligible JSON/Markdown indexes. No redistribution rights are inferred.

## Reproduce, validate and resume

From the repository root, run:

```sh
python3 scripts/sample_references.py
python3 scripts/verify_references.py
python3 scripts/index_references.py
```

Requires installed FFmpeg/FFprobe, ImageMagick and DejaVu Sans; versions are recorded
in [versions.txt](../../evidence/task-04/versions.txt). Completed video caches are
reused after source/frame hash checks. If extraction was interrupted before a
video's `frames.json` was written, move that incomplete generated `video-NN/`
directory aside before retrying; originals are never overwrite targets.
Scene notes are human-reviewed input in
[scene_notes.json](../../evidence/task-04/scene_notes.json); adding/changing source
media requires a deliberate new inventory, not bypassing the integrity assertions.
Exact extraction argument arrays: [extraction_commands.json](../../evidence/task-04/extraction_commands.json).
Validation: [verification.txt](../../evidence/task-04/verification.txt).

TASK-04 is complete. At its completion, the next task was TASK-05.
See [STATUS.md](../STATUS.md) for current progress and the next task to request.
