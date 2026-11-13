#!/usr/bin/env python3
"""Validate TASK-22 native captures, dimension transitions and client profiles."""
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

from replay import PRESETS, PROFILES, ROOT, pack

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import baseline, FIELDS, profile_settings

BATCHES = ('control-01', 'lighting-01', 'sodium-01', 'sodium-02', 'lighting-02', 'control-02')
DIMENSIONS = ('minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end',
              'minecraft:overworld')


def check_png(path):
    with path.open('rb') as file:
        header = file.read(24)
    baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n' and
                     struct.unpack('>II', header[16:24]) == (2560, 1440),
                     f'{path}: expected a 2560x1440 PNG')


def check_settings(directory, reference, iris, filenames):
    for name in filenames:
        baseline.require((directory / name).read_bytes() == (reference / name).read_bytes(),
                         f'{directory}: {name} differs from TASK-10')
    actual = baseline.read_options((directory / 'iris.properties').read_text(), '=')
    baseline.require(actual == iris, f'{directory}: Iris settings differ')


def check_profile_camera(recording, scene):
    # Stay inside nearby static terrain. Lightmap flicker can shift a few codes.
    region = {'night': '440x144+1016+1212', 'cave': '200x150+280+520'}[scene]
    images = [subprocess.check_output(['magick', str(recording / name), '-crop', region,
                                      '+repage', '-alpha', 'off', '-depth', '8', 'rgb:-'])
              for name in ('before.png', 'after.png')]
    delta = sum(abs(a - b) for a, b in zip(*images, strict=True)) / len(images[0])
    baseline.require(delta <= 2.0, f'{recording}: static terrain MAE {delta:.3f} exceeds 2 codes')


def check_session(batch, directory, mode, captures):
    logs, = directory.glob('logs-*')
    path = logs / 'latest.log'
    latest = path.read_text()
    expected = 'Shaders are disabled' if mode == 'sodium' else f'Using shaderpack: {pack(mode).name}'
    baseline.require(expected in latest and 'All dimensions are saved' in latest,
                     f'{batch}: missing pack or save acknowledgment')
    ready = tuple(re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest))
    build = ('build',) if batch == 'control-01' else ()
    returned = ('daylight',) if captures else ()
    baseline.require(ready == (*build, *captures, *returned, *PROFILES),
                     f'{batch}: unexpected preset sequence {ready}')
    baseline.require(latest.count('Stopped tick profiling') == len(PROFILES),
                     f'{batch}: wrong profile count')
    errors = re.findall(r'^.*(?:(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl)'
                        r'|failed to (?:compile|link)|ShaderCompileException|OpenGL error).*$', latest,
                        re.IGNORECASE | re.MULTILINE)
    baseline.require(not errors, f'{batch}: shader-related errors: {errors}')
    if mode != 'sodium':
        dimensions = tuple(re.findall(r'Creating pipeline for dimension (\S+)', latest))
        expected_dimensions = (DIMENSIONS[0], *(DIMENSIONS if captures else DIMENSIONS[:1]))
        baseline.require(dimensions == expected_dimensions,
                         f'{batch}: unexpected pipeline sequence {dimensions}')
        debug = (logs / 'debug.log').read_text()
        baseline.require(re.search(r'Render target settings for colortex0: .*requestedFormat=RGBA16F\b',
                                   debug), f'{batch}: missing RGBA16F render target')
    return path


def index(root):
    reference = ROOT / 'artifacts/task-10/sodium-01/runs/daylight/recording'
    ref_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(ref_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    baseline.require(json.loads((root / 'presets.json').read_text()) == PRESETS,
                     'Retained presets differ from the replay source')
    rows = []
    for batch in BATCHES:
        mode = batch.split('-')[0]
        directory = root / batch
        name = '' if mode == 'sodium' else pack(mode).name
        expected_iris = dict(iris, shaderPack=name, enableShaders=str(bool(name)).lower())
        captures = tuple(PRESETS) if batch.endswith('-01') else ()
        log = check_session(batch, directory, mode, captures)
        for scene in (*captures, 'return/daylight') if captures else ():
            capture = directory / scene
            baseline.require(json.loads((capture / 'preset.json').read_text()) ==
                             PRESETS[Path(scene).name], f'{capture}: preset differs')
            check_settings(capture, reference, expected_iris, baseline.SHARED_FILES[:4])
            check_png(capture / 'native.png')
        for scene in PROFILES:
            run = directory / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == PRESETS[scene],
                             f'{run}: preset differs')
            check_settings(recording, reference, expected_iris, baseline.SHARED_FILES)
            for filename in ('before.png', 'after.png'):
                check_png(recording / filename)
            check_profile_camera(recording, scene)
            archive, = recording.glob('*.zip')
            baseline.require(profile_settings(archive) == (runtime, options, name or '(off)'),
                             f'{run}: archive runtime, options or pack differs')
            analysis = run / 'analysis'
            if analysis.is_dir():
                with baseline.TemporaryDirectory() as temp:
                    generated = Path(temp) / 'analysis'
                    stats = baseline.convert(archive, generated)
                    for filename in ('client-ticking-raw.csv', 'frametimes.csv'):
                        baseline.require((analysis / filename).read_bytes() ==
                                         (generated / filename).read_bytes(),
                                         f'{run}: stored {filename} differs from the archive')
            else:
                stats = baseline.convert(archive, analysis)
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
    index(Path(sys.argv[1]).resolve())
