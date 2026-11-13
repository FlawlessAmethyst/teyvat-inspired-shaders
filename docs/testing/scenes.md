# Deterministic visual scenes — TASK-03

Developer-only controlled test map for the existing **GenshinShaderDev** Prism
Flatpak instance, Minecraft 1.21.1 / NeoForge / Iris / Sodium. No shader source,
companion mod, custom resource pack, or player-facing settings were added.
See [harness.md](harness.md) for exact environment versions and desktop permissions.

## World and geometry

World: `minecraft/saves/TASK-03 Visual Scenes` under the authorized instance.
Seed: **-6092235014036965370** (signed 64-bit value read from WorldGenSettings).
It is a copy of `New World`; the original remains untouched. The seed determines
surrounding terrain; explicit vanilla block commands determine the test platform.
The map is in the Overworld, roughly X/Z 950–1050, with grass at Y182, a shallow
33×59 water basin, nine persistent-leaf trees, stone/brick/moss references and an
enclosed lantern-lit stone cave. Biomes in the test volume are explicitly plains.
This isolates lighting/material behavior rather than representing a natural biome
or a full ocean workload. Original references were not used or changed in this task.

The source is `scripts/scenes/`: a vanilla developer datapack (format 48), with
`data/task03/function/build.mcfunction` and seven scene functions. Keep it in this
world only: build replaces blocks in its documented bounds. It is test tooling,
not part of the deliverable shaderpack. No load/tick functions belong in shaderpack/.

All presets set creative mode, peaceful difficulty, no effects, empty inventory,
fixed daylight/weather, randomTickSpeed 0, and disable mob spawning, insomnia and
fire spread. Persistent leaves do not decay. Time/weather durations are reset at
each invocation. Empty hotbar slots act as developer triggers; slot 8 resets the
trigger and preloads the platform, and slot 9 builds the map. Do not use this world
for ordinary inventory/gameplay: preset invocation clears inventory.

## Camera presets

Positions below are teleport feet coordinates. The inherited creative player has
flight off. Outdoor Y184 teleports settle to feet Y183 on the grass platform;
cave feet remain at Y184. The shore camera is explicitly Y183. Leave flight off
and use first person; camera eye height is the normal standing-player offset. Yaw 180 faces north, 0 south,
90 west; positive pitch looks down. Machine-readable authority: `presets.json`.

| Key | Preset | XYZ | Yaw / pitch | Time | Weather |
| --- | --- | --- | --- | --- | --- |
| 1 | daylight | 1000.5, 184, 1036.5 | 180 / 8 | 6000 | clear |
| 2 | sunset | 1000.5, 184, 1000.5 | 90 / 2 | 12000 | clear |
| 3 | night | 1000.5, 184, 1036.5 | 180 / 8 | 18000 | clear |
| 4 | rain | 1000.5, 184, 1036.5 | 180 / 8 | 6000 | rain |
| 5 | forest | 1018.5, 184, 1005.5 | 180 / 5 | 6000 | clear |
| 6 | open-water | 974.5, 183, 1020.5 | 180 / 5 | 6000 | clear |
| 7 | cave | 970.5, 184, 1027.5 | 0 / 3 | 6000 | clear |

## Baseline client policy

Native captures: **2560×1440**, fullscreen, FOV **70°** (`fov:0.0`), render distance
**12 chunks**, simulation distance **8**, GUI scale 3. Fancy graphics, smooth
lighting on, biome blend radius 2, mipmaps 4, brightness option 0.5, all particles,
clouds enabled, Sodium weather quality FAST, vignette off, entity shadows off, entity distance 0.75. VSync off, FPS cap 240.
First person, no input during warm-up/capture, bobbing off, HUD/hand/chat hidden
with F1, debug/FPS overlays off. Shaders **disabled** in Iris. Only vanilla and
loader-provided built-in resources enabled; the previously selected
`file/Project Amber.zip` is disabled for these captures, not deleted or edited.
No mod JARs or loader versions changed. This is the existing modded Sodium client
with vanilla textures, not a certification of an unmodded Minecraft installation.

Original client files are backed up in `artifacts/task-03/preparation/`.
Baseline settings remain installed for later testing in this dedicated instance.
Each capture stores options/Iris/Sodium configuration; supplemental config and
version/mod inventory are retained with the TASK-03 evidence. Keep those with the
raw images for handoff. To undo client-setting changes, stop the instance and copy
the preparation files back to their original options.txt/config paths. Do not
restore level.dat or replace the original world to undo client settings.

Warm-up is 3 seconds after preset acknowledgment plus **20 seconds** of focused
rendering before F2. Slot 8 first gives chunks three seconds to load. A fresh log
acknowledgment is required; stale screenshots cannot pass. The script refuses an
existing output directory and captures exactly one fresh native F2 image, checks
its dimensions, then restores the HUD. Start with visible HUD, closed menus/chat,
and no debug overlay. Use `--resume-paused` only if the pause menu is visible.
Cloud translation, rain particles, water animations and light flicker are not
phase-locked. Comparable frames, not bit-identical whole images, are the criterion.

## Replay

