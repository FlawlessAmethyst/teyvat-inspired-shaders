#!/usr/bin/env python3
"""Verify TASK-27 raw measurements and regenerate the comparison indices."""
import argparse
import csv
import json
from pathlib import Path
import re
from statistics import median
import sys
from zipfile import ZipFile

from optimize import MODES, PROFILES, ROOT, VISUALS, pack, presets, tree_manifest
from review import FIELDS, baseline, check_camera, profile_settings

SESSIONS = (
    ('sodium-01',),
    ('full-01', 'shadow-01', 'fog-01'),
    ('fog-02', 'shadow-02', 'full-02'),
    ('sodium-02',),
)


def verify_session(root, session):
    log, = (root / session[0]).glob('logs-*/latest.log')
    latest = log.read_text()
    events = []
    views = []
    for batch in session:
        mode, round_id = batch.rsplit('-', 1)
        events.append(f'Using shaderpack: {pack(mode).name}\n' if mode != 'sodium'
                      else 'Shaders are disabled because enableShaders is set to false')
        for name in PROFILES:
            events += [f'[CHAT] TASK03_READY_{name}', 'Stopped tick profiling']
            views.append(name)
        if round_id == '01':
            for name in VISUALS.get(mode, ()):
                events.append(f'[CHAT] TASK03_READY_{name}')
                views.append(name)
    events += ['Stopping!', 'All dimensions are saved']
    tail = latest
    for event in events:
        _, found, tail = tail.partition(event)
        baseline.require(found, f'{log}: missing or out of order: {event.strip()}')
    baseline.require(re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest) == views,
                     f'{log}: unexpected camera sequence')
    baseline.require(latest.count('Stopped tick profiling') == len(PROFILES) * len(session),
                     f'{log}: unexpected profile count')
    baseline.require('Iris 1.8.14-beta.1+mc1.21.1' in latest and 'Sodium 0.8.13' in latest,
                     f'{log}: missing Iris or Sodium version')
    baseline.require(not re.search(
        r'^.*(?:(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl)'
        r'|ShaderCompileException|ProgramLinkException|OpenGL error|falling back to vanilla shading).*$', latest,
        re.IGNORECASE | re.MULTILINE), f'{log}: shader-related error')
    if session[0] == 'full-01':
        baseline.require('TASK16_READY_FIXTURE' in latest, f'{log}: shadow fixture build missing')
    if not session[0].startswith('sodium-'):
        debug = log.with_name('debug.log').read_text()
        targets = re.findall(r'Render target settings for colortex0: .*requestedFormat=([A-Z0-9]+)', debug)
        baseline.require(targets == ['RGBA16F'] * len(session),
                         f'{log}: expected one RGBA16F directive per shader build')


