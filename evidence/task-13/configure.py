#!/usr/bin/env python3
"""Stage the matched TASK-13 packs and reuse the TASK-10 settings backup."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'evidence/task-10'))
import configure as baseline

MODES = ('sunlight', 'ambient')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore'))
    parser.add_argument('artifacts', type=Path)
    args = parser.parse_args()
    game = baseline.mc.GAME
    packs = {mode: game / 'shaderpacks' / f'TASK-13-{mode}' for mode in MODES}
    sources = {mode: args.artifacts / 'variants' / mode / 'shaders' for mode in MODES}

    if baseline.mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing files')
    if args.action == 'prepare':
        for mode in MODES:
            if packs[mode].exists() or packs[mode].is_symlink():
                raise RuntimeError(f'Temporary pack path already exists: {packs[mode]}')
            if not (sources[mode] / 'final.fsh').is_file():
                raise RuntimeError(f'Missing staged {mode} source')

    baseline.PACK = packs.get(args.action, packs['sunlight'])
    action = 'neutral' if args.action in MODES else args.action
    sys.argv = [sys.argv[0], '--artifacts-dir', str(args.artifacts),
                '--shaders-dir', str(sources['sunlight']), action]
    baseline.main()

    if args.action == 'prepare':
        shutil.copytree(sources['ambient'], packs['ambient'] / 'shaders')
    elif args.action == 'restore':
        if packs['ambient'].is_dir():
            shutil.rmtree(packs['ambient'])
        print('Removed both temporary TASK-13 packs')
    else:
        print(f'Selected {baseline.PACK.name}')


if __name__ == '__main__':
    main()
