# TASK-25 visual comparison evidence

- [Visual comparison report](../../docs/testing/visual_comparison.md) records
  the S1–S7 rubric judgments and ranked gaps by shader module.
- [Comparison index](comparisons.csv) links each labeled sheet and its two
  native Minecraft PNGs. It gives the source video, decoded frame number,
  presentation timestamp and SHA-256 for each of the seven Genshin stills.
  Cave is a Minecraft-only lighting control.
- [Presets](presets.json) record camera position, rotation, time and weather.
  The original comparison replay stages the retained TASK-22 shader tree
  from `artifacts/task-22/shaders/`. [Replay commands](commands.txt),
  [original manifest](../task-22/pack.sha256), [verification](verification.txt).
- The [clear-air fog follow-up](../../docs/testing/visual_comparison.md#clear-air-fog-follow-up)
  includes five matched recaptures. The replay starts with the same TASK-22
  tree and stages the tuned `lib/fog.glsl` from the working source. It uses
  the original TASK-25 stills, settings and verified world-list image.
  [Fog replay commands](fog-commands.txt), [current shader manifest](fog-pack.sha256).
- Retain `artifacts/task-25/` for the archived comparison world, staged
  shaders, five original settings files, native captures, comparison sheets
  and session logs. Retain `artifacts/task-25-fog-tuning/` for the current
  shader tree, tuned stills, comparison sheets, runtime logs and archived
  fixture. Both replays need the TASK-15 world at `artifacts/task-15/world/`
  and the TASK-22 source-world manifest. The original comparisons also
  need the TASK-04 decoded PNGs and original source clips.
  [TASK-15 fixture](../task-15/verification.txt), [TASK-19 basin build function](../task-19/fixture.mcfunction).
