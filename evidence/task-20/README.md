# TASK-20 vegetation evidence

[Vegetation report](../../docs/testing/vegetation.md) ·
[Replay and verification commands](commands.txt) ·
[Accepted source manifest](pack.sha256) · [Profile index](runs.csv) ·
[Pixel patches](pixels.csv) · [Verification record](verification.txt)

Retain the ignored `artifacts/task-20/` directory. It contains the accepted
vegetation and TASK-19 control shader trees, the saved disposable world,
native PNGs, profiler ZIPs and raw CSVs, and the client logs.

The comparisons pair TASK-19 and TASK-20 at the same camera, time and
weather in [daylight](../../artifacts/task-20/daylight.jpg),
[forest](../../artifacts/task-20/forest.jpg),
[the dense understory](../../artifacts/task-20/dense.jpg) and
[above the canopy](../../artifacts/task-20/canopy-top.jpg).

TASK-21 used `artifacts/task-20/shaders/` as its incremental control and
copied `artifacts/task-20/world/` with the cameras in
`artifacts/task-20/presets.json`. [Weather evidence](../task-21/README.md).
