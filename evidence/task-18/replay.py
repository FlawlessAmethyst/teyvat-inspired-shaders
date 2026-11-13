#!/usr/bin/env python3
"""Install, capture and restore TASK-18 variants in the scoped test instance."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'evidence/task-17'))
import replay as harness

mc = harness.scenes.mc
WORLD = harness.SOURCE_WORLD.with_name('TASK-18 Cloud Scenes')
CLOUDS = mc.GAME / 'shaderpacks/TASK-18-clouds'
CONTROL = mc.GAME / 'shaderpacks/TASK-18-control'
SCENES = ('daylight', 'sunset', 'rain', 'night', 'cave')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'control', 'clouds', 'capture', 'restore'))
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    harness.scenes.WORLD = WORLD
    harness.PACK = CLOUDS
    if args.action == 'capture':
        for name in SCENES:
            harness.scenes.replay(name, args.root / name, resume=False)
        return
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing the instance')
    if args.action == 'prepare':
        if any(path.exists() or path.is_symlink() for path in (CLOUDS, CONTROL, WORLD)):
            raise RuntimeError('A TASK-18 fixture already exists')
        control = ROOT / 'artifacts/task-17/shaders'
        if not (control / 'gbuffers_skybasic.fsh').is_file():
            raise RuntimeError('The verified TASK-17 control is missing')
        harness.prepare(args.root)
        shutil.copytree(control, CONTROL / 'shaders')
        shutil.copytree(control, args.root / 'control-shaders')
    elif args.action == 'restore':
        archive = args.root / 'world'
        if WORLD.exists() and archive.exists():
            raise RuntimeError(f'World archive already exists: {archive}')
        harness.configure_mode('restore', args.root)
        if WORLD.is_dir():
            shutil.move(WORLD, archive)
        if CONTROL.is_dir():
            shutil.rmtree(CONTROL)
    else:
        harness.PACK = CONTROL if args.action == 'control' else CLOUDS
        harness.configure_mode('prototype', args.root)


if __name__ == '__main__':
    main()
