# Minecraft launch, capture and metrics harness

TASK-02, validated 2026-11-11. Run from the repository root. The harness imports
`tools/minecraft.py`; it does not duplicate instance discovery or install mods.
It targets only Prism Flatpak's `GenshinShaderDev`, with game folder `minecraft`.
The existing NeoForge/Iris/Sodium combination is retained. See
[the environment handoff](../minecraft-environment.md) for the full path.

## Commands and permission boundary

```bash
python3 scripts/harness.py paths
python3 scripts/harness.py launch --timeout 120
python3 scripts/harness.py window
python3 scripts/harness.py screenshot artifacts/task-02/title.png
python3 scripts/harness.py click 1280 535
python3 scripts/harness.py screenshot artifacts/task-02/world-list-current.png
```

Desktop commands require approved execution outside the Codex filesystem sandbox,
using the scoped `python3 scripts/harness.py` or `python3 tools/minecraft.py` prefix.
Preserve session DISPLAY/XAUTHORITY. No sudo, global X access changes, new display
permissions or credentials are required. `paths`, `logs` and CSV analysis work in
the sandbox. Dependencies: Python standard library, flatpak, wmctrl, xdotool, maim;
optional diagnostic `input-info` uses setxkbmap. Do not run automation concurrently.

`launch` is idempotent for this instance, but waits only for its window. Inspect a
fresh capture before navigation. At the tested 2560×1440 resolution, GUI scale 3,
the existing `New World` entry was selected with `click 1200 200`, then opened with
`click 1050 1315`. These are observed coordinates, not a universal scene preset.
Always inspect the current world list first. No automated world deletion/creation
is performed. TASK-03 owns deterministic scenes.

The existing creative world was backed up to `artifacts/task-02/world-before/`
before opening it. Normal time, entities and saves advanced during this test;
the backup was not restored over the saved world. No block edits or scene commands
were issued. No unrelated instance was touched.

```bash
# Inspect state first. Use --resume-paused only when the pause menu is visible.
python3 scripts/harness.py record artifacts/task-02/run-new --resume-paused
# If the world is already running, omit --resume-paused.
python3 scripts/frametimes.py 'artifacts/task-02/run-new/ACTUAL-ARCHIVE.zip' artifacts/task-02/run-new/analysis
python3 scripts/harness.py key F2
python3 scripts/harness.py screenshot artifacts/task-02/current-world.png
python3 scripts/harness.py logs
python3 scripts/harness.py stop --timeout 60
python3 scripts/harness.py logs
```

Use the actual ZIP name printed in the game's log or found in the run directory.
Recording and analysis directories must be new: existing evidence is not overwritten.
`--artifacts-dir PATH`, placed before the subcommand, redirects launcher/log output.
Screenshots use their explicit output path; choose a new name to preserve evidence.

Input is sent only to a window matched through this instance's Java cwd and Flatpak
namespace PID. Focus is checked before input. Keyboard chords use window-targeted
keydown/keyup, 100 ms spacing and reverse release in `finally`. Use **uppercase
letters in debug chords**, e.g. `F3+L`: lowercase attempts failed in this session;
uppercase succeeded repeatedly. The exact underlying keyboard/GLFW cause is not
established. Regular F2 and Escape were verified. A focus change can pause the game
between commands. Recording keeps its operation together and rejects sampled focus
loss; this is not a guarantee against a focus change shorter than the polling interval.

`stop` sends WM_DELETE_WINDOW to the verified window, waits for target Java processes
to disappear and never kills them forcibly. A timeout is an error and leaves the
game running for investigation. The in-world test saved players and all dimensions,
completed FastQuit saves, and exited. Inspect the final logs for save completion;
process exit alone is not proof of a successful save.

## What the performance record means

