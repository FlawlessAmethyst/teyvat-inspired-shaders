#!/usr/bin/env python3
"""Measure settled patches and the largest adjacent-frame change in live rain clips."""
import csv
import json
from pathlib import Path
from statistics import mean, median
import subprocess
import sys

WIDTH, HEIGHT = 640, 360
ROW_BYTES = WIDTH * 3
# Coordinates are in the 640 × 360 review raster. Stay inside each material
# so moving precipitation and clouds do not turn edges into false flashes.
PATCHES = {
    'daylight': {
        'near-grass': (254, 303, 110, 36),
        'near-stone': (552, 128, 55, 13),
        'horizon-sky': (46, 135, 125, 11),
        'distant-stone': (280, 98, 15, 21),
    },
    'open-water': {
        'sky': (61, 145, 100, 12),
        'far-water': (272, 187, 62, 11),
        'near-water': (255, 284, 110, 35),
    },
    'dense': {
        'plains-oak': (84, 53, 30, 25),
        'jungle-oak': (535, 55, 29, 25),
        'lit-path': (319, 285, 22, 24),
        'shadowed-path': (315, 219, 16, 5),
    },
}
RAIN_VIEWS = {'daylight': 'rain', 'open-water': 'water-rain', 'dense': 'dense-rain'}


def rgb_patch(frame, rect):
    x, y, w, h = rect
    pixels = b''.join(frame[(row * WIDTH + x) * 3:(row * WIDTH + x + w) * 3]
                      for row in range(y, y + h))
    # Median ignores isolated animated streaks without assuming a particle mask.
    return tuple(median(pixels[channel::3]) for channel in range(3))


def frames(path):
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-threads', '4', '-i', str(path),
               '-an', '-filter_threads', '2', '-vf', f'scale={WIDTH}:{HEIGHT}:flags=area',
               '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-threads', '2', 'pipe:1']
    size = WIDTH * HEIGHT * 3
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        while frame := process.stdout.read(size):
            if len(frame) != size:
                raise RuntimeError(f'Truncated frame from {path}')
            yield frame
        if process.wait() != 0:
            raise RuntimeError(f'Could not decode {path}')


def settled(root):
    out = csv.writer(sys.stdout, lineterminator='\n')
    out.writerow(('view', 'weather', 'patch', 'rect', 'control_r', 'control_g', 'control_b',
                  'candidate_r', 'candidate_g', 'candidate_b'))
    for view, patches in PATCHES.items():
        for weather, name in (('clear', view), ('rain', RAIN_VIEWS[view])):
            images = []
            for batch in ('control-01', 'weather-01'):
                image, = frames(root / batch / name / 'native.png')
                images.append(image)
            for patch, rect in patches.items():
                control, candidate = (rgb_patch(image, rect) for image in images)
                out.writerow((view, weather, patch, ' '.join(map(str, rect)), *control, *candidate))


def transitions(root):
    out = csv.writer(sys.stdout, lineterminator='\n')
    out.writerow(('view', 'direction', 'patch', 'frames', 'start_r', 'start_g', 'start_b',
                  'end_r', 'end_g', 'end_b', 'max_adjacent_channel_change',
                  'frame_of_max_change', 'seconds_of_max_change'))
    for view, patches in PATCHES.items():
        for target in ('rain', 'clear'):
            capture = root / 'weather-live/transitions' / view / f'to-{target}'
            trigger = json.loads((capture / 'trigger.json').read_text())
            fps = trigger['nominal_fps']
            with (capture / 'capture-times.csv').open(newline='') as timing:
                seconds = [row['seconds'] for row in csv.DictReader(timing)]
            values = {patch: [] for patch in patches}
            for frame in frames(capture / 'native/%04d.png'):
                if any(max(frame[row:row + ROW_BYTES]) <= 4 for row in range(0, len(frame), ROW_BYTES)):
                    raise RuntimeError(f'Unexpected black row in {capture}')
                for patch, rect in patches.items():
                    values[patch].append(rgb_patch(frame, rect))
            for patch, samples in values.items():
                if len(samples) != len(seconds):
                    raise RuntimeError(f'Native frame and timing counts differ in {capture}')
                start = [mean(values) for values in zip(*samples[:fps])]
                end = [mean(values) for values in zip(*samples[-fps:])]
                steps = [max(abs(a - b) for a, b in zip(previous, current))
                         for previous, current in zip(samples, samples[1:])]
                largest = max(steps)
                frame_index = steps.index(largest) + 1
                out.writerow((view, f'to-{target}', patch, len(samples),
                              *(f'{channel:.2f}' for channel in (*start, *end)),
                              f'{largest:.1f}', frame_index, seconds[frame_index]))


if __name__ == '__main__':
    {'settled': settled, 'transitions': transitions}[sys.argv[1]](Path(sys.argv[2]))
