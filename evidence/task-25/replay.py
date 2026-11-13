#!/usr/bin/env python3
"""Capture TASK-25 comparison views in a disposable copy of the fog fixture."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
scenes = harness.scenes
mc = scenes.mc
harness.SOURCE_WORLD = ROOT / 'artifacts/task-15/world'
harness.PACK = mc.GAME / 'shaderpacks/TASK-25-comparison'
scenes.WORLD = mc.GAME / 'saves/TASK-25 Visual Comparison'
PRESETS = {
    name: dict(preset, dimension='minecraft:overworld', warmup_seconds=20)
    for name, preset in json.loads((HERE / 'presets.json').read_text()).items()
}
# Slot 8 is the reset key used by scenes.replay. The last view uses slot 9.
scenes.SPEC = {name: preset for name, preset in PRESETS.items() if name != 'cave'}
scenes.SPEC.update(reset=None, cave=PRESETS['cave'])


def world_manifest(path):
    rows = []
    for file in sorted(path.rglob('*')):
        if file.is_file():
            with file.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            rows.append(f'{digest}  {file.relative_to(path)}\n')
    return ''.join(rows)


def prepare(root):
    if any(path.exists() or path.is_symlink() for path in (root, scenes.WORLD, harness.PACK)):
        raise RuntimeError('A TASK-25 artifact root, world or pack already exists')
    if not (harness.SOURCE_WORLD / 'level.dat').is_file():
        raise RuntimeError('Retain the TASK-15 fog fixture at artifacts/task-15/world')
    shaders = ROOT / 'artifacts/task-22/shaders'
    manifest = (ROOT / 'evidence/task-22/pack.sha256').read_text()
    subprocess.run(['sha256sum', '--quiet', '-c', '-'], cwd=shaders, check=True,
                   input=manifest.replace('  shaderpack/shaders/', '  '), text=True)
    if len(manifest.splitlines()) != sum(path.is_file() for path in shaders.rglob('*')):
        raise RuntimeError('The retained TASK-22 shader tree has unexpected files')
    source_manifest = world_manifest(harness.SOURCE_WORLD)
    harness.prepare(root, shaders)
    (root / 'source-world.sha256').write_text(source_manifest)
    (root / 'presets.json').write_text(json.dumps(PRESETS, indent=2) + '\n')
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    for slot, (name, preset) in enumerate(scenes.SPEC.items()):
        lines = [f'scoreboard players set @s task03 {slot}']
        if preset is not None:
            position = ' '.join(map(str, preset['position']))
            lines += [
                'gamemode creative @s',
                'clear @s',
                f"execute in minecraft:overworld run tp @s {position} {preset['yaw']} {preset['pitch']}",
                f"time set {preset['time']}",
                f"weather {preset['weather']} 1000000",
            ]
            if name == 'shallows':
                lines.append('execute unless block 1037 175 1037 minecraft:sea_lantern run function task03:task25-load-water')
            if name == 'night':
                lines += [
                    'setblock 993 183 1021 minecraft:lantern',
                    'setblock 1004 183 1016 minecraft:lantern',
                    'setblock 1010 183 1007 minecraft:lantern',
                ]
            lines.append(f'tellraw @s {{"text":"TASK03_READY_{name}"}}')
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(lines) + '\n')
    (functions / 'task25-load-water.mcfunction').write_text(
        'forceload add 1007 1028 1047 1046\n'
        'schedule function task03:task25-water-build 4s replace\n'
    )
    (functions / 'task25-water-build.mcfunction').write_text(
        'execute as @a at @s run function task03:task25-water-fixture\n'
        'forceload remove 1007 1028 1047 1046\n'
    )
    shutil.copy2(ROOT / 'evidence/task-19/fixture.mcfunction',
                 functions / 'task25-water-fixture.mcfunction')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'pack', 'sodium', 'capture', 'restore'))
    parser.add_argument('path', type=Path)
    parser.add_argument('scene', nargs='*', choices=tuple(PRESETS))
    args = parser.parse_args()
    root = args.path
    if args.action == 'capture':
        for name in args.scene or PRESETS:
            scenes.replay(name, root / name, resume=False)
        return
    if args.scene:
        parser.error('Scene arguments require capture')
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if args.action == 'prepare':
        prepare(root)
    elif args.action == 'restore':
        archive = root / 'world'
        if scenes.WORLD.exists() and archive.exists():
            raise RuntimeError('World archive already exists')
        harness.configure_mode('restore', root)
        if scenes.WORLD.is_dir():
            shutil.move(scenes.WORLD, archive)
        if world_manifest(harness.SOURCE_WORLD) != (root / 'source-world.sha256').read_text():
            raise RuntimeError('TASK-15 source world differs from the preflight manifest')
        print('Archived the comparison world and verified the unchanged TASK-15 source')
    else:
        harness.configure_mode('prototype' if args.action == 'pack' else 'sodium', root)


if __name__ == '__main__':
    main()
