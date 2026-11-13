#!/usr/bin/env python3
"""Validate and summarize paired GPU time queries from the TASK-26 timers."""
import argparse
import csv
import re
from pathlib import Path
from statistics import median
import sys

TESTS = {
    'shadow-receiver': (('foliage-lit', 'foliage-range-fade', 'stone-night'), 'off', 'full'),
    'terrain-lighting': (('foliage-lit', 'foliage-range-fade', 'stone-night'), 'off', 'full'),
    'sky-gradient': (('sunset', 'rain', 'night', 'upward'), 'control', 'clouds'),
    'cloud': (('sunset', 'rain', 'night', 'upward'), 'control', 'clouds'),
    'grade': (('valley-source',), 'control', 'spatial'),
    'water-depth': (('water-clear', 'water-rain', 'water-under'), 'off', 'full'),
    'water-material': (('water-clear', 'water-rain', 'water-under'), 'off', 'full'),
    'fog': (('fog-near', 'fog-clear', 'fog-dusk', 'fog-rain', 'fog-under'), 'off', 'full'),
}


# Positive probes confirm the intended branch changed a rendered pixel.
UNCHANGED = {
    'shadow-receiver': {'stone-night'},
    'water-depth': {'water-under'},
    'fog': {'fog-near'},
}


def check_probes(device, test, scenes):
    probes = re.findall(r'^([\w-]+) max sampled linear RGB delta (\d+\.\d+)$',
                        device, re.MULTILINE)
    if tuple(scene for scene, _ in probes) != scenes:
        raise ValueError(f'{test}: incomplete geometry pixel probes')
    for scene, delta in probes:
        unchanged = scene in UNCHANGED.get(test, ())
        if (float(delta) == 0.0) != unchanged:
            raise ValueError(f'{test}: unexpected color probe for {scene}: {delta}')


def summarize(root):
    for test, (scenes, off, full) in TESTS.items():
        for run in ('01', '02'):
            source = root / f'{test}-{run}.csv'
            device = (root / f'{test}-{run}-device.txt').read_text().strip()
            if 'NVIDIA' not in device or 'llvmpipe' in device:
                raise ValueError(f'{source}: unexpected timer device {device}')
            if off == 'off':
                check_probes(device, test, scenes)
            with source.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            if len(rows) != 32 * len(scenes):
                raise ValueError(f'{source}: unexpected query count')
            for index, scene in enumerate(scenes):
                group = rows[index * 32:(index + 1) * 32]
                timings = []
                for repeat, row in enumerate(group, 1):
                    order = off if repeat % 2 else full
                    values = int(row[f'{off}_ns']), int(row[f'{full}_ns'])
                    if (row.get('scene', scene) != scene or int(row['repeat']) != repeat
                            or row['order'] != f'{order}-first' or int(row['draws']) != 64
                            or min(values) <= 0):
                        raise ValueError(f'{source}: invalid timer row {row}')
                    off_ms, full_ms = (value / 64e6 for value in values)
                    timings.append((off_ms, full_ms, full_ms - off_ms))
                yield (test, run, scene, len(group),
                       *(f'{median(values):.6f}' for values in zip(*timings)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gpu_dir', type=Path)
    out = csv.writer(sys.stdout, lineterminator='\n')
    out.writerow(('effect', 'run', 'scene', 'paired_batches', 'off_median_ms',
                  'full_median_ms', 'paired_delta_median_ms'))
    out.writerows(summarize(parser.parse_args().gpu_dir))


if __name__ == '__main__':
    main()
