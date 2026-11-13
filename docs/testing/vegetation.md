# Vegetation color and lighting

TASK-20, 2026-11-13. [Evidence index](../../evidence/task-20/README.md).

## Shader behavior

The terrain vertex shader reads Iris's block material attribute. Pack-local
ID 10002 selects vanilla leaf blocks. ID 10003 selects grass blocks, short
and tall grass, and both sizes of fern. The correction scales with how much
green exceeds the stronger of red and blue in the original vertex tint. It
slightly cools green leaves and restrains grass saturation. Neutral tints
such as grass-block dirt retain their existing color. The tint is still
multiplied by the atlas color and retains the original biome and vertex AO
variation. [Block mapping](../../shaderpack/shaders/block.properties),
[vertex path](../../shaderpack/shaders/lib/geometry_vertex.glsl).

Leaf fill increases by up to 28% of its existing value on off-sun faces.
The existing daylight, skylight and block-light terms bound the increase,
so dim interiors and lamp-lit geometry receive less of it. The receiver
still evaluates the original face normal and direct light through the
existing shadow map. The material adds arithmetic at vertices and reuses
the existing draw, texture reads and interpolants. Alpha tests, vertex
positions and the shadow caster use their existing paths. The shipped
effect is static because S7's reference evidence supports a color and
lighting change. Sway would require separate plant anchoring and matching
caster displacement.
[Lighting code](../../shaderpack/shaders/lib/terrain_lighting.glsl),
[S7 reference rubric](../research/style_targets.md#s7--bright-vegetation-with-retained-volume).

## Capture conditions

The original daylight and forest presets retain their cameras and settings.
A disposable TASK-03 world copy adds two oak crowns across a plains/jungle
boundary, overlapping jungle, spruce, birch, dark oak and cherry crowns,
short and tall grass, ferns, and a stone-brick path for shadow inspection.
One camera looks along the path below the crowns. A second looks down from
a perch toward the sunlit tops. Both use clear weather at time 6000.
Each native F2 capture follows 20 focused seconds in its preset. Cloud
phase varies independently. [Fixture source](../../evidence/task-20/fixture.mcfunction),
[recorded presets](../../artifacts/task-20/presets.json).

## Visual review

| View | Observation |
| --- | --- |
| [Daylight](../../artifacts/task-20/daylight.jpg) | The foreground remains yellow-green with less saturation. The stone-brick wall and grass still read as separate materials. |
| [Forest](../../artifacts/task-20/forest.jpg) | The shaded oak faces are a little brighter and cooler. Dark pockets, cutout edges and the darker trunks retain their contrast. |
| [Dense understory](../../artifacts/task-20/dense.jpg) | The yellow-green plains oak and deeper green jungle oak remain distinct. Short grass, tall grass and fern silhouettes retain their cutouts and the visible tall grass halves join at the same positions. Cast shadows stay aligned with the crowns and trunks. |
| [Canopy tops](../../artifacts/task-20/canopy-top.jpg) | Sunlit surfaces still stand out over darker sides and overlapping crowns. Leaf gaps remain visible along the edges. |

The daylight grass patch changed from mean display RGB `(101, 136, 32)`
to `(106, 130, 36)`. The forest oak crown patch brightened from
`(40, 66, 8)` to `(44, 75, 13)`. Selected wall, trunk, lit path and
shadowed path patches are byte-identical. The comparisons use the native
8-bit captures. Two leaf/sky edge patches also match in coverage.
R2's yellow-green grass and cooler crowns guided the relative palette.
R1 and R5 also retain dark foliage and green/stone
separation. [Patch values and coordinates](../../evidence/task-20/pixels.csv),
[indexed reference stills](../../evidence/task-17/references.csv).

## Performance

Each mode ran in two fresh sessions at 2560×1440, 70° FOV, 12 chunks render
distance, 8 chunks simulation distance, unlimited FPS and VSync off. Each
session recorded the original daylight scene and the dense ground-level
view after the same 20-second warm-up. The stack was Minecraft 1.21.1,
NeoForge 21.1.265, Iris 1.8.14-beta.1 and Sodium 0.8.13 on CachyOS with a
Ryzen 9 9950X and RTX 4080 SUPER, NVIDIA driver 580.196.07. The archive
runtime, options and mod hashes matched TASK-10.
[Harness metric](harness.md#what-the-performance-record-means),
[archive and raw CSV index](../../evidence/task-20/runs.csv).

| View | Sodium shaders off | TASK-19 control | TASK-20 vegetation | Vegetation increment |
| --- | ---: | ---: | ---: | ---: |
| Daylight | 0.2023 ms | 0.4977 ms | 0.4931 ms | −0.0046 ms (−0.92%) |
| Dense canopy | 0.2131 ms | 0.4993 ms | 0.5009 ms | +0.0016 ms (+0.32%) |

Each value averages the two session means from Minecraft's F3+L CPU
client-loop samples. The vegetation-control differences were −0.0059 and
−0.0033 ms in daylight and −0.0027 and +0.0059 ms under dense canopy. The
p95 differences changed sign between repeats in both scenes. These
differences are small at the observed run-to-run variation. Keep the
vertex-only material for the visual improvement. TASK-26 includes tint
and leaf fill in the grouped terrain-lighting ablation. The foliage-only
GPU cost, presentation cadence and representative gameplay performance
remain open. [TASK-26 terrain lighting coverage](effect_costs.md#coverage-and-limits).

The first TASK-19 control trial lost focus and was excluded. Its fresh
repeat and all other accepted sessions match the selected static camera
patches before and after profiling. [Replay and checks](../../evidence/task-20/commands.txt).

## Limits and handoff

Validation covers fixed clear-day Overworld scenes on the installed Iris
beta and the vanilla terrain materials visible in the fixture. TASK-21
reuses the fixture for live rain onset and clearing under the dense canopy.
TASK-23 walks through the original TASK-03 forest in clear daylight. Oak
cutout shimmer persists with the accepted pack and the spatial AA trial.
Dimension-specific vegetation rendering, individual mapping coverage for
all listed leaf species, and waterlogged leaves remain open. TASK-21 used
the exact TASK-20 shader snapshot for its incremental comparison.
[Source manifest](../../evidence/task-20/pack.sha256),
[replay commands](../../evidence/task-20/commands.txt), [weather report](weather.md),
[foliage motion review](anti_aliasing.md#visual-review).
