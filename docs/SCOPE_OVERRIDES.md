# Active scope and historical brief

The owner-supplied brief (`task.md`) is kept locally for artistic and research
context. Newer explicit user instructions, local `AGENTS.md`, and the narrowed
local task plan (`task_decomposed.md`) define the active implementation scope.

| Historical brief / recommendation | Active requirement |
| --- | --- |
| Select shaderpack, mod or hybrid | One Iris shaderpack; document Iris limitations without switching architecture. |
| Graphics settings, quality profiles and localization | One coherent default style; developer flags only for necessary debugging/benchmarking. No player-facing settings. |
| Resource/asset or interface changes | No resource-pack authoring, proprietary extraction, custom textures/meshes or UI overhaul. |
| Broad loader/version support | Claim only combinations actually tested. No blanket compatibility certification. |
| Release-ready deliverable | Clean development source and developer handoff; no distribution/release packaging. |
| Performance/profile targets and similarity percentages | Performance leads; original budgets are aspirations. Use reproducible measured costs and qualitative evidence, never invented scores. |
| Windows reference path | Use repository `references/pictures/settings_screen/` and `references/video/gameplay/`; never modify originals. |
| Suggested Fabric baseline in plan | Reuse actual CachyOS / Prism Flatpak / GenshinShaderDev / Minecraft 1.21.1 NeoForge / Iris / Sodium baseline. |
| Broad implementation stages | Execute only the requested task. Research and feasibility precede TASK-09 implementation; only a scoped TASK-08 spike may precede it. |

TASK-00 demonstrated startup, automation, capture and metadata-only pack discovery.
It did not demonstrate GLSL compilation, in-world shader rendering or frame-time
recording. TASK-02 subsequently verified native CPU render-loop recording and
TASK-03 established controlled visual baselines. TASK-09 verified neutral GLSL
compilation and Overworld rendering on the installed stack. TASK-10 measured
matched Sodium and neutral-pack client loop baselines.
See [STATUS.md](STATUS.md) for current progress.
Exact versions, commands, paths and desktop permission requirements live in
[minecraft-environment.md](minecraft-environment.md).

Study targeted canonical upstream sources and record revision/license before any
compatible reuse. Prefer cheap stylized approximations; justify costly effects
with visual evidence and measurements against Sodium without shaders.
