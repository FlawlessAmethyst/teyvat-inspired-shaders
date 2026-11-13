#!/usr/bin/env bash
# Verify restoration and retained inputs while the dedicated game is stopped.
set -euo pipefail
root=$1
game=$(python3 - <<'PY'
import sys
sys.path.insert(0, 'tools')
import minecraft

assert not minecraft.game_pids(), 'GenshinShaderDev is still running'
print(minecraft.GAME)
PY
)
for path in options.txt config/{iris.properties,sodium-options.json,sodium-extra-options.json,dynamic_fps.json}; do
    cmp "$game/$path" "$root/before/${path##*/}"
done
test ! -e "$game/saves/TASK-25 Visual Comparison"
test -d "$root/world"
test -z "$(find "$game/shaderpacks" -maxdepth 1 -name 'TASK-27-*' -print -quit)"
world_manifest=$(realpath "$root/source-world.sha256")
(cd artifacts/task-25-fog-tuning/world && sha256sum --quiet -c "$world_manifest")
sha256sum --quiet -c artifacts/task-22/source-world.sha256
diff -rq artifacts/task-25-fog-tuning/shaders "$root/variants/full/shaders"
python3 - "$root/world" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, 'evidence/task-27')
from optimize import scenes

scenes.WORLD = Path(sys.argv[1])
try:
    scenes.require_scene_world()
except RuntimeError as error:
    assert str(error).startswith('The dedicated TASK-03 world is not open')
else:
    raise RuntimeError('The archived fixture still holds a session lock')
PY
printf 'PASS restored five settings, removed temporary packs, and verified both source worlds\n'
