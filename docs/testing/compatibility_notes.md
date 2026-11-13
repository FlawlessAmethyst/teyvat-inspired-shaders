# TASK-29 — Limited compatibility investigation

**DONE**, 2026-11-13. TASK-29 matched the working shader tree to the
TASK-28 snapshot and reviewed the saved run, installed metadata and
upstream documentation. TASK-30 repeated that runtime suite against the
same fog-tuned TASK-25 source on the same stack.
[Shader manifest](../../evidence/task-25/fog-pack.sha256),
[runtime regression](regression_report.md), [TASK-30 verification](../../evidence/task-30/verification.txt).

## Tested development stack

- **Client.** Minecraft Java Edition 1.21.1, NeoForge 21.1.265, Iris
  `1.8.14-beta.1+mc1.21.1`, Sodium `0.8.13+mc1.21.1`, Microsoft Java
  21.0.7+6-LTS and LWJGL 3.3.3 (`3.3.3+5` in the client log). Prism Launcher
  11.1.1 Flatpak ran the existing `GenshinShaderDev` mod set, including
  Forgified Fabric API, Connector and optimization mods. The archived
  log contains the actual mod list. [Environment](../minecraft-environment.md),
  [client log](../../artifacts/task-28/logs-20261113-194922/latest.log),
  [instance components](../../artifacts/task-28/logs-20261113-194922/mmc-pack.json).
