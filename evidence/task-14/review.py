#!/usr/bin/env python3
"""Measure native sky colors and check the recorded dusk and dawn patches."""
import argparse
import csv
import json
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np

CAPTURE_FPS = 3
SWEEP_CROPS = {'upper sky': '96x48+1472+80', 'low sky': '96x48+1472+620'}
SCENE_CROPS = {
    'daylight': {'upper sky': SWEEP_CROPS['upper sky'], 'low sky': '96x48+450+520',
                 'grass': '400x160+1050+1060'},
    'night': {'upper sky': SWEEP_CROPS['upper sky'], 'grass': '400x160+1050+1060'},
    'cave': {'ceiling recess': '120x60+1250+360'},
}


def sample_png(image, geometry):
    raw = subprocess.check_output(['magick', str(image), '-crop', geometry, '+repage',
                                   '-alpha', 'off', '-depth', '8', 'rgb:-'])
    return np.median(np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3), axis=0)


def pixels(root):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('variant', 'scene', 'step', 'tick', 'patch', 'crop', 'r', 'g', 'b'))
    for variant in ('ambient', 'sky'):
        batch = root / f'{variant}-01'
        for scene, crops in SCENE_CROPS.items():
            tick = json.loads((batch / scene / 'preset.json').read_text())['time']
            for patch, crop in crops.items():
                rgb = sample_png(batch / scene / 'native.png', crop)
                writer.writerow((variant, scene, 0, tick, patch, crop, *rgb))

        sweep = batch / 'sweep'
        frames = [(0, 12000, sweep / 'preset/native.png')]
        for frame in sorted(sweep.glob('*.png')):
            step, tick = map(int, frame.stem.split('-'))
            frames.append((step, tick, frame))
        if [step for step, _, _ in frames] != list(range(20)):
            raise ValueError(f'Expected 20 frames in {sweep}')
        for step, tick, frame in frames:
            for patch, crop in SWEEP_CROPS.items():
                writer.writerow((variant, 'sweep', step, tick, patch, crop, *sample_png(frame, crop)))


def video(root):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('transition', 'duration_s', 'frames', 'max_sample_gap_s', 'patch', 'crop',
                     'p95_frame_step_rgb', 'max_frame_step_rgb', 'max_day_wrap_step_rgb'))
    for transition, duration in (('dusk', 78), ('dawn', 84)):
        recording = root / 'sky-video' / transition
        clip = recording / 'transition.mp4'
        streams = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', clip,
        ]))['streams']
        stream, = streams
        frames = int(stream['nb_frames'])
        if (stream['width'], stream['height'], stream['r_frame_rate']) != (1280, 720, f'{CAPTURE_FPS}/1'):
            raise ValueError(f'Unexpected clip dimensions or rate: {clip}')
        if frames != duration * CAPTURE_FPS:
            raise ValueError(f'Unexpected clip frame count: {clip}')
        with (recording / 'capture-times.csv').open() as timings:
            seconds = [float(row['seconds']) for row in csv.DictReader(timings)]
        gaps = np.diff(seconds)
        if len(seconds) != frames or gaps.min() <= 0 or gaps.max() > 0.6:
            raise ValueError(f'Unexpected native capture cadence: {recording}')
        for index in range(frames):
            with (recording / 'native' / f'{index:04d}.png').open('rb') as png:
                header = png.read(24)
            if (header[:8] != b'\x89PNG\r\n\x1a\n' or
                    struct.unpack('>II', header[16:24]) != (2560, 1440)):
                raise ValueError(f'Unexpected native frame {index} in {recording}')
        for patch, x, y in (('upper sky', 736, 40), ('low sky', 736, 310)):
            crop = f'48:24:{x}:{y}'
            raw = subprocess.check_output([
                'ffmpeg', '-v', 'error', '-i', clip, '-vf', f'crop={crop},format=rgb24',
                '-f', 'rawvideo', '-threads', '1', '-',
            ])
            rgb = np.frombuffer(raw, dtype=np.uint8).reshape(frames, 48 * 24, 3)
            frame_step = np.abs(np.diff(rgb.mean(axis=1), axis=0)).max(axis=1)
            # Dawn starts near 22530. This window includes the day wrap at 20 TPS
            # and allows for the delay between the trigger and ffmpeg's first frame.
            wrap = (round(float(frame_step[69 * CAPTURE_FPS:77 * CAPTURE_FPS].max()), 3)
                    if transition == 'dawn' else '')
            writer.writerow((transition, duration, frames, round(float(gaps.max()), 3), patch, crop,
                             round(float(np.percentile(frame_step, 95)), 3),
                             round(float(frame_step.max()), 3), wrap))


def clean(clip):
    """Check all frames for black bands or failed captures."""
    raw = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', clip, '-vf', 'scale=160:90,format=gray',
        '-f', 'rawvideo', '-threads', '1', '-',
    ])
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 90, 160)
    damaged = (frames.mean(axis=2).min(axis=1) < 4).sum()
    if damaged:
        raise ValueError(f'{damaged}/{len(frames)} frames have black bands: {clip}')
    print(f'PASS {len(frames)} clean frames: {clip}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('pixels', 'video', 'clean'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    {'pixels': pixels, 'video': video, 'clean': clean}[args.mode](args.path)