def client(root):
    reference = root / 'sodium-01/runs/valley/recording'
    ref_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(ref_archive)
    expected = {'maxFps': '260', 'enableVsync': 'false', 'renderDistance': '12',
                'simulationDistance': '8', 'fov': '70', 'fullscreen': 'true', 'guiScale': '3'}
    baseline.require(all(options.get(key) == value for key, value in expected.items())
                     and runtime['Window size'] == '2560x1440', 'Unexpected profile settings')
    for mode in MODES[1:]:
        variant = root / 'variants' / mode
        baseline.require(tree_manifest(variant / 'shaders') == (variant / 'pack.sha256').read_text(),
                         f'{variant}: shader tree differs from its manifest')
    for session in SESSIONS:
        verify_session(root, session)
        for batch in session:
            mode, _ = batch.rsplit('-', 1)
            pack_name = '' if mode == 'sodium' else pack(mode).name
            for name in PROFILES:
                run = root / batch / 'runs' / name
                recording = run / 'recording'
                archive, = recording.glob('*.zip')
                baseline.require(profile_settings(archive) == (runtime, options, pack_name or '(off)'),
                                 f'{archive}: mismatched runtime, settings or shaderpack')
                baseline.require(json.loads((run / 'preset.json').read_text()) == presets[name],
                                 f'{run}: preset differs')
                iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
                baseline.require(baseline.read_options((recording / 'iris.properties').read_text(), '=')
                                 == dict(iris, shaderPack=pack_name, enableShaders=str(bool(pack_name)).lower()),
                                 f'{run}: Iris configuration differs')
                for file in baseline.SHARED_FILES:
                    original = (reference / file).read_bytes()
                    if file == 'options.txt' and pack_name:
                        original = original.replace(b'key_iris.keybind.reload:key.keyboard.unknown',
                                                    b'key_iris.keybind.reload:key.keyboard.f9')
                    baseline.require((recording / file).read_bytes() == original,
                                     f'{run}: {file} differs')
                camera_mae = check_camera(recording, name)
                analysis = run / 'analysis'
                with baseline.TemporaryDirectory(dir=run) as temp:
                    generated = Path(temp) / 'analysis'
                    stats = baseline.convert(archive, generated)
                    if analysis.exists():
                        for file in ('client-ticking-raw.csv', 'frametimes.csv'):
                            baseline.require((analysis / file).read_bytes() == (generated / file).read_bytes(),
                                             f'{analysis}: {file} differs')
                    else:
                        generated.rename(analysis)
                baseline.require(9900 <= stats['profile_span_ms'] <= 10500,
                                 f'{run}: unexpected profile span')
                with ZipFile(archive) as profile:
                    breakdown = profile.read('client/profiling.txt').decode()
                shadow = re.search(r'shadows\(\d+/1\) - [\d.]+%/([\d.]+)%', breakdown)
                baseline.require(bool(shadow) == bool(pack_name), f'{run}: unexpected shadow section')
                yield {'batch': batch, 'scene': name, 'camera_patch_mae': f'{camera_mae:.3f}',
                       'shadow_cpu_root_percent': shadow[1] if shadow else '',
                       'archive': str(archive.relative_to(ROOT)),
                       'raw_csv': str((analysis / 'client-ticking-raw.csv').relative_to(ROOT)),
                       **{field: stats[field] for field in FIELDS}}


def gpu(root):
    cases = {'shadow': ('shadow-caster',), 'fog': ('fog-near', 'fog-clear', 'fog-dusk', 'fog-rain', 'fog-under')}
    for trial, scenes in cases.items():
        for run in ('01', '02'):
            source = root / f'{trial}-{run}.csv'
            device = (root / f'{trial}-{run}-device.txt').read_text()
            baseline.require('NVIDIA GeForce RTX 4080 SUPER' in device, f'{source}: unexpected GPU')
            if trial == 'shadow':
                for size in (1024, 768):
                    baseline.require(f'{size} map depths 0.800 0.800 0.250' in device,
                                     f'{source}: invalid depth probes at {size}')
            else:
                probes = re.findall(r'^([\w-]+) max sampled linear RGB delta (\d+\.\d+)$',
                                    device, re.MULTILINE)
                baseline.require(tuple(scene for scene, _ in probes) == scenes
                                 and max(float(delta) for _, delta in probes) <= 0.001,
                                 f'{source}: unexpected fog color probe')
            with source.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            baseline.require(len(rows) == 32 * len(scenes), f'{source}: unexpected query count')
            for index, scene in enumerate(scenes):
                timings = []
                for repeat, row in enumerate(rows[index * 32:(index + 1) * 32], 1):
                    order = 'off-first' if repeat % 2 else 'full-first'
                    before, after = int(row['off_ns']), int(row['full_ns'])
                    baseline.require(row['scene'] == scene and int(row['repeat']) == repeat
                                     and row['order'] == order and int(row['draws']) == 64
                                     and min(before, after) > 0, f'{source}: invalid timer row')
                    timings.append((before / 64e6, after / 64e6, (after - before) / 64e6))
                yield {'trial': trial, 'round': run, 'scene': scene, 'paired_batches': len(timings),
                       **dict(zip(('control_median_ms', 'trial_median_ms', 'paired_delta_median_ms'),
                                  (f'{median(group):.6f}' for group in zip(*timings))))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', choices=('client', 'gpu'))
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    rows = iter(client(root) if args.method == 'client' else gpu(root / 'gpu'))
    first = next(rows)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(first), lineterminator='\n')
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


if __name__ == '__main__':
    main()
