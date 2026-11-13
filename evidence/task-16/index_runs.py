#!/usr/bin/env python3
"""Verify matched capture conditions and index TASK-16 profile archives."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

import replay

sys.path.insert(0, str(replay.ROOT / 'evidence/task-11'))
from summarize import FIELDS, baseline, profile_settings


def index(root):
    reference = replay.ROOT / 'artifacts/task-10/sodium-01/runs/daylight/recording'
    reference_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(reference_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    presets = replay.scenes.SPEC
    baseline.require(json.loads((root / 'presets.json').read_text()) == presets,
                     'Fixture presets differ from replay source')
    rows = []
    for batch in replay.BATCHES:
        mode = batch.split('-')[0]
        enabled = mode != 'sodium'
        pack = replay.pack(mode).name if enabled else ''
        expected_iris = dict(iris, shaderPack=pack, enableShaders=str(enabled).lower())
        for scene in replay.PROFILE_SCENES:
            run = root / batch / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == presets[scene],
                             f'{run}: camera preset differs')
            for name in baseline.SHARED_FILES:
                baseline.require((recording / name).read_bytes() == (reference / name).read_bytes(),
                                 f'{run}: {name} differs from TASK-10')
            config = baseline.read_options((recording / 'iris.properties').read_text(), '=')
            baseline.require(config == expected_iris, f'{run}: Iris settings differ')
            for name in ('before.png', 'after.png'):
                with (recording / name).open('rb') as file:
                    header = file.read(24)
                baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                                 struct.unpack('>II', header[16:24]) == (2560, 1440),
                                 f'{run}: profile screenshot has wrong dimensions')
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
            row = {'batch': batch, 'scene': scene,
                   'archive': str(archive.relative_to(replay.ROOT) if archive.is_relative_to(replay.ROOT)
                                  else archive),
                   'raw_csv_sha256': hashlib.sha256(
                       (analysis / 'client-ticking-raw.csv').read_bytes()).hexdigest()}
            row.update({key: stats[key] for key in FIELDS})
            rows.append(row)

    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    index(parser.parse_args().artifacts.resolve())