Minecraft's native F3+L recorder runs for approximately ten seconds, as documented
in [Mojang's release notes](https://www.minecraft.net/pt-br/article/caves---cliffs--part-i-out-today-java).
The tested 1.21.1 client writes `minecraft/debug/profiling/*.zip`. The harness waits
up to 30 seconds for exactly one new complete ZIP, verifies ZIP CRCs, copies it and
captures the final window. It also saves a before image, client/Iris/Sodium settings,
version manifest and enabled mod JAR SHA-256 inventory. An old ZIP never counts as
a fresh recording. Failure leaves its partial run directory for diagnosis.

`scripts/frametimes.py` reads **client/metrics/ticking.csv**, not server timings.
The CSV labels samples `@tick,ticktime`, but the client profiler's `updateDisplay`
count matches each sample: these are render-loop iterations, not 20 Hz server ticks.
Local bytecode inspection confirmed `ClientMetricsSamplersProvider` uses
`ServerMetricsSamplersProvider.tickTimeSampler`, whose stopwatch reports NANOSECONDS.
Evidence: `artifacts/task-02/{client-metric-bytecode,metric-bytecode}.txt` from the
installed 1.21.1 SRG JAR. No upstream code was copied into the shaderpack.

Exports preserve original CSV values, convert nanoseconds to milliseconds and
report sample count / profiler wall duration as observed frame-loop FPS. Percentiles
use nearest rank with every sample retained. Unknown schemas, empty/nonfinite/
nonpositive data, sample gaps, mismatched spans and absent display-update counts
are rejected. The original ZIP includes hardware, JVM, profile and server reports.

These are instrumented **CPU render-loop durations**, including work/waits within
that loop. They are not GPU timings, compositor presentation intervals or input
latency. Profiler overhead is unquantified. Keep raw ZIPs; do not equate reciprocal
mean loop time to independently measured display FPS. The original TASK-02
smoke runs used the debug HUD and a 240 FPS cap. The later matched
benchmarks use fixed presets with the HUD hidden and Unlimited FPS.

TASK-26 retains `client/metrics/gpu.csv` from each ZIP. Its
`gpuUtilization` ratio uses asynchronous query results and Minecraft's
saved CPU duration. Rows can repeat values. The raw export cannot yield
per-frame GPU nanoseconds by multiplying it by the corresponding CPU
loop sample. [TASK-26 timing method and GPU evidence](effect_costs.md#client-method).

## Observed baseline and evidence

Hardware: Ryzen 9 9950X, RTX 4080 SUPER; NVIDIA 580.196.07, OpenGL 4.6.0.
Software: CachyOS kernel 7.3.3-1-cachyos; Prism Flatpak 11.1.1; Minecraft 1.21.1;
NeoForge 21.1.265; Microsoft Java 21.0.7; LWJGL 3.3.3; Iris
1.8.14-beta.1+mc1.21.1; Sodium 0.8.13+mc1.21.1 plus existing optimization mods.
Full inventory/hashes: `artifacts/task-02/baseline-02/mods.json` and profiling ZIP.

2560×1440 fullscreen; GUI scale 3; FOV option 0.0 (70° default); render distance 12;
simulation distance 8; VSync off; max FPS 240; shaders disabled. Existing plains
hill/river viewpoint: XYZ 10.5, 94, -5.5, approximately yaw 25.4°, pitch 18.3°.
Weather/time were not locked, and warm-up was not standardized. Treat this as
Sodium-without-shaders **harness smoke evidence**, not a reproducible scene benchmark.

| Capture | Samples | Profile duration | Profile frame-loop FPS | Mean loop ms | p99 loop ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-01 | 2400 | 10002 ms | 239.952 | 4.158182 | 4.319998 |
| baseline-02 | 2399 | 10001 ms | 239.876 | 4.161625 | 4.246821 |

Raw ZIP, converted CSV and summary live under `artifacts/task-02/baseline-01/` and
`baseline-02/`. `baseline-02/before.png` and `after.png` show the world; `native-f2.png`
is the native game screenshot. `startup.png` shows the first title screen.
`logs-20261111-214255/` includes in-world shutdown/save evidence. The initial launcher
and one exploratory log copy were written to the historical `artifacts/task-00/`
default before the new entry point was added; subsequent runs use TASK-02 paths.
Small reviewed summaries and command/test records are under `evidence/task-02/`.
Large runtime artifacts remain ignored/local and must accompany a developer handoff.

Startup contains existing optional mixin/class warnings and the sampler warning.
Native level-debug dump creation logged `Negative index in crash report handler`
and `Preparing crash report` at ERROR/FATAL severity. Inspection found
`example_crash.txt` with `Description: Level dump` and `java.lang.Exception: dummy`;
the game continued, completed archives and later saved/exited normally. This is
observed diagnostic noise associated with dump generation, not a claimed clean log
or broad compatibility pass. No GLSL compilation or shader rendering was tested.

TASK-03 subsequently established fixed scenes, camera/time/weather presets, client
settings, warm-up and HUD policy. TASK-10 reused that setup with Unlimited FPS
for matched Sodium and neutral-pack client loop profiles. Use the
[scene replay](scenes.md) for visual captures and the
[performance baseline](baseline.md) for benchmark conditions.

TASK-23 uses Spectacle's KWin window recording for motion clips. The
scoped replay checks the disposable world and focused game window before
holding a movement key through the user's existing uinput access. It
captures native F2 stills and F3+L profiles separately. The decoded clip
cadence describes the recorder output. Presentation pacing requires its
own measurement. [TASK-23 replay and verification](../../evidence/task-23/README.md).
