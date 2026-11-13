#!/usr/bin/env python3
"""Validate the TASK-17 capture matrix and index the raw timings and images."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

from replay import BATCHES, PACK, ROOT, scenes

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import FIELDS, baseline, profile_settings


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(path):
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def check_log(logs, batch, enabled):
    latest = (logs / 'latest.log').read_text()
    expected = f'Using shaderpack: {PACK.name}' if enabled else 'Shaders are disabled'
    baseline.require(expected in latest, f'{batch}: missing loaded-mode message')
    ready = re.findall(r'TASK03_READY_([a-z-]+)', latest)
    baseline.require(ready == list(scenes.SPEC), f'{batch}: wrong scene acknowledgments {ready}')
    baseline.require('All dimensions are saved' in latest, f'{batch}: save not recorded')
    baseline.require(latest.count('Stopped tick profiling') == len(scenes.SPEC),
                     f'{batch}: profile completion count differs')
    if enabled:
        debug = (logs / 'debug.log').read_text()
        baseline.require(re.search(r'Render target settings for colortex0: .*requestedFormat=RGBA16F\b', debug),
                         f'{batch}: missing shader target')
        errors = re.findall(r'^.*(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl).*$',
                            latest, flags=re.IGNORECASE | re.MULTILINE)
        baseline.require(not errors, f'{batch}: shader-related errors: {errors}')


def index(root):
    reference = ROOT / 'artifacts/task-10/sodium-01/runs/daylight/recording'
    reference_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(reference_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    rows = []
    for batch in BATCHES:
        enabled = batch.startswith('prototype')
        pack = PACK.name if enabled else ''
        expected_iris = dict(iris, shaderPack=pack, enableShaders=str(enabled).lower())
        logs, = (root / batch).glob('logs-*')
        check_log(logs, batch, enabled)
        for scene, preset in scenes.SPEC.items():
            run = root / batch / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == preset,
                             f'{run}: preset differs')
            for name in baseline.SHARED_FILES:
                baseline.require((recording / name).read_bytes() == (reference / name).read_bytes(),
                                 f'{run}: {name} differs from TASK-10')
            config = baseline.read_options((recording / 'iris.properties').read_text(), '=')
            baseline.require(config == expected_iris, f'{run}: Iris settings differ')
            images = [recording / name for name in ('before.png', 'after.png')]
            for path in images:
                with path.open('rb') as file:
                    header = file.read(24)
                baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                                 struct.unpack('>II', header[16:24]) == (2560, 1440),
                                 f'{path}: wrong capture dimensions')
            archive, = recording.glob('*.zip')
            baseline.require(profile_settings(archive) == (runtime, options, pack or '(off)'),
                             f'{run}: archive runtime, options or pack differ')
            analysis = run / 'analysis'
            with baseline.TemporaryDirectory() as temp:
                generated = Path(temp) / 'analysis'
                stats = baseline.convert(archive, generated)
                if analysis.is_dir():
                    for name in ('client-ticking-raw.csv', 'frametimes.csv'):
                        baseline.require((analysis / name).read_bytes() == (generated / name).read_bytes(),
                                         f'{run}: stored {name} differs from the archive')
                else:
                    shutil.copytree(generated, analysis)
            baseline.require(9900 <= stats['profile_span_ms'] <= 10500,
                             f'{run}: profile duration outside the expected interval')
            raw = analysis / 'client-ticking-raw.csv'
            row = {'batch': batch, 'scene': scene, 'archive': local_path(archive),
                   'raw_csv': local_path(raw), 'raw_csv_sha256': digest(raw),
                   'latest_log': local_path(logs / 'latest.log')}
            for path in images:
                row[path.stem + '_png'] = local_path(path)
                row[path.stem + '_sha256'] = digest(path)
            row.update({key: stats[key] for key in FIELDS})
            rows.append(row)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    index(parser.parse_args().artifacts.resolve())
