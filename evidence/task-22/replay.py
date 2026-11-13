#!/usr/bin/env python3
"""Replay lighting and dimension fixtures in a disposable TASK-03 world copy."""
import argparse
import importlib.util
import json
from math import floor
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
scenes = harness.scenes
mc = scenes.mc
WORLD = harness.SOURCE_WORLD.with_name('TASK-22 Lighting Scenes')
scenes.WORLD = WORLD
EXTRA = json.loads((HERE / 'presets.json').read_text())
ALL_PRESETS = scenes.SPEC | EXTRA
PRESETS = {name: ALL_PRESETS[name]
           for name in ('daylight', 'night', 'cave', 'lamps', 'unlit', 'nether', 'end')}
scenes.SPEC = PRESETS
PROFILES = ('night', 'cave')
MODES = ('lighting', 'control', 'sodium')


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-22-{mode}'


def install_functions():
    functions = WORLD / 'datapacks/task03/data/task03/function'
    for slot, (name, preset) in enumerate(PRESETS.items()):
        position = ' '.join(map(str, preset['position']))
        dimension = preset['dimension']
        overworld = dimension == 'minecraft:overworld'
        lines = [
            f'scoreboard players set @s task03 {slot}',
            'gamemode creative @s',
            'effect clear @s',
            'clear @s',
        ]
        if not overworld:
            x, y, z = map(floor, preset['position'])
            lines.append(f'execute in {dimension} run setblock {x} {y - 1} {z} minecraft:barrier')
        lines.append(f"execute in {dimension} run tp @s {position} {preset['yaw']} {preset['pitch']}")
        if overworld:
            lines += [f"time set {preset['time']}", f"weather {preset['weather']} 1000000"]
        # Refresh the command source position after teleport, including its dimension.
        lines.append(f'execute at @s if dimension {dimension} run '
                     f'tellraw @s {{"text":"TASK03_READY_{name}"}}')
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(lines) + '\n')
    (functions / 'slot7.mcfunction').write_text('scoreboard players set @s task03 7\n')
    (functions / 'slot8.mcfunction').write_text(
        'scoreboard players set @s task03 8\nfunction task03:build\n')
    shutil.copy2(HERE / 'build.mcfunction', functions / 'build.mcfunction')


def prepare(root):
    if any(path.exists() or path.is_symlink()
           for path in (root, WORLD, pack('lighting'), pack('control'))):
        raise RuntimeError('A TASK-22 artifact root, world or pack already exists')
    manifest = (ROOT / 'evidence/task-21/pack.sha256').read_text()
    subprocess.run(['sha256sum', '--quiet', '-c', '-'],
                   input=manifest.replace('shaderpack/shaders/', 'artifacts/task-21/shaders/'),
                   cwd=ROOT, text=True, check=True)
    harness.prepare(root)
    shutil.copytree(ROOT / 'artifacts/task-21/shaders', root / 'control-shaders')
    shutil.copytree(root / 'control-shaders', pack('control') / 'shaders')
    install_functions()
    (root / 'presets.json').write_text(json.dumps(PRESETS, indent=2) + '\n')


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if action == 'prepare':
        prepare(root)
    elif action == 'restore':
        archive = root / 'world'
        if WORLD.exists() and archive.exists():
            raise RuntimeError('World archive already exists')
        harness.configure_mode('restore', root)
        if WORLD.is_dir():
            shutil.move(WORLD, archive)
        if pack('control').is_dir():
            shutil.rmtree(pack('control'))
    else:
        if action == 'control':
            harness.PACK = pack('control')
        harness.configure_mode('sodium' if action == 'sodium' else 'prototype', root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'capture', 'profile'))
    parser.add_argument('path', type=Path)
    parser.add_argument('scenes', nargs='*', metavar='SCENE')
    args = parser.parse_args()
    harness.PACK = pack('lighting')
    if args.action in ('capture', 'profile'):
        profile = args.action == 'profile'
        names = args.scenes or (PROFILES if profile else tuple(PRESETS))
        for name in names:
            if name not in (*PRESETS, 'build') or (profile and name == 'build'):
                parser.error(f'Unknown scene for {args.action}: {name}')
            scenes.replay(name, args.path / name, resume=False, profile=profile)
    elif args.scenes:
        parser.error('Scene arguments require capture or profile')
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
