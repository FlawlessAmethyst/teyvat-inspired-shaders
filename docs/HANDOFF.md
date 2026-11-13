# Developer handoff

## Accepted development source

Use [`shaderpack/shaders/`](../shaderpack/README.md) and the
[TASK-25 fog-tuned manifest](../evidence/task-25/fog-pack.sha256). TASK-27
retained this build after the shadow and fog trials. TASK-28 exercised it
in-game and TASK-30 repeated the suite against the same bytes. The manifest
covers 38 files, including 13 vertex/fragment pairs, 10 include modules
and two property files. [TASK-30 replay verification](../evidence/task-30/verification.txt).

The tested stack is Minecraft Java Edition 1.21.1, NeoForge 21.1.265,
Iris `1.8.14-beta.1+mc1.21.1`, Sodium `0.8.13+mc1.21.1`, Microsoft
Java 21.0.7+6-LTS and LWJGL 3.3.3 (`3.3.3+5` in the log). Prism Launcher
11.1.1 Flatpak launched `GenshinShaderDev` on CachyOS x86-64
(`7.3.3-1-cachyos`) with a GeForce RTX 4080 SUPER, NVIDIA
`580.196.07` and OpenGL 4.6.0. The archived instance manifest and client
log identify the rest of the installed stack. The Iris beta's embedded
Minecraft range excludes the tested endpoint, although the published build
lists it and the local runtime loaded it successfully.
[Compatibility details and version checks](testing/compatibility_notes.md#tested-development-stack).

## Load the unpacked source

1. With the dedicated Prism instance stopped, run the commands below from
   the repository root. The toolkit resolves the Flatpak instance path from
   the current user's home directory. For a different install layout,
   replace the `game=...` line with the game directory shown in Prism.
   The automated replays use the original Flatpak layout.
2. Start the instance. Open **Options → Video Settings → Shader Packs**,
   select **GenshinDev-source**, enable shaders and apply. Open the
   dedicated test world and check the sky, terrain shadows and a lit cave.
   If the scene world is missing, use the [fixture installation instructions](../evidence/README.md#install-the-task-03-fixture).
3. Check the instance's `logs/latest.log` for the selected pack name and
   `logs/debug.log` for shader compilation or link errors. Before a
   controlled replay, close the client and let the replay stage its own
   temporary pack and settings.

```bash
set -euo pipefail
sha256sum --quiet -c evidence/task-25/fog-pack.sha256
game=$(python3 tools/minecraft.py paths | python3 -c 'import json, sys; print(json.load(sys.stdin)["minecraft"])')
pack="$game/shaderpacks/GenshinDev-source"
mkdir -p -- "$game/shaderpacks"
mkdir -- "$pack"
cp -r -- shaderpack/shaders "$pack/"
```

After loading the world, run
`rg -F 'Using shaderpack: GenshinDev-source' "$game/logs/latest.log"`
in the same shell.

`mkdir` stops the copy if the name is already in use. For later edits,
re-copy the development shaders into your own staged folder and reload
through Iris. The archived manifest checks the handed-off baseline, so
source changes will fail that check. Keep an independent baseline copy
for comparison.

## Render path and source map

All root programs use GLSL 330 compatibility for Iris to patch at load
time. Shared geometry routes decode into scene-linear RGB and write to
`colortex0` (`RGBA16F`). Iris supplies alpha tests and blending.
The pack uses forward geometry, a depth-only shadow pass, and one
full-screen `final` draw.

| Stage | Source and behavior |
| --- | --- |
| Shadow depth | [`shadow_solid`](../shaderpack/shaders/shadow_solid.fsh) writes opaque depth without an atlas read. [`shadow`](../shaderpack/shaders/shadow.fsh) samples atlas alpha at mip 0 to keep holes in cutout casters. [`shadows.glsl`](../shaderpack/shaders/lib/shadows.glsl) defines a 1024² map at 64 blocks, projects terrain into light space, biases by slope and fades one hardware-filtered comparison near the boundary. |
| Forward terrain | [`gbuffers_terrain`](../shaderpack/shaders/gbuffers_terrain.vsh) uses [`geometry_vertex.glsl`](../shaderpack/shaders/lib/geometry_vertex.glsl) and [`geometry_fragment.glsl`](../shaderpack/shaders/lib/geometry_fragment.glsl). [`terrain_lighting.glsl`](../shaderpack/shaders/lib/terrain_lighting.glsl) computes vertex sunlight and lightmap fill from sun elevation, face orientation, light levels and rain. The fragment path modulates the linear material by lightmap fill, shadowed direct sun and a bounded low-light lift. Selected lamp faces receive less lightmap gain. Mapped leaves and grasses retain biome tint and combined vertex AO with a small tint correction and off-sun leaf fill. |
| Other geometry | `gbuffers_basic`, `gbuffers_textured`, `gbuffers_textured_lit`, `gbuffers_block` and `gbuffers_damagedblock` select vertex-color, atlas and lightmap behavior in the shared geometry includes. Iris routes absent specialized programs through its fallback chain. `gbuffers_weather` mutes the blue cast of precipitation while preserving alpha. |
| Sky and fog | [`gbuffers_skybasic`](../shaderpack/shaders/gbuffers_skybasic.fsh) uses [`sky.glsl`](../shaderpack/shaders/lib/sky.glsl) for an elevation-based day, twilight and night palette with a sunward lobe. [`clouds.glsl`](../shaderpack/shaders/lib/clouds.glsl) projects one drifting procedural layer onto the sky and masks stars. `gbuffers_skytextured` carries the sun and moon textures. [`fog.glsl`](../shaderpack/shaders/lib/fog.glsl) uses squared view distance and a smooth ramp toward that same sky horizon. At 12 chunks the tested ranges are 88–180 blocks in clear air and 22–136 in settled rain. The submerged ramp attenuates color across 3–26 blocks. |
| Translucent water | [`gbuffers_water`](../shaderpack/shaders/gbuffers_water.fsh) calls [`water.glsl`](../shaderpack/shaders/lib/water.glsl) for mapped water. It fetches Iris's pre-hand `depthtex2` and reconstructs background depth with `gbufferProjectionInverse` for shallow-to-deep tint and alpha. Missing or invalid depth gets a bounded fallback. Two normal waves vary the analytic sky reflection and sun highlight. The eye-medium branch selects the submerged underside treatment. Other translucent surfaces use the lightmapped path. |
| Display | [`final.fsh`](../shaderpack/shaders/final.fsh) samples `colortex0` once. [`tonemap.glsl`](../shaderpack/shaders/lib/tonemap.glsl) applies 1.48× exposure, rain-dependent chroma and a hue-preserving rational highlight shoulder. [`color.glsl`](../shaderpack/shaders/lib/color.glsl) supplies the sRGB transfer functions. |

[`block.properties`](../shaderpack/shaders/block.properties) assigns local
material IDs for water, leaves, grass/ferns and light sources.
[`shaders.properties`](../shaderpack/shaders/shaders.properties) keeps
combined vertex AO, disables legacy directional light and vanilla clouds,
and limits shadow casters to terrain and block entities. The procedural
air fog, sky and terrain sun/fill depend on `hasSkylight && !hasCeiling`.
Nether and End terrain retain the engine lightmap through the shared path.
[Pass ownership and algorithm rationale](architecture/shaderpack_design.md#pass-and-resource-ownership).

## Repeat the runtime checks

Run the [offline checks](../README_DEV.md#iris-shaderpack-development) first.
For the full live smoke test, use the [TASK-28 replay](../evidence/task-28/README.md).
It stages a disposable world from the archived TASK-22 fixture, verifies
the installed TASK-03 world before and after the run, and matches the
working shaders to the TASK-25 fog-tuned snapshot. Install the
[preserved TASK-03 fixture](../evidence/README.md#install-the-task-03-fixture)
if needed. To keep its archived checksum, leave that exact copy idle and
use a disposable world for manual checks.
Use the dedicated Flatpak instance on a host with XWayland window access
(`wmctrl`, `xdotool`, `maim`), KWin/Spectacle and existing per-user
`/dev/uinput` access. ImageMagick 7 (`magick`), FFmpeg/FFprobe, a C
compiler, GNU utilities and `rg` are also used. See the scoped
[desktop access and toolkit](minecraft-environment.md#toolkit).

Launch and close the dedicated client once if its configuration files
have yet to be generated. The replay expects `options.txt` and the four
mod configuration files under `config/` shown in the saved settings.
Match the client settings before running the script. It inherits fullscreen at 2560×1440, GUI
scale 3, 70° FOV, render/simulation distances of 12/8 chunks, built-in
resources and the default hotbar and movement keys. Start with the HUD
visible and the debug and FPS overlays off. Preparation backs up five
settings files, selects the accepted pack and sets Unlimited FPS with
VSync off. [Saved settings](../artifacts/task-30-regression/settings/),
[regression conditions](testing/regression_report.md#test-conditions).

From the repository root with the instance idle:

```bash
root=artifacts/task-30-repeat
python3 evidence/task-28/replay.py prepare "$root"
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-28/motion_input.c -o "$root/motion-input"
bash evidence/task-28/session.sh "$root"
```

Run the session command with host desktop access. It verifies the new
world name in the first menu row and captures the fixed scenes, motion,
waterline and weather transitions, and Nether/End/Overworld views. The
reviewer checks those outputs, selected pack, pipeline rebuilds, movement,
eye-medium crossings and save/exit.

After the session, including after a failed capture, check that the
client has saved and stopped before restoring. If needed, use
`python3 tools/minecraft.py stop --timeout 60` with host desktop access.
Keep the original backup in the same output root. Use a fresh root for
a retry after restoration. If the menu check fails, inspect the captured
world list, confirm the layout and world order, then restore and retry
from a fresh output root.

```bash
python3 evidence/task-28/replay.py restore "$root"
diff -rq shaderpack/shaders "$root/shaders"
python3 evidence/task-28/review.py "$root"
```

For a read-only check of the delivered run, use
`python3 evidence/task-28/review.py artifacts/task-30-regression`.
[Fresh replay commands](../evidence/task-30/commands.txt),
[verification](../evidence/task-30/verification.txt).

For historical tests, the [complete replay index](../evidence/README.md#replay-by-task)
points to each task's exact commands and pinned inputs. Some scripts
expect the historical shader source under `shaderpack/shaders/` or use
fixed artifact paths. Read the command file before replaying and use a
separate source copy for those tests. Preserve the original artifacts.

## Benchmark and interpret comparisons

- **Integrated comparison.** Use the [TASK-26 prerequisites and commands](../evidence/task-26/README.md)
  with a fresh output root, the archived TASK-25 fog-tuned world and a
  stopped client. Its four sessions bracket the shader sessions with
  Sodium shaders-off and reverse the ablation order on repeat. Compare
  the same camera, world state, time/weather, 2560×1440 resolution, 70°
  FOV, 12/8 chunk distances and built-in resources. Match the saved
  client settings for the inherited values above. The replay disables
  VSync and the FPS cap, waits 20 seconds after preset acknowledgment,
  and records about ten seconds with F3+L. Preserve the raw ZIPs,
  before/after PNGs, settings, mod hashes, logs and telemetry.
- **Per-effect comparisons.** Use TASK-26 for paired ablations and
  [TASK-27](../evidence/task-27/README.md) for shadow resolution and fog
  arithmetic. The GPU harnesses use OpenGL elapsed queries on paired
  offscreen draws with the client stopped. They require EGL/OpenGL
  development libraries and access to the NVIDIA device. The benchmark
  scripts also use `nvidia-smi` for telemetry. The offscreen timings
  report milliseconds per synthetic draw or iteration. The client profiles
  report CPU render-loop samples including waits. Loop throughput and
  the utilization column do not provide GPU frame times or presentation
  intervals. Compare paired repeats and p50/p95/p99 alongside the means.
  [Method and measured limits](testing/effect_costs.md#client-method).
- **Read the results.** TASK-26 measured **+0.354–0.466 ms** mean client
  loop time for the full pack versus Sodium across five synthetic
  scenes. Removing shadows gave the largest repeatable reduction.
  Compare that result with the paired visual loss before changing the
  caster or receiver. The 768² trial softened foliage and glass
  shadows, and the fog rewrite had no repeatable GPU improvement.
  [Effect results](testing/effect_costs.md#client-results),
  [optimization decision](testing/optimization.md#decision-and-handoff).
- **Visual checks.** Compare full-size native Minecraft captures at
  identical presets. TASK-25 pairs Sodium with the original shader build
  and separately records the retained fog follow-up. Judge hue, tonal
  separation and atmosphere against the timestamped Genshin stills using
  the qualitative S1–S7 rubric. Use motion clips for foliage, diagonal
  banks and waterline transitions, and inspect log markers to confirm
  weather, camera or dimension changes. [Visual comparisons](testing/visual_comparison.md),
  [reference rubric](research/style_targets.md#repeatable-qualitative-comparison).

## Provenance and continuation

The pack uses Jorge Jimenez's published Interleaved Gradient Noise
formula and constants for the sky dither in `gbuffers_skybasic.fsh`.
The course material is the attribution source. No separate code
license for the formula is recorded in the project.
[Shader source](../shaderpack/shaders/gbuffers_skybasic.fsh),
[SIGGRAPH 2014 course material](https://advances.realtimerendering.com/s2014/index.html).

MakeUp Ultra Fast (LGPL v3.0) and Complementary Reimagined
(Complementary License Agreement 1.7) were studied at pinned revisions.
The source tree contains no vendored shaderpack code, libraries or assets
from those studies. Iris, Sodium, Minecraft and the host tools are external
dependencies. The project has no declared source license.
[Upstream study and reuse record](research/implementation_patterns.md#study-boundary-and-provenance).

Start with the [known gaps and starter tasks](KNOWN_GAPS.md). Keep the
accepted manifest and matching visual and timing records as the control
for further shader work. The [evidence index](../evidence/README.md#what-to-transfer)
and [script inventory](../scripts/README.md) identify the files that must
accompany the working source.
