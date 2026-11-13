# Development script inventory

Run the commands from the repository root. See the
[developer handoff](../docs/HANDOFF.md) for the tested stack and scoped
host access, and the [evidence index](../evidence/README.md#replay-by-task)
for every task's inputs, results and exact commands.

## Shared tools

| Path | Use |
| --- | --- |
| [`tools/minecraft.py`](../tools/minecraft.py) | Resolves the dedicated Prism instance. Launches, focuses, sends input, captures native metrics and window screenshots, collects logs and saves/exits. Start with `python3 tools/minecraft.py --help` or `python3 tools/minecraft.py paths`. |
| [`harness.py`](harness.py) | TASK-02 entry point for the scoped toolkit with a task-local default artifact directory. [Harness procedure](../docs/testing/harness.md). |
| [`scenes.py`](scenes.py), [`scenes/`](scenes/presets.json) | Prepares the disposable TASK-03 world, invokes its vanilla developer datapack through hotbar actions and captures or profiles fixed presets. [Fixture and replay](../docs/testing/scenes.md#replay). |
| [`frametimes.py`](frametimes.py) | Validates a native profile ZIP, exports untouched source samples, converts ns to ms and writes the summary. `python3 scripts/frametimes.py <archive.zip> <new-output-dir>`. |
| [`compare_scenes.py`](compare_scenes.py) | Uses ImageMagick to compare repeat frames from the TASK-03 captures. |
| [`test_frametimes.py`](test_frametimes.py), [`test_scenes.py`](test_scenes.py) | Cover raw metrics and invalid archives, preset/camera agreement, command bounds and closed-world refusal. Run with `python3 -m unittest discover -s scripts -p 'test_*.py' -v`. |
| [`sample_references.py`](sample_references.py), [`verify_references.py`](verify_references.py), [`index_references.py`](index_references.py) | Inventory immutable media, extract timestamped native frames, verify hashes/dimensions/coverage and generate Markdown reference indexes. [Reference procedure](../docs/research/reference_index.md), [exact sampling commands](../evidence/task-04/commands.txt). |
| [`verify_task01.py`](verify_task01.py) | Historical source/layout integrity check. Its original toolkit hash and repository layout predate later tasks. |

## Task-local validation and replay

| Path | Use |
| --- | --- |
| [`evidence/task-22/link_shaders.py`](../evidence/task-22/link_shaders.py), [`evidence/task-12/check_glsl.py`](../evidence/task-12/check_glsl.py) | Expand Iris includes with the render-stage defines and link vertex/fragment pairs offline with `glslangValidator`. The TASK-22 entry point covers all 13 accepted programs. |
| [`evidence/task-28/`](../evidence/task-28/README.md) | `replay.py` stages and restores the fixture and checks transitions. `session.sh` verifies the menu and runs the live checks. `motion_input.c` supplies continuous scoped movement via the existing input device. `review.py` verifies saved stills, clips and logs offline. |
| [`evidence/task-25/`](../evidence/task-25/README.md) | `replay.py` and `session.sh` stage the original visual comparison. `comparisons.py` builds native-frame pairings and reference sheets from `presets.json` and the TASK-04 sample index. `fog-commands.txt` replays the accepted fog follow-up. |
| [`evidence/task-26/`](../evidence/task-26/README.md) | `variants.py` prepares disposable ablations. `replay.py`, `matrix.sh` and `session.sh` run paired client sessions. `review.py` and `compare.py` produce the runs and deltas. `gpu.sh`, `geometry_timer.c` and `summarize_gpu.py` time and summarize paired draws, reusing the TASK-18 sky timer and TASK-23 final timer. |
| [`evidence/task-27/`](../evidence/task-27/README.md) | `optimize.py` and `session.sh` stage and run the shadow and fog trials. `gpu.sh` and `shadow_timer.c` measure offscreen work. `review_results.py`, `visuals.sh` and `visual_metrics.py` summarize samples and visual changes. |
| [`evidence/task-23/`](../evidence/task-23/README.md) | `replay.py` and `session.sh` capture motion and stills. `hold_key.c` supplies continuous input. `gpu.sh` and `final_timer.c` time the isolated spatial AA trial. |
| [`evidence/task-18/`](../evidence/task-18/README.md) | `sky_timer.c` and `summarize_gpu.py` time and summarize paired sky draws. The shell and Python replay files capture the client comparisons. |

Earlier task directories contain their own configuration, fixture,
`replay.py`, `session.sh` and reviewer scripts as needed. Keep those
files in place because later replays import earlier modules. Use each
task's [command record](../evidence/README.md#replay-by-task) for its
historical shader snapshot and fixture.
