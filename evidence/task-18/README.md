# TASK-18 evidence

[Cloud report](../../docs/testing/clouds.md),
[replay and verification commands](commands.txt),
[accepted pack manifest](pack.sha256),
[verification record](verification.txt),
[GPU timing summary](gpu-summary.csv).

Preserve the ignored [artifact directory](../../artifacts/task-18/) with the
developer handoff. It contains the following records.

| Path under `artifacts/task-18/` | Contents |
| --- | --- |
| `control/`, `clouds/` | Native F2 PNGs, exact preset and options snapshots for daylight, sunset, settled rain, night and cave. Each session has startup and graceful-save logs. |
| `daylight.jpg`, `sunset.jpg`, `rain.jpg`, `night.jpg`, `cave.jpg` | Side-by-side TASK-17 control and TASK-18 candidate. |
| `control-shaders/`, `shaders/`, `shaders-trial/` | Exact TASK-17 control, accepted TASK-18 source, and initial cloud trial. |
| `clouds-trial/` | Initial cloud trial captures and logs. |
| `timer-source/`, `gpu-*.csv`, `gpu-*-device.txt` | Expanded sky GLSL, raw batch durations in nanoseconds and renderer/driver identification. |
| `world/`, `source-world.sha256`, `before/` | Saved test world copy, original world integrity record and five settings backups. |

[TASK-17 Sodium captures](../../docs/testing/prototype_checkpoint.md#visual-review)
provide the shaders-off context. The incremental control uses the accepted
TASK-17 prototype with Iris enabled.
