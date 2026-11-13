#!/usr/bin/env python3
"""Validate saved capture coverage, decoded motion and the runtime log."""
import argparse
import csv
import json
from math import dist
from pathlib import Path
import re
import struct
import subprocess

from replay import GROUPS, PRESETS

SIZE = (2560, 1440)
STILLS = (*GROUPS[0], *GROUPS[1][:5], 'underwater', 'underside')
MOTION = {
    'stone-strafe': 'daylight',
    'forest-walk': 'forest',
    'forest-turn': 'forest',
    'shore-strafe': 'shore-motion',
    'waterline': 'waterline',
    'cave-entry': 'cave-entry',
}
MARKERS = (
    *GROUPS[0], 'daylight', 'forest', 'forest', 'lamps', 'unlit', 'nether', 'end', 'return',
    'shore-motion', 'valley', 'rain-on_6000', 'rain-off_6000',
    'underwater', 'underside', 'waterline', 'cave-entry',
)
TRANSITIONS = (
    'minecraft:overworld => minecraft:the_nether',
    'minecraft:the_nether => minecraft:the_end',
    'minecraft:the_end => minecraft:overworld',
)
SHADER_ERRORS = re.compile(
    r'/(?:ERROR|FATAL)\].*(?:iris|shader|pipeline|framebuffer|glsl)'
    r'|failed to (?:compile|link).*shader|ShaderCompileException|OpenGL error|falling back to vanilla',
    re.IGNORECASE,
)


def png(path):
    with path.open('rb') as source:
        header = source.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', header[16:24]) == SIZE, path


def movement(path):
    result = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,codec_name,nb_read_frames:format=duration',
        '-of', 'json', path,
    ]))
    stream, = result['streams']
    frames = int(stream['nb_read_frames'])
    duration = float(result['format']['duration'])
    assert (stream['width'], stream['height']) == SIZE and frames / duration >= 25, path
    # Decode all frames. Inspect downscaled luma for blank frames and, in
    # outdoor paths, the black bands seen in the TASK-23 X11 capture trial.
    proxy = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', path, '-vf', 'scale=80:45:flags=area',
        '-pix_fmt', 'gray', '-fps_mode', 'passthrough', '-f', 'rawvideo', '-',
    ])
    area = 80 * 45
    assert len(proxy) == area * frames, path
    assert all(max(proxy[i:i + area]) > 8 for i in range(0, len(proxy), area)), path
    if path.stem not in ('cave-entry', 'waterline'):
        assert all(max(proxy[i:i + 80]) > 8 for i in range(0, len(proxy), 80)), path
    return frames, duration


def position_after(log, preset, previous):
    start = log.index(f'[CHAT] TASK28_READY_{preset}\n', previous)
    match = re.search(r'\[CHAT\] TASK28_POSITION \[([^]]+)\] ROTATION \[([^]]+)\]', log[start:])
    assert match, preset
    position, rotation = ([float(value[:-1]) for value in group.split(',')] for group in match.groups())
    return position, rotation, start


def review(root):
    logs, = root.glob('logs-*')
    log = (logs / 'latest.log').read_text()
    debug = (logs / 'debug.log').read_text()
    assert 'Using shaderpack: TASK-28-regression' in log
    assert 'All dimensions are saved' in log and 'Finished saving "TASK-28 Runtime Regression"' in log
    assert not SHADER_ERRORS.search(log) and not SHADER_ERRORS.search(debug)
    assert not re.search(r'/(?:FATAL)\]|---- Minecraft Crash Report ----', log)
    assert (root / 'crashes-before.txt').read_bytes() == (root / 'crashes-after.txt').read_bytes()
    ready = re.findall(r'\[CHAT\] TASK28_READY_([\w-]+)', log)
    assert ready == list(MARKERS), ready
    dimensions = re.findall(r'Reloading pipeline on dimension change: (.+)', log)
    assert [line for line in dimensions if line != 'minecraft:overworld => minecraft:overworld'] == list(TRANSITIONS)
    assert 'Render target settings for colortex0:' in debug and 'requestedFormat=RGBA16F' in debug
    assert '[CHAT] TASK03_READY_build' in log
    assert re.findall(r'\[CHAT\] TASK28_EYES_(IN|OUT)', log) == ['IN', 'OUT', 'IN']
    assert set((root / 'stills').glob('*.png')) == {root / 'stills' / f'{name}.png' for name in STILLS}
    for name in STILLS:
        png(root / 'stills' / f'{name}.png')
    for region in ('440x144+1016+1212', '220x52+2208+512'):
        before, after = (
            subprocess.check_output(['magick', root / 'stills' / f'{name}.png',
                                     '-crop', region, '+repage', '-alpha', 'off', '-depth', '8', 'rgb:-'])
            for name in ('daylight', 'return')
        )
        assert before == after and before, region
    with (root / 'weather/timeline.csv').open(newline='') as source:
        frames = list(csv.DictReader(source))
    assert [int(row['frame']) for row in frames] == list(range(42))
    assert [row['event'] for row in frames if row['event']] == ['rain-on', 'rain-off']
    seconds = [float(row['seconds']) for row in frames]
    assert all(0.05 < after - before < 1.5 for before, after in zip(seconds, seconds[1:]))
    for frame in range(42):
        png(root / 'weather' / f'{frame:03}.png')
    print(f'PASS {len(STILLS)} native stills, 42 timed weather frames and three Iris dimension changes')
    print('PASS two static Overworld return patches are byte-identical')
    print('PASS waterline IN → OUT → IN, basin block checks, active pack, saved world and crash-file check')
    start = log.index('[CHAT] TASK28_READY_cave\n')
    for name, preset in MOTION.items():
        position, rotation, start = position_after(log, preset, start + 1)
        if name == 'forest-turn':
            assert abs((rotation[0] - PRESETS[preset]['yaw'] + 180) % 360 - 180) >= 25, rotation
        elif name == 'cave-entry':
            assert 1025 < position[2] < 1044, position
        elif name != 'waterline':
            assert dist(position[::2], PRESETS[preset]['position'][::2]) > 3, position
        frame_count, duration = movement(root / 'clips' / f'{name}.mp4')
        print(f'PASS {name}: {frame_count} frames, {duration:.3f} s, XYZ {position}, yaw/pitch {rotation}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    review(parser.parse_args().root)
