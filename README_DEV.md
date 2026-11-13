# Iris shaderpack development

The working pack is [`shaderpack/`](shaderpack/README.md). Iris loads the
unpacked directory and expects `shaders/` at its root. Start with the
[developer handoff](docs/HANDOFF.md) for the load, regression and benchmark
procedures. The [known gaps](docs/KNOWN_GAPS.md) include reproductions and
small starter tasks.

The retained source was tested on Minecraft Java Edition **1.21.1** with
NeoForge **21.1.265**, Iris **1.8.14-beta.1+mc1.21.1**, Sodium
**0.8.13+mc1.21.1** and Microsoft Java **21.0.7+6-LTS** in the Prism Flatpak
`GenshinShaderDev` instance. Use the [compatibility record](docs/testing/compatibility_notes.md)
for the tested mod set, GPU, driver and version boundaries.

Run these checks from the repository root with Python 3, GNU coreutils
and `glslangValidator` on PATH.

```bash
sha256sum --quiet -c evidence/task-25/fog-pack.sha256
python3 evidence/task-22/link_shaders.py shaderpack/shaders
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Expect 13 linked program pairs and nine passing tests. Both TASK-28 and
TASK-30 ran the accepted source in Iris.
[Runtime regression](docs/testing/regression_report.md),
[TASK-30 replay verification](evidence/task-30/verification.txt).

- [Evidence index](evidence/README.md) maps each task to its replay, raw inputs and reviewed results.
- [Script inventory](scripts/README.md) identifies the shared tools, fixture sources and task-specific entry points.
- [Project status](docs/STATUS.md), [decisions](docs/DECISIONS.md) and [test log](docs/TEST_LOG.md) record the project history.

For a handoff, include the current working source and reviewed evidence
files. Local `main` ends at TASK-05, so a checkout of that commit alone
lacks the working shaders and later replays. Preserve the required ignored
fixtures, snapshots, media and raw evidence alongside the source using
the [transfer checklist](evidence/README.md#what-to-transfer).
