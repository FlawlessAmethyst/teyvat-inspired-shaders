#!/usr/bin/env bash
# Run with the profiling client stopped and access to the NVIDIA device.
set -euo pipefail
root=$1
input="$root/sodium-01/runs/valley/recording/before.png"
out="$root/gpu"
mkdir "$out"
python3 - "$root" "$out" <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, 'evidence/task-12')
from check_glsl import expand

root, out = map(Path, sys.argv[1:])
stages = {'SKY': 1, 'SUNSET': 2, 'STARS': 6, 'HAND_SOLID': 16, 'CLOUDS': 20,
          'RAIN_SNOW': 21, 'HAND_TRANSLUCENT': 23}
defines = ''.join(f'#define MC_RENDER_STAGE_{name} {value}\n' for name, value in stages.items())
passes = {
    'full': ('gbuffers_skybasic', 'final', 'gbuffers_water', 'gbuffers_textured_lit', 'gbuffers_terrain'),
    'shadowless': ('gbuffers_terrain',),
    'terrain-vanilla': ('gbuffers_terrain',),
    'cloudless': ('gbuffers_skybasic',),
    'gradeless': ('final',),
    'water-depthless': ('gbuffers_water',),
    'water-vanilla': ('gbuffers_water',),
    'fogless': ('gbuffers_textured_lit',),
}
for variant, shaders in passes.items():
    source = root / 'variants' / variant / 'shaders'
    for shader in shaders:
        for stage, ext in [('vsh', 'vert'), ('fsh', 'frag')]:
            version, body = expand(source / f'{shader}.{stage}', source).split('\n', 1)
            (out / f'{variant}-{shader}.{ext}').write_text(version + '\n' + defines + body)

# Preserve the sky stage and the palette. Substitute the horizon color for
# directional shading and dither within the cloudless draw.
vert = out / 'cloudless-gbuffers_skybasic.vert'
(out / 'flat-gbuffers_skybasic.vert').write_bytes(vert.read_bytes())
frag = (out / 'cloudless-gbuffers_skybasic.frag').read_text()
start = frag.index('            vec3 ray = normalize(viewRay);')
end = frag.index('            gl_FragData[0] = vec4(color, 1.0);', start)
(out / 'flat-gbuffers_skybasic.frag').write_text(
    frag[:start] + '            vec3 color = skyHorizon;\n' + frag[end:])
PY
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-18/sky_timer.c -o "$out/sky_timer" -lEGL -lGL -lm
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-23/final_timer.c -o "$out/final_timer" -lEGL -lGL -lm
cc -std=c11 -O2 -Wall -Wextra -Werror evidence/task-26/geometry_timer.c -o "$out/geometry_timer" -lEGL -lGL -lm
magick "$input" -flip -alpha off -depth 8 "rgb:$out/valley.rgb"
for run in 01 02; do
    "$out/sky_timer" "$out/"{cloudless,full}-gbuffers_skybasic.{vert,frag} \
        > "$out/cloud-$run.csv" 2> "$out/cloud-$run-device.txt"
    "$out/sky_timer" "$out/"{flat,cloudless}-gbuffers_skybasic.{vert,frag} \
        > "$out/sky-gradient-$run.csv" 2> "$out/sky-gradient-$run-device.txt"
    "$out/final_timer" "$out/"{gradeless,full}-final.{vert,frag} "$out/valley.rgb" \
        > "$out/grade-$run.csv" 2> "$out/grade-$run-device.txt"
    "$out/geometry_timer" water "$out/"{water-depthless,full}-gbuffers_water.{vert,frag} \
        > "$out/water-depth-$run.csv" 2> "$out/water-depth-$run-device.txt"
    "$out/geometry_timer" water "$out/"{water-vanilla,full}-gbuffers_water.{vert,frag} \
        > "$out/water-material-$run.csv" 2> "$out/water-material-$run-device.txt"
    "$out/geometry_timer" fog "$out/"{fogless,full}-gbuffers_textured_lit.{vert,frag} \
        > "$out/fog-$run.csv" 2> "$out/fog-$run-device.txt"
    "$out/geometry_timer" terrain "$out/"{shadowless,full}-gbuffers_terrain.{vert,frag} \
        > "$out/shadow-receiver-$run.csv" 2> "$out/shadow-receiver-$run-device.txt"
    "$out/geometry_timer" terrain "$out/"{terrain-vanilla,shadowless}-gbuffers_terrain.{vert,frag} \
        > "$out/terrain-lighting-$run.csv" 2> "$out/terrain-lighting-$run-device.txt"
done
