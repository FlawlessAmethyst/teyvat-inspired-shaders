#!/usr/bin/env python3
"""Run TASK-21 in a disposable copy of the accepted vegetation fixture."""
import argparse
import csv
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
scenes = harness.scenes
mc = scenes.mc
WORLD = harness.SOURCE_WORLD.with_name('TASK-21 Weather Scenes')
SOURCE = ROOT / 'artifacts/task-20/world'
MODES = ('weather', 'control', 'sodium')
BATCHES = ('weather-01', 'control-01', 'sodium-01', 'sodium-02', 'control-02', 'weather-02')
PROFILES = ('daylight', 'rain')
CAPTURES = ('daylight', 'rain', 'open-water', 'water-rain', 'dense', 'dense-rain')
PRESETS = json.loads((ROOT / 'artifacts/task-20/presets.json').read_text())
PRESETS = {name: dict(PRESETS[base], weather=weather) for name, base, weather in (
    ('daylight', 'daylight', 'clear'), ('dense', 'dense', 'clear'),
    ('dense-rain', 'dense', 'rain'), ('rain', 'rain', 'rain'),
    ('water-rain', 'open-water', 'rain'), ('open-water', 'open-water', 'clear'),
)}
LOG = mc.GAME / 'logs/latest.log'
CAPTURE_FPS = 4
CAPTURE_SECONDS = 11


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-21-{mode}'


def install_functions():
    functions = WORLD / 'datapacks/task03/data/task03/function'
    for slot, (name, preset) in enumerate(PRESETS.items()):
        position = ' '.join(map(str, preset['position']))
        lines = [
            f'scoreboard players set @s task03 {slot}',
            'gamerule doDaylightCycle false',
            'gamerule doWeatherCycle false',
            'gamemode creative @s',
            'clear @s',
            f"execute in minecraft:overworld run tp @s {position} {preset['yaw']} {preset['pitch']}",
            f"time set {preset['time']}",
            f"weather {preset['weather']} 1000000",
            f'tellraw @s {{"text":"TASK03_READY_{name}"}}',
        ]
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(lines) + '\n')
    (functions / 'slot7.mcfunction').write_text('scoreboard players set @s task03 7\n')
    for slot, weather in ((6, 'rain'), (8, 'clear')):
        lines = [
            f'scoreboard players set @s task03 {slot}',
            f'weather {weather} 1000000',
            'execute store result score #task21_time task03 run time query daytime',
            f'tellraw @s [{{"text":"TASK21_{weather}_"}},'
            '{"score":{"name":"#task21_time","objective":"task03"}}]',
        ]
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(lines) + '\n')


def prepare(root):
    paths = (root, WORLD, pack('weather'), pack('control'))
    if any(path.exists() or path.is_symlink() for path in paths):
        raise RuntimeError('A TASK-21 artifact root, world or pack already exists')
    control = ROOT / 'artifacts/task-20/shaders'
    manifest = (ROOT / 'evidence/task-20/pack.sha256').read_text()
    subprocess.run(['sha256sum', '--quiet', '-c', '-'],
                   input=manifest.replace('shaderpack/shaders/', 'artifacts/task-20/shaders/'),
                   cwd=ROOT, text=True, check=True)
    root.mkdir(parents=True)
    shutil.copytree(ROOT / 'shaderpack/shaders', root / 'shaders')
    harness.configure_mode('prepare', root)
    shutil.copytree(control, root / 'control-shaders')
    shutil.copytree(control, pack('control') / 'shaders')
    shutil.copytree(SOURCE, WORLD, ignore=shutil.ignore_patterns('session.lock'))
    level = WORLD / 'level.dat'
    raw = gzip.decompress(level.read_bytes())
    fields = scenes.nbt_fields(raw)
    name = WORLD.name.encode()
    values = {'LevelName': struct.pack('>H', len(name)) + name,
              'LastPlayed': struct.pack('>q', time.time_ns() // 1_000_000)}
    edits = [(fields['Data', key][1:], value) for key, value in values.items()]
    for (start, end), value in sorted(edits, reverse=True):
        raw = raw[:start] + value + raw[end:]
    scenes.nbt_fields(raw)
    level.write_bytes(gzip.compress(raw))
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


def require_focus(wid):
    if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
        raise RuntimeError('Focus lost during transition recording')


def record_transition(output, wid, weather):
    output.mkdir(parents=True, exist_ok=False)
    offset = LOG.stat().st_size
    screenshots = mc.GAME / 'screenshots'
    before = set(screenshots.glob('*.png'))
    trigger = None
    start = time.monotonic()
    with (output / 'capture-times.csv').open('w') as timing:
        writer = csv.writer(timing)
        writer.writerow(('frame', 'seconds'))
        for index in range(CAPTURE_SECONDS * CAPTURE_FPS):
            deadline = start + index / CAPTURE_FPS
            time.sleep(max(0.0, deadline - time.monotonic()))
            require_focus(wid)
            if index == 2 * CAPTURE_FPS:
                trigger = time.monotonic() - start
                mc.press(['7' if weather == 'rain' else '9'])
            elapsed = time.monotonic() - start
            if elapsed > index / CAPTURE_FPS + 0.28:
                raise RuntimeError('Missed native screenshot deadline')
            mc.press(['F2'])
            writer.writerow((index, f'{elapsed:.6f}'))
    time.sleep(1)
    acknowledgment = f'[CHAT] TASK21_{weather}_6000'
    if acknowledgment not in LOG.read_bytes()[offset:].decode(errors='replace'):
        raise RuntimeError(f'Missing fixed-time weather acknowledgment: {acknowledgment}')
    frames = sorted(set(screenshots.glob('*.png')) - before)
    if len(frames) != CAPTURE_SECONDS * CAPTURE_FPS:
        raise RuntimeError(f'Unexpected count of native captures: {len(frames)}')
    native = output / 'native'
    native.mkdir()
    for index, frame in enumerate(frames):
        shutil.move(frame, native / f'{index:04d}.png')
    (output / 'trigger.json').write_text(json.dumps({
        'weather': weather, 'trigger_seconds_after_capture_start': trigger,
        'daytime': 6000, 'nominal_fps': CAPTURE_FPS,
    }, indent=2) + '\n')
    print(native, flush=True)


def encode_transition(output):
    with (output / 'ffmpeg.log').open('w') as log:
        subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-n',
                        '-framerate', str(CAPTURE_FPS), '-i', str(output / 'native/%04d.png'),
                        '-vf', 'scale=1280:720', '-c:v', 'libx264', '-crf', '17',
                        '-threads', '3', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        str(output / 'preview.mp4')], stdout=log, stderr=log, check=True)


def transition_series(root):
    for scene in ('daylight', 'open-water', 'dense'):
        output = root / scene
        scenes.replay(scene, output / 'preset', resume=False)
        wid = mc.focus()
        mc.press(['F1'])
        try:
            record_transition(output / 'to-rain', wid, 'rain')
            record_transition(output / 'to-clear', wid, 'clear')
        finally:
            mc.press(['F1'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'capture',
                                           'profile', 'transitions', 'encode'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    scenes.WORLD = WORLD
    scenes.SPEC = PRESETS
    harness.PACK = pack('weather')
    if args.action == 'transitions':
        transition_series(args.path)
    elif args.action == 'encode':
        for directory in sorted(args.path.glob('*/to-*')):
            encode_transition(directory)
    elif args.action in ('capture', 'profile'):
        profile = args.action == 'profile'
        for name in PROFILES if profile else CAPTURES:
            scenes.replay(name, args.path / name, resume=False, profile=profile)
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
