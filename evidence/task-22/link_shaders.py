#!/usr/bin/env python3
"""Link every expanded shader pair with the render-stage macros Iris supplies."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'task-12'))
from check_glsl import expand

stages = {'SKY': 1, 'SUNSET': 2, 'STARS': 6, 'HAND_SOLID': 16, 'CLOUDS': 20,
          'RAIN_SNOW': 21, 'HAND_TRANSLUCENT': 23}
defines = [f'-DMC_RENDER_STAGE_{name}={value}' for name, value in stages.items()]
shaders = Path(sys.argv[1])
with TemporaryDirectory(prefix='task-22-glsl-') as temp:
    for fragment in sorted(shaders.glob('*.fsh')):
        vertex = fragment.with_suffix('.vsh')
        vert = Path(temp) / (vertex.stem + '.vert')
        frag = Path(temp) / (fragment.stem + '.frag')
        vert.write_text(expand(vertex, shaders))
        frag.write_text(expand(fragment, shaders))
        subprocess.run(['glslangValidator', '-l', *defines, vert, frag], check=True)
        print(f'PASS {fragment.stem}', flush=True)
