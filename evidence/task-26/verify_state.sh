#!/usr/bin/env bash
# Check the dedicated instance and retained inputs after restoration.
set -euo pipefail
root=$1
game=$(python3 -c 'import sys; sys.path.insert(0,"tools"); import minecraft; print(minecraft.GAME)')
for path in options.txt config/{iris.properties,sodium-options.json,sodium-extra-options.json,dynamic_fps.json}; do
    cmp "$game/$path" "$root/before/${path##*/}"
done
test ! -e "$game/saves/TASK-25 Visual Comparison"
test -d "$root/world"
test -z "$(find "$game/shaderpacks" -maxdepth 1 -name 'TASK-26-*' -print -quit)"
world_manifest=$(realpath "$root/source-world.sha256")
(cd artifacts/task-25-fog-tuning/world && sha256sum --quiet -c "$world_manifest")
sha256sum --quiet -c artifacts/task-22/source-world.sha256
diff -rq artifacts/task-25-fog-tuning/shaders "$root/variants/full/shaders"
