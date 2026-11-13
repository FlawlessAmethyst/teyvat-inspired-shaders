#!/usr/bin/env python3
"""Measure display-encoded luma and highlights in fixed native screenshot patches."""
import csv
from pathlib import Path
from statistics import mean, quantiles
import subprocess
import sys

# Coordinates are x, y, width, height in the native 2560x1440 PNG.
PATCHES = {
    'daylight': {'grass': (1016, 1212, 440, 144), 'stone-wall': (2208, 512, 220, 52)},
    'night': {'grass': (1016, 1212, 440, 144), 'stone-wall': (2208, 512, 220, 52)},
    'cave': {'recess': (1210, 390, 140, 75), 'lantern-pool': (827, 797, 100, 27)},
    'lamps': {'sea-lantern-face': (1264, 562, 30, 28),
              'glowstone-face': (1090, 562, 28, 28),
              'shroomlight-face': (1435, 562, 28, 28),
              'lit-wall': (1315, 615, 90, 40)},
    'unlit': {'step-faces': (1050, 676, 420, 190),
              'foreground': (1000, 1120, 560, 150),
              'dark-wall': (1570, 420, 220, 100)},
}


def measurements(path, region):
    x, y, width, height = region
    raw = subprocess.check_output(['magick', str(path), '-crop', f'{width}x{height}+{x}+{y}',
                                   '+repage', '-alpha', 'off', '-depth', '8', 'rgb:-'])
    if len(raw) != 3 * width * height:
        raise ValueError(f'Unexpected RGB crop length for {path}')
    rgb = list(zip(raw[0::3], raw[1::3], raw[2::3], strict=True))
    luma = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in rgb]
    percentiles = quantiles(luma, n=100, method='inclusive')
    peak = quantiles(map(max, rgb), n=100, method='inclusive')[98]
    return percentiles[9], mean(luma), percentiles[89], peak


def main(root):
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('scene', 'patch', 'x', 'y', 'width', 'height', 'mode',
                     'luma_p10', 'luma_mean', 'luma_p90', 'peak_channel_p99'))
    for scene, regions in PATCHES.items():
        for name, region in regions.items():
            for mode in ('sodium', 'control', 'lighting'):
                values = measurements(root / f'{mode}-01' / scene / 'native.png', region)
                writer.writerow((scene, name, *region, mode, *(f'{value:.3f}' for value in values)))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
