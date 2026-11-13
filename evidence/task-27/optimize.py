#!/usr/bin/env python3
"""Stage and replay the TASK-27 shadow-map and distance-fog trials."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'task-26'))

import replay
from variants import MANIFEST, SHADERS, tree_manifest

harness, scenes, mc = replay.harness, replay.scenes, replay.mc
harness.SOURCE_WORLD = ROOT / 'artifacts/task-25-fog-tuning/world'
PROFILES = ('valley', 'grove', 'rain')
MODES = ('sodium', 'full', 'shadow', 'fog')
VISUALS = {
    'full': ('contact', 'sunset', 'range', 'dusk', 'ridges'),
    'shadow': ('contact', 'sunset', 'range'),
    'fog': ('dusk', 'ridges'),
}
presets = {name: replay.comparison.PRESETS[name]
           for name in (*PROFILES, 'dusk', 'ridges')}
shadow_presets = json.loads((ROOT / 'artifacts/task-16/presets.json').read_text())
presets.update({name: shadow_presets[name] for name in ('contact', 'sunset', 'range')})
# Hotbar 8 resets the trigger in the shared scene harness.
scenes.SPEC = {name: presets[name] for name in (*PROFILES, 'contact', 'sunset', 'range', 'dusk')}
scenes.SPEC.update(reset=None, ridges=presets['ridges'])


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-27-{mode}'


replay.pack = pack
replay.MODES = MODES


def prepare(root):
    expected = MANIFEST.read_text().replace('  shaderpack/shaders/', '  ')
    if tree_manifest(SHADERS) != expected:
        raise RuntimeError('The retained shader tree differs from the TASK-25 manifest')
    if any(path.exists() or path.is_symlink()
           for path in (root, scenes.WORLD, *(pack(mode) for mode in MODES[1:]))):
        raise RuntimeError('A TASK-27 output, world or temporary pack already exists')
    for mode in MODES[1:]:
        variant = root / 'variants' / mode
        shaders = variant / 'shaders'
        shutil.copytree(SHADERS, shaders)
        if mode != 'full':
            subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i',
                            str(HERE / f'{mode}-trial.patch')], cwd=shaders, check=True)
        (variant / 'pack.sha256').write_text(tree_manifest(shaders))
        with (variant / 'static-link.txt').open('w') as output:
            subprocess.run([sys.executable, str(ROOT / 'evidence/task-22/link_shaders.py'),
                            str(shaders.resolve())], stdout=output, stderr=subprocess.STDOUT, check=True)
        if (variant / 'static-link.txt').read_text().count('PASS ') != 13:
            raise RuntimeError(f'{variant}: expected 13 shader pairs')
    (root / 'source-world.sha256').write_text(tree_manifest(harness.SOURCE_WORLD))
    harness.PACK = pack('full')
    stage = root / 'instance-setup'
    harness.prepare(stage, root / 'variants/full/shaders')
    shutil.move(stage / 'before', root / 'before')
    shutil.rmtree(stage)
    for mode in MODES[2:]:
        shutil.copytree(root / 'variants' / mode / 'shaders', pack(mode) / 'shaders')
    shutil.copy2(ROOT / 'artifacts/task-26/world-list-reference.png',
                 root / 'world-list-reference.png')
    (root / 'presets.json').write_text(json.dumps(presets, indent=2) + '\n')
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
            if name == 'contact':
                lines.append('execute unless block 1017 183 1029 minecraft:chest run function task03:task27-load')
            lines.append(f'tellraw @s {{"text":"TASK03_READY_{name}"}}')
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(lines) + '\n')
    # Rebuild the TASK-16 fixtures once, after the copied regions are loaded.
    (functions / 'task27-load.mcfunction').write_text(
        'forceload add 1008 1027 1096 1049\n'
        'schedule function task03:task27-build 4s replace\n'
    )
    (functions / 'task27-build.mcfunction').write_text(
        'execute as @a at @s run function task03:task27-fixture\n'
        'forceload remove 1008 1027 1096 1049\n'
    )
    shutil.copy2(HERE.parent / 'task-16/fixture.mcfunction',
                 functions / 'task27-fixture.mcfunction')


def profile(root, batch):
    mode, round_id = batch.rsplit('-', 1)
    for name in PROFILES:
        scenes.replay(name, root / batch / 'runs' / name, resume=False, profile=True)
    if round_id == '01':
        for name in VISUALS.get(mode, ()):
            scenes.replay(name, root / batch / 'views' / name, resume=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'configure', 'switch', 'profile', 'restore'))
    parser.add_argument('root', type=Path)
    parser.add_argument('batch', nargs='?')
    args = parser.parse_args()
    batches = tuple(f'{mode}-{round_id}' for mode in MODES for round_id in ('01', '02'))
    if args.action in ('configure', 'switch', 'profile'):
        if args.batch not in batches:
            parser.error(f'{args.action} requires a valid batch name')
    elif args.batch is not None:
        parser.error(f'{args.action} takes only the artifact root')
    if args.action in ('prepare', 'configure', 'restore') and mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if args.action == 'prepare':
        prepare(args.root)
    elif args.action == 'restore':
        replay.restore(args.root)
    elif args.action == 'profile':
        profile(args.root, args.batch)
    elif args.action == 'switch':
        replay.switch(args.root, args.batch.rsplit('-', 1)[0])
    else:
        replay.configure(args.root, args.batch.rsplit('-', 1)[0])


if __name__ == '__main__':
    main()
