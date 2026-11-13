#!/usr/bin/env python3
"""Stage TASK-14 controls and capture the fixed and running sky series."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'evidence/task-12'))
import replay as sunlight

baseline = sunlight.baseline
mc = sunlight.mc
scenes = sunlight.scenes
MODES = ('ambient', 'sky')
TIMES = (12000, 12400, 12785, 13100, 13600, 15000, 18000, 21900, 22500,
         23000, 23215, 23600, 23999, 0, 400, 1000, 1800, 6000, 10000, 11300)
# Use the unused forest and open-water bindings. Keep the cave preset on slot 6.
TRANSITIONS = {'dusk': (4, 12300, 78, 90), 'dawn': (5, 22530, 84, -90)}
CAPTURE_FPS = 3
FUNCTIONS = Path('data/task03/function')
LOG = mc.GAME / 'logs/latest.log'


def triggers():
    score = '#task14_time task03'
    query_time = f'execute store result score {score} run time query daytime'
    selector = '{"score":{"name":"#task14_time","objective":"task03"}}'
    freeze = ['scoreboard players set @s task03 3', 'gamerule doDaylightCycle false',
              query_time, 'tellraw @s [{"text":"TASK14_FROZEN_"},' + selector + ']',
              f'scoreboard players reset {score}']
    sweep = ['scoreboard players set @s task03 8', query_time]
    for start, end in zip(TIMES, TIMES[1:]):
        condition = f'execute if score {score} matches {start} run '
        sweep.extend((condition + f'time set {end}',
                      condition + f'tellraw @s {{"text":"TASK14_TIME_{end}"}}'))
    sweep.append(f'scoreboard players reset {score}')
    files = {'slot3.mcfunction': freeze, 'slot8.mcfunction': sweep}
    for name, (slot, tick, _, yaw) in TRANSITIONS.items():
        files[f'slot{slot}.mcfunction'] = [
            f'scoreboard players set @s task03 {slot}',
            f'tp @s 1000.5 184 1000.5 {yaw} 2',
            f'time set {tick}', 'gamerule doDaylightCycle true',
            f'tellraw @s {{"text":"TASK14_RUNNING_{name}_{tick}"}}',
        ]
    return {name: ('\n'.join(commands) + '\n').encode() for name, commands in files.items()}


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing files')
    packs = {mode: mc.GAME / f'shaderpacks/TASK-14-{mode}' for mode in MODES}
    sources = {mode: root / 'variants' / mode / 'shaders' for mode in MODES}
    source = ROOT / 'scripts/scenes' / FUNCTIONS
    installed = scenes.WORLD / 'datapacks/task03' / FUNCTIONS
    changes = triggers()
    if action == 'prepare':
        for mode in MODES:
            if packs[mode].exists() or packs[mode].is_symlink():
                raise RuntimeError(f'Temporary pack path exists: {packs[mode]}')
            if not (sources[mode] / 'final.fsh').is_file():
                raise RuntimeError(f'Missing staged {mode} source')
        for name in changes:
            if (installed / name).read_bytes() != (source / name).read_bytes():
                raise RuntimeError(f'Installed scene trigger differs: {name}')
    elif action == 'restore':
        for name, content in changes.items():
            if (installed / name).read_bytes() not in (content, (source / name).read_bytes()):
                raise RuntimeError(f'Unexpected edits to scene trigger: {name}')

    variant = 'sky' if action == 'sky-video' else action
    baseline.PACK = packs.get(variant, packs['ambient'])
    baseline_action = 'neutral' if variant in MODES else action
    sys.argv = [sys.argv[0], '--artifacts-dir', str(root), '--shaders-dir',
                str(sources['ambient']), baseline_action]
    baseline.main()
    if action == 'sky-video':
        options = mc.GAME / 'options.txt'
        options.write_text(baseline.settings(options.read_text(),
                                             {'enableVsync': 'true', 'maxFps': '60'}, ':'))
    if action == 'prepare':
        shutil.copytree(sources['sky'], packs['sky'] / 'shaders')
        snapshot = root / 'triggers'
        snapshot.mkdir()
        for name, content in changes.items():
            (snapshot / name).write_bytes(content)
            (installed / name).write_bytes(content)
    elif action == 'restore':
        if packs['sky'].is_dir():
            shutil.rmtree(packs['sky'])
        for name in changes:
            shutil.copy2(source / name, installed / name)
            if (installed / name).read_bytes() != (source / name).read_bytes():
                raise RuntimeError(f'Failed to restore scene trigger: {name}')
        print('Restored original scene triggers and removed TASK-14 packs')


def sweep(output):
    output.mkdir(parents=True, exist_ok=False)
    scenes.replay('sunset', output / 'preset', resume=False)
    wid = mc.focus()
    mc.press(['F1'])
    try:
        for index, tick in enumerate(TIMES[1:], start=1):
            offset = LOG.stat().st_size
            mc.press(['4', '9'])
            # Let the integrated server's clock sync reach the rendering client.
            time.sleep(2)
            sunlight.require_acknowledgment(LOG, offset, f'TASK14_TIME_{tick}')
            sunlight.capture_native(output / f'{index:02d}-{tick:05d}.png', wid)
    finally:
        mc.press(['F1', '2'])


def record_transition(output, name):
    slot, tick, duration, _ = TRANSITIONS[name]
    output.mkdir(parents=True, exist_ok=False)
    scenes.replay('sunset', output / 'preset', resume=False)
    wid = mc.focus()
    offset = LOG.stat().st_size
    screenshots = mc.GAME / 'screenshots'
    before = set(screenshots.glob('*.png'))
    mc.press(['F1', str(slot + 1)])
    try:
        time.sleep(1.5)
        sunlight.require_acknowledgment(LOG, offset, f'TASK14_RUNNING_{name}_{tick}')
        start = time.monotonic()
        with (output / 'capture-times.csv').open('w') as timing:
            timing.write('frame,seconds\n')
            for index in range(duration * CAPTURE_FPS):
                deadline = start + index / CAPTURE_FPS
                time.sleep(max(0.0, deadline - time.monotonic()))
                if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
                    raise RuntimeError('Focus lost during native recording')
                elapsed = time.monotonic() - start
                if elapsed > index / CAPTURE_FPS + 0.25:
                    raise RuntimeError('Missed native screenshot deadline')
                mc.press(['F2'])
                timing.write(f'{index},{elapsed:.6f}\n')
        mc.press(['4'])
        time.sleep(2)
        entries = LOG.read_bytes()[offset:].decode(errors='replace')
        frozen, = re.findall(r'TASK14_FROZEN_(\d+)\n', entries)
        advanced = (int(frozen) - tick) % 24000
        if abs(advanced - duration * 20) > 100:
            raise RuntimeError(f'Unexpected day-clock advance during {name}: {advanced}')
        print(f'{name}: {tick} to {frozen} ({advanced} ticks)', flush=True)
    finally:
        # The stock sunset preset freezes the world clock before the game is closed.
        mc.press(['F1', '2'])

    frames = sorted(set(screenshots.glob('*.png')) - before)
    if len(frames) != duration * CAPTURE_FPS:
        raise RuntimeError(f'Expected {duration * CAPTURE_FPS} native frames, found {len(frames)}')
    native = output / 'native'
    native.mkdir()
    for index, frame in enumerate(frames):
        shutil.move(frame, native / f'{index:04d}.png')
    with (output / 'ffmpeg.log').open('w') as log:
        subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-n',
                        '-framerate', str(CAPTURE_FPS), '-i', str(native / '%04d.png'),
                        '-vf', 'scale=1280:720', '-c:v', 'libx264', '-preset', 'veryfast',
                        '-crf', '16', '-pix_fmt', 'yuv420p', '-threads', '3',
                        str(output / 'transition.mp4')], stdout=log, stderr=log, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'sky-video', 'restore',
                                           'sweep', *TRANSITIONS))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.action == 'sweep':
        sweep(args.path)
    elif args.action in TRANSITIONS:
        record_transition(args.path, args.action)
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
