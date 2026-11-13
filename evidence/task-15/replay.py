#!/usr/bin/env python3
"""Stage and replay the distance-fog fixture in a copy of the TASK-03 world."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import struct
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'evidence/task-10'), str(ROOT / 'scripts')]
import configure as baseline
import scenes

mc = scenes.mc
SOURCE_WORLD = scenes.WORLD
scenes.WORLD = SOURCE_WORLD.with_name('TASK-15 Fog Scenes')
MODES = ('sodium', 'sky', 'fog')
DISTANCE_PRESETS = ('daylight', 'sunset', 'night', 'rain')
FIXTURE_CHUNKS = '831 1064 1014 1144'
for name in DISTANCE_PRESETS:
    preset = scenes.SPEC[name]
    preset.update(position=[1004.5, 184, 1100.5], yaw=90, pitch=2)
    if name == 'sunset':
        preset['time'] = 12785


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-15-{mode}'


def prepare(root):
    targets = (scenes.WORLD, pack('sky'), pack('fog'))
    if any(path.exists() or path.is_symlink() for path in targets):
        raise RuntimeError('TASK-15 instance path already exists')
    if not (root / 'variants/sky/shaders/final.fsh').is_file():
        raise RuntimeError('Missing TASK-14 snapshot')
    before = root / 'before'
    before.mkdir()
    for rel in baseline.FILES:
        shutil.copy2(mc.GAME / rel, before / Path(rel).name)
    shutil.copytree(root / 'variants/sky/shaders', pack('sky') / 'shaders')
    shutil.copytree(SOURCE_WORLD, scenes.WORLD, ignore=shutil.ignore_patterns('session.lock'))

    level = scenes.WORLD / 'level.dat'
    raw = gzip.decompress(level.read_bytes())
    fields = scenes.nbt_fields(raw)
    name = scenes.WORLD.name.encode()
    edits = [('LevelName', struct.pack('>H', len(name)) + name),
             ('LastPlayed', struct.pack('>q', time.time_ns() // 1_000_000))]
    ranges = [(fields['Data', key][1:], value) for key, value in edits]
    for (start, end), value in sorted(ranges, reverse=True):
        raw = raw[:start] + value + raw[end:]
    scenes.nbt_fields(raw)
    level.write_bytes(gzip.compress(raw))
    # Only the copied datapack is edited.
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    for name in DISTANCE_PRESETS:
        preset = scenes.SPEC[name]
        source = functions / f'{name}.mcfunction'
        lines = source.read_text().splitlines()
        position = ' '.join(str(value) for value in preset['position'])
        for index, line in enumerate(lines):
            if line.startswith('execute in minecraft:overworld run tp '):
                lines[index] = f'execute in minecraft:overworld run tp @s {position} {preset["yaw"]} {preset["pitch"]}'
            if line.startswith('time set '):
                lines[index] = f'time set {preset["time"]}'
        source.write_text('\n'.join(lines) + '\n')
    install_builder()
    (root / 'presets.json').write_text(json.dumps(scenes.SPEC, indent=2) + '\n')
    print(f'Prepared {scenes.WORLD}')


def install_builder():
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    (functions / 'slot8.mcfunction').write_text(
        'scoreboard players set @s task03 8\n'
        f'forceload add {FIXTURE_CHUNKS}\n'
        'schedule function task03:fog-fixture-wait 10s replace\n')
    (functions / 'fog-fixture-wait.mcfunction').write_text(
        'execute as @a at @s run function task03:fog-fixture\n'
        f'forceload remove {FIXTURE_CHUNKS}\n')
    shutil.copy2(HERE / 'build.mcfunction', functions / 'fog-fixture.mcfunction')


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing files')
    if action == 'prepare':
        prepare(root)
        return
    if action == 'restore':
        before = root / 'before'
        if not all((before / Path(rel).name).is_file() for rel in baseline.FILES):
            raise RuntimeError('Incomplete settings backup')
        archived_world = root / 'world'
        if scenes.WORLD.is_dir() and archived_world.exists():
            raise RuntimeError(f'Copied world archive already exists: {archived_world}')
        for rel in baseline.FILES:
            saved = before / Path(rel).name
            shutil.copy2(saved, mc.GAME / rel)
            if saved.read_bytes() != (mc.GAME / rel).read_bytes():
                raise RuntimeError(f'Restoration failed: {rel}')
        for mode in ('sky', 'fog'):
            if pack(mode).is_dir():
                shutil.rmtree(pack(mode))
        if scenes.WORLD.is_dir():
            shutil.move(scenes.WORLD, archived_world)
        print('Restored five byte-identical settings files and archived the copied world')
        return

    if action == 'stage-fog':
        shutil.copytree(root / 'variants/fog/shaders', pack('fog') / 'shaders')
        return
    if action != 'sodium' and not pack(action).is_dir():
        raise RuntimeError(f'Missing staged shaderpack: {action}')
    baseline.PACK = pack('sky' if action == 'sodium' else action)
    sys.argv = [sys.argv[0], '--artifacts-dir', str(root),
                'sodium' if action == 'sodium' else 'neutral']
    baseline.main()


def build():
    scenes.require_scene_world()
    mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8', '1'])
    time.sleep(20)
    if 'TASK03_READY_daylight' not in log.read_bytes()[offset:].decode(errors='replace'):
        raise RuntimeError('Could not reach the fixture camera')
    mc.press(['9'])
    time.sleep(13)
    if 'TASK15_READY_FIXTURE' not in log.read_bytes()[offset:].decode(errors='replace'):
        raise RuntimeError('Fixture block checks failed')
    print('Confirmed fixture near, middle and far blocks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'stage-fog', 'restore',
                                           'build', 'capture', 'profile'))
    parser.add_argument('path', type=Path)
    parser.add_argument('presets', nargs='*')
    args = parser.parse_args()
    if args.action == 'build':
        build()
    elif args.action in ('capture', 'profile'):
        for name in args.presets:
            scenes.replay(name, args.path / name, resume=False, profile=args.action == 'profile')
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
