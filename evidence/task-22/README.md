# TASK-22 evidence

- [Lighting and dimensions report](../../docs/testing/lighting_dimensions.md)
  records the visual review, measurements and condition-specific defects.
- [Replay commands](commands.txt) reproduce the fixtures, profiles, verification
  and development-instance restoration. [Shader manifest](pack.sha256).
- [Pixel patches](pixels.csv), [native profile index](runs.csv) and
  [verification record](verification.txt) identify the reviewed results.

Keep `artifacts/task-22/` for the exact TASK-22 and TASK-21 shader trees,
native F2 captures, comparison sheets, profile ZIPs and CSVs, settings,
client logs, and the archived disposable world. The replay copies the
installed TASK-03 world and uses `artifacts/task-21/shaders/` for its control.
The commands verify the original world against
`artifacts/task-21/source-world.sha256`. The profile reviewer compares
configuration and runtime with
`artifacts/task-10/sodium-01/runs/daylight/recording/`.

The [replay](commands.txt) uses a fresh artifact root and an inspected
world-list screenshot to guard selection of the disposable world. From the
repository root, run `python3 evidence/task-22/review_runs.py artifacts/task-22`
and `python3 evidence/task-22/review_pixels.py artifacts/task-22` to regenerate
the retained CSVs from the saved captures and profiles.
TASK-23 used `artifacts/task-22/shaders/` as its control and retained the
same shader source after deferring AA. [TASK-23 motion report](../../docs/testing/anti_aliasing.md).

The initial spectator input trial is under `artifacts/task-22-control-trial/`.
The accepted replay uses creative cameras standing on barrier anchors.
