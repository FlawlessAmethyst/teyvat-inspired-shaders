#!/usr/bin/env python3
"""Measure matching patches in the 1440p Sodium, sky and fog captures."""
import argparse
import csv
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np

OVERLOOK = {
    'foreground grass': '128x96+1110+1040',
    'near cutout edge': '180x140+620+145',
    'near trunk': '24x55+822+470',
    'middle stone face': '100x40+1000+548',
    'far stone face': '85x28+1336+521',
    'last ridge': '8x32+1242+580',
    'low sky': '84x26+1710+609',
    'near glass': '34x26+1570+500',
    'overlapping glass': '26x20+1531+570',
}
PATCHES = dict.fromkeys(('daylight', 'sunset', 'rain', 'night'), OVERLOOK)
PATCHES['open-water'] = {'foreground water': '180x90+1040+1090'}
PATCHES['cave'] = {'ceiling recess': '120x60+1250+360',
                   'floor near lantern': '90x40+1840+820'}
MODES = ('sodium', 'sky', 'fog')


def capture(root, mode, scene):
    path = root / f'{mode}-01' / scene / 'native.png'
    with path.open('rb') as file:
        header = file.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (2560, 1440):
        raise ValueError(f'Invalid native capture: {path}')
    raw = subprocess.check_output(['magick', str(path), '-alpha', 'off',
                                   '-depth', '8', 'rgb:-'])
    return np.frombuffer(raw, dtype=np.uint8).reshape(1440, 2560, 3)


def patch(image, geometry):
    dimensions, x, y = geometry.split('+')
    width, height = map(int, dimensions.split('x'))
    x, y = int(x), int(y)
    return image[y:y + height, x:x + width].reshape(-1, 3)


def review(root):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('scene', 'patch', 'crop', 'mode', 'r', 'g', 'b',
                     'equal_to_sky_pct', 'p95_abs_channel_delta_from_sky'))
    for scene, patches in PATCHES.items():
        images = {mode: capture(root, mode, scene) for mode in MODES}
        for name, geometry in patches.items():
            control = patch(images['sky'], geometry)
            for mode in MODES:
                sample = patch(images[mode], geometry)
                delta = np.abs(sample.astype(np.int16) - control)
                writer.writerow((scene, name, geometry, mode, *np.median(sample, axis=0),
                                 round(float(100 * np.all(delta == 0, axis=1).mean()), 3),
                                 float(np.percentile(delta, 95, method='nearest'))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    review(parser.parse_args().artifacts)