Run all commands from the repository root. Desktop operations need the same scoped
approved execution as TASK-02; do not run multiple automation processes concurrently.

Use the [preserved TASK-03 fixture](../../evidence/README.md#install-the-task-03-fixture)
for the later regression and benchmark replays. The original setup below
builds the map from the scoped instance's `New World` and writes a fresh
TASK-03 settings backup. It requires both the destination world and
`artifacts/task-03/preparation/` to be absent. Use a disposable world for
manual checks when preserving the archived fixture's exact hashes.

```bash
# Historical setup only, with the client stopped:
python3 scripts/scenes.py prepare
# For an existing or preserved fixture, start here:
python3 scripts/harness.py --artifacts-dir artifacts/task-03 launch --timeout 120
python3 scripts/harness.py screenshot artifacts/task-03/new-title.png
```

Inspect the title/world-list screens and select **TASK-03 Visual Scenes**, never
`New World`. At the tested resolution, Singleplayer is at 1280,535; after selecting
the correct row, Play Selected World is at 1050,1315. Row order changes with saves.
Wait for in-world rendering. The script additionally requires the dedicated world's
Java session lock to be held before sending any input.

```bash
# Build once after first opening the new copy; repeat only to rebuild this test map.
python3 scripts/scenes.py capture build artifacts/task-03/new-build
python3 scripts/scenes.py capture daylight artifacts/task-03/new-daylight
python3 scripts/scenes.py capture sunset artifacts/task-03/new-sunset
python3 scripts/scenes.py capture night artifacts/task-03/new-night
python3 scripts/scenes.py capture rain artifacts/task-03/new-rain
python3 scripts/scenes.py capture forest artifacts/task-03/new-forest
python3 scripts/scenes.py capture open-water artifacts/task-03/new-water
python3 scripts/scenes.py capture cave artifacts/task-03/new-cave
python3 scripts/harness.py stop --timeout 60
python3 scripts/harness.py --artifacts-dir artifacts/task-03 logs
```

The same functions can be invoked manually with `/function task03:daylight`, etc.
Automated typing was rejected during validation: punctuation arrived as other
characters; clipboard bridging also failed. The final runner uses verified number
keys only and does not alter keyboard layouts, clipboard or global display access.

## Validation and limits

See `evidence/task-03/results.json`, `tests.txt`, `commands.txt` and the TASK-03 entry
in [TEST_LOG.md](../TEST_LOG.md) for results, hashes and exact evidence locations.
`artifacts/task-03/<preset>-01/native.png` holds daylight, night, rain, forest
and cave baselines; **sunset-02** and **open-water-02** are the final revised cameras.
Their `-01` images are retained exploratory views, not the final presets. Daylight,
forest and cave `-02` captures repeat their unchanged presets after intervening scenes. Compare full frames
visually for framing and static landmark placement; numerical differences include
animated regions and must not be reported as artistic similarity scores.

TASK-03 captures establish the visual baselines. For performance comparisons,
TASK-10 reuses the fixed presets and warm-up with Unlimited FPS and VSync off.
Use its repeated-run procedure and retain the raw profiles for comparisons.
The small synthetic map provides a controlled workload for these scenes.
See the [performance baseline](baseline.md) and [current status](../STATUS.md).

Later tasks extend disposable copies of this world. The water replay adds a
stepped basin with settled rain and submerged views. The vegetation replay
keeps the original daylight and forest presets and adds views below and
above a dense canopy across a plains/jungle boundary. The weather replay
uses this world copy and fixes the camera and clock while rain starts
and clears in the daylight, open-water and canopy views. The TASK-22 copy
reuses the daylight, night and cave coordinates, adds a sealed lamp room and
an unlit stair fixture, and uses fixed Nether and End cameras. Its hotbar
slots are assigned by the TASK-22 replay.
[Water replay](../../evidence/task-19/commands.txt),
[vegetation replay](../../evidence/task-20/commands.txt),
[weather replay](../../evidence/task-21/commands.txt),
[lighting and dimension replay](../../evidence/task-22/commands.txt).

The TASK-23 copy retains the daylight and forest starts and rotates the
open-water camera toward the bank. It uses a three-second strafe for
daylight and open water and a three-second walk for forest. Its native
stills and fixed-camera CPU profiles run separately from motion recording.
[TASK-23 starts and paths](anti_aliasing.md#capture-conditions).

TASK-28 uses a disposable copy of the TASK-22 fixture. It replays all seven
original cameras, then exercises movement, weather at the TASK-25 valley
camera, a waterline crossing in each direction, cave entry and three
dimension changes. TASK-28 uses an eight-second wait for fixed native stills.
[Regression report](regression_report.md), [replay](../../evidence/task-28/README.md).

Observed repeat results: outdoor lower-half mean absolute difference **0** for
both daylight and forest; full-frame cave normalized MAE **0.000641911**. Whole-frame
outdoor MAE was 0.0139199 / 0.0211061 because cloud positions differ. Static landmark
framing was also visually inspected. The 0.01 static-region threshold is a developer
regression diagnostic, not a shader/Genshin quality metric. All three passed.
