#!/usr/bin/env python3
"""Validate the matched TASK-10 run matrix and export a reviewed metrics index."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from frametimes import convert

BATCHES = ('sodium-01', 'neutral-01', 'neutral-02', 'sodium-02')
SCENES = ('daylight', 'forest', 'cave')
SHARED_FILES = ('options.txt', 'sodium-options.json', 'sodium-extra-options.json',
                'dynamic_fps.json', 'mmc-pack.json', 'mods.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_options(text, separator):
    pairs = (line.split(separator, 1) for line in text.splitlines()
             if separator in line and not line.startswith('#'))
    return {key: value.strip() for key, value in pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', type=Path, default=ROOT / 'artifacts/task-10')
    artifacts = parser.parse_args().artifacts_dir.resolve()
    presets = json.loads((ROOT / 'scripts/scenes/presets.json').read_text())
    reference = artifacts / BATCHES[0] / 'runs/daylight/recording'
    options = read_options((reference / 'options.txt').read_text(), ':')
    expected = {'maxFps': '260', 'enableVsync': 'false', 'renderDistance': '12',
                'simulationDistance': '8', 'fov': '0.0', 'fullscreen': 'true',
                'guiScale': '3', 'bobView': 'false'}
    require(all(options.get(k) == v for k, v in expected.items()), 'Unexpected video settings')
    reference_iris = read_options((reference / 'iris.properties').read_text(), '=')
    expected_profile = dict(expected, fov='70')
    del expected_profile['bobView']  # Minecraft omits this from the ZIP options report.
    runtime_keys = ('Minecraft Version', 'Operating System', 'Java Version',
                    'Processor Name', 'Backend API', 'Window size', 'JVM Flags')
    reference_runtime = None
    rows = []
    for batch in BATCHES:
        enabled = batch.startswith('neutral')
        expected_iris = dict(reference_iris, enableShaders=str(enabled).lower(),
                             shaderPack='TASK-10-neutral' if enabled else '')
        for scene in SCENES:
            run = artifacts / batch / 'runs' / scene
            recording = run / 'recording'
            require(json.loads((run / 'preset.json').read_text()) == presets[scene],
                    f'{run}: preset mismatch')
            for name in SHARED_FILES:
                require((recording / name).read_bytes() == (reference / name).read_bytes(),
                        f'{run}: {name} differs')
            require(read_options((recording / 'iris.properties').read_text(), '=') == expected_iris,
                    f'{run}: Iris configuration differs')
            for name in ('before.png', 'after.png'):
                with (recording / name).open('rb') as file:
                    header = file.read(24)
                require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                        struct.unpack('>II', header[16:24]) == (2560, 1440),
                        f'{run}: incorrect window capture')
            archive, = recording.glob('*.zip')
            with ZipFile(archive) as profile:
                runtime = read_options(profile.read('system.txt').decode(), ':')
                runtime = {key: runtime[key] for key in runtime_keys}
                recorded_options = read_options(profile.read('client/options.txt').decode(), ':')
            require(runtime['Window size'] == '2560x1440', f'{run}: incorrect render resolution')
            if reference_runtime is None:
                reference_runtime = runtime
            require(runtime == reference_runtime, f'{run}: profiler hardware/software differs')
            require(all(recorded_options.get(k) == v for k, v in expected_profile.items()),
                    f'{run}: profiler options differ')
            analysis = run / 'analysis'
            if analysis.exists():
                # Re-run analysis in a new directory to avoid trusting old output.
                with TemporaryDirectory() as tmp:
                    stats = convert(archive, Path(tmp) / 'analysis')
                    for name in ('client-ticking-raw.csv', 'frametimes.csv'):
                        require((analysis / name).read_bytes() ==
                                (Path(tmp) / 'analysis' / name).read_bytes(),
                                f'{run}: stored analysis differs')
            else:
                stats = convert(archive, analysis)
            require(9900 <= stats['profile_span_ms'] <= 10500,
                    f'{run}: profile duration outside the expected interval')
            fields = ('samples', 'profile_span_ms', 'profile_frames_per_second',
                      'mean_client_loop_ms', 'p50_client_loop_ms', 'p95_client_loop_ms',
                      'p99_client_loop_ms', 'max_client_loop_ms', 'source_sha256')
            row = {'batch': batch, 'scene': scene,
                   'archive': str(archive.relative_to(ROOT) if archive.is_relative_to(ROOT)
                                  else archive),
                   'raw_csv_sha256': hashlib.sha256(
                       (analysis / 'client-ticking-raw.csv').read_bytes()).hexdigest()}
            row.update({key: stats[key] for key in fields})
            rows.append(row)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    main()
