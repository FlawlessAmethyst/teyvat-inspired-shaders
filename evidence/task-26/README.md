# TASK-26 evidence

[Effect costs and limits](../../docs/testing/effect_costs.md) · [Replay commands](commands.txt) · [Verification record](verification.txt).

- `variants.py` verifies the retained TASK-25 fog-tuned shader tree against
  its manifest and derives eight ablations and a full control. A live replay
  uses the saved shader tree, world and world-list image in
  `artifacts/task-25-fog-tuning/`. The restoration check also uses the
  TASK-22 source-world manifest and the installed TASK-03 fixture.
  Verify the inherited video and input settings before running. The
  world-list guard expects the 2560×1440 fullscreen layout at GUI scale 3.
  [Replay prerequisites](../README.md#replay-prerequisites),
  [Client settings](../../docs/HANDOFF.md#repeat-the-runtime-checks).
  [Replay commands](commands.txt).
- `replay.py`, `session.sh` and `matrix.sh` stage and run both rounds in the
  scoped instance. `review.py` validates the per-run options, shader selection,
  preset sequence, camera captures and raw sample count.
- [Per-run client profiles](runs.csv) and [paired client-loop deltas](effect-deltas.csv)
  index both rounds. [Matched comparison sheets](../../artifacts/task-26/comparisons/)
  use the native-size window captures from before each profile.
- `gpu.sh`, `geometry_timer.c` and `summarize_gpu.py` reproduce the
  [paired GPU results](gpu-summary.csv). The harness also reuses the TASK-18
  sky timer and TASK-23 final timer.
- Retain `artifacts/task-26/` for source snapshots and manifests, native-size
  window frames before and after profiles, original Minecraft profiler ZIPs,
  raw loop and utilization CSVs, raw GPU timer CSVs, device telemetry,
  settings, logs, comparisons and the disposable world. The artifact root
  belongs with the developer handoff.

The copied world retains the TASK-25 title so the replay can verify the
first menu row against its saved capture. Profile files stay inside the
scoped instance or the ignored artifact tree. The replay temporarily binds
Iris reload to F9 for shader sessions and restores the five original
settings files after the final client exits.

Review the existing evidence from the repository root without launching
Minecraft.

```bash
python3 evidence/task-26/review.py artifacts/task-26
python3 evidence/task-26/compare.py evidence/task-26/runs.csv
python3 evidence/task-26/summarize_gpu.py artifacts/task-26/gpu
```

The first command validates the recordings and regenerates the metrics
index. The other two regenerate the client-loop deltas and GPU summary.
For a fresh live run, use a new output directory and the scoped desktop
and NVIDIA access described in the replay commands. If interrupted, save
and stop the scoped instance with `python3 tools/minecraft.py stop --timeout 60`,
then run `python3 evidence/task-26/replay.py restore <artifact-root>` with
the original backup still present.
