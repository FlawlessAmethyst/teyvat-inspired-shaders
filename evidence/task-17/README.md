# TASK-17 evidence index

- [Checkpoint report](../../docs/testing/prototype_checkpoint.md) records the
  decision, visual rubric, runtime and performance.
- [Run index](runs.csv) links all 28 profiler ZIPs, raw client CSVs, before/after
  full-resolution window PNGs and session logs by repository-relative path.
  The index includes SHA-256 hashes for the archives, CSVs and images.
  [Before-profile grid](../../artifacts/task-17/comparisons/repeats-before.jpg),
  [after-profile grid](../../artifacts/task-17/comparisons/repeats-after.jpg).
- [Reference index](references.csv) records the exact video, presentation
  timestamp, decoded frame number and original/decoded SHA-256 hashes for R1–R10.
  [Reference review sheet](../../artifacts/task-17/reference-review.jpg).
- [Replay commands](commands.txt) reproduce the four sessions, the index and
  comparison sheets. [Verification record](verification.txt).
- [TASK-16 shader manifest](../task-16/pack.sha256) identifies the 33 shader
  files reviewed here. [TASK-16 effect timings](../task-16/runs.csv) retain the
  matched shadow-vs-fog comparison used to contextualize this checkpoint.

Preserve `artifacts/task-17/` for the archived test world, staged shader
snapshot, five preflight settings backups, client logs, native-size captures,
profiler archives, per-run options/version manifests and raw/converted CSVs.
Preserve the indexed stills under `artifacts/task-04/` and the fog and shadow
fixture evidence under `artifacts/task-15/` and `artifacts/task-16/`.
