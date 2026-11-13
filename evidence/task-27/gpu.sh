#!/usr/bin/env bash
# Run after the GenshinShaderDev client has stopped.
set -euo pipefail
root=$1
out="$root/gpu"
mkdir "$out"
python3 - "$root" "$out" <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, 'evidence/task-12')
from check_glsl import expand

root, out = map(Path, sys.argv[1:])
passes = {
    'full': ('shadow', 'shadow_solid', 'gbuffers_textured_lit'),
    'fog': ('gbuffers_textured_lit',),
}
defines = ''.join(f'#define MC_RENDER_STAGE_{name} {value}\n' for name, value in
                  {'HAND_SOLID': 16, 'CLOUDS': 20, 'RAIN_SNOW': 21, 'HAND_TRANSLUCENT': 23}.items())
for variant, shaders in passes.items():
    source = root / 'variants' / variant / 'shaders'
    for shader in shaders:
        for stage, ext in [('vsh', 'vert'), ('fsh', 'frag')]:
            version, body = expand(source / f'{shader}.{stage}', source).split('\n', 1)
            (out / f'{variant}-{shader}.{ext}').write_text(version + '\n' + defines + body)
PY
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-27/shadow_timer.c -o "$out/shadow_timer" -lEGL -lGL -lm
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-26/geometry_timer.c -o "$out/geometry_timer" -lEGL -lGL -lm
map_size() {
    sed -n 's/^const int shadowMapResolution = \([0-9]*\);$/\1/p' "$root/variants/$1/shaders/lib/shadows.glsl"
}
for run in 01 02; do
    "$out/shadow_timer" "$out/full-shadow_solid."{vert,frag} "$out/full-shadow."{vert,frag} \
        "$(map_size full)" "$(map_size shadow)" > "$out/shadow-$run.csv" 2> "$out/shadow-$run-device.txt"
    "$out/geometry_timer" fog "$out/"{full,fog}-gbuffers_textured_lit.{vert,frag} \
        > "$out/fog-$run.csv" 2> "$out/fog-$run-device.txt"
done
