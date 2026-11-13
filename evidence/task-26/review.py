#!/usr/bin/env python3
"""Verify the matrix and extract client-loop samples without converting GPU utilization."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from zipfile import ZipFile

from replay import comparison, pack
from variants import MODES, ROOT, SCENES, tree_manifest

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import FIELDS, baseline, profile_settings

RUNS = (
    ('sodium-01',),
    tuple(f'{mode}-01' for mode in MODES[1:]),
    tuple(f'{mode}-02' for mode in reversed(MODES[1:])),
    ('sodium-02',),
)
CAMERA_PATCH = {
    'valley': '180x90+1130+640',
    'rain': '180x90+1130+640',
    'grove': '220x135+1100+1160',
    'shallows': '220x115+1100+520',
    'cave': '200x150+280+520',
}


def check_log(path, batches):
    latest = path.read_text()
    events = []
    if batches[0].startswith('sodium-'):
        events.append('Shaders are disabled because enableShaders is set to false')
    for batch in batches:
        mode = batch.rsplit('-', 1)[0]
        if mode != 'sodium':
            events.append(f'Using shaderpack: {pack(mode).name}\n')
        for scene in SCENES[mode]:
            events.extend((f'[CHAT] TASK03_READY_{scene}', 'Stopped tick profiling'))
    events.append('All dimensions are saved')
    tail = latest
    for event in events:
        _, found, tail = tail.partition(event)
        baseline.require(found, f'{path}: missing or out of order: {event.strip()}')
    expected_scenes = [scene for batch in batches for scene in SCENES[batch.rsplit('-', 1)[0]]]
    observed_scenes = re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest)
    # The copied fixture can build the water basin before its first warm-up.
    observed_scenes = [scene for scene in observed_scenes if scene != 'build']
    baseline.require(observed_scenes == expected_scenes, f'{path}: unexpected preset sequence')
    baseline.require(latest.count('Stopped tick profiling') == len(expected_scenes),
                     f'{path}: unexpected profile count')
    baseline.require('Iris 1.8.14-beta.1+mc1.21.1' in latest and 'Sodium 0.8.13' in latest,
                     f'{path}: missing Iris or Sodium runtime version')
    baseline.require(not re.search(
        r'^.*(?:(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl)'
        r'|failed to (?:compile|link)|ShaderCompileException|OpenGL error).*$',
        latest, re.IGNORECASE | re.MULTILINE), f'{path}: shader-related error')


def check_camera(recording, scene):
    for name in ('before.png', 'after.png'):
        with (recording / name).open('rb') as stream:
            header = stream.read(24)
        baseline.require(header[:8] == b'\x89PNG\r\n\x1a\n'
                         and struct.unpack('>II', header[16:24]) == (2560, 1440),
                         f'{recording}: incorrect {name} capture')
    frames = [subprocess.check_output([
        'magick', str(recording / name), '-crop', CAMERA_PATCH[scene],
        '+repage', '-alpha', 'off', '-depth', '8', 'rgb:-',
    ]) for name in ('before.png', 'after.png')]
    return sum(abs(a - b) for a, b in zip(*frames, strict=True)) / len(frames[0])


def review(root):
    reference = root / 'sodium-01/runs/valley/recording'
    ref_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(ref_archive)
    expected = {'maxFps': '260', 'enableVsync': 'false', 'renderDistance': '12',
                'simulationDistance': '8', 'fov': '70', 'fullscreen': 'true', 'guiScale': '3'}
    baseline.require(all(options.get(key) == value for key, value in expected.items())
                     and runtime['Window size'] == '2560x1440', 'Unexpected profile settings')
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    control = root / 'variants/full/shaders'
    expected_manifest = (ROOT / 'evidence/task-25/fog-pack.sha256').read_text()
    baseline.require(tree_manifest(control) == expected_manifest.replace('  shaderpack/shaders/', '  '),
                     f'{control}: full build differs from TASK-25')
    for mode in MODES[1:]:
        snapshot = root / 'variants' / mode
        baseline.require(tree_manifest(snapshot / 'shaders') ==
                         (snapshot / 'pack.sha256').read_text(), f'{snapshot}: variant changed')
    for session in RUNS:
        log, = (root / session[0]).glob('logs-*/latest.log')
        check_log(log, session)
        if not session[0].startswith('sodium-'):
            debug = log.with_name('debug.log').read_text()
            targets = re.findall(r'Render target settings for colortex0: .*requestedFormat=([A-Z0-9]+)', debug)
            baseline.require(targets == ['RGBA16F'] * len(session),
                             f'{log}: expected one RGBA16F directive per shader build')
        for batch in session:
            mode = batch.rsplit('-', 1)[0]
            pack_name = '' if mode == 'sodium' else pack(mode).name
            for scene in SCENES[mode]:
                run = root / batch / 'runs' / scene
                recording = run / 'recording'
                archive, = recording.glob('*.zip')
                baseline.require(profile_settings(archive) == (runtime, options, pack_name or '(off)'),
                                 f'{archive}: runtime, video settings or shaderpack differs')
                baseline.require(json.loads((run / 'preset.json').read_text()) ==
                                 comparison.PRESETS[scene], f'{run}: preset differs')
                baseline.require(baseline.read_options(
                    (recording / 'iris.properties').read_text(), '=') ==
                    dict(iris, shaderPack=pack_name, enableShaders=str(bool(pack_name)).lower()),
                    f'{run}: Iris configuration differs')
                for name in baseline.SHARED_FILES:
                    value = (recording / name).read_bytes()
                    original = (reference / name).read_bytes()
                    if name == 'options.txt' and pack_name:
                        original = original.replace(b'key_iris.keybind.reload:key.keyboard.unknown',
                                                    b'key_iris.keybind.reload:key.keyboard.f9')
                    baseline.require(value == original, f'{run}: {name} differs')
                camera_mae = check_camera(recording, scene)
                analysis = run / 'analysis'
                with baseline.TemporaryDirectory(dir=run) as temp:
                    generated = Path(temp) / 'analysis'
                    stats = baseline.convert(archive, generated)
                    if analysis.exists():
                        for name in ('client-ticking-raw.csv', 'frametimes.csv'):
                            baseline.require((analysis / name).read_bytes() ==
                                             (generated / name).read_bytes(), f'{run}: {name} differs')
                    else:
                        generated.rename(analysis)
                baseline.require(9900 <= stats['profile_span_ms'] <= 10500,
                                 f'{run}: unexpected profile span')
                with ZipFile(archive) as profile:
                    utilization = profile.read('client/metrics/gpu.csv')
                    breakdown = profile.read('client/profiling.txt').decode()
                shadow = re.search(r'shadows\(\d+/1\) - [\d.]+%/([\d.]+)%', breakdown)
                expects_shadow = mode not in ('sodium', 'shadowless', 'terrain-vanilla')
                baseline.require(bool(shadow) == expects_shadow,
                                 f'{run}: unexpected shadow section in CPU profile')
                (analysis / 'gpu-utilization-raw.csv').write_bytes(utilization)
                yield {'batch': batch, 'scene': scene, 'camera_patch_mae': f'{camera_mae:.3f}',
                       'shadow_cpu_root_percent': shadow[1] if shadow else '',
                       'archive': str(archive.relative_to(ROOT)),
                       'raw_csv': str((analysis / 'client-ticking-raw.csv').relative_to(ROOT)),
                       'raw_gpu_utilization_sha256': hashlib.sha256(utilization).hexdigest(),
                       **{field: stats[field] for field in FIELDS}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    rows = iter(review(parser.parse_args().root.resolve()))
    first = next(rows)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(first), lineterminator='\n')
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


if __name__ == '__main__':
    main()
