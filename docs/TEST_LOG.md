# Test and evidence ledger

Next-task pointers below describe the handoff at each entry's completion.
[STATUS.md](STATUS.md) tracks the current task boundary.

## TASK-00 — inherited results (2026-11-11)

See [minecraft-environment.md](minecraft-environment.md) for exact prior commands,
versions and observations. Evidence remains local in `artifacts/task-00/`.
These checks were not rerun in TASK-01. The metadata-only probe does not prove
GLSL compilation, in-world rendering or frame-time recording.

## TASK-01 — repository initialization (2026-11-11)

Scope: source layout, preservation, scope consistency, ignores and state ledger.

Commands executed from the repository root:

- `git status --short` — initially failed: `.git` was an empty restricted placeholder.
- `ls -la .git` — confirmed the empty read-only placeholder.
- `git init` — PASS through approved escalated execution; initialized repository.
- `du -sh references` and `rg --files references | wc -l` — approximately 1.5 GiB, 30 files.
- `python3 scripts/verify_task01.py > evidence/task-01/verification.txt` — PASS;
  full repeatable assertions in the script and output in the linked report below.
- `git status --short --untracked-files=all` — reviewed eligible source/text files.
- `git diff --check` — PASS, but initial files are untracked, so this is not
  comprehensive whitespace validation and is not used as proof of content quality.

Before edits, SHA-256/size records were generated for original brief, plan,
AGENTS.md, environment handoff, toolkit and every supplied reference file.
The verification script rereads them and checks the original reference path set,
archive byte equality, required structure and Git ignore behavior. No reference
content was changed or analyzed. Manual review checked scope overrides against
TASK-01 and AGENTS.md, and confirmed the next-task boundary and runtime caveats.

Evidence:
- [Input integrity manifest](../evidence/task-01/input-integrity.json)
- [Verification output](../evidence/task-01/verification.txt)

Result: **PASS for TASK-01**. No commit or remote created, no binaries staged.
No Minecraft launch or shader/performance claims in this task. Local ignored
runtime evidence and original media must be supplied separately at handoff.

## TASK-02 — harness validation (report completed 2026-11-12)

Runtime artifacts carry host timestamps 2026-11-11 21:33–21:45. Commands and paths
are recorded in [commands.txt](../evidence/task-02/commands.txt); usage and detailed
measurement limits are in [harness.md](testing/harness.md).

PASS: real GPU startup twice; isolated world loading by automated mouse input;
2560×1440 window and native F2 screenshots; two validated ten-second native metrics
archives; raw/converted CSV export; configuration/mod snapshots; log collection;
in-world graceful shutdown with players/all dimensions saved and FastQuit finished;
title-screen shutdown and repeated stop returning already stopped.

baseline-01: 2400 samples / 10002 ms; baseline-02: 2399 / 10001 ms. These are
instrumented client CPU render-loop records at the existing 240 FPS cap, with debug
HUD and uncontrolled time/weather. No effect benchmark, GPU latency, shader compile
or visual-style claim. Exact summaries/hashes: [results.json](../evidence/task-02/results.json).
Native ZIPs, CSVs and captures: artifacts/task-02/baseline-01 and baseline-02.
In-world final logs: artifacts/task-02/logs-20261111-214255; second startup/shutdown:
artifacts/task-02/logs-20261111-214542. World backup: artifacts/task-02/world-before.

