#!/usr/bin/env python3
"""Install and replay the water fixture in the dedicated Prism instance."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

scenes = harness.scenes
mc = scenes.mc
WORLD = harness.SOURCE_WORLD.with_name('TASK-19 Water Scenes')
MODES = ('control', 'water', 'depth', 'sodium')
PROFILES = ('basin', 'basin-rain')
PRESETS = {
    'daylight': ('basin', [1006.5, 183, 1037.5], -90, 12, 6000, 'clear'),
    'sunset': ('basin-sunset', [1006.5, 183, 1037.5], -90, 12, 11600, 'clear'),
    'night': ('underwater', [1025.5, 179, 1037.5], -90, 5, 6000, 'clear'),
    'rain': ('basin-rain', [1006.5, 183, 1037.5], -90, 12, 6000, 'rain'),
    'forest': ('underside', [1025.5, 179, 1037.5], -90, -25, 6000, 'clear'),
    'cave': ('shore', [1008.5, 183, 1037.5], -90, 45, 6000, 'clear'),
}


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-19-{mode}'


def preset_specs():
    for old, spec in scenes.SPEC.items():
        if old in PRESETS:
            name, pos, yaw, pitch, tick, weather = PRESETS[old]
            yield name, dict(spec, position=pos, yaw=yaw, pitch=pitch, time=tick, weather=weather)
        else:
            yield old, spec


def install_functions(specs):
    functions = WORLD / 'datapacks/task03/data/task03/function'
    for old, (name, *_) in PRESETS.items():
        spec = specs[name]
        pos = ' '.join(map(str, spec['position']))
        lines = [
            'clear @s',
            'gamemode creative @s',
            f"tp @s {pos} {spec['yaw']} {spec['pitch']}",
            f"time set {spec['time']}",
            f"weather {spec['weather']} 1000000",
        ]
        if name == 'basin':
            lines += [
                'item replace entity @s hotbar.0 with minecraft:stone',
                'item replace entity @s weapon.offhand with minecraft:light_blue_stained_glass',
            ]
        lines.append(f'tellraw @s {{"text":"TASK03_READY_{name}"}}')
        (functions / f'{old}.mcfunction').write_text('\n'.join(lines) + '\n')
    (functions / 'build.mcfunction').write_text(
        'forceload add 1007 1028 1047 1046\n'
        'schedule function task03:water-build 3s replace\n'
    )
    (functions / 'water-build.mcfunction').write_text(
        'execute as @a at @s run function task03:water-fixture\n'
        'forceload remove 1007 1028 1047 1046\n'
    )
    shutil.copy2(HERE / 'fixture.mcfunction', functions / 'water-fixture.mcfunction')


def build_fixture():
    scenes.require_scene_world()
    mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8'])
    mc.press(['9'])
    for _ in range(15):
        if 'TASK03_READY_build' in log.read_bytes()[offset:].decode(errors='replace'):
            return
        time.sleep(1)
    raise RuntimeError('Water fixture block checks failed')


def capture_motion(dest):
    wid = mc.focus()
    mc.press(['F1'])
    try:
        for frame in ('wave-a.png', 'wave-b.png'):
            time.sleep(0.7)
            if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
                raise RuntimeError('Focus lost during wave capture')
            mc.run('maim', '-i', wid, str(dest / frame))
    finally:
        mc.press(['F1'])


def prepare(root, specs):
    paths = (WORLD, pack('water'), pack('control'), pack('depth'))
    if any(path.exists() or path.is_symlink() for path in paths):
        raise RuntimeError('A TASK-19 world or pack already exists')
    control = ROOT / 'artifacts/task-18/shaders'
    if not (control / 'lib/clouds.glsl').is_file():
        raise RuntimeError('Missing the verified TASK-18 control')
    harness.prepare(root)
    shutil.copytree(control, root / 'control-shaders')
    shutil.copytree(control, pack('control') / 'shaders')
    shutil.copytree(root / 'shaders', root / 'depth-shaders')
    fragment = root / 'depth-shaders/gbuffers_water.fsh'
    fragment.write_text(fragment.read_text().replace('#define STYLIZED_WATER',
                                                       '#define STYLIZED_WATER\n#define WATER_DEPTH_DEBUG'))
    shutil.copytree(root / 'depth-shaders', pack('depth') / 'shaders')
    install_functions(specs)
    (root / 'presets.json').write_text(json.dumps(specs, indent=2) + '\n')


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
        for mode in ('control', 'depth'):
            if pack(mode).is_dir():
                shutil.rmtree(pack(mode))
    else:
        if action != 'sodium':
            harness.PACK = pack(action)
        harness.configure_mode('sodium' if action == 'sodium' else 'prototype', root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'build', 'capture',
                                           'profile', 'refresh-functions'))
    parser.add_argument('path', type=Path)
    parser.add_argument('presets', nargs='*')
    args = parser.parse_args()
    specs = dict(preset_specs())
    scenes.SPEC = specs
    scenes.WORLD = WORLD
    harness.PACK = pack('water')
    if args.action == 'build':
        build_fixture()
    elif args.action == 'refresh-functions':
        if mc.game_pids():
            raise RuntimeError('Stop GenshinShaderDev before changing the fixture')
        install_functions(specs)
        (args.path / 'presets.json').write_text(json.dumps(specs, indent=2) + '\n')
    elif args.action in ('capture', 'profile'):
        profile = args.action == 'profile'
        for name in args.presets or (PROFILES if profile else specs):
            dest = args.path / name
            scenes.replay(name, dest, resume=False, profile=profile)
            if name == 'basin' and not profile:
                mc.run('maim', '-i', mc.focus(), str(dest / 'held-items.png'))
            if name == 'shore' and not profile:
                capture_motion(dest)
    else:
        configure(args.action, args.path, specs)


if __name__ == '__main__':
    main()
