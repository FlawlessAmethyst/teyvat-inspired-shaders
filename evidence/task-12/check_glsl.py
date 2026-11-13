#!/usr/bin/env python3
"""Expand Iris includes and link each shader pair."""
import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


def expand(path, shaders):
    return re.sub(r'^#include "/([^"]+)"$', lambda match: expand(shaders / match[1], shaders),
                  path.read_text(), flags=re.MULTILINE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('shaders', type=Path)
    shaders = parser.parse_args().shaders
    with TemporaryDirectory(prefix='task-12-glsl-') as temp:
        fragments = sorted(shaders.glob('*.fsh'))
        if not fragments:
            raise ValueError(f'No fragment shaders in {shaders}')
        for fragment in fragments:
            vertex = fragment.with_suffix('.vsh')
            vert = Path(temp) / (vertex.stem + '.vert')
            frag = Path(temp) / (fragment.stem + '.frag')
            vert.write_text(expand(vertex, shaders))
            frag.write_text(expand(fragment, shaders))
            subprocess.run(['glslangValidator', '-l', vert, frag], check=True, capture_output=False)
            print(f'PASS {fragment.stem}', flush=True)
