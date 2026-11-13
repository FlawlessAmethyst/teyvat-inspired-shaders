# TASK-23 evidence

[Decision and visual review](../../docs/testing/anti_aliasing.md) ·
[Replay commands](commands.txt) · [Verification](verification.txt)

| Evidence | Retained path |
| --- | --- |
| Accepted control | `artifacts/task-23/shaders/` and the [TASK-22 shader manifest](../task-22/pack.sha256) |
| Spatial trial | `artifacts/task-23/spatial-shaders/` and [trial fragment function](spatial-aa.glsl) |
| Nine native 2560×1440 PNGs | `artifacts/task-23/{control,spatial,sodium}-01/{daylight,forest,open-water}/native.png` |
| Nine motion clips | `artifacts/task-23/{control-02,spatial-02,sodium-motion}/{daylight,forest,open-water}/motion.mp4`, [clip index](video.csv) |
| Enlarged still crops, motion contact sheets and side-by-side video crops | `artifacts/task-23/review/` |
| Twelve native profiles and raw samples | `artifacts/task-23/*-0*/runs/{forest,open-water}/`, [profile index](runs.csv) |
| Six runs of the isolated GPU timer | `artifacts/task-23/gpu-{daylight,forest,open-water}-{01,02}.csv`, [GPU summary](gpu-summary.csv) |
| Runtime and environment logs | `artifacts/task-23/{control-01,control-02,spatial-01,spatial-02,sodium-01,sodium-02,sodium-motion}/logs-*/` |
| Archived disposable fixture | `artifacts/task-23/world/` |

The reviewed comparisons include [shoreline stills](../../artifacts/task-23/review/open-water-detail.png)
and the [foliage motion crop](../../artifacts/task-23/review/forest-motion-detail.mp4).
The side-by-side motion crops put the TASK-22 control on the left and the
trial on the right.

From the repository root, regenerate the three indices from saved evidence
with `python3 evidence/task-23/review.py runs artifacts/task-23`, repeating
with `gpu` and `video` in place of `runs`. These checks use the retained
TASK-22 Sodium night profile as a settings and runtime reference. A live
replay checks that `shaderpack/shaders/` matches the TASK-22 snapshot.
Use a separate source copy with the retained `artifacts/task-22/shaders/`
tree in that location. The replay also uses the TASK-22 source-world manifest
and the installed TASK-03 world. Follow the [replay commands](commands.txt)
in stages, inspect the first world-list row before copying the guard, and
set `root` to a fresh artifact directory.

Transfer the ignored snapshots, native images, motion clips, raw GPU timers,
profile ZIPs and logs separately for a developer handoff. TASK-24 verified
the live shaders against this retained TASK-22 control and used the forest
and open-water stills in its review. [TASK-24 triage and evidence](../../docs/architecture/deferred_effects.md).
