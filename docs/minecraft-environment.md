# TASK-00 environment validation

Validated 2026-11-11 from Codex on CachyOS. Scope: shaderpack source only; no mod development, graphics settings system, release packaging, or shader implementation was started. The older task.md has broader alternatives; TASK-00's explicit shaderpack-only scope takes precedence.

This document records the TASK-00 setup and toolkit. For the retained shader
build, see the [tested stack and compatibility limits](testing/compatibility_notes.md)
and [project status](STATUS.md). The Git limitation below was resolved in TASK-01.

## Instance and runtime

The actual instance is:

`~/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances/GenshinShaderDev`

Its game directory is `minecraft`, **not `.minecraft`**. The previously suggested native-launcher path does not exist. All game directories below are relative to this actual instance:

| Purpose | Path | Validation |
| --- | --- | --- |
| Custom shaderpacks | `minecraft/shaderpacks` | Temporary file write/read/remove and Iris loader probe |
| Logs | `minecraft/logs` | Temporary file write/read/remove; latest.log/debug.log collected |
| Game screenshots | `minecraft/screenshots` | Temporary file write/read/remove; F2 generated a PNG |
| Iris configuration | `minecraft/config/iris.properties` | Restored to shaders disabled and empty pack selection |
| Version manifest | `mmc-pack.json` | Read successfully |

The TASK-00 stack used Prism Flatpak 11.1.1, Minecraft 1.21.1, NeoForge
21.1.265, LWJGL 3.3.3, Microsoft Java 21.0.7, Iris
`1.8.14-beta.1+mc1.21.1` and Sodium `0.8.13+mc1.21.1`. The installed
mod set includes Forgified Fabric API, Connector and other optimization mods.
The Iris JAR declares Embeddium incompatible and names Sodium 0.8 in the
explanation. Embeddium was absent.

Live startup initialized Iris and Sodium on the NVIDIA RTX 4080 SUPER with
OpenGL 4.6.0 and driver 580.196.07. Startup logged optional mixin warnings,
NVIDIA workarounds and a vanilla sampler warning. The beta JAR's embedded
Minecraft range `[1.21,1.21.1)` excludes the tested endpoint. The release
lists NeoForge 1.21.1, and both TASK-00 and TASK-28 ran the installed build.
[Compatibility evidence and metadata](testing/compatibility_notes.md#tested-development-stack).

## Toolkit

Run from the project root:

```bash
# Run from the repository root.
python3 tools/minecraft.py paths
python3 tools/minecraft.py launch --timeout 120
python3 tools/minecraft.py window
python3 tools/minecraft.py focus
python3 tools/minecraft.py key F2
python3 tools/minecraft.py screenshot artifacts/task-00/current.png
python3 tools/minecraft.py logs
python3 tools/minecraft.py --help
```

`click X Y` uses actual window pixel coordinates, not coordinates from a resized image preview. Inspect a current screenshot before clicking. `key Escape` navigates back; input commands focus the game first and allow two seconds for rendering afterward. Loading screens may require longer waits and another capture. `launch` waits for a window, not for the title screen or a loaded world; inspect the screenshot/logs before input. It skips launching if this instance's Java process already exists.

The script requires Python 3, flatpak, wmctrl, xdotool, and maim. It verifies Java's working directory against this exact instance, translates host PIDs to Flatpak namespace PIDs for X11 window matching, and refuses absent/ambiguous windows or namespace-ID collisions. It does not select windows by title alone. Do not run simultaneous automation commands or move the mouse while a click is being sent. No global permissions, root access, or other instance modifications are required.

**Codex execution constraint:** filesystem commands (`paths`, `logs`) work in the sandbox. Desktop commands fail there with `Cannot open display`; the host desktop and Java processes require an approved `exec_command` with `sandbox_permissions="require_escalated"`. Use the scoped command `python3 tools/minecraft.py ...`; do not use sudo, change X server access controls, or grant broad Python execution. Preserve the session's DISPLAY and XAUTHORITY instead of hardcoding the ephemeral auth filename. Observed DISPLAY was `:0`, on a Wayland session with accessible XWayland windows.

Log collection writes timestamped directories under `artifacts/task-00`, copying plain `.log` files and the version manifest. It redacts command-line access tokens; logs may still contain usernames/server addresses, so inspect before sharing. Rotated gzip logs are left in the instance. Artifacts are ignored by git. At TASK-00 validation, the supplied workspace's `.git` was a restricted placeholder, so `git status` was unavailable and no commit was made. TASK-01 subsequently initialized Git; this limitation is historical. See [STATUS.md](STATUS.md) for current repository state.

## Results and evidence

| Capability | Result | Evidence |
| --- | --- | --- |
| Locate actual Flatpak instance | PASS | Manifest and instance.cfg inspected |
| Iris and rendering dependencies initialize | PASS | Fresh startup log, Sodium UI, Iris version UI |
| Custom pack discovery and loading | PASS (loader only) | `Using shaderpack: TASK-00-loader-probe` in latest.log |
| Shaderpacks/logs/screenshots filesystem access | PASS | Read/write/remove probes in all three directories |
| Reusable repository toolkit | PASS | tools/minecraft.py exercised from Codex |
| Launch Minecraft | PASS | Flatpak `--launch GenshinShaderDev`, title screen reached |
| Detect and focus target window | PASS | Host Java cwd + NSpid mapping, active-window assertion |
| Mouse input | PASS | Navigated settings, Iris selection, and normal quit |
| Keyboard input | PASS | Escape navigation and F2 screenshot |
| Window screenshot capture | PASS | maim PNGs at 2560×1440 |
| Native F2 screenshot | PASS | `minecraft/screenshots/2026-11-11_21.18.39.png` |
| Collect logs | PASS | artifacts/task-00/logs-20261111-212352 |
| Future-session commands | PASS | Commands and escalation boundary above |
| Desktop access without escalation | FAIL | Sandbox cannot connect to display; approved escalation works |

Evidence in `artifacts/task-00`: title.png, video.png, iris.png, pack-loaded.png, final-title.png, launcher.log, and timestamped log snapshots. The final log snapshot includes the probe load and clean game shutdown.

The temporary probe contained only `shaders/shaders.properties` with a comment, no GLSL. Iris listed, selected, and loaded it. This proves custom-pack loader access, **not GLSL compilation or in-world rendering**; those checks belong to later shader development. The probe was removed, the original disabled/empty Iris selection restored, and the test-launched game exited normally. No world was opened or changed during this validation. Other Prism instances were not modified.

TASK-00 cleared the environment gate for shader development through approved
desktop access. TASK-09 subsequently verified neutral GLSL compilation and
Overworld rendering. TASK-10 recorded matched client loop profiles. See the
[test log](TEST_LOG.md) and [baseline report](testing/baseline.md).
TASK-22 smoke-tested fixed Nether and End views and an Overworld return on
the same stack. TASK-28 rechecked the command-teleport sequence on the
retained fog-tuned pack and covered live weather, camera motion, waterline
crossings and cave entry in a disposable copy. TASK-30 repeated that suite
and preserved a checksum-verified copy of the original TASK-03 fixture.
[Dimension results and limits](testing/lighting_dimensions.md#dimensions),
[retained-pack regression](testing/regression_report.md),
[fixture installation](../evidence/README.md#install-the-task-03-fixture).
