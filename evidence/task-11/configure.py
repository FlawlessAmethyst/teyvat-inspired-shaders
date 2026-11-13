#!/usr/bin/env python3
"""Reuse TASK-10's configuration backup and apply the TASK-11 test variants."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('baseline_config', BASE / 'task-10/configure.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', required=True, type=Path)
    parser.add_argument('action', choices=('prepare', 'neutral', 'graded', 'diagnostic', 'restore'))
    args = parser.parse_args()
    packs = {name: baseline.mc.GAME / f'shaderpacks/TASK-11-{name}'
             for name in ('neutral', 'graded', 'diagnostic')}
    if baseline.mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev first')

    action = args.action
    variant = action if action in packs else 'graded'
    baseline.PACK = packs[variant]
    if action == 'prepare':
        for name, path in packs.items():
            if path.exists() or path.is_symlink():
                raise RuntimeError(f'Temporary shaderpack path already exists: {path}')
            if not (args.artifacts_dir / 'variants' / name / 'shaders/final.fsh').is_file():
                raise RuntimeError(f'Missing staged {name} shader')
        if not (args.artifacts_dir / 'variants/graded/shaders/lib/tonemap.glsl').is_file():
            raise RuntimeError('Missing staged tone mapping module')

    baseline_action = 'neutral' if action in packs else action
    sys.argv = [sys.argv[0], '--artifacts-dir', str(args.artifacts_dir),
                '--shaders-dir', str(args.artifacts_dir / 'variants/graded/shaders'),
                baseline_action]
    baseline.main()

    if action == 'prepare':
        for name in ('neutral', 'diagnostic'):
            shutil.copytree(args.artifacts_dir / 'variants' / name / 'shaders',
                            packs[name] / 'shaders')
    elif action == 'restore':
        for name in ('neutral', 'diagnostic'):
            if packs[name].is_dir():
                shutil.rmtree(packs[name])


if __name__ == '__main__':
    main()
