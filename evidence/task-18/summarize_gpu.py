#!/usr/bin/env python3
"""Report milliseconds per sky draw from paired GL_TIME_ELAPSED batches."""
import argparse
import csv
import math
from pathlib import Path
import statistics
import sys

SCENES = ('sunset', 'rain', 'night', 'upward')


def summarize(path):
    pairs = {name: [] for name in SCENES}
    with path.open(newline='') as source:
        for row in csv.DictReader(source):
            samples = pairs[row['scene']]
            repeat = len(samples) + 1
            order = 'clouds-first' if repeat % 2 == 0 else 'control-first'
            draws = int(row['draws'])
            control, clouds = int(row['control_ns']), int(row['clouds_ns'])
            if (int(row['repeat']) != repeat or row['order'] != order or draws != 64
                    or min(control, clouds) <= 0):
                raise ValueError(f'{path}: invalid timer row {row}')
            scale = draws * 1e6
            samples.append((control / scale, clouds / scale, (clouds - control) / scale))
    for scene, samples in pairs.items():
        if len(samples) != 32:
            raise ValueError(f'{path}: expected 32 paired batches for {scene}')
        control, clouds, deltas = zip(*samples)
        p95 = sorted(deltas)[math.ceil(0.95 * len(deltas)) - 1]
        yield [path.stem, scene, len(samples),
               *(f'{value:.5f}' for value in (statistics.median(control), statistics.median(clouds),
                                             statistics.median(deltas), p95))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_csv', type=Path, nargs='+')
    args = parser.parse_args()
    out = csv.writer(sys.stdout, lineterminator='\n')
    out.writerow(('run', 'scene', 'paired_batches', 'control_median_ms', 'clouds_median_ms',
                  'paired_delta_median_ms', 'paired_delta_p95_ms'))
    for path in args.raw_csv:
        out.writerows(summarize(path))


if __name__ == '__main__':
    main()