Initial lowercase debug chords failed to start recording; explicit uppercase
window-targeted F3+L succeeded. Earlier discovery also looked at debug/*.zip;
actual output is debug/profiling/*.zip. Failed probes remain local. One final
screenshot attempt ran before asynchronous launch completed, failed without input,
and was repeated successfully after launch returned its window. Do not issue a
second desktop command until the first process finishes.

Existing optional startup warnings remain. Profiling emitted ERROR/FATAL diagnostic
lines while generating example_crash.txt level dumps containing a dummy exception;
archives completed, rendering continued and safe shutdown passed. No actual client
crash observed. This is not a warning-free compatibility certification.

Automated tests: `python3 -m unittest discover -s scripts -p 'test_*.py' -v` — six
PASS (unit conversion, server exclusion, invalid data/gaps, span/schema rejection,
no overwrite). `python3 -m py_compile tools/minecraft.py scripts/harness.py
scripts/frametimes.py scripts/test_frametimes.py` — PASS. Help command — PASS.
Results: evidence/task-02/tests.txt. Original inputs/references rechecked against
TASK-01 manifest excluding the intentionally extended toolkit. No shader files,
reference contents, loader or installed mods changed. No commit or staging performed.

Changed source: .gitignore; tools/minecraft.py; scripts/harness.py,
frametimes.py, test_frametimes.py, README.md; docs/testing/harness.md;
docs/STATUS.md, DECISIONS.md, TEST_LOG.md; evidence/task-02 text/JSON records.
Status: **DONE**. Next task: **TASK-03**, not started.

## TASK-03 — deterministic scenes (2026-11-12)

**DONE.** Seven scene presets built in a dedicated copy, TASK-03 Visual Scenes,
seed -6092235014036965370. Original New World level.dat SHA256 is unchanged. A
vanilla world-local developer datapack constructs controlled geometry and sets
camera, time, weather and game rules. Installed datapack bytes match source.
Original client settings are backed up; baseline uses vanilla textures, shaders
disabled, 2560×1440, FOV 70, render/simulation distances 12/8, 240 FPS cap and hidden
HUD. Existing enabled mod JAR hashes match TASK-02 exactly.

Real client PASS: build, seven native F2 baselines, three preset repeats after
intervening views, screenshot/config/metadata preservation, revised sunset and
stable shore camera after a restart, graceful save/exit and all-dimensions-save
confirmation. Final saved player XYZ is 974.5,183,1020.5, confirming shore position.
Final baseline sunset/open-water are `-02`; their `-01` images are superseded
exploratory camera views. Other presets use `-01`. All accepted images are 2560×1440.

Repeat QA: full-frame visual review confirmed identical static landmark/camera
alignment. Daylight and forest lower-half pixel MAE = 0; full-frame cave normalized
MAE = 0.000641911. Full-frame outdoor values 0.0139199 / 0.0211061 include moving
clouds. No similarity/artistic-quality score inferred. Details/hashes:
[evidence/task-03/repeats.json](../evidence/task-03/repeats.json).

Exact successful commands and exploratory input failures:
[commands.txt](../evidence/task-03/commands.txt). Automated checks:

- `python3 -m unittest discover -s scripts -p 'test_*.py' -v` — **9 PASS**,
  including scene-world lock guard, build bounds/command limits and camera/spec
  agreement; six existing frame-time tests remain passing.
- `python3 -m py_compile scripts/scenes.py scripts/test_scenes.py scripts/compare_scenes.py`
  — PASS; `python3 scripts/scenes.py --help` — PASS.
- `python3 scripts/compare_scenes.py artifacts/task-03 > evidence/task-03/repeats.json`
  — PASS for three repeats, with numerical and visual checks kept distinct.
- SHA256 recheck of 34 original manifest inputs/references, excluding the historical
  toolkit hash intentionally changed in TASK-02 — PASS. No references changed.
- Closed-world input guard, installed/source datapack equality, saved camera,
  final PNG dimensions/preset metadata and unchanged mod inventory — PASS.

Initial text commands changed punctuation (slash to pipe, colon to caret); clipboard
probes also produced no command acknowledgment. These failed probes were not accepted
as evidence. Final runner uses number keys and never reads/writes the clipboard.
Initial unit test forkserver was denied a sandbox socket; explicit Linux fork context
resolved the test without escalation. Pillow was absent, so ImageMagick supplied
contact sheets and pixel comparisons. No new dependency was installed.

Runtime evidence: `artifacts/task-03/`, including native PNGs, three contact sheets,
`preparation/`, `environment/` and logs. Capture-series/save logs:
`logs-20261112-012205/`; final revised-camera/save logs: `logs-20261112-012427/`.
No ERROR/FATAL lines in the final runtime log; existing optional mixin/class warnings
and sampler warning remain. The client is stopped. No shader compile/performance
claim or broad compatibility certification. Large artifacts and the saved world
remain local/ignored and must accompany the handoff.

Changed files: `.gitignore`; `scripts/scenes.py`, `scripts/scenes/` datapack and
manifest, `scripts/test_scenes.py`, `scripts/compare_scenes.py`, `scripts/README.md`;
`docs/testing/scenes.md`, `docs/STATUS.md`, `docs/DECISIONS.md`, this log; reviewed
`evidence/task-03/{commands.txt,tests.txt,repeats.json,results.json}`.
No commit/staging, shader implementation or reference-analysis work performed.
Limitations: small synthetic grove/basin/cave; animation not phase-locked; 240 FPS
cap retained; visual baselines only. Next task: **TASK-04**, not started.

## Documentation drift correction (2026-11-12)

DONE: CODEX_TASKS.md now delegates progress/next-task state to STATUS.md;
testing/harness.md links the completed TASK-03 scene workflow instead of requesting
it as future work; SCOPE_OVERRIDES.md distinguishes TASK-00's historical limits from
TASK-02's completed frame-time recording and TASK-03's visual baselines.
Validation: reviewed these three documents against STATUS.md and the task evidence;
checked their local Markdown links resolve. Documentation only; no runtime tests
needed and no implementation or scope decisions changed. Next task remains TASK-04.

## TASK-04 — reference inventory and sampling (2026-11-12)

**DONE.** Accounted for all 30 sources: 19 settings JPEGs and 11 gameplay MP4s.
TASK-04-VID-001 through TASK-04-VID-011 are complete. Extracted 144 native-size
1920×1080 PNGs at source start, five-second marks and final decoded frame; actual
presentation timestamps, zero-based frame indices, source paths and hashes are
recorded for every frame. Generated 11 labeled video contact sheets and one settings
sheet. All sheets visually inspected; settings 12/13 and the rain sample at
02.mp4 / 45.016650 s additionally inspected at full resolution. Cataloged sampled
scene groups and coverage limitations without advancing to visual target selection.

Commands executed from the repository root:

- `python3 scripts/sample_references.py > evidence/task-04/sampling.txt 2>&1`
  — PASS, initial extraction and subsequent hash-validated cache/rebuild run.
- `python3 scripts/index_references.py` — PASS, source and complete frame indexes.
- `python3 scripts/verify_references.py > evidence/task-04/verification.txt`
  — PASS: 34 original input hashes unchanged (historically extended toolkit excluded),
  all 30 sources accounted for, 144 PNG hashes/dimensions checked, start/interior/end
  sampling for every clip, gaps <5.1 seconds, all samples covered by scene notes,
  and 434 Markdown local links resolve.
- `python3 -m py_compile scripts/sample_references.py scripts/verify_references.py scripts/index_references.py`
  — PASS.
- `git check-ignore artifacts/task-04/video-01/frame-001.png references/video/gameplay/01.mp4`
  — PASS, originals/generated media remain ignored. Reviewed `git status --short
  --untracked-files=all`; small TASK-04 evidence is eligible for version control.

Evidence: [reference inventory](research/reference_index.md),
[frame index](research/frame_index.md), [verification](../evidence/task-04/verification.txt),
[commands](../evidence/task-04/commands.txt), metadata/hashes/scene notes and exact
FFmpeg argument arrays under `evidence/task-04/`. Tool versions recorded there.
Native PNGs/contact sheets: `artifacts/task-04/` (~207 MiB, local/ignored).
Original `references/` and generated media must accompany the developer handoff.

Changed files: `.gitignore`; `scripts/{sample_references,verify_references,index_references}.py`;
`scripts/README.md`; `docs/research/{reference_index,frame_index}.md`;
`docs/{STATUS,DECISIONS,TEST_LOG}.md`; `evidence/task-04/` text/JSON records.
No original source changes, shader implementation, Minecraft execution, commit or
staging. No benchmark or implementation-feasibility claims.

Limitations: still sampling can miss brief events and cannot validate temporal
behavior; compressed recordings have unknown capture/settings provenance; no full
conventional cave/interior gameplay sequence or controlled settings A/B evidence
was identified in samples. Scene ranges group sampled observations, not exact cut
boundaries. No blocker remains. Next task: **TASK-05**, not started.

## TASK-05 — visual targets and qualitative rubric (2026-11-12)

**DONE.** [style_targets.md](research/style_targets.md) defines seven ranked essential
signatures, observed reference relationships, proposed cheap first-choice algorithms,
scene-specific pass checks, optional embellishments and out-of-scope asset needs.
Rubric separates qualitative status/direction, temporal evidence and performance;
no Genshin similarity percentage or implementation-support claim is introduced.

Visually inspected ten TASK-04 PNGs from nine source clips: video/frame pairs
01/001, 06/001, 03/009, 02/010, 08/008, 09/013, 07/009, 11/004, 02/001, 10/011.
Their exact source presentation times and clickable evidence are in the deliverable.
Also reviewed TASK-03 lighting/materials contact sheets and final sunset-02 and
open-water-02 captures; superseded -01 views are not accepted comparison anchors.
Identified limited distant-geometry and water-depth coverage and retained explicit
motion/snow/cave-reference gaps. No new media extraction or Minecraft launch needed.

Exact repeatable validation command from repository root:

```sh
bash evidence/task-05/commands.txt > evidence/task-05/verification.txt
```

The [command record](../evidence/task-05/commands.txt) contains the existing
`python3 scripts/verify_references.py` integrity check plus an inline Python check
of local links, trailing whitespace, source/frame/timestamp agreement and target
section count. [Verification output](../evidence/task-05/verification.txt) records
results. Manual acceptance review checked all seven evidence/scene/criterion
mappings and that algorithm ratings are provisional. This validates documentation,
not attainment of the visual targets. No runtime/unit-test suite was required for
this documentation-only change.

Changed files: docs/research/style_targets.md; docs/STATUS.md; docs/DECISIONS.md;
docs/TEST_LOG.md; .gitignore; evidence/task-05/commands.txt and verification.txt.
Original reference integrity rechecked; no reference, shader, test-world or client
configuration edits. No commit/staging. Native media remains local/ignored and
must accompany the developer handoff. Limitations: still evidence only, unknown
source settings, incomplete test-scene coverage; candidate Iris feasibility and
performance remain unverified. No blocker for TASK-05. Next: **TASK-06**, not started.

## TASK-06 — Iris capability constraints (2026-11-12)

**DONE.** [iris_feasibility.md](research/iris_feasibility.md) maps all seven essential
signatures to feasible minimum methods, named uncertainties and scoped limitations.
Investigated passes, GLSL patching, light/texture/depth inputs, shadows, weather/time,
dimensions, material IDs and compatibility. Official docs/source revisions and 35
file hashes are in [sources.json](../evidence/task-06/sources.json). Inspected installed
Iris metadata and selected class byte strings; this is not runtime validation.

Current 1.21.1 source is not proven to build the installed beta. Its HEAD fixes
block-entity shadows; current docs warn about separate AO without shadows and have
historical material-ID width inconsistency. Water opaque-depth access is supported,
but correct thickness, shoreline/transparency and underwater behavior need later
real-client tests. Matrix full-name byte searches returned false because source
constructs names; these negatives are not unsupported-uniform findings.

Exact repeatable check:

```sh
bash evidence/task-06/commands.txt > evidence/task-06/verification.txt
```

The [command record](../evidence/task-06/commands.txt) also records clone commands
and evidence collection (`python3 evidence/task-06/collect_sources.py`). Network
source reads used scoped approved execution after sandbox DNS failed. No access
settings changed. [Verification](../evidence/task-06/verification.txt) checks pinned
revisions, source/JAR hashes, target coverage, citation mapping and local links.
No runtime/unit test suite is appropriate for this research-only deliverable.

Changed files: docs/research/iris_feasibility.md; docs/{STATUS,DECISIONS,TEST_LOG}.md;
.gitignore; evidence/task-06/{sources.json,collect_sources.py,commands.txt,verification.txt}.
Ignored source/docs clones: artifacts/task-06/{iris-source,iris-docs}. Original media,
shaderpack, test world, mods and instance configuration remain unchanged; no commit
or staging. No upstream shaderpack study or final architecture chosen. No performance
or wider compatibility claim. No blocker remains. Next: **TASK-07**, not started.

## Documentation drift correction (2026-11-12, after TASK-06)

**DONE.** User-requested follow-up; no numbered task advanced. Labeled TASK-03/04/05
next-task pointers as historical, linked TASK-05 provisional feasibility to TASK-06,
and clarified the resolved TASK-00 Git limitation. Updated the reference-index
generator to preserve its correction. STATUS remains the current handoff authority.
Dated test results and original integrity manifest remain unchanged.

Changed files: docs/research/{style_targets,reference_index}.md;
docs/testing/scenes.md; docs/minecraft-environment.md;
docs/{STATUS,DECISIONS,TEST_LOG}.md; scripts/{index_references,verify_references}.py.
The reference verifier now excludes the authorized environment-document wording
edit from TASK-01's historical hashes, alongside the prior toolkit exception; it
still hashes every original reference source and extracted PNG.

Exact commands and observed results:

- `python3 scripts/index_references.py` — PASS; regenerated 30-source/144-frame indexes.
- `python3 scripts/verify_references.py` — PASS; 33 unchanged original inputs,
  all 30 reference sources, 144 PNGs, scene coverage and 435 local links verified.
- `bash evidence/task-06/commands.txt` — PASS; pinned source/JAR hashes,
  target/source coverage and deliverable/ledger links.

Evidence: corrected documents and the existing manifests under evidence/task-04/
and evidence/task-06/; check results above are from this follow-up, not replacements
for historical verification files. No client execution or shader changes. No blockers.
Next task: **TASK-07**, not started.

## TASK-07 — Targeted upstream shaderpack study (2026-11-12)

**DONE.** TASK-07-A/B studied MakeUp Ultra Fast and Complementary Reimagined;
TASK-07-C synthesized original alternatives and verified provenance. Deliverable:
[implementation_patterns.md](research/implementation_patterns.md). Two approaches
for each S1–S7, exact modules, upstream revisions/licenses, structural cost estimates,
rejected dependencies and TASK-08 runtime questions. No source or assets reused.

Exact acquisition/check commands are in [commands.txt](../evidence/task-07/commands.txt).
Repeat validation from the repository root:

```sh
bash evidence/task-07/commands.txt > evidence/task-07/verification.txt
```

Checks: two pinned clean clones, 19 source/license hashes and permalinks, S1–S7
alternative coverage, local handoff links, absence of GLSL implementation and the
existing original-reference/frame integrity verifier. See
[verification.txt](../evidence/task-07/verification.txt) for observed results.
Initial sandbox clone failed DNS; scoped approved network clone succeeded without
changing access settings. No shader compilation/client/benchmark test applies to
this research-only change; source inspection is not runtime acceptance.

Changed files: docs/research/implementation_patterns.md; docs/{STATUS,DECISIONS,TEST_LOG}.md;
.gitignore; evidence/task-07/{sources.json,verify.py,commands.txt,verification.txt}.
Ignored evidence: artifacts/task-07/{makeup,complementary}. Existing shaderpack,
original references, client configuration and world were not edited. No staging
or commit. Limitations: beta AO/shadows/water ordering, scene coverage and temporal
QA remain unresolved. No research blocker. Next: **TASK-08**, not started.

## TASK-08 — Iris-only architecture gate (2026-11-12)

**DONE.** [shaderpack_design.md](architecture/shaderpack_design.md) selects forward
geometry lighting, one linear RGBA16F color attachment, final output processing
and one bounded later shadow pass. It defines color/alpha/depth ownership, material
routes, fog/transparency approximations, S1–S7 methods, numbered implementation
sequence, blocked/reduced features and concrete later validation gates.

TASK-08-SPIKE was assessed and not run: the minimum does not require separate AO,
block-entity shadows or water depth absorption. Depth-independent water remains
PARTIAL for the depth cue. These are explicit scope reductions/fallbacks, not passed
runtime tests. Read pinned official gbuffers, depth and feature documentation plus
TASK-05–07 inputs; no new online research or upstream code reuse was needed.

Exact validation from repository root:

```sh
bash evidence/task-08/commands.txt > evidence/task-08/verification.txt
```

The check covers local document links, trailing whitespace, S1–S7 coverage, gate
and status markers, absence of GLSL, and the existing reference integrity verifier.
[Observed output](../evidence/task-08/verification.txt) records the results. Manual
review checks that the buffer/pass choice supports each selected method, that
nonlinear depth is not treated as distance, that no scene-color feedback or final
fog pass is assumed, and that deferred feature tests have owners and fallbacks.
Documentation checks are not visual, runtime or performance acceptance. No unit
suite or Minecraft launch is necessary for this documentation-only gate.

Changed files: docs/architecture/shaderpack_design.md; docs/STATUS.md;
docs/DECISIONS.md; docs/TEST_LOG.md; .gitignore;
evidence/task-08/commands.txt and verification.txt. No shader, original reference,
world, mod or instance configuration changes. No staging or commit.
Limitations: all custom GLSL remains untested; water depth/blending, beta shadows,
scene coverage, temporal QA and measured costs remain open in their owning tasks.
No architecture blocker under the documented reductions. Next: **TASK-09**, not started.

## TASK-09 — Minimal loadable shaderpack (2026-11-12)

**DONE.** The installed Iris 1.8.14-beta.1 compiled and loaded the neutral pack
in the Overworld of `TASK-03 Visual Scenes` on Minecraft 1.21.1 / NeoForge
21.1.265 / Sodium 0.8.13. The initial run failed because the framebuffer
format declaration reached the GLSL compiler as code. After moving the Iris
directive into a block comment, a fresh launch logged the pack and the
Overworld pipeline with zero shader compile or pipeline errors. The debug log
records `colortex0` requested as RGBA16F with clearing enabled.

Reused the fixed daylight and cave presets and the 20-second scene warm-up.
The native 2560×1440 daylight image shows grass and stone, cutout foliage and
the shallow basin. The cave image shows dark stone and brighter pools around
the lanterns. The daylight horizon has a hard color boundary with the neutral
scaffold. Exact vanilla fog, transparency, and specialized draw parity were
not exercised. No FPS or effect measurements were collected.

[Exact desktop and GLSL commands](../evidence/task-09/commands.txt) cover the
scoped launch, world selection, both scene captures, save/stop and log
collection, and `glslangValidator -l` for all four expanded shader pairs.
[Static validation](../evidence/task-09/verification.txt) and
[runtime checks](../evidence/task-09/results.txt) record the observed results.
Raw local evidence:

- `artifacts/task-09/logs-20261112-104008/latest.log` records the initial compiler failure.
- `artifacts/task-09/logs-20261112-104212/{latest,debug}.log` record the corrected run.
- `artifacts/task-09/{daylight,cave}/native.png` contain the F2 images, with camera
  presets and client configurations alongside each image.
- `artifacts/task-09/before/` contains the three preflight configuration files.
  The pack copy matched repository sources before removal. After normal world
  save and exit, the scene lock was released and the backed-up options, Iris and
  Sodium files were verified byte-for-byte in the instance. The test world
  advanced normally and retained the last scene and its normal save.

Changed files: `shaderpack/README.md`, `shaderpack/shaders/`, `.gitignore`,
`docs/{STATUS,DECISIONS,TEST_LOG}.md`, and reviewed records in
`evidence/task-09/`. Compatibility evidence covers the tested Overworld
configuration. Next: **TASK-10**, matched Sodium and neutral-pack baselines.

## TASK-10 — Baseline measurements and test matrix (2026-11-12)

**DONE.** Recorded 12 matched 2560×1440 native client profiles in the TASK-03
Visual Scenes world. Daylight, forest and cave each ran twice per mode, with
fresh client sessions in Sodium, neutral, neutral, Sodium order. Both modes
used the same camera presets, fixed time and weather, 20 seconds of focused
warm-up, hidden HUD, VSync off and Unlimited FPS.

All 335,017 client-loop samples passed the schema, continuity and display-update
count checks. The profile spans were 9.993–10.000 seconds. The neutral-pack
averages were 52.7–55.3% lower in profiled client-loop FPS by scene. The
instrumented CPU loop includes waits and has unquantified profiler overhead.
The comparison includes Iris pipeline and scaffold work. See the
[baseline report](testing/baseline.md) for conditions, per-scene distributions
and limitations.

The four session logs identify the expected shader modes, preset acknowledgments
and successful world saves. Both neutral sessions built the Overworld pipeline
with the RGBA16F request. The existing profiler-generated level-dump diagnostic
messages recurred. Before/after screenshot grids show matching scene framing,
hidden HUD and the neutral pack's missing clouds and hard horizon. The dedicated
world saved normally and retained its last scene. The client stopped, the world
lock was released, all five settings files matched their backups byte-for-byte
and the temporary pack was removed.

Changed files include `docs/testing/baseline.md`, the status, decision and test
ledgers, `scripts/{scenes.py,frametimes.py,README.md}`, `.gitignore` and the
reviewed files in `evidence/task-10/`. Exact commands, checks and paths are
recorded in [commands.txt](../evidence/task-10/commands.txt) and
[verification.txt](../evidence/task-10/verification.txt). The original ZIPs,
raw and converted CSVs, screenshots and client logs remain in
`artifacts/task-10/`. Next task is **TASK-11**.

## TASK-11 — Color grading and tonemapping (2026-11-12)

**DONE.** The existing final pass applies fixed scene-linear exposure, bounded
chroma expansion and a smooth highlight shoulder before the sRGB encode.
All four shipped GLSL pairs linked with expanded Iris includes. The tested
Iris beta built the Overworld pipeline in both neutral and graded modes.
See [the palette report](testing/palette.md) for the five native pairs, snow
swatch, diagnostic ramp and performance comparison.

The corrected grade improves the grass-to-stone and foliage-to-bark separation
toward the reference material palette. It preserves the lantern-lit floor,
snow relief and brighter levels inside the sunset sun texture. The first
trial crushed the blue channel on some leaves. The revised chroma bound removed
those zeros in the matched forest frame. No channel reached 255 in the five
graded scene captures. Night retained the existing black sky. The diagnostic
ramps agreed with the expected sRGB output to within one 8-bit code.

Twelve profiles recorded 211,181 client-loop samples under the TASK-10 capture
conditions. Mean loop duration changed by −0.03% in daylight, −0.35% in forest
and +2.41% in cave. Daylight and cave p95 increased in both graded repeats.
See [runs.csv](../evidence/task-11/runs.csv) for ranges and archive hashes.
GPU pass timing and display cadence were outside this measurement.

An early local input attempt triggered the dedicated map's existing build
preset. The final swatch used a temporary, acknowledged scene trigger. Its
30 blocks were removed and the installed datapack was verified against the
repository copy. Every retained session saved the world normally.
GenshinShaderDev stopped with its world lock released, five original settings
files restored byte-for-byte and all three temporary packs removed.

Changed files include `shaderpack/shaders/{final.fsh,lib/tonemap.glsl}`,
`shaderpack/README.md`, `docs/testing/palette.md`, the status, decision and test
ledgers, `.gitignore` and the reviewed files in `evidence/task-11/`.
[Exact commands](../evidence/task-11/commands.txt) and
[verification results](../evidence/task-11/verification.txt) accompany the
raw files under `artifacts/task-11/`. No staging or commit was made.
Compatibility evidence covers the tested Overworld configuration.
Next task is **TASK-12**.

Post-task documentation audit aligned the architecture and research handoff with
the tested grade. TASK-10 and TASK-11 replay now stage hash-verified shader
snapshots. Both command files passed `bash -n`. The two configuration helpers
passed `py_compile` and prepare/restore checks in a temporary instance. The
neutral and graded snapshot manifests and all nine repository tests passed.

## TASK-12 — Sunlight and primary illumination (2026-11-12)

**DONE.** Terrain now uses Iris's sun direction, surface normals and separate
sky/block light levels for a warm directional term with a continuous low-sun
tint and strength curve. The engine lightmap still supplies the fill. The
sunset probe shows a warm west face and cool south face on the same stone
material. Daylight plains grass, oak leaves, bark and stone stay legible. A
fixed-camera sequence checks 15 times plus a repeat of tick 12000 across dusk,
night, dawn and daylight in both modes. The cave retains warm lantern pools
and darker recesses. Some sidewalls brighten with legacy shading disabled.
[Visual report](testing/sunlight.md).

All eight expanded GLSL pairs linked. Four fresh GenshinShaderDev sessions
loaded the expected Iris Overworld pipeline and recorded 16 matched 1440p
profiles with 281,008 client-loop samples. Mean duration changed by +0.44%
in daylight, −1.06% in sunset, +0.67% in forest and +0.95% in cave. The p95
repeat ranges overlap in every scene. The profiles measure instrumented CPU
render loops. GPU pass timing and display cadence remain open.

All four sessions saved the dedicated world normally. The client stopped and
released its world lock. Five settings files and the scene datapack matched
their original bytes after restoration. Both temporary test packs were removed.
The logs contain the existing profiler level-dump diagnostics and show the
expected pack load, target allocation and scene acknowledgments.

Changed files include `shaderpack/shaders/lib/{sunlight,geometry_vertex,geometry_fragment}.glsl`,
`shaderpack/shaders/shaders.properties`, the terrain, block, damagedblock and
water program pairs, `shaderpack/README.md`, the architecture and task ledgers,
`docs/testing/sunlight.md`, `.gitignore` and the reviewed TASK-12 evidence.
The TASK-11 metrics helper accepts the TASK-12 matrix and still reproduces its
original CSV byte-for-byte.

[Replay commands](../evidence/task-12/commands.txt),
[validation results](../evidence/task-12/verification.txt) and
[run metrics](../evidence/task-12/runs.csv) accompany native PNGs, client logs,
profile ZIPs and converted CSVs under `artifacts/task-12/`. Compatibility
evidence covers the fixed scenes on the installed Overworld stack. Continuous
motion, other biomes and dimensions, and specialized draw parity remain open.
Next task is **TASK-13**.

## Documentation drift correction (2026-11-12, after TASK-12)

**DONE.** The architecture now distinguishes the shipped sunlight and fallback
routes from planned passes. The feasibility, style and baseline reports point
to the TASK-12 runtime evidence and its snapshot as the TASK-13 control. The
sunlight report links the pinned Iris matrix and fallback definitions. The
TASK-13 handoff includes a model recommendation and the scenes to compare.

Changed `docs/{STATUS,TEST_LOG}.md`, `docs/architecture/shaderpack_design.md`,
`docs/research/{iris_feasibility,style_targets}.md`,
`docs/testing/{baseline,sunlight}.md`, `shaderpack/README.md` and the artifact
prerequisite comment in `evidence/task-12/commands.txt`.

- A local Markdown link and heading check passed across the project docs and
  the shaderpack, scripts and evidence READMEs.
- `sha256sum -c evidence/task-12/pack.sha256` passed for the live shader tree.
  The same manifest matched the retained TASK-12 sunlight snapshot after
  remapping its paths. `diff -rq shaderpack/shaders artifacts/task-12/variants/sunlight/shaders`
  also passed.
- `python3 evidence/task-12/index_runs.py --artifacts-dir artifacts/task-12 | cmp - evidence/task-12/runs.csv`
  reproduced the retained timing index byte-for-byte.
- `bash -n evidence/task-12/commands.txt` passed and
  `python3 -m unittest discover -s scripts` passed all nine tests.

The [TASK-12 report](testing/sunlight.md) records the tested control for TASK-13.

## TASK-13 — Ambient light and shaded-region response (2026-11-12)

**DONE.** Terrain scales the engine lightmap fill with a cool tint that follows
sun elevation and tapers with block light, direct sun and low skylight. The
forest stone and sunset wall shift cooler while daylight grass and the sunset
doorway retain their sampled values. Night landmarks remain legible. The cave
retains warm lantern pools and a dark ceiling recess. The floor sample near
the lantern varies across captures, including within the ambient run.
[Visual review](testing/ambient.md#visual-review).

All eight expanded GLSL pairs linked. Four fresh GenshinShaderDev sessions
loaded the expected Iris Overworld pipeline, captured five native scene pairs
and recorded 12 matched 1440p profiles. The profiles contain 280,821 CPU
client-loop samples. Mean loop duration changed by +0.72% in forest, +1.48% in
cave and −0.31% at night. GPU timing, display cadence and continuous ambient
transitions remain unverified. [Profile results](testing/ambient.md#performance).

All four sessions saved normally. The client stopped, released the world lock
and restored five settings files byte-for-byte. The installed scene datapack
matched the repository copy. Both temporary shaderpacks were removed.

Changed the terrain program pair and shared geometry includes, and replaced
`shaderpack/shaders/lib/sunlight.glsl` with `terrain_lighting.glsl`. Updated the
shaderpack README, architecture, style and testing reports, task ledgers and
`.gitignore`. Added the ambient report and replay tooling, shader manifest,
pixel samples and run index in `evidence/task-13/`.

[Exact commands](../evidence/task-13/commands.txt) and
[verification](../evidence/task-13/verification.txt) accompany the native
captures, logs and raw metrics in `artifacts/task-13/`. The next task is
**TASK-14**.

## Documentation audit after TASK-13 (2026-11-12)

**DONE.** Updated the architecture, Iris feasibility, sunlight and ambient
reports, shaderpack README and project status to describe the TASK-13 pack
and the remaining sky validation. The handoff records the TASK-14 control
hash check and the temporary trigger requirement for the TASK-12 sweep.
The recommended model is GPT-6 Astra with High reasoning.

- Checked local Markdown links and heading anchors across the project docs,
  shaderpack, scripts and evidence READMEs, and AGENTS.md.
- `sha256sum -c evidence/task-13/pack.sha256` passed on the live shader tree
  and with paths remapped to the retained ambient snapshot.
  `diff -rq shaderpack/shaders artifacts/task-13/variants/ambient/shaders`
  also passed.
- `python3 evidence/task-12/index_runs.py --artifacts-dir artifacts/task-12 | cmp - evidence/task-12/runs.csv`
  and `python3 evidence/task-13/index_runs.py --artifacts-dir artifacts/task-13 | cmp - evidence/task-13/runs.csv`
  reproduced both timing indices.
- `python3 evidence/task-13/sample_pixels.py artifacts/task-13 | cmp - evidence/task-13/pixels.csv`
  reproduced the pixel index. Both TASK-12 and TASK-13 replay command files
  passed `bash -n`. All nine tests passed under
  `python3 -m unittest discover -s scripts`.

TASK-14 is ready to request. This audit used existing captures and profiler
archives. [Project status](STATUS.md).

## TASK-14 — Sky gradients and atmospheric color (2026-11-12)

**DONE.** The Overworld sky blends pale horizon blue, sun-facing peach
and lavender twilight, and cool night blue using sun elevation and view
direction. The sun, moon and stars remain visible. The disc-to-horizon
seam is gone in the paired captures. Daylight grass, night grass and the
cave recess keep their sampled RGB codes.
[Visual review](testing/sky.md#visual-review).

All nine expanded GLSL pairs linked and the installed Iris beta loaded the
Overworld pipeline. The fixed sweep has 20 native frames per pack. The
running dusk and dawn review uses 486 native frames sampled at 3 Hz,
including the day wrap. The earliest test was interrupted by focus loss,
a temporary dawn binding was moved off the cave preset, and X11 recordings
with black bands were replaced with native F2 captures.

Eight matched 1440p profiles contain 184,799 CPU client-loop samples. The
mean loop duration changed by +0.09% in daylight and −1.65% at sunset. GPU
pass timings, cloud coverage and other dimensions remain open.
[Performance](testing/sky.md#performance).

The client saved, released the test world's lock and stopped. Five settings
files and the test-world triggers were restored byte-for-byte. The installed
scene datapack matches the repository copy and both temporary packs were removed.

Added the `gbuffers_skybasic` pair and `lib/sky.glsl`. Updated the shaderpack
README, architecture, Iris feasibility and project ledgers. Added the sky
report and the replay tooling, shader manifest and measurements in
`evidence/task-14/`.
[Exact commands](../evidence/task-14/commands.txt),
[verification](../evidence/task-14/verification.txt).
The next task is **TASK-15**.

## Documentation audit after TASK-14 (2026-11-12)

**DONE.** Updated the architecture, style targets, ambient and baseline
reports, shaderpack README and project status to reflect the tested sky
gradient and the remaining cloud coverage gap. The TASK-15 handoff points
to the verified sky control, the geometry fog contract and the baseline
conditions for new near, middle and far landmarks. The selected Codex
model was GPT-6 Astra with High reasoning. [TASK-15 report](testing/fog.md).

- `sha256sum -c evidence/task-14/pack.sha256` passed for the live shaders
  and the retained snapshot. The two trees match.
- `python3 evidence/task-14/index_runs.py --artifacts-dir artifacts/task-14`,
  `python3 evidence/task-14/review.py pixels artifacts/task-14` and
  `python3 evidence/task-14/review.py video artifacts/task-14` reproduced
  the retained indices.
- Local Markdown links and anchors resolved. All nine script tests and both
  TASK-14 replay files' Bash syntax checks passed.
  `python3 scripts/verify_references.py` verified the original inputs and
  all 144 reference frame hashes.

## TASK-15 — Distance fog and atmospheric perspective (2026-11-12)

**DONE.** Added a scene-linear distance and chroma ramp with the TASK-14
horizon color and sunward twilight tint. Rain shortens the ramp. Six
presets compared Sodium, TASK-14 and TASK-15 at 2560×1440. Foreground grass,
trunk and cutout edge patches match the daylight control. The distant
ridges approach the horizon while the near water, glass and cave remain
readable. The captured edges passed the visual halo and transition checks.
[Visual comparisons and limitations](testing/fog.md#visual-review).

All ten expanded GLSL pairs linked. Iris loaded the selected Overworld
pipeline with the existing RGBA16F target. Six fresh sessions produced
12 matched profiles with 397,216 CPU client-loop samples. Mean duration
rose by 0.49% in daylight and 1.02% at sunset versus the sky control.
GPU pass duration, long enclosed sightlines, live weather changes and
submerged views remain unverified. [Profile results](testing/fog.md#performance).

The fixture was built and tested in a copy of the TASK-03 world. The
setup retries corrected chunk availability and trunk fill order before the
accepted runs. The client saved and released the copy's lock. All five
settings files were restored byte-for-byte and both temporary packs were
removed. The original world passed 75 file hash checks. The copied world
is archived alongside the screenshots, raw profiles and logs under
`artifacts/task-15/`.

Changed the shared geometry includes, textured fallback vertex entry
points, sky and terrain lighting helpers, and added the fog module and
textured sky pair. Updated the shaderpack README, style targets, design,
baseline and sky handoffs, and task ledgers. Added the fixture, replay
tools, manifest and measurement indices under `evidence/task-15/`.
[Exact commands](../evidence/task-15/commands.txt),
[verification](../evidence/task-15/verification.txt).
The next task is **TASK-16**.

## Documentation audit after TASK-15 (2026-11-12)

**DONE.** Updated the architecture, Iris feasibility notes and sky and fog
reports to reflect the implemented fog and draw routes. Repaired the historical
TASK-15 handoff link. The TASK-16 handoff identifies the installed-beta
caster coverage checks and requires fresh fog-control timings on the same
shadow test cameras. The recommended model is GPT-6 Astra with High reasoning.
[TASK-16 report](testing/shadows.md).

- Local Markdown links and heading anchors resolved. The source and retained
  TASK-15 snapshot both passed the shader manifest check.
- The timing and pixel indices reproduced with
  `python3 evidence/task-15/index_runs.py artifacts/task-15` and
  `python3 evidence/task-15/review.py artifacts/task-15`.
- All nine tests passed with `python3 -m unittest discover -s scripts`.
  Both TASK-15 replay files passed `bash -n`.
  `python3 scripts/verify_references.py` verified the original inputs and all
  144 reference frame hashes. The audit used the retained client evidence.

The next task is **TASK-16**.

## TASK-16 — Basic optimized shadows (2026-11-12)

**DONE.** Added the depth-only solid and alpha-tested caster programs and
the bounded terrain receiver. The retained source uses a 1024² map, one
hardware-filtered lookup and base-level caster alpha. Stone, oak leaves,
the chest and cutout glass frame cast on terrain in the installed beta.
Matched screenshots cover contact, low sun, the range fade, forest,
open water, cave and night. Eleven distinct fixed-angle camera frames
cover ten 1/16-block steps. [Shadow report](testing/shadows.md).

- All 12 shader pairs linked with `glslangValidator -l` and the recorded
  render-stage defines. The installed Overworld pipeline loaded without
  shader errors. All nine tests passed with
  `python3 -m unittest discover -s scripts`.
- `python3 evidence/task-16/index_runs.py artifacts/task-16` verified 12
  accepted F3+L archives, matched settings and 362,699 raw CPU loop samples.
  Mean incremental cost versus TASK-15 fog was +0.0432 ms in forest and
  +0.0426 ms in the low-angle pad scene. GPU pass timings and continuous
  motion remain unverified. [Timing index](../evidence/task-16/runs.csv).
- The scoped client saved and exited. All five settings files were restored
  byte-for-byte and 75 source-world hashes matched. Keep the final snapshot,
  full logs, captures and raw profiles under `artifacts/task-16/`.
  [Exact replay and verification commands](../evidence/task-16/commands.txt),
  [verification record](../evidence/task-16/verification.txt).

The next task is **TASK-17**.

## Documentation audit after TASK-16 (2026-11-12)

**DONE.** Updated the status, architecture, feasibility, style rubric,
decision log and lighting reports to reflect the tested shadow coverage.
Recorded the checkpoint inputs, required report and decision in the
[TASK-17 checkpoint status](STATUS.md#task-17-checkpoint). Selected
GPT-6 Astra with High reasoning for the combined visual review, timing
analysis and checkpoint decision.

- The TASK-16 source and retained shadow snapshot matched the pack manifest.
  `python3 evidence/task-16/index_runs.py artifacts/task-16` and
  `python3 evidence/task-16/review.py artifacts/task-16` reproduced the
  retained timing and pixel indices.
- Local links and heading anchors resolved in the current project docs.
  All nine harness tests passed with `python3 -m unittest discover -s scripts`.
  `python3 scripts/verify_references.py` verified the original inputs and
  all 144 reference frame hashes.

The next task is **TASK-17**.

## TASK-17 — Prototype checkpoint (2026-11-12)

**DONE — CONTINUE.** Compared the verified TASK-16 pack with Sodium shaders
off in all seven TASK-03 presets at 2560×1440. Each mode ran twice in fresh
sessions. Reviewed the matched PNGs against the indexed R1–R10 stills and
the S1–S7 rubric. The checkpoint records the remaining cloud, water and rain
gaps and the next priorities. [Checkpoint report](testing/prototype_checkpoint.md).

- The 28 archives contained 986,782 CPU render-loop samples, with mean
  increases of 0.267–0.304 ms per scene over shaders-off. Both prototype
  runs loaded the RGBA16F Iris pipeline and all four sessions saved cleanly.
  GPU pass timing and display cadence remain open.
  [Timing index](../evidence/task-17/runs.csv).
- `python3 evidence/task-17/index_runs.py artifacts/task-17` validated
  runtime, mod hashes, options, preset acknowledgments, image dimensions,
  and the raw archive samples. `bash evidence/task-17/comparisons.sh
  artifacts/task-17` produced the comparison and before/after grids.
- `python3 -m unittest discover -s scripts` passed nine tests. The Python
  replay/index modules and Bash scripts passed syntax checks. The reference
  integrity script verified 33 original inputs and 144 decoded frame hashes.
  The 76 original world file hashes and the 33-file shader manifest matched.
- GenshinShaderDev stopped, all five settings files were restored byte-for-byte,
  and the world copy was archived. Keep the raw archives, images, logs, world
  and shader snapshot under `artifacts/task-17/`.
  [Exact commands](../evidence/task-17/commands.txt),
  [verification](../evidence/task-17/verification.txt).

The next task is **TASK-18**.

## Documentation audit after TASK-17 (2026-11-12)

**DONE.** Clarified the benchmark-only pack activation and shaders-off
restoration in the status, checkpoint and pack README. Updated the
architecture and feasibility records to reflect the missing clouds in
the shader-enabled captures. Updated the baseline and shadow handoffs to
point to the completed checkpoint. The TASK-18 handoff now specifies
incremental GPU timing and records GPT-6 Astra with High reasoning.
[TASK-18 validation](STATUS.md#task-18-validation).

- Both prototype logs identify the loaded pack. The instance's Iris
  settings match the preflight backup and the temporary pack is absent.
- `python3 evidence/task-17/index_runs.py artifacts/task-17 | cmp evidence/task-17/runs.csv -`
  reproduced the 28-profile index. The source and retained shader snapshot
  match the 33-file TASK-16 manifest.
- `python3 -m unittest discover -s scripts` passed nine tests.
  `python3 scripts/verify_references.py` verified 33 original inputs and
  144 reference frames. Local documentation links and heading anchors resolved.

The next task is **TASK-18 — Lightweight stylized clouds**.

## TASK-18 — Lightweight stylized clouds (2026-11-12)

**DONE.** The final cloud layer renders in the existing Overworld sky draw.
Compared five matched native 2560×1440 captures with the TASK-17 prototype.
The sunset has peach cloud shapes, the rain view has a slate deck and the
night view retains stars in cloud gaps. The daylight foreground crop
matched byte-for-byte and the cave retained lantern contrast.
[Cloud report](testing/clouds.md).

- All 12 expanded shader pairs linked with `glslangValidator -l`.
  `python3 -m unittest discover -s scripts` passed nine tests.
  `python3 scripts/verify_references.py` verified the 33 original inputs and
  144 decoded reference frames.
- Two NVIDIA EGL runs measured 256 paired batches in total. The median
  incremental sky-draw GPU time was 0.011–0.013 ms in the preset-like
  views and about 0.023 ms in the upward stress case. Integrated frame time
  remains unmeasured. [Timing summary](../evidence/task-18/gpu-summary.csv).
- Both accepted Iris sessions logged the selected pack, five scene
  acknowledgements and a graceful world save. Five preflight files were
  restored byte-for-byte. The temporary packs were removed, the copied
  world was archived, and the original world's 76 hashes matched.
  [Exact commands and checks](../evidence/task-18/commands.txt),
  [evidence index](../evidence/task-18/README.md).

The next task is **TASK-19 — Stylized water**.

## Documentation audit after TASK-18 (2026-11-12)

**DONE.** Updated the TASK-19 handoff with the accepted TASK-18 control,
the `depthtex2` runtime check, the S6 fallback and the daylight/rain evidence
required by the plan. Recorded GPT-6 Astra with High reasoning for the
implementation, live rendering diagnosis and measurement work. Added the
reviewed TASK-18 evidence to the Git allowlist. Raw captures and timers stay
under `artifacts/task-18/`. [Water report](testing/water.md).

- `sha256sum --quiet -c evidence/task-18/pack.sha256` and
  `diff -rq shaderpack/shaders artifacts/task-18/shaders` verified the accepted
  control. The GPU summary reproduced from the three raw CSVs.
- `git ls-files --others --exclude-standard evidence/task-18` lists all nine
  reviewed files. `git check-ignore --quiet artifacts/task-18/gpu-01.csv`
  confirmed the raw timer file remains ignored.
- Local documentation links and heading anchors resolved.
  `python3 -m unittest discover -s scripts` passed nine tests.
  `python3 scripts/verify_references.py` verified 33 original inputs and
  144 reference frames.

The next task is **TASK-19 — Stylized water**.

## TASK-19 — Stylized water (2026-11-12)

The seven changed shader files are the two `gbuffers_water` wrappers,
`block.properties`, and `lib/{water,fog,geometry_vertex,geometry_fragment}.glsl`.
The water branch uses the pre-hand depth snapshot, a bounded tint and opacity
ramp, two normal waves, and a skylight-gated reflection. A shared submerged
fog ramp retains nearby bottom contrast. The exact TASK-18 snapshot was the
incremental control. [Water report](testing/water.md),
[source manifest](../evidence/task-19/pack.sha256).

The matched visual pair captured daylight, rain, sunset, open water,
shoreline, submerged floor and underside at 2560×1440. The depth variant
visualized the basin ramp and underwater branch and covered stained glass
overlap and stone and glass held items. The first trial used spectator mode,
which intercepted hotbar commands. The accepted preset stands on the flat
basin floor in creative mode. A Prism launch timed out while fetching
Mojang's asset index and succeeded on retry. [Replay and logs index](../evidence/task-19/README.md).

Twelve F3+L archives passed the option, mode, preset, runtime and sample
checks. Mean CPU client-loop time increased by 0.0071 ms (+1.3%) in
daylight and 0.0132 ms (+2.3%) in rain versus TASK-18. Sodium shaders-off
averaged 0.2181 ms in daylight and 0.2572 ms in rain. The GPU contribution
and presentation pacing remain unmeasured. [Run index](../evidence/task-19/runs.csv).

`glslangValidator -l` linked 12 expanded production pairs and the diagnostic
water pair. `python3 -m unittest discover -s scripts -p 'test_*.py' -v`
passed nine tests. Python/Bash syntax, capture metadata, static RGB crops,
source manifests and the original reference integrity check passed.
All accepted sessions saved and exited. The fixture world was archived,
three temporary packs were removed, five settings files were restored
byte-for-byte and all 76 TASK-03 world file hashes matched.
[Exact commands](../evidence/task-19/commands.txt),
[verification record](../evidence/task-19/verification.txt).

**DONE.** Shader source, `shaderpack/README.md`, architecture and feasibility
handoffs, the project ledgers, and `evidence/task-19/` are updated. Keep
`artifacts/task-19/` for the saved fixture, shader trees, captures, native
metrics and logs. Flowing and waterlogged edges, continuous underwater
movement, live weather transitions and other dimensions remain unverified.
Next task **TASK-20**.

## Documentation audit after TASK-19 (2026-11-12)

**DONE.** Aligned the architecture, feasibility, style rubric, fog and
checkpoint docs with TASK-19's fixed Overworld water validation. Kept
waterline crossings, continuous motion and broader compatibility as open
checks. Clarified that TASK-20 starts from the existing forest/daylight
presets and adds a dense-canopy fixture. The retained TASK-19 pack is the
incremental control. The handoff recommends GPT-6 Astra with Medium
reasoning for shader changes, visual review and performance validation.
[TASK-20 validation](STATUS.md#task-20-validation).

- `sha256sum --quiet -c evidence/task-19/pack.sha256` and
  `diff -rq shaderpack/shaders artifacts/task-19/shaders` verified the
  accepted pack. Re-running `python3 evidence/task-19/index_runs.py artifacts/task-19`
  reproduced the reviewed CSV.
- Local Markdown paths and heading anchors resolved.
  `python3 -m unittest discover -s scripts -p 'test_*.py' -v` passed nine tests.
  `python3 scripts/verify_references.py` verified 33 original inputs and
  144 reference frames.

## TASK-20 — Vegetation color and lighting (2026-11-13)

`block.properties` maps vanilla leaves and grasses. The shared
`lib/geometry_vertex.glsl` and `lib/terrain_lighting.glsl` apply a bounded
green-tint correction and skylight-weighted fill on off-sun leaf faces.
The material uses the existing draw, alpha tests, interpolants and
shadow programs. Vegetation geometry is static. [Vegetation report](testing/vegetation.md).

Four native TASK-19/TASK-20 pairs cover daylight, forest, dense
understory and canopy tops. The fixture verified short and tall plants,
multiple leaf materials and the plains/jungle biome boundary. Inspected
cutouts retained their silhouettes. Two leaf/sky masks matched, as did
selected stone wall, trunk and lit and shadowed stone path RGB patches.
[Visual evidence](../evidence/task-20/README.md), [pixel patches](../evidence/task-20/pixels.csv).

Twelve matched 1440p F3+L profiles passed the runtime, options, preset,
camera and raw sample checks. An initial control trial lost focus and
was excluded and rerun. Mean CPU client-loop time changed by −0.0046 ms
in daylight and +0.0016 ms under dense canopy versus TASK-19. Dense-canopy
differences changed sign between the two repeats. GPU cost and
presentation cadence remain unmeasured. [Profile index](../evidence/task-20/runs.csv).

`glslangValidator -l` linked all 12 expanded shader pairs.
`python3 -m unittest discover -s scripts -p 'test_*.py' -v` passed nine tests.
Replay syntax, source integrity and reference checks passed. All six accepted
sessions saved and exited. The fixture world was archived, both temporary
packs were removed, five settings files were restored byte-for-byte and
all 76 original TASK-03 world hashes matched.
[Exact commands](../evidence/task-20/commands.txt),
[verification record](../evidence/task-20/verification.txt).

**DONE.** Shader source, project ledgers, vegetation report and replay
evidence are updated. Keep `artifacts/task-20/` for the retained shader
trees and raw evidence. Individual species coverage, waterlogged leaves,
weather transitions and other dimensions remain open. Next task **TASK-21**.

## Documentation audit after TASK-20 (2026-11-13)

**DONE.** Aligned the status, architecture, Iris feasibility, style rubric,
shaderpack README, scene and baseline guides, checkpoint, and water and
vegetation handoffs with the retained evidence. The TASK-21 handoff records
the current rain inputs, the TASK-20 control, settled reference views and
both live transition directions. [Weather report](testing/weather.md).

- `sha256sum --quiet -c evidence/task-20/pack.sha256` and
  `diff -rq artifacts/task-20/shaders shaderpack/shaders` verified the
  accepted source. `python3 evidence/task-20/index_runs.py artifacts/task-20`
  reproduced the reviewed profile index.
- Local Markdown paths and heading anchors resolved. `git diff --check`
  and all nine harness/scene unit tests passed. `python3 scripts/verify_references.py`
  verified 33 original inputs and 144 reference frames.

## TASK-21 — Weather transitions (2026-11-13)

**DONE.** The sky, fog, terrain, water and final grade now share Iris's
rain ramp. The existing precipitation draw uses its own shader pair to
mute blue falling streaks. Six matched endpoint pairs and six native
series cover both directions at fixed midday across daylight, open water
and dense canopy. The 264 native frames show no severe jump or flash at
the sampled cadence. The initial X11 clips had black bands and were
replaced with native captures. [Visual review](testing/weather.md#visual-review).

Twelve matched 1440p profiles recorded mean CPU client-loop changes of
−0.0028 ms in daylight and −0.0013 ms in rain relative to TASK-20. Two
offscreen timer runs measured no added cost in the isolated sky draw.
Full-client GPU cost and presentation cadence remain open.
[Performance report](testing/weather.md#performance).

Changed `final.{vsh,fsh}`, `gbuffers_skybasic.vsh`, added
`gbuffers_weather.{vsh,fsh}`, and updated the sky, fog, clouds, geometry,
terrain lighting, water and tone mapping libraries. Updated the project
ledgers and handoff, shader README, weather report and reviewed replay
evidence. All 13 expanded GLSL pairs linked, nine unit tests passed, and
the accepted client logs show normal saves. Five settings files were
restored, both temporary packs removed and the TASK-03 and TASK-20 source
world files verified byte for byte. [Exact commands](../evidence/task-21/commands.txt),
[verification record](../evidence/task-21/verification.txt).

The raw profiles, native frames, preview clips, shader snapshots and
saved fixture are under `artifacts/task-21/`. Live validation covers
midday Overworld rain. Snow, thunder, rainy twilight and night, underwater
transitions and other dimensions remain open. Next task **TASK-22**.

## Documentation audit after TASK-21 (2026-11-13)

**DONE.** Aligned the shader README, pass table, style and feasibility
notes, and historical effect reports with the accepted TASK-21 source.
Corrected the TASK-20 evidence link and recorded the TASK-21 replay
dependencies and TASK-22 starting snapshot. The TASK-22 handoff points
to the existing night and lantern-lit cave evidence.
[Lighting validation](STATUS.md#task-22-validation),
[weather evidence](../evidence/task-21/README.md).

- `sha256sum --quiet -c evidence/task-21/pack.sha256` and
  `diff -rq artifacts/task-21/shaders shaderpack/shaders` verified the
  current source. Both source-world manifests matched.
- `python3 evidence/task-21/index_runs.py artifacts/task-21` reproduced
  the 12-profile index. The documented review commands reproduced the
  settled, transition and isolated sky GPU summaries.
  [Exact commands](../evidence/task-21/commands.txt).
- Local Markdown links and heading anchors resolved. The nine harness
  and scene unit tests, `bash -n evidence/task-21/commands.txt`, and
  `git diff --check` passed. The reference verifier checked 33 original
  inputs and 144 reference frames. Next task **TASK-22**.

## TASK-22 — Night, caves, artificial lighting and dimensions (2026-11-13)

**DONE.** Added bounded neutral terrain fill and low-light attenuation for
selected lamp faces. Night grass, cave recesses and unlit steps gain detail.
The three sampled wall-mounted sources have lower peak channels, and the
cave lantern pool remains bright. Clear-day terrain crops match TASK-21.
The Nether, End and Overworld return render in the installed client.
The report records dimension atmosphere gaps and untested special cases.
[Lighting and dimensions](testing/lighting_dimensions.md).

Twelve matched 1440p CPU client-loop profiles compare TASK-22, TASK-21 and
Sodium with Iris shaders disabled. Mean changes versus TASK-21 are
+0.004569 ms at night and −0.002247 ms in the cave. GPU cost and presentation
cadence remain unmeasured. [Reviewed profile index](../evidence/task-22/runs.csv).

Changed the terrain lighting and shared geometry libraries plus
`block.properties`. Updated the project ledgers, architecture and shaderpack
handoff. All 13 expanded GLSL pairs linked and nine harness/scene tests
passed. Six accepted sessions saved and exited, five settings files were
restored byte for byte, both temporary packs were removed, and all 76
original scene-world hashes matched.
[Exact commands](../evidence/task-22/commands.txt),
[verification](../evidence/task-22/verification.txt).

Retain `artifacts/task-22/` for native images, raw profiles, logs, shader
snapshots and the saved fixture. Next task **TASK-23**.

## Documentation audit after TASK-22 (2026-11-13)

**DONE.** Corrected the TASK-22 Unlimited FPS setting and the current Git
baseline. Updated the pass table, terrain and weather reports, compatibility
notes, and scene and benchmark guides with the scope of the night, cave and
dimension checks. The TASK-23 handoff identifies the verified shader control,
prior camera-step evidence and the sampling limit of the weather clips.
[Current status](STATUS.md), [lighting report](testing/lighting_dimensions.md).

- The TASK-22 shader manifest, both retained shader trees and all 76
  source-world hashes verified. The profile and pixel reviewers reproduced
  the retained CSVs, covering 12 profiles and patch measurements from the
  matched views. [Replay and evidence](../evidence/task-22/README.md).
- Local Markdown links and heading anchors resolved. Replay shell syntax,
  nine harness and scene tests, and the reference verifier passed. The
  reference verifier checked 33 original inputs and 144 sampled frames.

## TASK-23 — Anti-aliasing and temporal artifacts (2026-11-13)

The TASK-22 pack and the disposable spatial trial each linked all 13 shader
pairs and loaded in the installed Iris client. The motion fixture compares
three clear-day paths against Sodium with shaders off. Native stills show a
smoother diagonal bank and softened foliage holes. Moving cutout shimmer and
some edge crawl remain visible. [Motion review](testing/anti_aliasing.md).

Early X11 clips contained black bands and held X11 key events failed to move
the camera in the first Spectacle trial. The accepted clips use Spectacle's
KWin window capture and one movement key per path through the user's existing
uinput access. Decoded frames are checked for black bands and terrain travel.
[Replay commands](../evidence/task-23/commands.txt).

**DONE.** The nine native stills, nine 1440p clips, and twelve client profiles
passed the evidence checks. The six `GL_TIME_ELAPSED` runs on RTX 4080 SUPER
measured an extra 0.0091–0.0097 ms per isolated final draw. The visual review
defers spatial AA and retains the TASK-22 shader source. Integrated GPU frame
time and presentation pacing remain open. [Reviewed evidence](../evidence/task-23/README.md).

The instance saved and exited, the five settings files matched their backups,
both temporary packs were removed, the fixture was archived and all 76 source
world hashes matched. Nine unit tests, static linking, Python and shell syntax,
C compilation and the reference verifier passed. Next task is TASK-24.

## Documentation audit after TASK-23 (2026-11-13)

**DONE.** Replaced the obsolete TASK-23 handoff link, updated the shaderpack
and feature reports with the AA decision and clear-day motion coverage, and
documented the replay inputs and TASK-24 triage boundary.
[AA report](testing/anti_aliasing.md), [replay index](../evidence/task-23/README.md),
[TASK-24 triage](architecture/deferred_effects.md).

The shader manifest and retained control match. The source-world hashes
and all three TASK-23 evidence indices reproduced. Local documentation links
and heading anchors, replay shell syntax, nine unit tests, and the reference
integrity verifier passed.

## TASK-24 — Additional visual effects triage (2026-11-13)

**DONE.** Reviewed timestamped footage, two supplemental sequence strips
and prior Minecraft captures. Recorded twelve dispositions with expected
GPU work and one optional sun halo trial. This documentation task used no
new Minecraft run or GPU benchmark. [Report, evidence paths and replay commands](architecture/deferred_effects.md).

`python3 scripts/verify_references.py` verified 33 original inputs, 30 media
sources and 144 decoded PNGs. `sha256sum --quiet -c evidence/task-22/pack.sha256`
verified all 38 accepted shader files. `diff -qr shaderpack/shaders artifacts/task-23/shaders`
matched the entire retained control. Both FFmpeg strips reproduced byte for
byte. The review also checked all twelve dispositions, thirteen exact source
timestamps, 287 local links and anchors, and nine harness tests
(`python3 -m unittest discover -s scripts`). Next numbered task is TASK-25.

## Documentation audit after TASK-24 (2026-11-13)

**DONE.** Updated the task entry point, status, style rubric, Iris feasibility,
architecture, feature reports and replay indexes to reflect the TASK-24
decisions. The TASK-25 handoff now identifies the reference cues, report path
and shader manifest. TASK-24A identifies only the optional sun halo trial.
[TASK-25 comparison](STATUS.md#task-25-visual-comparison),
[effects triage](architecture/deferred_effects.md).

The local Markdown path and heading-anchor audit passed across 43 documents.
`python3 scripts/verify_references.py` verified the original media and all
144 decoded frames. The archived brief matched `task.md` byte for byte.
`sha256sum --quiet -c evidence/task-22/pack.sha256` and
`diff -qr shaderpack/shaders artifacts/task-23/shaders` verified the accepted
shader baseline. All nine tests passed with
`python3 -m unittest discover -s scripts`.

## TASK-25 — End-to-end visual comparison (2026-11-13)

**DONE.** Captured eight Overworld views in the accepted Iris pack and
shaders-off Sodium, then repeated the natural valley and cave in a fresh
shader-on session. The labeled sheets pair seven views with timestamped
Genshin stills. The cave guards warm block light and dark recesses.
The report ranks six unresolved art gaps and identifies their shader modules.
[Visual comparison](testing/visual_comparison.md),
[native captures, references and replay](../evidence/task-25/README.md).

`bash evidence/task-25/session.sh artifacts/task-25 pack open` and
`bash evidence/task-25/session.sh artifacts/task-25 sodium` captured the
matched views. The Sodium capture completed before the replay wrapper
failed at shutdown. The scoped toolkit then saved, exited and archived that
session's logs. `bash evidence/task-25/session.sh artifacts/task-25 pack-repeat valley cave`
recorded the repeat. `python3 evidence/task-25/comparisons.py artifacts/task-25`
checked matched settings and reference hashes and built the eight sheets.
[Exact commands and cleanup checks](../evidence/task-25/commands.txt).

The accepted 38-file shader manifest, 13 static GLSL link checks, nine
unit tests, replay syntax and original reference integrity passed. Both
render modes saved and exited. Restored the five original settings files,
archived the disposable world and verified the two source world manifests.
GPU performance and temporal behavior remain outside this still comparison.
Next numbered task is TASK-26.

## TASK-25 follow-up — Clear-air fog (2026-11-13)

**DONE.** Delayed the clear-air fog start from 28 to 88 blocks at the tested
12-chunk distance. The clear far bound remains 180 blocks. The settled-rain
ramp is 22–136 blocks. The tuned shader tree differs from the original
TASK-25 capture tree only in `shaders/lib/fog.glsl`.
[Current manifest](../evidence/task-25/fog-pack.sha256).

`bash evidence/task-25/session.sh artifacts/task-25-fog-tuning pack valley rain ridges dusk night`
captured five native 2560×1440 views. Compared byte-identical camera and video
settings against TASK-25. The far-hill patch gains contrast, the nearby
grass probe matches pixel for pixel, the ridges still recede and settled
rain retains its overall appearance. Dusk and night retain readable near
landmarks. [Matched captures and pixel probe](testing/visual_comparison.md#clear-air-fog-follow-up).

All 13 static program links and nine harness unit tests passed. The Iris log
at `artifacts/task-25-fog-tuning/pack/logs-20261113-135535/latest.log` records
the pack load, five fresh camera acknowledgments and graceful save, with no
ERROR-level entries. Restored all five settings files, removed the temporary
pack, archived the fixture and verified the TASK-15 and TASK-03 source-world
hashes. [Exact replay and checks](../evidence/task-25/fog-commands.txt).

Live weather transitions, other render distances in-client and GPU cost
remain unmeasured for the new ramp. The next numbered task is TASK-26.

## Documentation audit after TASK-25 fog tuning (2026-11-13)

**DONE.** Aligned the status, decision ledger, developer entry points,
architecture, visual and weather reports, and replay guides with the
fog-tuned source. The handoff uses the tuned build for TASK-26. TASK-24
verification and the original TASK-25 replay use the retained TASK-22 tree.
The reports record settled weather evidence for the tuned ramp and
live transition evidence for TASK-21.
[TASK-26 handoff](STATUS.md#task-26-per-effect-profiling),
[TASK-25 replay guide](../evidence/task-25/README.md).

`sha256sum --quiet -c evidence/task-25/fog-pack.sha256` verified the working
source. The retained TASK-22 tree matched its manifest and the TASK-23 and
original TASK-25 snapshots. `python3 evidence/task-25/comparisons.py <audit-root>`
reproduced the eight original sheets and comparison index from retained
captures. The offline review section of
`evidence/task-25/fog-commands.txt` reproduced all five fog sheets and the
valley luma probe. Local links and anchors, Bash syntax, nine harness tests
(`python3 -m unittest discover -s scripts`), and reference integrity
(`python3 scripts/verify_references.py`) passed. The audit used saved
captures. Next numbered task is TASK-26.

## Public repository audit (2026-11-13)

**DONE.** Reviewed the five commits on local main and the tracked and
Git-eligible working files. Original shader source, development tools,
fixture definitions, research citations and reviewed text evidence belong
in the source repository. Supplied reference media, the original brief,
local agent instructions, raw runtime data and environment files stay
local. Public readers need the local evidence bundle to open capture links
or replay the full reference comparison. [Evidence layout](../evidence/README.md).

Rebuilt all five commits in their original order. Removed the archived
brief from every tree and made machine-specific paths portable. Verified
the raw author and committer headers, including both dates and time zones,
and the full message bytes against each original commit. The original
brief remains byte-identical on disk. The rewritten history has new object
IDs. Local Codex refs and the original history backup are local records.

`git fsck --no-dangling --no-reflogs main` and representative
`git check-ignore --no-index` probes passed. All five trees and the eligible
working files contain UTF-8 text. Targeted checks found no absolute home
or workspace paths or common credential patterns. The fog manifest,
reference verifier and nine harness tests passed.

The GitHub remote ref check returned an SSH authentication error.
Publication and repository visibility were outside this local audit.
The preserved commit metadata includes the existing email address.
The repository has no project license. Next numbered task is TASK-26.

## TASK-26 per-effect performance profiling (2026-11-13)

**DONE.** The accepted shaders and retained fog-tuned snapshot match the
TASK-25 manifest. All 13 programs link in each of nine temporary pack
builds. The runtime matrix records 44 validated profiles and 805,413
client-loop samples across five fixed 1440p Overworld views. The two
shader sessions run the ablations in opposite order. Both Sodium
sessions use the same scene and video settings.

The shadowless variant removes the CPU shadow section in both rounds.
The full pack adds 0.045–0.093 ms of mean client-loop time versus that
variant in the valley and grove. Offscreen NVIDIA timer queries measure
selected draw costs with paired batches and geometry pixel probes. See
the [report](testing/effect_costs.md) for per-effect results and remaining
GPU and presentation gaps.

All four clients saved and exited. Verified five byte-identical settings
files, the absent temporary packs, the archived fixture, the 87 retained
TASK-25 world hashes, and the 76 original TASK-03 world hashes. Nine
harness tests and reference verification passed. [Replay commands](../evidence/task-26/commands.txt),
[verification record](../evidence/task-26/verification.txt). Next numbered
task is TASK-27.

## Documentation audit after TASK-26 (2026-11-13)

**DONE.** Updated the status, architecture, replay entry points and effect
reports to reflect the fog-tuned profiling results. The reports distinguish
client-loop ablations from offscreen GPU draws and identify in-client GPU
frame time, shadow-caster time, the pre-hand depth copy and presentation
cadence as open. The TASK-27 handoff starts with shadows and links the
full-pack baseline, replay and visual checks.
[Effect costs and TASK-27 handoff](testing/effect_costs.md#task-27-handoff).

Regenerated the three TASK-26 CSV indices with `review.py`, `compare.py`
and `summarize_gpu.py`. All matched their reviewed copies byte for byte.
Checked local Markdown links and anchors, the accepted shader manifest,
the saved instance state, nine harness tests and reference integrity.
[Review commands](../evidence/task-26/README.md).

## TASK-27 targeted performance optimization (2026-11-13)

**DONE.** Linked 13 shader pairs each for the fog-tuned baseline, a
768² shadow-map trial and a fog blend arithmetic trial. Four fresh
client sessions captured 24 validated 1440p profiles and 549,153
loop samples. Shader sessions used opposite build order. Reviewed
ten native stills, 48 profile-window frames and targeted crops.
Two independent offscreen GPU comparisons per trial recorded 384
paired batches and validated depth or linear RGB probes.

The smaller map reduced synthetic shadow render-and-copy time by
0.0062–0.0083 ms and softened thin cast shadows. The fog rewrite
showed no repeatable GPU improvement. Both trial trees were
discarded from the development instance. The working shader tree
matches the TASK-25 fog manifest byte for byte.

Verified all four saves, five restored settings, removal of temporary
packs, release of the archived world lock and unchanged manifests for
the 87 retained TASK-25 and 76 original TASK-03 world files. Nine
harness tests and reference verification passed. In-client GPU frame
duration and presentation cadence remain open. Next is TASK-28.
[Report](testing/optimization.md),
[exact commands and evidence](../evidence/task-27/README.md).

## Documentation audit after TASK-27 (2026-11-13)

**DONE.** Corrected the TASK-25 Unlimited FPS setting and updated the
shadow and fog reports with TASK-27's trial decisions. The synthetic
shadow pass includes a shadow-map depth copy. In-client GPU frame and
shadow-pass durations, the water pre-hand depth copy and presentation
cadence remain open. The TASK-28 handoff links each runtime coverage area
to the closest existing fixture and evidence, including historical
weather and dimension checks on earlier builds.
[Optimization results](testing/optimization.md),
[TASK-28 regression results](testing/regression_report.md).

Verified the accepted shader manifest and compared the source with the
retained full tree. Regenerated the three TASK-27 indices byte for byte
from saved artifacts using the offline review commands. The instance
restoration check, local Markdown targets and headings, nine harness
tests and reference verification passed. Next numbered task is TASK-28.
[Offline review commands](../evidence/task-27/README.md#offline-review).

## TASK-28 runtime regression and robustness (2026-11-13)

**DONE.** Verified the fog-tuned TASK-25 shader manifest and linked all
13 expanded GLSL program pairs. Ran one fresh GenshinShaderDev client
session with the retained pack. A disposable copy of the TASK-22 world
provided the original seven TASK-03 cameras, cave, lamp and unlit
fixtures and the Nether and End cameras. Reused the stepped basin and
added a walkable entrance approach for the cave clip.

Reviewed 14 native 1440p stills, 42 timed rain frames and six 1440p
KWin recordings. The client log confirms both rain commands at tick
6000, waterline IN → OUT → IN, actual movement and a 66.15° forest
turn, cave entry, and all three dimension pipeline changes. Two
static Overworld crops match after return. The review records
nonblocking foliage and shoreline aliasing, a sharp color change at
the waterline and weak distant contrast in the Nether and End.

The accepted run saved all dimensions and exited without a crash or
pack shader error. Five settings files were restored, the temporary
pack was removed, the copied world was archived and both source-world
manifests verified. Nine harness tests and reference integrity checks
passed. The first menu attempt exited cleanly after OCR misread the
world name. The accepted run uses the verified menu mask.
[Report](testing/regression_report.md),
[exact commands and evidence](../evidence/task-28/README.md).
Next numbered task is TASK-29.

## Documentation audit after TASK-28 (2026-11-13)

**DONE.** Updated the weather and fog reports with the sampled rain cycle
on the tuned build. The shadow, lighting and architecture notes now
include the observed motion, cave entry and command-teleport return.
The replay index documents how to keep the saved evidence when repeating
the test. The TASK-29 handoff identifies the tested stack, pinned research
and optional additional-version scope. Portal travel and overlays,
fine shadow-edge jitter and in-client GPU frame time remain open.
[Regression results](testing/regression_report.md),
[TASK-29 compatibility notes](testing/compatibility_notes.md).

The offline TASK-28 review matched its saved output. Verified the shader
manifest and saved snapshot, local Markdown targets and anchors, nine
harness tests and the original reference inventory.
[Review command](../evidence/task-28/README.md).

## TASK-29 limited compatibility investigation (2026-11-13)

**DONE.** Checked the scoped Prism instance manifest, cached game and
loader JARs, installed Iris/Sodium hashes and Iris's embedded NeoForge
metadata against the TASK-28 runtime evidence. The 1.21.1 launch and
pack load are recorded in the archived log. The optional 26.3 test was
skipped because only its game client was cached for that target and a
matching loader and Iris/Sodium stack would need setup.

The retained source verified against all 38 TASK-25 hashes and matched
the TASK-28 snapshot. All 13 GLSL pairs linked offline. The saved
regression review validated 14 stills, 42 timed weather frames, three
dimension changes and six motion clips. Nine harness tests and
reference integrity checks passed. Runtime coverage remains the TASK-28
run. [Commands and version notes](testing/compatibility_notes.md#verification-commands),
[saved evidence](../evidence/task-28/README.md). Next numbered task is TASK-30.

## Documentation audit after TASK-29 (2026-11-13)

**DONE.** Linked the pack, environment, architecture, script and evidence
entry points to the tested stack. Corrected the Iris metadata description,
recorded the built-in resources from the saved client options and included
the retained pack's TASK-28 dimension retest in the feasibility record.
The Prism inventory commands now resolve the instance from the current
user's home directory. Removed a trailing space from the TASK-04 tool
version listing. [Compatibility notes](testing/compatibility_notes.md),
[saved client options](../artifacts/task-28/settings/options.txt).

Ran both documented command blocks, including the shader manifest and
snapshot checks, 13 GLSL links, saved regression review, nine harness tests
and reference verification. Checked local Markdown links and anchors and
ran `git diff --check`. The audit used saved runtime evidence. Next
numbered task is [TASK-30](STATUS.md#task-30-developer-handoff).

## TASK-30 developer handoff (2026-11-13)

**DONE.** Verified all 38 source files against the retained TASK-25
manifest and both runtime snapshots. All 13 GLSL pairs linked and nine
harness tests passed. The original media and all 144 sampled frames
verified. Recomputed the TASK-26 and TASK-27 reviewed indices from the
saved raw samples and matched the existing indices byte for byte.

Repeated the TASK-28 client replay in `artifacts/task-30-regression/`.
The reviewer passed 14 native stills, 42 weather frames, six motion clips,
three dimension changes and both static Overworld return patches. The
client saved and exited normally. The temporary pack was removed and
five settings restored byte for byte. Both source worlds matched the
earlier manifests. A separate copy of the 76-file TASK-03 world now
accompanies the replay evidence. [Commands](../evidence/task-30/commands.txt),
[verification and evidence locations](../evidence/task-30/verification.txt).

Changed the developer entry point, handoff and gaps guides, evidence and
script indexes, project ledgers and related pointers. GLSL, original
references and Git history remained unchanged. Runtime coverage is the
tested 1.21.1 NeoForge stack. Full-client GPU time and display
presentation remain open. **Next task ID: none.**

## Documentation audit after TASK-30 (2026-11-13)

**DONE.** Corrected the handoff's sky dither attribution, documented the
client settings inherited by the replays and linked the TASK-30 evidence
from the shader, compatibility and regression guides. Added fixture
installation and path rebasing steps for the TASK-26/27 checksum check
when the destination Prism instance uses a different home directory.
Clarified that the stock runtime replay verifies the accepted source
manifest before staging. [Handoff](HANDOFF.md),
[fixture installation and replay prerequisites](../evidence/README.md#install-the-task-03-fixture).

Exercised the documented shader copy, fixture install and checksum
rebasing with temporary destination paths. Verified the shader manifest
against both saved runtime trees, linked 13 program pairs, ran nine
harness tests and checked reference hashes and local documentation links.
The TASK-28 reviewer passed on both saved runtime runs, and all six
TASK-26/27 benchmark indices matched byte for byte. This audit used the
saved captures and metrics. **Next task ID: none.**
