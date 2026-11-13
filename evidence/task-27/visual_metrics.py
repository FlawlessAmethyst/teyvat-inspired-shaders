#!/usr/bin/env python3
"""Sample the established shadow crops and the matched fog views."""
import argparse
import csv
import importlib.util
from pathlib import Path
import subprocess
import sys

import numpy as np

spec = importlib.util.spec_from_file_location(
    'shadow_review', Path(__file__).resolve().parents[1] / 'task-16/review.py')
shadow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shadow)

PATCHES = {
    'valley': '420x220+1080+510',
    'rain': '420x220+1080+510',
    'dusk': '520x250+1020+420',
    'ridges': '500x180+1050+565',
}


def capture(root, mode, scene):
    if scene in ('valley', 'rain'):
        recording = root / f'{mode}-01/runs/{scene}'
        # The matched profile screenshots are native-sized PNG window captures.
        raw = subprocess.check_output([
            'magick', str(recording / 'recording/before.png'), '-alpha', 'off', '-depth', '8', 'rgb:-',
        ])
        return np.frombuffer(raw, dtype=np.uint8).reshape(1440, 2560, 3)
    return shadow.read_capture(root, f'{mode}-01/views', scene)


def review(root):
    for trial, views in (
        ('shadow', {name: shadow.PATCHES[name] for name in ('contact', 'sunset', 'range')}),
        ('fog', {name: {'terrain and horizon': crop} for name, crop in PATCHES.items()}),
    ):
        for scene, regions in views.items():
            full, candidate = (capture(root, mode, scene) for mode in ('full', trial))
            for label, crop in regions.items():
                before = shadow.patch(full, crop)
                after = shadow.patch(candidate, crop)
                delta = after.astype(np.int16) - before
                luma = np.array([0.2126, 0.7152, 0.0722])
                yield (trial, scene, label, crop, f'{100 * np.all(delta == 0, axis=1).mean():.3f}',
                       f'{np.abs(delta).mean():.3f}', f'{np.percentile(np.abs(delta), 95):.3f}',
                       f'{(delta @ luma).mean():+.3f}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('trial', 'scene', 'patch', 'crop', 'identical_rgb_pct',
                     'rgb_mean_abs_delta', 'rgb_p95_abs_delta', 'mean_luma_delta'))
    writer.writerows(review(parser.parse_args().root))


if __name__ == '__main__':
    main()
