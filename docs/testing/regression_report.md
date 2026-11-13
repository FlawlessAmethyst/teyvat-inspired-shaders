# TASK-28 — Runtime regression and robustness

**DONE.** The fog-tuned TASK-25 build retained by TASK-27 completed the
suite without a blocking render failure or client crash on the installed
development stack. TASK-30 passed a fresh replay with the same shader
tree and checker. The tabulated observations below are from TASK-28.
[Shader manifest](../../evidence/task-25/fog-pack.sha256),
[original verification](../../evidence/task-28/verification.txt),
[TASK-30 verification](../../evidence/task-30/verification.txt).

## Test conditions

GenshinShaderDev ran Minecraft 1.21.1, NeoForge 21.1.265, Iris
1.8.14-beta.1+mc1.21.1 and Sodium 0.8.13+mc1.21.1 on CachyOS with
an RTX 4080 SUPER, NVIDIA 580.196.07 and OpenGL 4.6.0. Settings were
2560×1440 fullscreen, 70° FOV, 12/8 chunk render/simulation distance,
VSync off, Unlimited FPS and built-in resources (`vanilla`, `fabric` and
`mod_resources`). One fresh single-player session used a disposable copy
of the TASK-22 world. The replay built the TASK-19 stepped basin after the
original scene captures
and added a stone approach for the cave walk.
[Environment](../minecraft-environment.md),
[replay and evidence](../../evidence/task-28/README.md).

Fixed views waited eight seconds after the preset acknowledgment before
native F2 capture. Motion tests use KWin window recordings and position
or rotation readings from the game log. Rain onset and clearing use
native F2 frames at approximately 2 Hz with time held at tick 6000.
The waterline clip uses vertical movement and logs changes in the
player's eye block between air and water. Clip cadence describes the
recorder's samples.

## Runtime results

| Check | Observed | Evidence |
| --- | --- | --- |
| Seven TASK-03 scenes | Daylight, sunset, night, settled rain, forest, open water and lantern cave all rendered. Sky tint and clouds, night contrast, rain haze, tree shadows, the shallow floor and warm cave pools were visible. | [Seven-scene sheet](../../artifacts/task-28/review/scenes.jpg) |
| Movement and rotation | The stone strafe and forest walk each covered about 13 blocks. The forest turn changed yaw by 66.15°. The shoreline strafe reached the shallow floor with the camera above water. Fine leaf holes shimmered and oblique stone and shoreline edges showed steps. Tree shadows stayed attached to their casters, with no large flash or dropout apparent in the clips. | [Stone strafe](../../artifacts/task-28/clips/stone-strafe.mp4), [forest walk](../../artifacts/task-28/clips/forest-walk.mp4), [forest turn](../../artifacts/task-28/clips/forest-turn.mp4), [shoreline strafe](../../artifacts/task-28/clips/shore-strafe.mp4) |
| Live weather | At the TASK-25 valley camera, 42 native frames cover clear air, rain onset, settled rain, clearing and returned clear air over 20.5 s. The distant ridge fades as the sky goes gray and rain thickens, then reappears. Foreground geometry stays in place, with no full-view flash in the sampled frames. | [Weather sheet](../../artifacts/task-28/review/weather.jpg), [capture times](../../artifacts/task-28/weather/timeline.csv) |
| Submerged and waterline | The basin's lit floor, darker far wall and blue underside render. The player rose above the surface and submerged again in the same clip. The log records IN → OUT → IN. The view switches sharply between the blue-tinted basin viewed from air and the underwater palette. Geometry stays visible and both states settle. Brief squares and rings are splash and bubble particles. | [Submerged views](../../artifacts/task-28/review/underwater.jpg), [crossing frames](../../artifacts/task-28/review/waterline-crossings.jpg), [crossing clip](../../artifacts/task-28/clips/waterline.mp4) |
| Cave entry and interiors | The walk crossed the doorway from X/Z 969.5/1020.5 to 969.5/1033.45. Floor and walls stayed visible as the cool entrance gave way to warm lantern pools. The sealed unlit room retained readable steps and floor joints. The separate lamp room rendered all five fixture light sources. | [Cave entry](../../artifacts/task-28/clips/cave-entry.mp4), [interior sheet](../../artifacts/task-28/review/dimensions-interiors.jpg) |
| Dimension changes | Command teleports exercised Overworld → Nether → End → Overworld. Iris logged each pipeline rebuild. Netherrack, lava and fire rendered, as did End stone, obsidian pillars, crystals and sky. Two static grass and stone RGB crops matched byte for byte before departure and after return. | [Dimension sheet](../../artifacts/task-28/review/dimensions-interiors.jpg), [runtime logs](../../artifacts/task-28/logs-20261113-194922/) |

The logs show the selected pack and its RGBA16F color attachment. The
review found no pack shader compile or link errors, pipeline fallback,
GL errors or fatal crash. Startup logged optional mod and mixin warnings
and the vanilla translucent-emissive Sampler2 warning seen in the
environment validation. The client saved all dimensions and exited
normally. The crash-report directory gained no files.

## Prioritized open bugs

| Priority | Open issue | Reproduction |
| --- | --- | --- |
| P2 | **Foliage and shoreline aliasing.** Fine foliage shimmer is the most visible motion defect. Stone and the diagonal bank also show moving stair steps. TASK-23 deferred its AA trial. | Walk north from the forest preset or strafe right from the open-water camera rotated to yaw 150°. Inspect the sky-facing leaf holes and the near diagonal bank. [Leaf detail](../../artifacts/task-28/review/leaf-detail.jpg), [AA decision](anti_aliasing.md) |
| P3 | **Abrupt waterline color switch.** Crossing visibly changes the sky and the color of the same basin surfaces. The pack selects air and submerged shading from the eye medium. Both states settle after the switch. | Start at (1027.5, 179, 1037.5) looking east in the stepped basin. Hold jump to rise, then sneak to descend. [Crossing frames](../../artifacts/task-28/review/waterline-crossings.jpg) |
| P3 | **Low distant contrast in the Nether and End.** Dark Nether recesses and nearly black End pillars remain hard to separate. | Load the TASK-22 Nether wastes and End main island views. Inspect distant cavern walls and the obsidian faces. [Dimension sheet](../../artifacts/task-28/review/dimensions-interiors.jpg), [TASK-22 observations](lighting_dimensions.md#dimensions) |

Coverage is limited to the installed stack, scripted paths and one live
rain cycle. Dimension validation covers pipeline rebuilds and settled
post-teleport views. Portal travel and overlays, custom dimensions, lava
immersion, extended swimming, flowing or waterlogged edges and other
hardware or loaders remain untested. Weather sampling can miss shorter
artifacts between frames. In-client GPU frame time and presentation
pacing remain open from TASK-27.
[Performance limits](optimization.md#offscreen-gpu-results).

## Handoff

Five instance settings were restored byte for byte, the temporary pack
was removed and the disposable world was archived. The 76 original
TASK-03 world files and 112 archived TASK-22 world files verified
against preflight manifests. The first menu attempt stopped because
OCR misread the pixel font. The accepted replay checks a mask from the
visually verified world-name row and verifies the copied world's
session lock before issuing in-world input.
[Exact replay](../../evidence/task-28/commands.txt),
[verification](../../evidence/task-28/verification.txt).

The [TASK-29 compatibility investigation](compatibility_notes.md) uses this
run as its tested baseline. The [developer handoff](../HANDOFF.md#repeat-the-runtime-checks)
covers the shared TASK-28 and TASK-30 replay setup.
