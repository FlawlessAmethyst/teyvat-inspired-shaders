#!/usr/bin/env python3
"""Replay the TASK-03 presets in a disposable TASK-17 copy."""
import argparse
import gzip
import struct
import sys
import time
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'evidence/task-10'), str(ROOT / 'scripts')]

import configure
import scenes

SOURCE_WORLD = scenes.WORLD
scenes.WORLD = SOURCE_WORLD.with_name('TASK-17 Prototype Scenes')
PACK = scenes.mc.GAME / 'shaderpacks/TASK-17-prototype'
BATCHES = ('sodium-01', 'prototype-01', 'prototype-02', 'sodium-02')


def configure_mode(action, root):
    configure.PACK = PACK
    sys.argv = [sys.argv[0], '--artifacts-dir', str(root), '--shaders-dir',
                str(root / 'shaders'), 'neutral' if action == 'prototype' else action]
    configure.main()


def prepare(root, shaders_dir=ROOT / 'shaderpack/shaders'):
    if scenes.WORLD.exists() or scenes.WORLD.is_symlink():
        raise RuntimeError(f'World copy already exists: {scenes.WORLD}')
    root.mkdir(parents=True)
    shutil.copytree(shaders_dir, root / 'shaders')
    configure_mode('prepare', root)
    shutil.copytree(SOURCE_WORLD, scenes.WORLD, ignore=shutil.ignore_patterns('session.lock'))
    level = scenes.WORLD / 'level.dat'
    raw = gzip.decompress(level.read_bytes())
    fields = scenes.nbt_fields(raw)
    name = scenes.WORLD.name.encode()
    values = {'LevelName': struct.pack('>H', len(name)) + name,
              'LastPlayed': struct.pack('>q', time.time_ns() // 1_000_000)}
    edits = [(fields['Data', key][1:], value) for key, value in values.items()]
    for (start, end), value in sorted(edits, reverse=True):
        raw = raw[:start] + value + raw[end:]
    scenes.nbt_fields(raw)
    level.write_bytes(gzip.compress(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'sodium', 'prototype', 'profile', 'restore'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.path)
    elif args.action == 'profile':
        for name in scenes.SPEC:
            scenes.replay(name, args.path / name, resume=False, profile=True)
    elif args.action == 'restore':
        archive = args.path / 'world'
        if scenes.WORLD.exists() and archive.exists():
            raise RuntimeError(f'World archive already exists: {archive}')
        configure_mode('restore', args.path)
        if scenes.WORLD.is_dir():
            shutil.move(scenes.WORLD, archive)
    else:
        configure_mode(args.action, args.path)


if __name__ == '__main__':
    main()
