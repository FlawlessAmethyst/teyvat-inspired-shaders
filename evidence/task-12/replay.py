#!/usr/bin/env python3
"""Stage TASK-12 test packs and capture a fixed-camera time sweep."""
import argparse
import filecmp
import shutil
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'evidence/task-10'), str(ROOT / 'scripts')]
import configure as baseline
import scenes

mc = baseline.mc
MODES = ('graded', 'sunlight')
TIMES = (12000, 12400, 12750, 13000, 13600, 18000, 22500, 23200, 23800,
         0, 800, 1800, 6000, 10000, 11300, 12000)
FUNCTIONS = Path('data/task03/function')


def packs():
    return {mode: mc.GAME / f'shaderpacks/TASK-12-{mode}' for mode in MODES}


def triggers():
    lines = [
        'scoreboard players set @s task03 8',
        'execute store result score #task12_time task03 run time query daytime',
    ]
    for start, end in zip(TIMES, TIMES[1:]):
        condition = f'execute if score #task12_time task03 matches {start} run '
        lines.append(condition + f'time set {end}')
        lines.append(condition + f'tellraw @s {{"text":"TASK12_TIME_{end}"}}')
    lines.append('scoreboard players reset #task12_time task03')
    return {'slot3.mcfunction': 'scoreboard players set @s task03 3\n',
            'slot5.mcfunction': Path(__file__).with_name('facing.mcfunction').read_text(),
            'slot8.mcfunction': '\n'.join(lines) + '\n'}


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing files')
    installs = packs()
    source = ROOT / 'scripts/scenes' / FUNCTIONS
    installed = scenes.WORLD / 'datapacks/task03' / FUNCTIONS
    changes = triggers()
    baseline.PACK = installs.get(action, installs['graded'])
    if action == 'prepare':
        for mode, path in installs.items():
            if path.exists() or path.is_symlink():
                raise RuntimeError(f'Test pack path already exists: {path}')
            if not (root / 'variants' / mode / 'shaders/final.fsh').is_file():
                raise RuntimeError(f'Missing staged {mode} source')
        for name in changes:
            if not filecmp.cmp(source / name, installed / name, shallow=False):
                raise RuntimeError(f'Installed scene differs: {name}')
    elif action == 'restore':
        for name, content in changes.items():
            live = (installed / name).read_bytes()
            if live not in (content.encode(), (source / name).read_bytes()):
                raise RuntimeError(f'Unexpected edits to scene trigger: {name}')

    baseline_action = 'neutral' if action in MODES else action
    sys.argv = [sys.argv[0], '--artifacts-dir', str(root), '--shaders-dir',
                str(root / 'variants/graded/shaders'), baseline_action]
    baseline.main()
    if action in MODES:
        print(f'Selected {baseline.PACK.name}')
    if action == 'prepare':
        shutil.copytree(root / 'variants/sunlight/shaders', installs['sunlight'] / 'shaders')
        for name, content in changes.items():
            (installed / name).write_text(content)
        (root / 'transition-functions').mkdir()
        for name, content in changes.items():
            (root / 'transition-functions' / name).write_text(content)
    elif action == 'restore':
        if installs['sunlight'].is_dir():
            shutil.rmtree(installs['sunlight'])
        for name in changes:
            shutil.copy2(source / name, installed / name)
            if not filecmp.cmp(source / name, installed / name, shallow=False):
                raise RuntimeError(f'Failed to restore scene trigger: {name}')
        print('Restored scene triggers byte-for-byte')


def require_acknowledgment(log, offset, marker):
    with log.open('rb') as file:
        file.seek(offset)
        if (marker + '\n').encode() not in file.read():
            raise RuntimeError(f'Missing scene acknowledgment: {marker}')


def capture_native(dest, wid):
    if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
        raise RuntimeError('Focus lost during native capture')
    screenshots = mc.GAME / 'screenshots'
    before = set(screenshots.glob('*.png'))
    mc.press(['F2'])
    time.sleep(1)
    fresh, = set(screenshots.glob('*.png')) - before
    shutil.copy2(fresh, dest)
    with dest.open('rb') as file:
        header = file.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (2560, 1440):
        raise RuntimeError(f'Invalid native screenshot {dest}')
    print(dest, flush=True)


def sweep(output):
    scenes.require_scene_world()
    output.mkdir(parents=True, exist_ok=False)
    scenes.replay('sunset', output / 'preset', resume=False)
    wid = mc.focus()
    log = mc.GAME / 'logs/latest.log'
    mc.press(['F1'])
    try:
        for index, tick in enumerate(TIMES[1:], start=1):
            offset = log.stat().st_size
            mc.press(['4'])
            time.sleep(0.4)
            mc.press(['9'])
            time.sleep(2)
            require_acknowledgment(log, offset, f'TASK12_TIME_{tick}')
            capture_native(output / f'{index:02d}-{tick:05d}.png', wid)
    finally:
        mc.press(['F1'])
        # Leave a regular preset selected before the original slot 9 build
        # trigger is restored.
        mc.press(['2'])


def facing(output):
    scenes.require_scene_world()
    output.mkdir(parents=True, exist_ok=False)
    wid = mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8'])
    time.sleep(3)
    mc.press(['6'])
    time.sleep(3)
    require_acknowledgment(log, offset, 'TASK12_FACING_READY')
    mc.press(['F1'])
    try:
        time.sleep(scenes.SPEC['sunset']['warmup_seconds'])
        capture_native(output / 'native.png', wid)
    finally:
        mc.press(['F1'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'sweep', 'facing'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.action == 'sweep':
        sweep(args.path)
    elif args.action == 'facing':
        facing(args.path)
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
