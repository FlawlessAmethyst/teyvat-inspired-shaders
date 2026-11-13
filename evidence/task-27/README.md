# TASK-27 evidence

The [optimization report](../../docs/testing/optimization.md) reviews the
shadow and fog trials against the [fog-tuned TASK-25 manifest](../task-25/fog-pack.sha256).
Use the [exact replay](commands.txt) from the repository root with
GenshinShaderDev idle. Replay stages the shaders and world from
`artifacts/task-25-fog-tuning/{shaders,world}/`, uses the menu reference at
`artifacts/task-26/world-list-reference.png` and reads the shadow cameras
from `artifacts/task-16/presets.json`. Restoration verification also reads
`artifacts/task-22/source-world.sha256` and the installed TASK-03 world.
The replay uses the TASK-16 fixture function and the scoped desktop
toolkit. The world-list guard expects the same inherited client settings
as TASK-26. [Fixture source](../task-16/fixture.mcfunction),
[replay prerequisites](../README.md#replay-prerequisites),
[client settings](../../docs/HANDOFF.md#repeat-the-runtime-checks).

| Path | Content |
| --- | --- |
| [shadow-trial.patch](shadow-trial.patch), [fog-trial.patch](fog-trial.patch) | Source changes applied to independent copies of the control |
| [runs.csv](runs.csv) | Recomputed client-loop distribution, profile hash, static camera check and raw file paths per run |
| [gpu-summary.csv](gpu-summary.csv) | Offscreen medians and median paired differences, in ms per iteration |
| [pixels.csv](pixels.csv) | Shadow fixture crops and fog-view pixel differences |
| [verification.txt](verification.txt) | Runtime and restoration checks |
| [artifacts/task-27/variants](../../artifacts/task-27/variants/) | Exact shader trees, relative manifests and static link logs |
| [artifacts/task-27/comparisons](../../artifacts/task-27/comparisons/) | Fixed-camera comparison sheets |
| [artifacts/task-27/gpu](../../artifacts/task-27/gpu/) | Expanded GLSL, raw elapsed queries and recorded GPU/depth/color probes |

Keep the ignored `artifacts/task-27/` tree with the handoff. It includes
the original F3+L ZIPs, client-loop CSVs, native PNGs, runtime logs,
configuration backups, GPU telemetry and the archived copied world.
`runs.csv` locates each ZIP and its extracted raw samples. The first
batch directory of each client session contains that session's logs.

## Offline review

Regenerate the three reviewed indices from the saved evidence without
opening Minecraft or running new GPU queries.

```bash
set -o pipefail
python3 evidence/task-27/review_results.py client artifacts/task-27 | cmp - evidence/task-27/runs.csv
python3 evidence/task-27/review_results.py gpu artifacts/task-27 | cmp - evidence/task-27/gpu-summary.csv
python3 evidence/task-27/visual_metrics.py artifacts/task-27 | cmp - evidence/task-27/pixels.csv
```
