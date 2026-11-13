#!/usr/bin/env python3
"""Stage TASK-16 controls and replay the scoped shadow fixture."""
import argparse
import gzip
import hashlib
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
scenes.WORLD = SOURCE_WORLD.with_name('TASK-16 Shadow Scenes')
MODES = ('sodium', 'fog', 'shadows')
BATCHES = ('sodium-01', 'fog-01', 'shadows-01', 'shadows-02', 'fog-02', 'sodium-02')
PROFILE_SCENES = ('forest', 'sunset')
CAPTURE_SCENES = ('contact', 'forest', 'sunset', 'range', 'open-water', 'cave', 'night')
FIXTURE_CHUNKS = '1008 1027 1096 1049'

# Preserve the hotbar positions used by scripts/scenes.py.
CAMERAS = {
    'daylight': ('contact', [1009.5, 184, 1033.5], -90, 18, 4900),
    'sunset': ('sunset', [1026.5, 184, 1033.5], 90, 17, 10900),
    'rain': ('range', [1031.5, 184, 1041.5], -90, 4, 4900),
}
original_spec = scenes.SPEC
scenes.SPEC = {}
for old, preset in original_spec.items():
    if old in CAMERAS:
        name, position, yaw, pitch, tick = CAMERAS[old]
        preset = dict(preset, position=position, yaw=yaw, pitch=pitch, time=tick, weather='clear')
    else:
        name = old
    scenes.SPEC[name] = preset


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-16-{mode}'


def install_fixture_functions():
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    # The original reset teleports to the daylight preset. Keep the player
    # in place when resetting the hotbar trigger along the contact camera lane.
    (functions / 'slot7.mcfunction').write_text(
        'scoreboard players set @s task03 7\n'
        'execute unless entity @s[x=1009.5,y=183,z=1033.5,distance=..1] run function task03:idle\n')
    (functions / 'slot8.mcfunction').write_text(
        'scoreboard players set @s task03 8\n'
        'execute if block 1017 183 1029 minecraft:chest run function task03:shadow-step\n'
        'execute unless block 1017 183 1029 minecraft:chest run function task03:shadow-fixture-start\n')
    (functions / 'shadow-step.mcfunction').write_text(
        'tp @s ~ ~ ~0.0625 -90 18\n'
        'execute if entity @s[y_rotation=-90,x_rotation=18] run tellraw @s {"text":"TASK16_CAMERA_STEP"}\n')
    (functions / 'shadow-fixture-start.mcfunction').write_text(
        f'forceload add {FIXTURE_CHUNKS}\n'
        'schedule function task03:shadow-fixture-wait 5s replace\n')
    (functions / 'shadow-fixture-wait.mcfunction').write_text(
        'execute as @a at @s run function task03:shadow-fixture\n'
        f'forceload remove {FIXTURE_CHUNKS}\n')
    shutil.copy2(HERE / 'fixture.mcfunction', functions / 'shadow-fixture.mcfunction')


def prepare(root):
    paths = (scenes.WORLD, pack('fog'), pack('shadows'))
    if any(path.exists() or path.is_symlink() for path in paths):
        raise RuntimeError('TASK-16 instance path already exists')
    control = root / 'variants/fog/shaders'
    if not (control / 'final.fsh').is_file():
        raise RuntimeError('Missing TASK-15 snapshot')
    before = root / 'before'
    before.mkdir()
    for rel in baseline.FILES:
        shutil.copy2(mc.GAME / rel, before / Path(rel).name)
    shutil.copytree(control, pack('fog') / 'shaders')
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

    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    for old, (name, position, yaw, pitch, tick) in CAMERAS.items():
        source = functions / f'{old}.mcfunction'
        lines = source.read_text().splitlines()
        coords = ' '.join(map(str, position))
        for index, line in enumerate(lines):
            if line.startswith('execute in minecraft:overworld run tp '):
                lines[index] = f'execute in minecraft:overworld run tp @s {coords} {yaw} {pitch}'
            elif line.startswith('time set '):
                lines[index] = f'time set {tick}'
            elif line.startswith('weather '):
                lines[index] = 'weather clear 1000000'
            elif line.startswith('tellraw '):
                lines[index] = line.replace(f'TASK03_READY_{old}', f'TASK03_READY_{name}')
        source.write_text('\n'.join(lines) + '\n')
    install_fixture_functions()
    (root / 'presets.json').write_text(json.dumps(scenes.SPEC, indent=2) + '\n')
    print(f'Prepared {scenes.WORLD}')


def build():
    scenes.require_scene_world()
    mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8', '1'])
    time.sleep(5)
    mc.press(['9'])
    for _ in range(25):
        if 'TASK16_READY_FIXTURE' in log.read_bytes()[offset:].decode(errors='replace'):
            print('Confirmed chest, leaf, glass and far-lane fixture blocks')
            return
        time.sleep(1)
    raise RuntimeError('Fixture block checks failed')


def motion(output):
    scenes.require_scene_world()
    output.mkdir()
    wid = mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8', '1'])
    time.sleep(3)
    if 'TASK03_READY_contact' not in log.read_bytes()[offset:].decode(errors='replace'):
        raise RuntimeError('Motion camera acknowledgment absent')
    mc.press(['F1'])
    frames = set()
    try:
        for index in range(11):
            image = output / f'{index:02d}.png'
            mc.run('maim', '-i', wid, str(image))
            frames.add(hashlib.sha256(image.read_bytes()).digest())
            if index < 10:
                offset = log.stat().st_size
                mc.press(['8', '9'])
                if 'TASK16_CAMERA_STEP' not in log.read_bytes()[offset:].decode(errors='replace'):
                    raise RuntimeError('Camera step acknowledgment absent')
            if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
                raise RuntimeError('Focus lost during motion capture')
    finally:
        mc.press(['F1'])
    if len(frames) != 11:
        raise RuntimeError(f'Only {len(frames)} distinct motion frames')


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing files')
    if action == 'prepare':
        prepare(root)
        return
    if action == 'stage':
        shutil.copytree(root / 'variants/shadows/shaders', pack('shadows') / 'shaders')
        return
    if action == 'refresh-fixture-functions':
        install_fixture_functions()
        return
    baseline.PACK = pack('fog' if action in ('sodium', 'restore') else action)
    baseline_action = {'sodium': 'sodium', 'restore': 'restore'}.get(action, 'neutral')
    archive = root / 'world'
    if action == 'restore' and scenes.WORLD.exists() and archive.exists():
        raise RuntimeError('Copied world archive already exists')
    sys.argv = [sys.argv[0], '--artifacts-dir', str(root), baseline_action]
    baseline.main()
    if action == 'restore':
        if pack('shadows').is_dir():
            shutil.rmtree(pack('shadows'))
        if scenes.WORLD.is_dir():
            shutil.move(scenes.WORLD, archive)
        print('Archived the copied world and removed both temporary packs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'stage', 'restore',
                                           'refresh-fixture-functions', 'build',
                                           'capture', 'profile', 'motion'))
    parser.add_argument('path', type=Path)
    parser.add_argument('presets', nargs='*', choices=CAPTURE_SCENES)
    args = parser.parse_args()
    if args.action == 'build':
        build()
    elif args.action == 'motion':
        motion(args.path)
    elif args.action in ('capture', 'profile'):
        profile = args.action == 'profile'
        presets = PROFILE_SCENES if profile else CAPTURE_SCENES
        for name in args.presets or presets:
            scenes.replay(name, args.path / name, resume=False, profile=profile)
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
