#!/usr/bin/env python3
"""Verify TASK-21 captures, settings, logs and native profiles."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

from replay import BATCHES, CAPTURE_FPS, CAPTURE_SECONDS, CAPTURES, PROFILES, ROOT, pack

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import baseline, FIELDS, profile_settings


def check_png(path):
    with path.open('rb') as file:
        header = file.read(24)
    baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n'
                     and int.from_bytes(header[16:20]) == 2560
                     and int.from_bytes(header[20:24]) == 1440,
                     f'{path}: expected a 2560x1440 PNG')


def check_session(batch, directory, mode, captures, profiles=PROFILES):
    logs, = directory.glob('logs-*')
    path = logs / 'latest.log'
    latest = path.read_text()
    expected = 'Shaders are disabled' if mode == 'sodium' else f'Using shaderpack: {pack(mode).name}'
    baseline.require(expected in latest and 'All dimensions are saved' in latest,
                     f'{batch}: missing mode or save acknowledgment')
    ready = tuple(re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest))
    expected_presets = (*profiles, *captures)
    # The original candidate session also ran an excluded window-capture trial.
    trial_presets = ('daylight', 'open-water', 'dense') if batch == 'weather-01' else ()
    baseline.require(ready in (expected_presets, expected_presets + trial_presets),
                     f'{batch}: incorrect preset sequence {ready}')
    baseline.require(latest.count('Stopped tick profiling') == len(profiles),
                     f'{batch}: wrong profile count')
    errors = re.findall(r'^.*(?:(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl)'
                        r'|failed to (?:compile|link)|ShaderCompileException|OpenGL error).*$', latest,
                        re.IGNORECASE | re.MULTILINE)
    baseline.require(not errors, f'{batch}: shader-related errors: {errors}')
    if mode != 'sodium':
        debug = (logs / 'debug.log').read_text()
        baseline.require(re.search(r'Render target settings for colortex0: .*requestedFormat=RGBA16F\b',
                                   debug), f'{batch}: missing RGBA16F render target')
    return path


def check_settings(directory, reference, iris, filenames):
    for name in filenames:
        baseline.require((directory / name).read_bytes() == (reference / name).read_bytes(),
                         f'{directory}: {name} differs from TASK-10')
    actual_iris = baseline.read_options((directory / 'iris.properties').read_text(), '=')
    baseline.require(actual_iris == iris, f'{directory}: Iris settings differ')


def index(root):
    reference = ROOT / 'artifacts/task-10/sodium-01/runs/daylight/recording'
    reference_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(reference_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    presets = json.loads((root / 'presets.json').read_text())
    rows = []
    for batch in BATCHES:
        mode = batch.split('-')[0]
        directory = root / batch
        name = '' if mode == 'sodium' else pack(mode).name
        expected_iris = dict(iris, shaderPack=name, enableShaders=str(bool(name)).lower())
        captures = CAPTURES if batch in ('weather-01', 'control-01') else ()
        log = check_session(batch, directory, mode, captures)
        for scene in captures:
            capture = directory / scene
            baseline.require(json.loads((capture / 'preset.json').read_text()) == presets[scene],
                             f'{capture}: preset differs')
            check_settings(capture, reference, expected_iris, baseline.SHARED_FILES[:4])
            check_png(capture / 'native.png')
        for scene in PROFILES:
            run = directory / 'runs' / scene
            recording = run / 'recording'
            baseline.require(json.loads((run / 'preset.json').read_text()) == presets[scene],
                             f'{run}: preset differs')
            check_settings(recording, reference, expected_iris, baseline.SHARED_FILES)
            for filename in ('before.png', 'after.png'):
                check_png(recording / filename)
            archive, = recording.glob('*.zip')
            baseline.require(profile_settings(archive) == (runtime, options, name or '(off)'),
                             f'{run}: archive runtime, options or pack differs')
            analysis = run / 'analysis'
            if analysis.is_dir():
                with baseline.TemporaryDirectory() as temp:
                    generated = Path(temp) / 'analysis'
                    stats = baseline.convert(archive, generated)
                    for filename in ('client-ticking-raw.csv', 'frametimes.csv'):
                        baseline.require((analysis / filename).read_bytes() == (generated / filename).read_bytes(),
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
    transition_scenes = ('daylight', 'open-water', 'dense')
    live = root / 'weather-live'
    log = check_session('weather-live', live, 'weather', transition_scenes, profiles=())
    check_transitions(live / 'transitions', transition_scenes, log, presets, reference, iris)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


def check_transitions(root, scenes, log, presets, reference, iris):
    entries = log.read_text()
    for weather in ('rain', 'clear'):
        baseline.require(entries.count(f'[CHAT] TASK21_{weather}_6000') == len(scenes),
                         f'{log}: expected a fixed-time acknowledgment for each {weather} trigger')
    for scene in scenes:
        preset = root / scene / 'preset'
        baseline.require(json.loads((preset / 'preset.json').read_text()) == presets[scene],
                         f'{preset}: transition preset differs')
        check_png(preset / 'native.png')
        check_settings(preset, reference, dict(iris, shaderPack=pack('weather').name,
                                               enableShaders='true'), baseline.SHARED_FILES[:4])
        for weather in ('rain', 'clear'):
            capture = root / scene / f'to-{weather}'
            trigger = json.loads((capture / 'trigger.json').read_text())
            baseline.require(trigger['weather'] == weather and trigger['daytime'] == 6000
                             and trigger['nominal_fps'] == CAPTURE_FPS
                             and 2.0 <= trigger['trigger_seconds_after_capture_start'] < 2.5,
                             f'{capture}: trigger differs')
            with (capture / 'capture-times.csv').open(newline='') as file:
                timing = list(csv.DictReader(file))
            expected_frames = CAPTURE_SECONDS * CAPTURE_FPS
            baseline.require(len(timing) == expected_frames, f'{capture}: unexpected sample count')
            for index, frame in enumerate(timing):
                baseline.require(int(frame['frame']) == index and
                                 0 <= float(frame['seconds']) - index / CAPTURE_FPS < 0.28,
                                 f'{capture}: screenshot deadline missed at {index}')
                check_png(capture / f'native/{index:04d}.png')


if __name__ == '__main__':
    index(Path(sys.argv[1]).resolve())
