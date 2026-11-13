#!/usr/bin/env bash
# Run with GenshinShaderDev stopped, with access to the NVIDIA device.
set -euo pipefail
root=$1
test -f "$root/control-01/forest/native.png"
mkdir -p "$root/timer-source"
python3 - "$root" <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, 'evidence/task-12')
from check_glsl import expand

root = Path(sys.argv[1])
for name, directory in [('control', 'shaders'), ('spatial', 'spatial-shaders')]:
    source = root / directory
    for stage, ext in [('vsh', 'vert'), ('fsh', 'frag')]:
        (root / 'timer-source' / f'{name}.{ext}').write_text(expand(source / f'final.{stage}', source))
PY
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-23/final_timer.c -o "$root/final_timer" -lEGL -lGL -lm
for scene in daylight forest open-water; do
    magick "$root/control-01/$scene/native.png" -flip -alpha off -depth 8 "rgb:$root/timer-source/$scene.rgb"
    for repeat in 01 02; do
        "$root/final_timer" "$root/timer-source"/{control.vert,control.frag,spatial.vert,spatial.frag} \
            "$root/timer-source/$scene.rgb" > "$root/gpu-$scene-$repeat.csv" 2> "$root/gpu-$scene-$repeat-device.txt"
    done
done
