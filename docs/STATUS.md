# Project status

Updated: 2026-11-13. Final numbered task: **TASK-30 — DONE**.
No numbered task remains.

TASK-28 and TASK-30 verified the [fog-tuned TASK-25 shader source](../evidence/task-25/fog-pack.sha256)
retained by TASK-27 in the development client. The [TASK-22 manifest](../evidence/task-22/pack.sha256)
identifies the earlier dimension smoke-test build, the AA control and the
original TASK-25 comparison.

| Task | State | Evidence / limits |
| --- | --- | --- |
| TASK-00 | DONE (owner-confirmed; inherited handoff) | [Environment](minecraft-environment.md), local `artifacts/task-00/`. Launch/input/capture/metadata loader verified previously. |
| TASK-01 | DONE | Structure, brief archive, scope overrides, ledgers and Git initialization. |
| TASK-02 | DONE | [Harness](testing/harness.md): real startup, native captures, two validated CPU render-loop archives, logs and graceful save/exit. Capped profiled smoke evidence only. |
| TASK-03 | DONE | [Scenes](testing/scenes.md): seven fixed presets, vanilla-texture Sodium baseline screenshots, daylight/forest/cave repeat validation and safe shutdown. Synthetic map; animated regions vary. |
| TASK-04 | DONE | [Reference inventory](research/reference_index.md): 30 sources, 144 timestamped PNGs, 12 contact sheets, all sources unchanged. Still-sample coverage only. |
| TASK-05 | DONE | [Style targets](research/style_targets.md): seven ranked signatures, ten inspected frames, scene-linked qualitative rubric, cheap candidate methods and explicit coverage gaps. |
| TASK-06 | DONE | [Iris feasibility](research/iris_feasibility.md): S1–S7 mapped to pinned official docs and source. TASK-16 verifies the tested shadow casters, TASK-19 verifies pre-hand water depth, and TASK-20 exercises terrain vegetation IDs. TASK-24 leaves separate AO for handoff. |
| TASK-07 | DONE | [Implementation patterns](research/implementation_patterns.md): two pinned upstream studies, licenses, S1–S7 original alternatives; no code reuse or runtime validation. |
| TASK-08 | DONE | [Architecture](architecture/shaderpack_design.md): forward lighting, one HDR color attachment and final pass, bounded shadows delivered in TASK-16 and bounded water depth in TASK-19. |
| TASK-09 | DONE | Neutral GLSL scaffold loaded in the installed Iris beta; native daylight/cave captures, runtime logs and verified instance restoration. |
| TASK-10 | DONE | [Baseline](testing/baseline.md): 12 matched 1440p CPU render-loop profiles, raw metrics and restored instance configuration. |
| TASK-11 | DONE | [Palette](testing/palette.md): final-pass exposure, chroma and shoulder, five paired scenes, snow and ramps, and 12 matched loop profiles. |
| TASK-12 | DONE | [Sunlight](testing/sunlight.md) validates directional daylight and sunset, fixed-camera dawn/dusk, cave lighting and 16 matched profiles. |
| TASK-13 | DONE | [Ambient lighting](testing/ambient.md) validates terrain fill in five paired scenes and 12 matched loop profiles. |
| TASK-14 | DONE | [Sky gradients](testing/sky.md) validates 20 matched time samples, running dusk and dawn through day wrap, and eight matched CPU loop profiles. |
| TASK-15 | DONE | [Distance fog](testing/fog.md) validates six scenes in three modes and 12 matched CPU loop profiles. |
| TASK-16 | DONE | [Terrain shadows](testing/shadows.md) verifies contact, caster coverage, alpha cutouts, the range fade, camera steps and 12 matched CPU client-loop profiles. |
| TASK-17 | DONE | [Prototype checkpoint](testing/prototype_checkpoint.md) records seven scene comparisons, 28 matched CPU client-loop profiles and a CONTINUE decision. |
| TASK-18 | DONE | [Cloud report](testing/clouds.md) records five matched Overworld views and the 1440p offscreen sky-draw cost. |
| TASK-19 | DONE | [Water report](testing/water.md) records depth diagnostics, seven paired views and 12 matched 1440p CPU client-loop profiles. |
| TASK-20 | DONE | [Vegetation report](testing/vegetation.md) records four matched views and 12 CPU client-loop profiles. |
| TASK-21 | DONE | [Weather report](testing/weather.md) records six live sequences, six matched endpoint pairs, twelve client-loop profiles and isolated sky timings. |
| TASK-22 | DONE | [Lighting and dimension report](testing/lighting_dimensions.md) records matched interior and night views, Nether/End smoke tests and twelve client-loop profiles. |
| TASK-23 | DONE | [Motion and AA report](testing/anti_aliasing.md). Deferred AA after a matched motion and GPU-cost comparison. |
| TASK-24 | DONE | [Effects triage](architecture/deferred_effects.md) ranks the remaining effects against the reference footage and expected GPU work. One optional sky-draw trial is proposed. |
| TASK-25 | DONE | [Visual comparison](testing/visual_comparison.md) records eight matched views and seven timestamped references. The [fog follow-up](testing/visual_comparison.md#clear-air-fog-follow-up) improves mid-distance detail in the tested valley. |
| TASK-26 | DONE | [Effect costs](testing/effect_costs.md) records 44 client profiles and paired GPU draw timings. |
| TASK-27 | DONE | [Optimization report](testing/optimization.md) records 24 client profiles and paired GPU queries. Kept the 1024² map and original fog blend after testing both trials. |
| TASK-28 | DONE | [Regression report](testing/regression_report.md) covers the seven original presets, live weather, motion, waterline, cave and dimension transitions. |
| TASK-29 | DONE | [Compatibility notes](testing/compatibility_notes.md) identify the tested client, relevant API changes and untested combinations. The optional extra version would require a second stack. |
| TASK-30 | DONE | [Developer handoff](HANDOFF.md), [known gaps](KNOWN_GAPS.md), [evidence index](../evidence/README.md) and [fresh runtime verification](../evidence/task-30/verification.txt). |

## TASK-17 checkpoint

- **TASK-17-A — DONE.** Four fresh sessions captured all seven TASK-03
  presets. The 28 native profiles passed the runtime, options and raw sample
  checks. Both prototype sessions loaded `TASK-17-prototype`. After the
  final save and exit, the temporary pack was removed and the five preflight
  settings files were restored, leaving Iris shaders disabled and the pack
  selection empty. All 76 source-world file hashes matched.
- **TASK-17-B — DONE.** The visual rubric review records **CONTINUE**. Mean
  CPU client-loop time increased by 0.267–0.304 ms (+124.7–155.2%) over
  Sodium in the seven synthetic presets at 1440p. Full-client GPU time, display
  pacing and representative gameplay performance remain unmeasured. The
  checkpoint identified cloud form, water color and the overcast response as
  the largest visual gaps. TASK-18 subsequently added cloud form.
  [Report](testing/prototype_checkpoint.md),
  [evidence index](../evidence/task-17/README.md).

## TASK-18 validation

- **TASK-18-A — DONE.** Implemented and captured the directional revision
  of the single-layer cloud model. All 12 shader pairs link. Five native
  1440p comparisons cover daylight, sunset, settled rain, night and cave.
- **TASK-18-B — DONE.** Two offscreen RTX 4080 SUPER runs measure
  0.011–0.013 ms additional median GPU time per sky draw for the preset-like
  views and about 0.023 ms in upward rain. Integrated GPU frame time
  remains unverified. The client saved and exited,
  five settings files were restored, and all 76 source-world hashes matched.
  [Cloud report](testing/clouds.md), [replay and checks](../evidence/task-18/commands.txt).

## TASK-19 validation

- **TASK-19-A — DONE.** The water material and developer depth diagnostic
  passed linking and loaded in Iris. Seven paired views cover daylight,
  settled rain, sunset, the original open-water basin, shore, submerged floor
  and the underside. The diagnostic checks thickness, stained-glass overlap,
  held items and both submerged views.
- **TASK-19-B — DONE.** Twelve profiles compare Sodium shaders off, TASK-18
  and TASK-19. Mean CPU client-loop time increased by 0.0071 ms in daylight
  and 0.0132 ms in rain versus TASK-18 at 1440p. TASK-26 later timed the
  water material and depth sampling offscreen. The disposable world was
  saved and archived, the five settings files restored and all 76
  original TASK-03 world hashes matched.
  [Water report](testing/water.md), [replay](../evidence/task-19/commands.txt).

## TASK-20 validation

- **TASK-20-A — DONE.** Static terrain-vertex tint and leaf fill passed
  shader linking and four matched visual comparisons. The fixed views
  preserve biome tint, cutout silhouettes and cast shadow contact.
  [Vegetation report](testing/vegetation.md).
- **TASK-20-B — DONE.** Twelve profiles compare the candidate with TASK-19
  and Sodium shaders off at 1440p. Mean CPU client-loop time changed by
  −0.0046 ms in daylight and +0.0016 ms under dense canopy versus TASK-19.
  Foliage-only GPU cost remains open. The disposable world was saved and
  archived, five settings files were restored and all 76 TASK-03 world
  file hashes matched. [Replay and verification](../evidence/task-20/commands.txt).

## TASK-21 validation

- **TASK-21-A — DONE.** The TASK-20 source matched its manifest and saved
  tree before editing. The coordinated weather response and precipitation
  shader pair are implemented. All 13 expanded shader pairs link.
- **TASK-21-B — DONE.** Six settled comparison pairs and 264 native frames
  cover midday rain onset and clearing from three fixed cameras. Twelve
  CPU client-loop profiles compare TASK-21, TASK-20 and Sodium shaders off.
  Two offscreen runs measure the sky draw. The instance settings and both
  source-world manifests verified. The live clips sample about four frames
  per second. Full-client GPU time remains open.
  [Replay and evidence](../evidence/task-21/README.md).

## TASK-22 validation

- **TASK-22-A — DONE.** The TASK-21 manifest and retained shader tree
  matched the starting source. Added low-light terrain fill and bounded
  lamp faces. The matched night, cave, unlit and mixed-light views show
  better dark-surface detail with visible light pools. All 13 shader pairs
  link and the selected clear-day patches match the control.
- **TASK-22-B — DONE.** The candidate rendered the Nether and End and
  returned to the Overworld with matching daylight patches. Twelve profiles
  cover the night and cave views across three modes. The development instance
  is stopped with five settings restored, temporary packs removed and all 76
  original scene-world hashes verified. GPU time and specialized dimension
  effects remain open.

The [lighting and dimension report](testing/lighting_dimensions.md) records
the shader behavior and condition-specific gaps. The [replay](../evidence/task-22/commands.txt)
uses the original night and cave cameras, the disposable lamp and step
fixtures, and the retained TASK-21 shaders as its incremental control.

## TASK-23 validation

- **TASK-23-A — DONE.** Verified the TASK-22 shader manifest and snapshot.
  Staged a disposable five-sample spatial filter for comparison.
- **TASK-23-B — DONE.** Nine native stills and nine 1440p clips at about
  40 captured frames per second compare stone, oak cutouts and the shoreline.
  Twelve client profiles cover two scenes. Six isolated GPU runs show
  0.0091–0.0097 ms added per final draw on the RTX 4080 SUPER.
- **TASK-23-C — DONE.** Deferred spatial AA. The trial softened some edges,
  with persistent foliage shimmer and softer fine detail. The accepted pack
  matches TASK-22 byte for byte. The dedicated instance saved and exited,
  five settings files were restored, and all 76 source-world hashes matched.
  [Report](testing/anti_aliasing.md), [replay and evidence](../evidence/task-23/README.md).

## TASK-24 triage

- **Reference and baseline review — DONE.** Verified the TASK-22 shader
  manifest and the retained TASK-23 control. Reviewed timestamped Genshin
  footage, two short review strips, and prior Minecraft captures.
- **Effects triage — DONE.** Recorded visual value and expected GPU work for each
  candidate. The optional TASK-24A sun halo in the existing sky draw remains
  proposed. Scene-wide bloom and separate vertex AO go to handoff.
  Screen-space AO and geometry reflections are rejected for this pack.
  [Dispositions and evidence](architecture/deferred_effects.md).

## TASK-25 visual comparison

- **Selection — DONE.** The original comparison used the retained
  [TASK-22 shader snapshot](../evidence/task-22/pack.sha256).
  Selected seven reference cues from the
  [visual rubric](research/style_targets.md#repeatable-qualitative-comparison)
  and eight fixed Overworld views including the cave control.
- **Capture — DONE.** Both modes rendered all eight views in the disposable
  TASK-25 world. A fresh shader-on session repeated the valley and cave.
  The temporary pack and world were removed from the instance and the five
  settings files restored. [Capture and restoration evidence](../evidence/task-25/README.md).
- **Review and handoff — DONE.** The original comparison found that clear
  valley haze obscured the far hill. The [report](testing/visual_comparison.md)
  also ranks cloud form, rain values, water hue, canopy variation and dark
  outdoor detail.
- **Clear-air fog follow-up — DONE.** The delayed ramp restores valley
  hillside contrast while keeping distant haze and the settled-rain ramp.
  [Matched follow-up captures and current manifest](testing/visual_comparison.md#clear-air-fog-follow-up).

## TASK-26 per-effect profiling

- **TASK-26-A — DONE.** The accepted source and retained TASK-25 fog tree
  matched. The nine temporary shader builds each pass 13 expanded GLSL links.
- **TASK-26-B — DONE.** Two Sodium sessions and two shader sessions
  captured 44 matched 1440p profiles and 88 window frames. Both rounds
  show the largest client-loop reduction with the shadow map and receiver
  disabled. Reviewed both repeats and retained the raw archives.
- **TASK-26-C — DONE.** Two offscreen runs per selected comparison cover
  the sky gradient, clouds, fog, water, shadow receiver, grouped terrain
  lighting and grading. In-client GPU frame and shadow-caster timing, the
  pre-hand depth copy used by water and display presentation remain open.
  Restored the five instance settings and verified both world manifests.
  [Effect report](testing/effect_costs.md), [replay and evidence](../evidence/task-26/README.md).

## TASK-27 optimization

- **TASK-27-A — DONE.** Staged independent 768² shadow and fog arithmetic
  candidates from the verified TASK-25 control. All 13 pairs link in each tree.
- **TASK-27-B — DONE.** Captured 24 matched client profiles and timed the
  offscreen GPU trials twice. The smaller map saves 0.0062–0.0083 ms in
  the synthetic shadow pass and depth copy, with visibly softer leaf and
  glass shadows. The fog rewrite showed no repeatable GPU improvement.
- **TASK-27-C — DONE.** Retained the fog-tuned baseline. Four sessions
  saved and exited, five settings were restored and both world manifests
  verified. [Report](testing/optimization.md),
  [replay and evidence](../evidence/task-27/README.md).

## TASK-28 runtime regression

- **TASK-28-A — DONE.** Verified the retained shader source, linked 13
  program pairs and staged a disposable copy of the TASK-22 world.
- **TASK-28-B — DONE.** Captured 14 native stills, six KWin motion clips
  and 42 timed weather frames. The Overworld return restored both
  sampled static terrain patches. Waterline crossings and cave entry
  were verified by footage and the game log.
- **TASK-28-C — DONE.** Reviewed and prioritized the visual defects.
  The client saved all dimensions and exited normally. The five
  settings files, temporary-pack removal, archived fixture and both
  source-world manifests verified.
  [Report](testing/regression_report.md),
  [replay and evidence](../evidence/task-28/README.md).

## TASK-29 limited compatibility investigation

Verified the retained source against the TASK-25 manifest and TASK-28
snapshot and checked the saved runtime evidence. The notes record the
tested Minecraft 1.21.1 NeoForge stack, the Iris metadata discrepancy
and the shader interfaces to check on a different version. The scoped
Prism cache contains a 26.3 client JAR, but the matching loader and
Iris/Sodium stack would require provisioning.
[Compatibility notes and commands](testing/compatibility_notes.md).

## TASK-30 developer handoff

- **TASK-30-A — DONE.** Verified the retained shader tree against the TASK-25
  manifest and TASK-28 snapshot. All 13 GLSL pairs and nine harness tests pass.
  Saved TASK-28 review passes and the TASK-26 and TASK-27 summaries reproduce.
- **TASK-30-B — DONE.** Wrote the developer entry point, pass and module
  overview, replay and benchmark instructions, known gaps, evidence index
  and script inventory.
- **TASK-30-C — DONE.** A fresh TASK-28 replay passed the runtime reviewer.
  The client saved and exited, five settings were restored and both source
  world manifests matched the previous run. Preserved a verified TASK-03
  world copy in `artifacts/task-30-regression/fixtures/`.
  [Commands](../evidence/task-30/commands.txt), [verification](../evidence/task-30/verification.txt).
- **Documentation audit — DONE.** Aligned provenance and runtime coverage
  with the retained source. Verified the fixture installation and
  benchmark manifest rebasing on a different temporary instance path.
  [Audit record](TEST_LOG.md#documentation-audit-after-task-30-2026-11-13).

## Source and evidence state

Local `main` consolidates the project deliverables through TASK-30 into one
root commit. The original brief and local agent instructions are ignored. [Publication audit](TEST_LOG.md#public-repository-audit-2026-11-13).
TASK-00's unusable `.git` note is historical.
Original brief/plan/AGENTS/reference files remain unchanged;
34 original-input hashes were rechecked in TASK-04. The TASK-01 toolkit checksum
is historical because TASK-02 intentionally extended `tools/minecraft.py`.

Large references, screenshots, saved worlds, profiler archives and logs remain
local/ignored and must accompany a developer handoff. TASK-03 small text/JSON
results are under `evidence/task-03/`; native images/configs/logs are under
`artifacts/task-03/`. The installed test-world datapack source is in `scripts/scenes/`.
TASK-04 inventoried all references and reviewed timestamped still samples; originals
remain unchanged. Its text/JSON records are in `evidence/task-04/`, its generated
images in `artifacts/task-04/` (about 207 MiB).

TASK-05 adds a qualitative style rubric and reviewed text evidence in
`evidence/task-05/`; no generated media or source references were changed.
TASK-06 adds pinned source hashes, installed Iris metadata and capability findings
in `evidence/task-06/`; official source/docs clones are local/ignored under
`artifacts/task-06/`.
Read [SCOPE_OVERRIDES.md](SCOPE_OVERRIDES.md) for the active project scope.

TASK-07 adds two pinned upstream shaderpack studies and 19 source/license hashes in
`evidence/task-07/`; ignored research clones are under `artifacts/task-07/`.
No upstream code/assets were incorporated into deliverables. Original implementation
alternatives informed the architecture selected in TASK-08.

TASK-08 selects the Iris-only architecture and implementation order in
`docs/architecture/shaderpack_design.md`. No critical dependency requires a spike
before selecting this reduced minimum. TASK-16 subsequently verified terrain,
oak leaf, chest and cutout glass casting. TASK-19 verified the opaque depth
snapshot for water in the stepped basin. Separate AO remains runtime-unverified
and is a [handoff item](architecture/deferred_effects.md#dispositions-and-expected-gpu-work).
Small documentation checks are in `evidence/task-08/`. No shaders, references,
client configuration or world were changed. No runtime/performance claim is added.

TASK-09 adds the unpacked neutral source under `shaderpack/`. Actual Iris
Overworld compilation and rendering passed on the installed combination.
Reviewed records are under `evidence/task-09/`; native screenshots, client
configuration snapshots and logs are under `artifacts/task-09/`. The client is
stopped after a verified world save. Visual parity, later effects, and
compatibility beyond this runtime remain open.

TASK-10 profiled the unchanged neutral pack against the Sodium shaders-off
baseline across daylight, forest and cave. Both modes ran in two fresh sessions.
Reviewed metrics and replay tooling are under `evidence/task-10/`. The original
profile ZIPs, CSVs, screenshots, logs and settings snapshots are under
`artifacts/task-10/`. GenshinShaderDev is stopped with five preflight settings
files restored byte-for-byte. The CPU loop measurements cover this test stack
and do not establish GPU pass costs.

TASK-11 changes the final pass and adds a tone mapping module. Reviewed
evidence and replay tooling are under `evidence/task-11/`. Preserve
`artifacts/task-11/` for its native images, shader snapshots, diagnostic frame,
profiler archives, raw CSVs, and logs. The completed checks cover the tested
Overworld client and sRGB path.

TASK-12 adds terrain sunlight. The source, client replay and review are
complete. Keep `evidence/task-12/` for reviewed runs, pixel patches and commands
and `artifacts/task-12/` for native before/after captures, fixed-time sequences,
shader snapshots, profile archives and logs.

TASK-13 adds skylight-weighted terrain fill. Keep `evidence/task-13/` for
reviewed timings, patches and replay commands, and `artifacts/task-13/` for
native PNGs, the shader snapshots, logs and raw profiler files. Validation
covers the installed Overworld stack. TASK-16 checked cast shadows and
TASK-21 checked the combined terrain response during live midday weather.
TASK-26 profiled terrain lighting as a group. Ambient-only GPU timing
remains open. [Terrain measurement coverage](testing/effect_costs.md#coverage-and-limits).

TASK-14 adds an analytic sky gradient in the existing Overworld sky draw.
Keep `evidence/task-14/` for the pack manifest, reviewed timing and pixel
data and replay tools, and `artifacts/task-14/` for native PNGs, both live
time sequences, shader snapshots, profile archives and logs. TASK-18 adds
the projected cloud layer and records its
isolated sky-draw cost. [Cloud report](testing/clouds.md).

TASK-15 adds distance fog in the existing forward geometry passes. Keep
`evidence/task-15/` for the fixture source, commands, manifest, patch and
timing indices. Keep `artifacts/task-15/` for the copied overlook world,
native PNGs, shader snapshots, raw profiler data and client logs. The
original TASK-03 world and instance settings passed byte-level checks.

TASK-16 adds a 1024² directional depth map and one filtered terrain lookup.
Keep `evidence/task-16/` for the replay, pack manifest, reviewed image patches
and timing index. Keep `artifacts/task-16/` for the shadow fixture world, native
comparisons, camera steps, shader snapshots, raw profiles and logs. TASK-26
timed the offscreen receiver, and TASK-27 timed a synthetic caster draw
and shadow depth copy. In-client GPU timing and fine shadow-edge stability
during continuous travel remain open. The terrain receiver applies
directional shadows only in skylit dimensions without a ceiling.
[Shadow validation](testing/shadows.md#performance),
[dimension coverage](testing/lighting_dimensions.md#dimensions).

TASK-17 records the integrated checkpoint. Keep `evidence/task-17/` for the
reference and run indices and replay commands. Keep `artifacts/task-17/` for
the shader snapshot, archived world copy, settings backups, 56 window PNGs,
comparison sheets, client logs and raw CPU profiles. TASK-18 measures its
isolated sky-draw increment. Full-client GPU time, presentation cadence and
broader workload performance remain open.

TASK-18 adds a single projected cloud layer in `gbuffers_skybasic`.
Keep `evidence/task-18/` for the source manifest, replay, timing harness
and timing summary. Keep `artifacts/task-18/` for native comparisons,
the exact control and candidate sources, raw timer results, logs and world copy.

TASK-19 adds the water-specific translucent material and submerged fog ramp.
Keep `evidence/task-19/` for the fixture source, replay, manifest and profile
index. Keep `artifacts/task-19/` for the accepted, TASK-18 control and
diagnostic shader trees, native captures, raw profile data, logs and world.

TASK-20 adds static vegetation tint and leaf fill in the existing terrain
vertex shader. Keep [evidence/task-20](../evidence/task-20/README.md) for
replay, the fixture, source manifest and reviewed measurements, and
`artifacts/task-20/` for the exact shader trees, saved world, native images,
logs and raw profiles.

TASK-21 coordinates rain in the existing render sequence and adds an
explicit precipitation shader pair. Keep
[`evidence/task-21/`](../evidence/task-21/README.md) for replay, manifests
and reviewed measurements. Keep `artifacts/task-21/` for the accepted and
control shader trees, the saved copy, native frames, profiles, GPU timers
and logs.

TASK-22 adds the low-light terrain adjustment and records the Nether and End
smoke test. Keep [evidence/task-22](../evidence/task-22/README.md) with
`artifacts/task-22/` for the exact shader trees, native captures, raw profiles,
logs and saved fixture.

TASK-23 keeps the TASK-22 shaders and adds the AA decision and comparison
replay. Keep [evidence/task-23](../evidence/task-23/README.md) and
`artifacts/task-23/` for the exact trial source, native stills, motion clips,
raw timing data, logs and saved fixture.

TASK-24 adds the [effects triage and replay commands](architecture/deferred_effects.md).
Keep `artifacts/task-24/` for the two supplemental reference strips and the
earlier fixture captures linked in the triage.

TASK-25 adds the [comparison report and evidence index](../evidence/task-25/README.md).
Keep `artifacts/task-25/` for the original comparison, `artifacts/task-25-fog-tuning/`
for the tuned shader tree, native stills, review sheets, logs and archived
fixture, and `artifacts/task-04/` for the indexed reference PNGs.


TASK-26 adds the [effect-cost report](testing/effect_costs.md) and
[evidence index](../evidence/task-26/README.md). Keep `artifacts/task-26/`
for exact variant trees, comparison images, profiler ZIPs, raw GPU timers,
settings, telemetry, runtime logs and the archived fixture.

TASK-27 adds the [optimization report](testing/optimization.md) and
[trial evidence](../evidence/task-27/README.md). Keep `artifacts/task-27/`
for exact shader variants, comparison images, client profiles, GPU queries
and the saved fixture.

TASK-28 adds the [runtime regression report](testing/regression_report.md)
and [replay and evidence index](../evidence/task-28/README.md). Keep
`artifacts/task-28/` for native stills, movement clips, timed weather
captures, logs, shader snapshot and the archived fixture.

TASK-29 adds [compatibility notes and offline checks](testing/compatibility_notes.md)
using the TASK-28 snapshot, client log and instance manifest.

TASK-30 adds the [developer entry point](../README_DEV.md) and
[handoff](HANDOFF.md). Keep `artifacts/task-30-regression/` for the native
frames, motion clips, logs, restored test fixture archive and the verified
copy of the installed TASK-03 world. The [evidence transfer checklist](../evidence/README.md#what-to-transfer)
identifies the rest of the runtime and comparison inputs.
