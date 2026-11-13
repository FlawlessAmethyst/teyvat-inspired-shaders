# TASK-21 evidence

- [Weather report](../../docs/testing/weather.md) describes the shader and
  the matched Overworld validation.
- [Exact replay and checks](commands.txt) stage the fixture, capture the
  sessions, restore the instance and reproduce the reviewed indices.
- [Accepted shader hashes](pack.sha256) identify the candidate. The control
  uses the exact [TASK-20 shader manifest](../task-20/pack.sha256).
- [Settled pixel patches](pixels.csv) and [live frame measurements](transitions.csv)
  record the matched color and continuity checks.
- [Native profile index](runs.csv) and [isolated sky GPU timings](gpu-summary.csv)
  link the reviewed performance results. [Verification record](verification.txt).

Keep `artifacts/task-21/` for the native F2 PNGs, transition frames and
preview clips, raw Minecraft profile archives and CSVs, GPU timer samples,
logs, shader snapshots and the saved fixture. `weather-live/transitions/`
contains the accepted native series and `window-capture-trial/` contains
the excluded X11 clips. The matching index uses the
`artifacts/task-10/sodium-01/runs/daylight/recording/` runtime and settings
snapshot.

To repeat the live run, use a fresh artifact directory in [commands.txt](commands.txt).
The replay copies `artifacts/task-20/world/`, reads its sibling
`presets.json`, and stages the TASK-20 and TASK-21 shader trees. The
source integrity check uses the installed TASK-03 world and
`artifacts/task-20/source-world.sha256`. Use
`artifacts/task-21/shaders/` to reproduce TASK-22's incremental control.
[TASK-22 results and replay](../task-22/README.md).
