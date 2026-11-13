#!/usr/bin/env python3
"""Replay vegetation comparisons and profiles in a disposable TASK-03 copy."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

scenes = harness.scenes
mc = scenes.mc
WORLD = harness.SOURCE_WORLD.with_name('TASK-20 Vegetation Scenes')
MODES = ('control', 'vegetation', 'sodium')
PROFILES = ('daylight', 'dense')
CAPTURES = ('daylight', 'forest', 'dense', 'canopy-top')
BATCHES = ('vegetation-01', 'control-01', 'sodium-01', 'sodium-02', 'control-02', 'vegetation-02')
FIXTURE_PRESETS = {
    'sunset': ('dense', [1055.5, 183, 1008.5], -90, -3),
    'night': ('canopy-top', [1054.5, 192, 1008.5], -90, 16),
}


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-20-{mode}'


def install_functions(specs):
    functions = WORLD / 'datapacks/task03/data/task03/function'
    for old, (name, _, _, _) in FIXTURE_PRESETS.items():
        preset = specs[name]
        pos = ' '.join(map(str, preset['position']))
        lines = [
            'clear @s',
            'gamemode creative @s',
            f"tp @s {pos} {preset['yaw']} {preset['pitch']}",
            f"time set {preset['time']}",
            f"weather {preset['weather']} 1000000",
            f'tellraw @s {{"text":"TASK03_READY_{name}"}}',
        ]
        (functions / f'{old}.mcfunction').write_text('\n'.join(lines) + '\n')
    (functions / 'build.mcfunction').write_text(
        'forceload add 1051 990 1090 1026\n'
        'schedule function task03:vegetation-build 3s replace\n'
    )
    (functions / 'vegetation-build.mcfunction').write_text(
        'execute as @a at @s run function task03:vegetation-fixture\n'
        'forceload remove 1051 990 1090 1026\n'
    )
    shutil.copy2(HERE / 'fixture.mcfunction', functions / 'vegetation-fixture.mcfunction')


def prepare(root, specs):
    control = ROOT / 'artifacts/task-19/shaders'
    manifest = (ROOT / 'evidence/task-19/pack.sha256').read_text()
    subprocess.run(['sha256sum', '--quiet', '-c', '-'],
                   input=manifest.replace('shaderpack/shaders/', 'artifacts/task-19/shaders/'),
                   cwd=ROOT, text=True, check=True)
    paths = (WORLD, pack('vegetation'), pack('control'))
    if any(path.exists() or path.is_symlink() for path in paths):
        raise RuntimeError('A TASK-20 world or pack already exists')
    harness.prepare(root)
    shutil.copytree(control, root / 'control-shaders')
    shutil.copytree(control, pack('control') / 'shaders')
    install_functions(specs)
    (root / 'presets.json').write_text(json.dumps(specs, indent=2) + '\n')


def build_fixture():
    scenes.require_scene_world()
    mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8'])
    time.sleep(1)
    mc.press(['9'])
    for _ in range(20):
        if '[CHAT] TASK03_READY_build' in log.read_bytes()[offset:].decode(errors='replace'):
            print('Dense-canopy fixture checks passed')
            return
        time.sleep(1)
    raise RuntimeError('Dense-canopy fixture block or biome checks failed')


def configure(action, root, specs):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if action == 'prepare':
        prepare(root, specs)
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
            harness.PACK = pack(action)
        harness.configure_mode('sodium' if action == 'sodium' else 'prototype', root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'build', 'capture', 'profile'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    specs = {}
    for name, original in scenes.SPEC.items():
        if name in FIXTURE_PRESETS:
            name, pos, yaw, pitch = FIXTURE_PRESETS[name]
            specs[name] = dict(original, position=pos, yaw=yaw, pitch=pitch, time=6000, weather='clear')
        else:
            specs[name] = original
    scenes.SPEC = specs
    scenes.WORLD = WORLD
    harness.PACK = pack('vegetation')
    if args.action == 'build':
        build_fixture()
    elif args.action in ('capture', 'profile'):
        profile = args.action == 'profile'
        for name in PROFILES if profile else CAPTURES:
            scenes.replay(name, args.path / name, resume=False, profile=profile)
    else:
        configure(args.action, args.path, specs)


if __name__ == '__main__':
    main()
