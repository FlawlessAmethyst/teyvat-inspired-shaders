#!/usr/bin/env python3
"""Sample fixed regions in the matched native shadow and fog captures."""
import argparse
import csv
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np

PATCHES = {
    'contact': {
        'unoccluded stone': '108x60+1200+838',
        'suspended leaf footprint': '135x55+1058+588',
        'stone pillar contact': '135x25+1457+615',
    },
    'sunset': {
        'unoccluded stone': '100x60+1100+894',
        'chest cast shadow': '62x19+1738+615',
        'suspended leaf footprint': '172x190+1380+685',
        'stone pillar shadow': '66x35+720+808',
        'clear-glass footprint': '260x100+390+610',
    },
    'forest': {
        'under front canopy': '90x12+1370+715',
        'unoccluded grass': '100x66+1230+1140',
    },
    'range': {
        'near pillar footprint': '60x9+1606+749',
        'fade-zone pillar footprint': '26x6+1336+678',
        'far pillar footprint': '20x5+1299+673',
    },
    'cave': {'stone floor': '200x110+1080+1075'},
    'night': {'grass foreground': '300x120+1080+1050'},
    'open-water': {'low sky': '120x70+1090+430'},
}


def read_capture(root, batch, scene):
    path = root / batch / scene / 'native.png'
    with path.open('rb') as file:
        header = file.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (2560, 1440):
        raise ValueError(f'Expected a native 2560×1440 PNG: {path}')
    raw = subprocess.check_output(['magick', str(path), '-alpha', 'off', '-depth', '8', 'rgb:-'])
    return np.frombuffer(raw, dtype=np.uint8).reshape(1440, 2560, 3)


def patch(image, crop):
    dimensions, x, y = crop.split('+')
    width, height = map(int, dimensions.split('x'))
    x, y = int(x), int(y)
    return image[y:y + height, x:x + width].reshape(-1, 3)


def review(root):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('scene', 'patch', 'crop', 'fog_r', 'fog_g', 'fog_b',
                     'shadow_r', 'shadow_g', 'shadow_b', 'equal_rgb_pct',
                     'mean_luma_drop', 'p95_luma_drop'))
    luma_weights = np.array([0.2126, 0.7152, 0.0722])
    for scene, patches in PATCHES.items():
        fog = read_capture(root, 'fog-01', scene)
        shadow = read_capture(root, 'shadows-01', scene)
        for name, crop in patches.items():
            control = patch(fog, crop)
            candidate = patch(shadow, crop)
            delta = control.astype(np.int16) - candidate
            luma_drop = (delta * luma_weights).sum(axis=1)
            writer.writerow((scene, name, crop, *np.median(control, axis=0),
                             *np.median(candidate, axis=0),
                             round(100 * np.all(delta == 0, axis=1).mean(), 3),
                             round(float(luma_drop.mean()), 3),
                             round(float(np.percentile(luma_drop, 95)), 3)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    review(parser.parse_args().artifacts)
