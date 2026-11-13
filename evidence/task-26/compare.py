#!/usr/bin/env python3
"""Build matched window-frame sheets and summarize client ablation deltas."""
import argparse
import csv
from pathlib import Path
from statistics import mean
import subprocess
import sys

from variants import SCENES

COMPARISONS = {
    'sodium': 'full',
    'shadowless': 'full',
    'cloudless': 'full',
    'fogless': 'full',
    'water-depthless': 'full',
    'water-vanilla': 'full',
    'gradeless': 'full',
    'terrain-vanilla': 'shadowless',
    'rain-neutral': 'full',
}


def compare(rows, writer):
    by_run = {(row['batch'], row['scene']): row for row in rows}
    writer.writerow(('ablation', 'reference', 'scene', 'ablation_mean_01_ms',
                     'ablation_mean_02_ms', 'reference_mean_01_ms', 'reference_mean_02_ms',
                     'reference_minus_ablation_01_ms', 'reference_minus_ablation_02_ms',
                     'reference_minus_ablation_ms', 'reference_repeat_spread_ms',
                     'ablation_repeat_spread_ms'))
    for ablation, reference in COMPARISONS.items():
        for scene in SCENES[ablation]:
            if (f'{reference}-01', scene) not in by_run:
                raise ValueError(f'Missing reference: {reference}, {scene}')
            values = [
                [float(by_run[f'{mode}-{run}', scene]['mean_client_loop_ms']) for run in ('01', '02')]
                for mode in (ablation, reference)
            ]
            off, full = values
            deltas = [a - b for a, b in zip(full, off, strict=True)]
            writer.writerow((ablation, reference, scene,
                             *(f'{value:.6f}' for value in (
                                 *off, *full, *deltas, mean(deltas),
                                 abs(full[0] - full[1]), abs(off[0] - off[1])))))


def sheets(root):
    out = root / 'comparisons'
    out.mkdir(exist_ok=True)
    for ablation, reference in COMPARISONS.items():
        for scene in SCENES[ablation]:
            command = ['magick', 'montage', '-font', 'DejaVu-Sans', '-pointsize', '19']
            for run in ('01', '02'):
                for mode in (reference, ablation):
                    image = root / f'{mode}-{run}/runs/{scene}/recording/before.png'
                    command.extend(('-label', f'{scene} | {mode} {run}', str(image)))
            command.extend(('-tile', '2x2', '-geometry', '900x506+4+4',
                            '-background', '#171b22', '-fill', '#f3f3f3',
                            '-quality', '92', str(out / f'{ablation}-{scene}.jpg')))
            subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    parser.add_argument('--sheets-from', type=Path)
    args = parser.parse_args()
    with args.runs.open(newline='') as stream:
        compare(csv.DictReader(stream), csv.writer(sys.stdout, lineterminator='\n'))
    if args.sheets_from is not None:
        sheets(args.sheets_from)


if __name__ == '__main__':
    main()
