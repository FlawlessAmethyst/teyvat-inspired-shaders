# TASK-19 water evidence

[Water report](../../docs/testing/water.md) · [Replay and verification commands](commands.txt) ·
[Accepted source manifest](pack.sha256) · [Profile index](runs.csv) ·
[Verification record](verification.txt)

Retain the ignored `artifacts/task-19/` directory with this handoff. It contains
the accepted water, TASK-18 control and depth diagnostic shader trees, the
disposable saved world, native PNGs, profile ZIPs and raw CSVs, and the client
logs. The paired previews include [daylight](../../artifacts/task-19/basin.jpg),
[rain](../../artifacts/task-19/basin-rain.jpg), and the
[submerged basin](../../artifacts/task-19/underwater.jpg). The diagnostic
variant defines `WATER_DEPTH_DEBUG` in the fragment wrapper.

The retained `artifacts/task-19/shaders/` tree is the incremental control
for TASK-20. [Vegetation report](../../docs/testing/vegetation.md).
