# Evidence and replay index

Use task-scoped directories (`evidence/task-XX/`) for future generated evidence.
Record exact commands, capture conditions, source timestamps where relevant, and
relative artifact paths in `docs/TEST_LOG.md`. Keep raw captures, logs and metrics
local and ignored by default; selectively track small reviewed text indices.
Ignored evidence must be transferred separately when a later handoff needs it.

## What to transfer

- **Working source and reviewed evidence.** Include `shaderpack/`, `tools/`,
  `scripts/`, `docs/`, `README_DEV.md` and the task files under `evidence/`
  that Git includes or lists as eligible. Keep the paths below relative to
  the source root. The committed tree through TASK-05 is older than the
  accepted shaders and most of the replay tools.
- **Fixture worlds.** With the dedicated client stopped, place a copy of
  [the preserved TASK-03 fixture](../artifacts/task-30-regression/fixtures/TASK-03%20Visual%20Scenes/)
  in the destination instance as [described below](#install-the-task-03-fixture).
  Keep the copy under `artifacts/` as the reproducible input.
  TASK-28 also reads `artifacts/task-22/world/` and
  `artifacts/task-25-fog-tuning/shaders/`. TASK-26 and TASK-27 need the
  TASK-25 fog-tuned world, shader snapshot, saved menu guards and earlier
  fixture data. Preserve their paths as listed in the replay table.
- **Raw captures and historical inputs.** Keep the existing
  `artifacts/task-*/` directories locally for the full replay history.
  They contain source snapshots, world copies, comparison sheets, stills,
  motion clips, logs, profile ZIPs and raw CPU and GPU samples. Keep the
  original supplied `references/` and `artifacts/task-04/` for the
  visual comparison. The two research clones under `artifacts/task-07/`
  and the official clones under `artifacts/task-06/` are provenance inputs.
  Inspect local logs and world metadata before sharing them with another
  developer. [Environment and log collection](../docs/minecraft-environment.md#toolkit).

## Install the TASK-03 fixture

Run from the source root with the dedicated client stopped. The commands
verify the archive and create a new `minecraft/saves/TASK-03 Visual Scenes/`
folder. If the destination exists, compare it to the archive with
`diff -rq -- "$fixture" "$dest"` after setting the paths below.
Keep the installed fixture idle for checksum-based replays. Opening and
saving it can change the world files that older benchmark checks expect.

```bash
set -euo pipefail
game=$(python3 tools/minecraft.py paths | python3 -c 'import json, sys; print(json.load(sys.stdin)["minecraft"])')
root=$(realpath artifacts/task-30-regression)
fixture="$root/fixtures/TASK-03 Visual Scenes"
(cd "$fixture" && sha256sum --quiet -c "$root/original-world.sha256")
dest="$game/saves/TASK-03 Visual Scenes"
mkdir -p -- "$game/saves"
mkdir -- "$dest"
cp -a -- "$fixture/." "$dest/"
```

## Replay prerequisites

Archived command files are records of the runs. Some older ones expect
the historical shader version in `shaderpack/shaders/`, assume an
existing world or use fixed output paths. Read each record before running
it, use a separate source copy and fresh outputs, and apply the documented
cleanup and settings restoration. TASK-26 and TASK-27's `verify_state.sh`
read `artifacts/task-22/source-world.sha256` at that fixed path. On another
account or machine, rebase the absolute paths in that file in a separate
replay copy of the workspace. Keep the saved manifest with the original
evidence. This verifies the same hashes against the preserved fixture on
the destination machine from that replay copy. Run it after installing
the fixture above, with `dest` still set in the same shell.

```bash
python3 - "$dest" <<'PY'
from pathlib import Path
import sys

manifest = Path("artifacts/task-22/source-world.sha256")
fixture = Path(sys.argv[1]).resolve()
anchor = "/saves/TASK-03 Visual Scenes/"
entries = []
for line in manifest.read_text().splitlines():
    digest, path = line.split("  ", 1)
    relative = path.split(anchor, 1)[1]
    entries.append(f"{digest}  {fixture / relative}")
manifest.write_text("\n".join(entries) + "\n")
PY
sha256sum --quiet -c artifacts/task-22/source-world.sha256
```

The TASK-28 and TASK-30 replay scripts write world manifests relative to
the roots they inspect. Those manifests need no path rebasing.

## Replay by task

| Task | Commands and results | Retained raw evidence and replay inputs |
| --- | --- | --- |
| 00 · Client access | [Environment and toolkit commands](../docs/minecraft-environment.md) | `artifacts/task-00/` |
| 01 · Project integrity | [Verification record](task-01/verification.txt), [input manifest](task-01/input-integrity.json) and [historical verifier](../scripts/verify_task01.py) | Original brief, plan, agent instructions and reference media remain local. The toolkit and directory layout subsequently changed. |
| 02 · Capture and profiling harness | [Commands](task-02/commands.txt), [results](task-02/results.json), [harness guide](../docs/testing/harness.md) | `artifacts/task-02/`, including the original test-world backup |
| 03 · Seven fixed scenes | [Commands](task-03/commands.txt), [results](task-03/results.json), [scene setup and replay](../docs/testing/scenes.md#replay) | `artifacts/task-03/` and the TASK-03 fixture in the dedicated instance. The original preparation uses a copy of `New World`. |
| 04 · Reference sampling | [Commands](task-04/commands.txt), [verification](task-04/verification.txt), [inventory](../docs/research/reference_index.md) | `references/` and the 144 decoded frames and contact sheets in `artifacts/task-04/` |
| 05 · Visual rubric | [Commands](task-05/commands.txt), [rubric](../docs/research/style_targets.md#repeatable-qualitative-comparison) | TASK-03 captures and TASK-04 sampled reference frames |
| 06 · Iris API study | [Commands](task-06/commands.txt), [feasibility](../docs/research/iris_feasibility.md) | Pinned documentation and source clones in `artifacts/task-06/` and the installed Iris JAR |
| 07 · Upstream study | [Commands](task-07/commands.txt), [provenance](../docs/research/implementation_patterns.md) | Two pinned research clones in `artifacts/task-07/` |
| 08 · Architecture gate | [Commands](task-08/commands.txt), [design](../docs/architecture/shaderpack_design.md) | TASK-06 and TASK-07 records |
| 09 · Neutral pack | [Commands](task-09/commands.txt), [results](task-09/results.txt) | `artifacts/task-09/`, TASK-03 world and neutral source at `artifacts/task-11/variants/neutral/shaders/` |
| 10 · Sodium/neutral baseline | [Commands](task-10/commands.txt), [baseline](../docs/testing/baseline.md) | `artifacts/task-10/`, TASK-03 world and the same neutral snapshot |
| 11 · Grading | [Commands](task-11/commands.txt), [report](../docs/testing/palette.md) | `artifacts/task-11/` (neutral and graded variants, captures and profiles), TASK-03 world |
| 12 · Sunlight | [Commands](task-12/commands.txt), [report](../docs/testing/sunlight.md) | `artifacts/task-12/`, TASK-11 graded snapshot and TASK-03 world |
| 13 · Ambient | [Commands](task-13/commands.txt), [report](../docs/testing/ambient.md) | `artifacts/task-13/`, TASK-12 sunlight snapshot and TASK-03 world |
| 14 · Sky | [Commands](task-14/commands.txt), [report](../docs/testing/sky.md) | `artifacts/task-14/`, TASK-13 ambient snapshot and TASK-03 world |
| 15 · Distance fog | [Commands](task-15/commands.txt), [report](../docs/testing/fog.md) | `artifacts/task-15/`, TASK-14 sky snapshot and TASK-03 world |
| 16 · Terrain shadows | [Commands](task-16/commands.txt), [report](../docs/testing/shadows.md) | `artifacts/task-16/`, TASK-15 fog snapshot and TASK-03 world |
| 17 · Prototype checkpoint | [Evidence and commands](task-17/README.md), [report](../docs/testing/prototype_checkpoint.md) | `artifacts/task-17/`, TASK-03 world and TASK-04 frames |
| 18 · Clouds | [Evidence and commands](task-18/README.md), [report](../docs/testing/clouds.md) | `artifacts/task-18/`, TASK-17 control and world integrity records |
| 19 · Water | [Evidence and commands](task-19/README.md), [report](../docs/testing/water.md) | `artifacts/task-19/`, TASK-18 shader control and TASK-03 world |
| 20 · Vegetation | [Evidence and commands](task-20/README.md), [report](../docs/testing/vegetation.md) | `artifacts/task-20/`, TASK-19 shader control and TASK-03 world |
| 21 · Weather | [Evidence and commands](task-21/README.md), [report](../docs/testing/weather.md) | `artifacts/task-21/`, TASK-20 shader control and saved fixture |
| 22 · Lighting and dimensions | [Evidence and commands](task-22/README.md), [report](../docs/testing/lighting_dimensions.md) | `artifacts/task-22/`, TASK-21 shader control and TASK-03 world |
| 23 · Motion and AA | [Evidence and commands](task-23/README.md), [report](../docs/testing/anti_aliasing.md) | `artifacts/task-23/`, TASK-22 shader control and saved fixture |
| 24 · Effects triage | [Dispositions and commands](../docs/architecture/deferred_effects.md#evidence-and-verification) | `artifacts/task-24/` strips and the earlier linked reference and fixture captures |
| 25 · Visual comparison and fog tune | [Original and tuned replay](task-25/README.md), [report](../docs/testing/visual_comparison.md) | `artifacts/task-25/`, `artifacts/task-25-fog-tuning/`, TASK-15 world, TASK-22 shaders and TASK-04 frames |
| 26 · Effect costs | [Evidence and commands](task-26/README.md), [report](../docs/testing/effect_costs.md) | `artifacts/task-26/`, TASK-25 fog-tuned tree, world and menu guard, TASK-22 world manifest and installed TASK-03 world |
| 27 · Optimization trials | [Evidence and commands](task-27/README.md), [report](../docs/testing/optimization.md) | `artifacts/task-27/`, TASK-25 fog-tuned tree and world, TASK-26 menu guard, TASK-16 camera file, TASK-22 world manifest and installed TASK-03 world |
| 28 · Runtime regression | [Evidence and commands](task-28/README.md), [report](../docs/testing/regression_report.md) | `artifacts/task-28/`, TASK-22 world, TASK-25 fog-tuned snapshot and installed TASK-03 world |
| 29 · Compatibility | [Tested stack and commands](../docs/testing/compatibility_notes.md#verification-commands) | TASK-28 shader snapshot and archived client log, installed Prism metadata |
| 30 · Handoff | [Replay and verification commands](task-30/commands.txt), [results](task-30/verification.txt), [handoff](../docs/HANDOFF.md), [known gaps](../docs/KNOWN_GAPS.md) | `artifacts/task-30-regression/` and the [accepted shader manifest](task-25/fog-pack.sha256). Pass a fresh artifact root as the first argument when rerunning the command file. |
