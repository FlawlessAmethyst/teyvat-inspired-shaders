#!/usr/bin/env python3
"""Validate matched TASK-11 client profiles and index the retained raw samples."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
from zipfile import ZipFile

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('baseline_summary', BASE / 'task-10/summarize.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)
ROOT = baseline.ROOT
BATCHES = ('neutral-01', 'graded-01', 'graded-02', 'neutral-02')
RUNTIME_KEYS = ('Minecraft Version', 'Operating System', 'Java Version',
                'Processor Name', 'Backend API', 'Window size', 'JVM Flags')
FIELDS = ('samples', 'profile_span_ms', 'profile_frames_per_second', 'mean_client_loop_ms',
          'p50_client_loop_ms', 'p95_client_loop_ms', 'p99_client_loop_ms', 'source_sha256')


def profile_settings(archive):
    with ZipFile(archive) as profile:
        runtime = baseline.read_options(profile.read('system.txt').decode(), ':')
        options = baseline.read_options(profile.read('client/options.txt').decode(), ':')
    return ({key: runtime[key] for key in RUNTIME_KEYS}, options, runtime['Loaded Shaderpack'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', required=True, type=Path)
    summarize(parser.parse_args().artifacts_dir, 'TASK-11', BATCHES, baseline.SCENES)


def summarize(artifacts, task, batches, scenes):
    artifacts = artifacts.resolve()
    reference = ROOT / 'artifacts/task-10/neutral-01/runs/daylight/recording'
    ref_archive, = reference.glob('*.zip')
    expected_runtime, expected_options, _ = profile_settings(ref_archive)
    expected_iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    presets = json.loads((ROOT / 'scripts/scenes/presets.json').read_text())
    rows = []
    for batch in batches:
        variant = batch.split('-')[0]
        pack = f'{task}-{variant}'
        for scene in scenes:
            run = artifacts / batch / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == presets[scene],
                             f'{run}: preset mismatch')
            for name in baseline.SHARED_FILES:
                baseline.require((recording / name).read_bytes() == (reference / name).read_bytes(),
                                 f'{run}: {name} differs from TASK-10')
            iris = baseline.read_options((recording / 'iris.properties').read_text(), '=')
            baseline.require(iris == dict(expected_iris, shaderPack=pack),
                             f'{run}: Iris settings mismatch')
            for name in ('before.png', 'after.png'):
                with (recording / name).open('rb') as file:
                    header = file.read(24)
                baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                                 struct.unpack('>II', header[16:24]) == (2560, 1440),
                                 f'{run}: capture dimensions mismatch')
            archive, = recording.glob('*.zip')
            runtime, options, loaded_pack = profile_settings(archive)
            baseline.require(runtime == expected_runtime and options == expected_options,
                             f'{run}: runtime or profiler options differ from TASK-10')
            baseline.require(loaded_pack == pack, f'{run}: wrong loaded pack')

            analysis = run / 'analysis'
            if analysis.exists():
                with baseline.TemporaryDirectory() as temp:
                    stats = baseline.convert(archive, Path(temp) / 'analysis')
                    for name in ('client-ticking-raw.csv', 'frametimes.csv'):
                        baseline.require((analysis / name).read_bytes() ==
                                         (Path(temp) / 'analysis' / name).read_bytes(),
                                         f'{run}: stored analysis differs')
            else:
                stats = baseline.convert(archive, analysis)
            baseline.require(9900 <= stats['profile_span_ms'] <= 10500,
                             f'{run}: profile duration outside the expected interval')
            row = {'batch': batch, 'scene': scene,
                   'archive': str(archive.relative_to(ROOT) if archive.is_relative_to(ROOT)
                                  else archive),
                   'raw_csv_sha256': hashlib.sha256(
                       (analysis / 'client-ticking-raw.csv').read_bytes()).hexdigest()}
            row.update({key: stats[key] for key in FIELDS})
            rows.append(row)

    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    main()
