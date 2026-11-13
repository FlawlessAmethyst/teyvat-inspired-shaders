#!/usr/bin/env python3
"""Validate the matched TASK-19 client profiles and index their raw samples."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

from replay import PROFILES, ROOT, pack

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import FIELDS, baseline, profile_settings

BATCHES = ('water-01', 'control-01', 'sodium-01', 'sodium-02', 'control-02', 'water-02')
CAPTURE_PRESETS = ('basin-sunset', 'underwater', 'basin-rain', 'underside', 'open-water', 'shore')


def check_log(root, batch, mode):
    logs, = (root / batch).glob('logs-*')
    latest = (logs / 'latest.log').read_text()
    expected = 'Shaders are disabled' if mode == 'sodium' else f'Using shaderpack: {pack(mode).name}'
    baseline.require(expected in latest, f'{batch}: missing loaded-mode message')
    baseline.require('All dimensions are saved' in latest, f'{batch}: save not recorded')
    ready = tuple(re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest))
    expected_presets = (('basin', *PROFILES, *CAPTURE_PRESETS)
                        if batch in ('water-01', 'control-01') else PROFILES)
    baseline.require(ready == expected_presets, f'{batch}: incorrect preset sequence {ready}')
    baseline.require(latest.count('Stopped tick profiling') == len(PROFILES),
                     f'{batch}: wrong profile count')
    errors = re.findall(r'^.*(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl).*$',
                        latest, re.IGNORECASE | re.MULTILINE)
    baseline.require(not errors, f'{batch}: shader-related errors: {errors}')
    if mode != 'sodium':
        debug = (logs / 'debug.log').read_text()
        baseline.require(re.search(r'Render target settings for colortex0: .*requestedFormat=RGBA16F\b',
                                   debug), f'{batch}: missing RGBA16F render target')
    return logs / 'latest.log'


def check_png(path):
    with path.open('rb') as file:
        header = file.read(24)
    baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                     struct.unpack('>II', header[16:24]) == (2560, 1440),
                     f'{path}: expected a 2560x1440 PNG')


def index(root):
    reference = ROOT / 'artifacts/task-10/sodium-01/runs/daylight/recording'
    reference_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(reference_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    presets = json.loads((root / 'presets.json').read_text())
    rows = []
    for batch in BATCHES:
        mode = batch.split('-')[0]
        enabled = mode != 'sodium'
        name = pack(mode).name if enabled else ''
        expected_iris = dict(iris, shaderPack=name, enableShaders=str(enabled).lower())
        log = check_log(root, batch, mode)
        for scene in PROFILES:
            run = root / batch / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == presets[scene],
                             f'{run}: preset differs')
            for filename in baseline.SHARED_FILES:
                baseline.require((recording / filename).read_bytes() == (reference / filename).read_bytes(),
                                 f'{run}: {filename} differs from TASK-10')
            config = baseline.read_options((recording / 'iris.properties').read_text(), '=')
            baseline.require(config == expected_iris, f'{run}: Iris settings differ')
            for filename in ('before.png', 'after.png'):
                check_png(recording / filename)
            archive, = recording.glob('*.zip')
            baseline.require(profile_settings(archive) == (runtime, options, name or '(off)'),
                             f'{run}: archive runtime, options or pack differs')
            analysis = run / 'analysis'
            with baseline.TemporaryDirectory() as temp:
                generated = Path(temp) / 'analysis'
                stats = baseline.convert(archive, generated)
                if analysis.is_dir():
                    for filename in ('client-ticking-raw.csv', 'frametimes.csv'):
                        baseline.require((analysis / filename).read_bytes() == (generated / filename).read_bytes(),
                                         f'{run}: stored {filename} differs from the archive')
                else:
                    shutil.copytree(generated, analysis)
            baseline.require(9900 <= stats['profile_span_ms'] <= 10500,
                             f'{run}: profile duration outside the expected interval')
            raw = analysis / 'client-ticking-raw.csv'
            row = {'batch': batch, 'scene': scene, 'archive': str(archive.relative_to(ROOT)),
                   'raw_csv': str(raw.relative_to(ROOT)),
                   'raw_csv_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
                   'latest_log': str(log.relative_to(ROOT))}
            row.update({field: stats[field] for field in FIELDS})
            rows.append(row)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    index(parser.parse_args().artifacts.resolve())
