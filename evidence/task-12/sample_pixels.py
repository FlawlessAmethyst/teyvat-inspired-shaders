#!/usr/bin/env python3
"""Index median native sRGB codes in fixed surface patches."""
import argparse
import csv
from pathlib import Path
import subprocess
import sys

import numpy as np

from replay import TIMES

REGIONS = {
    'daylight': {'grass': '400x160+1050+1060', 'stone': '80x100+1130+405'},
    'cave': {'floor near lantern': '90x40+1840+820', 'ceiling recess': '120x60+1250+360'},
    'transition': {'grass': '400x160+1050+1060', 'stone': '130x100+200+435'},
    'facing': {'west face': '90x120+1140+490', 'south face': '90x120+1400+490'},
}


def sample(image, geometry):
    raw = subprocess.check_output(['magick', str(image), '-crop', geometry, '+repage',
                                   '-alpha', 'off', '-depth', '8', 'rgb:-'])
    rgb = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    return np.median(rgb, axis=0).tolist()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    args = parser.parse_args()
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('variant', 'scene', 'step', 'tick', 'surface', 'crop', 'r', 'g', 'b'))
    for variant in ('graded', 'sunlight'):
        batch = args.artifacts / f'{variant}-01'
        for scene, regions in REGIONS.items():
            if scene == 'transition':
                frames = [(0, TIMES[0], batch / 'transition/preset/native.png')]
                frames += [(step, tick, batch / 'transition' / f'{step:02d}-{tick:05d}.png')
                           for step, tick in enumerate(TIMES[1:], start=1)]
            elif scene == 'facing':
                frames = [(0, 12000, args.artifacts / f'{variant}-02/facing/native.png')]
            else:
                frames = [(0, 6000, batch / scene / 'native.png')]
            for step, tick, image in frames:
                for surface, geometry in regions.items():
                    writer.writerow((variant, scene, step, tick, surface, geometry,
                                     *sample(image, geometry)))