- **Rendering.** CachyOS x86-64, kernel `7.3.3-1-cachyos`, GeForce RTX
  4080 SUPER, NVIDIA `580.196.07`, OpenGL `4.6.0`. Single-player at
  2560×1440 fullscreen, 70° FOV and 12/8 chunk render/simulation distance.
  The saved options list `vanilla`, `fabric` and `mod_resources` with no
  third-party resource pack. Both runs exercised seven fixed scenes, motion,
  a clear/rain/clear cycle, the waterline, cave entry and command teleports
  through the three vanilla dimensions. The logs show the selected pack,
  dimension pipeline rebuilds and a normal save and exit.
  [Test conditions and results](regression_report.md#test-conditions),
  [saved options](../../artifacts/task-28/settings/options.txt),
  [runtime verification](../../evidence/task-28/verification.txt).

The installed Iris JAR declares Minecraft `[1.21,1.21.1)` in
`META-INF/neoforge.mods.toml`, which excludes the tested 1.21.1 endpoint.
Iris's published beta page lists Minecraft 1.21.1 for NeoForge and
describes the update to Sodium 0.8. The archived run confirms this
installation loaded the beta and rendered the pack. The reason the local
range did not prevent startup was not established. The same TOML declares
Embeddium incompatible. [Environment record](../minecraft-environment.md),
[Iris beta release](https://modrinth.com/mod/iris/version/1.8.14-beta.1%2B1.21.1-neoforge).

## API differences relevant to the pack

| Interface | Version difference and what to check |
| --- | --- |
| GLSL patching and vanilla vertex inputs | Iris patches `#version 330 compatibility` programs to the game's core rendering path. Iris Docs cites Minecraft 1.21.2's vanilla `chunkOffset` → `modelOffset` rename as an example of the mapping the patcher absorbs. The pack uses compatibility inputs such as `gl_Vertex` and the lightmap texture matrix. On another build, check the in-client terrain and fallback programs and the lit cave before drawing conclusions from a standalone GLSL link. [Geometry vertex code](../../shaderpack/shaders/lib/geometry_vertex.glsl), [Iris profile docs](https://shaders.properties/current/how-to/compatibility_vs_core/) |
| Shadow programs and the Sodium pair | Iris 1.8 introduced `shadow_solid`. This pack's specialized opaque caster writes depth without sampling the atlas. The shared `shadow` program alpha-tests cutouts. Older Iris lacks the specialized path, so caster coverage and cost would need checking even if the shared program renders. Iris 1.8.12 for this game and loader lists Sodium 0.6.13, while the tested 1.8.14 beta updates to Sodium 0.8. Match the pair to the selected Iris build. [Pack casters](../../shaderpack/shaders/shadow_solid.fsh), [shared caster](../../shaderpack/shaders/shadow.fsh), [Iris shadow docs](https://shaders.properties/current/reference/programs/shadow/), [Iris 1.8.12 release](https://modrinth.com/mod/iris/version/1.8.12%2B1.21.1-neoforge), [Iris beta release](https://modrinth.com/mod/iris/version/1.8.14-beta.1%2B1.21.1-neoforge) |
| Camera, dimension and depth bindings | The pack uses Iris-specific `cameraPositionInt` and `cameraPositionFract` for cloud and water phase, and `hasSkylight` and `hasCeiling` to gate Overworld shading. Water uses `depthtex2` with `gbufferProjectionInverse` for thickness. The pinned Iris 1.21.1 source takes that snapshot before the hand and the `depthtex1` snapshot before translucent terrain. Verify the depth contents, hand and glass edges, and dimension return on another build. [Iris camera docs](https://shaders.properties/current/reference/uniforms/camera/), [dimension uniforms](https://shaders.properties/current/reference/uniforms/biome/), [pinned pipeline](https://github.com/IrisShaders/Iris/blob/12ea3bf16b39c0a70ec31dc9de1483c77bd3ccc3/common/src/main/java/net/irisshaders/iris/pipeline/IrisRenderingPipeline.java), [water diagnostic](water.md) |
| Color attachments | Iris 1.10.5 raises the documented color-attachment limit from 16 to 32. The pack uses only `colortex0`, requested as `RGBA16F`, then sampled by `final` for grading and sRGB output. The larger limit adds no requirement for this source. Verify the attachment and display output independently of whether the pack compiles. [Final shader](../../shaderpack/shaders/final.fsh), [Iris color-buffer docs](https://shaders.properties/current/reference/buffers/colortex/), [palette validation](palette.md) |
| Minecraft block IDs and fog | Minecraft 1.20.3 renamed `minecraft:grass` to `minecraft:short_grass`. The pack's `block.properties` maps the latter to its vegetation material via `mc_Entity`. An older registry could miss that material tint even when the shaders link. Minecraft 1.21.6 also split vanilla fog into environmental and render-distance terms. The pack computes its own air fog. The vanilla change makes fallback draws and the sky/terrain boundary worth checking, with any actual effect on the pack still unverified. [Block mappings](../../shaderpack/shaders/block.properties), [Iris block mapping docs](https://shaders.properties/current/reference/miscellaneous/block_properties/), [Minecraft 1.20.3 release](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-3), [Minecraft 1.21.6 release](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-6) |

The pinned Iris source describes the 1.21.1 branch at a known revision.
Its correspondence to the installed beta's build commit is unverified.
The runtime claims above come from the installed client log and captures.
[Pinned source and version boundary](../research/iris_feasibility.md#evidence-and-version-boundary).

## Untested combinations

The scoped Prism inventory found cached Minecraft 1.21.1 and 26.3 client
JARs. It found only the 1.21.1 NeoForge loader in the library cache and
only the tested Iris/Sodium pair in `GenshinShaderDev`. Iris publishes a
26.3 NeoForge build, but a cached game JAR alone is insufficient for a
shader test. Skipped the optional run because it would require provisioning
a second stack. [Iris 26.3 release](https://modrinth.com/mod/iris/version/1.11.7%2B26.3-neoforge).

Minecraft 26.3, all other Minecraft releases and alternate Iris/Sodium
pairs remain untested for this pack. The Fabric and Quilt loaders, OptiFine, different
NeoForge builds, Windows, macOS, AMD/Intel GPUs and other driver versions
also remain untested. The evidence covers the existing mod set and built-in
resources. A minimal mod set, third-party resource packs,
Distant Horizons/Voxy, modded materials, custom dimensions and multiplayer
remain untested. The three vanilla dimension checks used command
teleports and settled views. Portal travel and overlays remain open.
[Runtime limits and known issues](regression_report.md#prioritized-open-bugs).

## Verification commands

Run from the repository root. The linker checks the 13 expanded GLSL
program pairs offline. The reviewer reads the saved captures and logs.

```bash
sha256sum --quiet -c evidence/task-25/fog-pack.sha256
diff -rq shaderpack/shaders artifacts/task-28/shaders
diff -rq shaderpack/shaders artifacts/task-30-regression/shaders
python3 evidence/task-22/link_shaders.py shaderpack/shaders
python3 evidence/task-28/review.py artifacts/task-28
python3 evidence/task-28/review.py artifacts/task-30-regression
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/verify_references.py
```

To inspect the development install and the scoped Prism library cache:

```bash
prism_root=~/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher
instance="$prism_root/instances/GenshinShaderDev"
diff -u artifacts/task-28/logs-20261113-194922/mmc-pack.json "$instance/mmc-pack.json"
find "$instance/minecraft/mods" -maxdepth 1 -type f -printf '%f\n' | sort
find "$prism_root/libraries" -type f \( -iname '*iris*.jar' -o -iname '*sodium*.jar' \
    -o -path '*/com/mojang/minecraft/*/*-client.jar' -o -name 'neoforge-*-universal.jar' \
    -o -name 'fabric-loader-*.jar' -o -name 'quilt-loader-*.jar' \) -printf '%P\n' | sort
sha256sum "$instance"/minecraft/mods/{iris-neoforge,sodium-neoforge}-*.jar
unzip -p "$instance/minecraft/mods/iris-neoforge-1.8.14-beta.1+mc1.21.1.jar" META-INF/neoforge.mods.toml
```

The [developer handoff](../HANDOFF.md) uses this stack as its runtime baseline.
