#!/usr/bin/env python3
"""Verify TASK-23 runtime evidence and produce compact CSV indices."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from statistics import median
import struct
import subprocess
import sys

from replay import MODES, ROOT, pack, scenes

sys.path.insert(0, str(ROOT / 'evidence/task-11'))
from summarize import baseline, FIELDS, profile_settings

BATCHES = ('control-01', 'spatial-01', 'sodium-01', 'sodium-02', 'spatial-02', 'control-02')
PROFILES = ('forest', 'open-water')
SIZE = (2560, 1440)


def write_rows(rows):
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


def check_png(path):
    with path.open('rb') as file:
        header = file.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', header[16:24]) == SIZE, path


def check_settings(directory, reference, iris, filenames):
    for name in filenames:
        assert (directory / name).read_bytes() == (reference / name).read_bytes(), directory / name
    assert baseline.read_options((directory / 'iris.properties').read_text(), '=') == iris, directory


def runs(root):
    reference = ROOT / 'artifacts/task-22/sodium-01/runs/night/recording'
    ref_archive, = reference.glob('*.zip')
    runtime, options, _ = profile_settings(ref_archive)
    iris = baseline.read_options((reference / 'iris.properties').read_text(), '=')
    assert json.loads((root / 'presets.json').read_text()) == scenes.SPEC
    rows = []
    for batch in BATCHES:
        mode = batch.split('-')[0]
        name = '' if mode == 'sodium' else pack(mode).name
        directory = root / batch
        logs, = directory.glob('logs-*')
        log = logs / 'latest.log'
        latest = log.read_text()
        expected = f'Using shaderpack: {name}' if name else 'Shaders are disabled'
        assert expected in latest and 'All dimensions are saved' in latest, log
        assert latest.count('Stopped tick profiling') == len(PROFILES), log
        assert not re.search(r'(?:/ERROR|/FATAL)\].*(?:shader|iris|pipeline|glsl)'
                             r'|failed to (?:compile|link)|ShaderCompileException|OpenGL error',
                             latest, re.IGNORECASE), log
        if name:
            debug = (logs / 'debug.log').read_text()
            assert re.search(r'Render target settings for colortex0: .*requestedFormat=RGBA16F\b', debug), logs
        ready = re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest)
        assert ready[-len(PROFILES):] == list(PROFILES), (log, ready)
        expected_iris = dict(iris, shaderPack=name, enableShaders=str(bool(name)).lower())
        if batch.endswith('-01'):
            for scene in scenes.SPEC:
                capture = directory / scene
                assert scene in ready, (log, ready)
                assert json.loads((capture / 'preset.json').read_text()) == scenes.SPEC[scene], capture
                check_png(capture / 'native.png')
                check_settings(capture, reference, expected_iris, baseline.SHARED_FILES[:4])
        for scene in PROFILES:
            run = directory / 'runs' / scene
            recording = run / 'recording'
            assert json.loads((run / 'preset.json').read_text()) == scenes.SPEC[scene], run
            check_settings(recording, reference, expected_iris, baseline.SHARED_FILES)
            for filename in ('before.png', 'after.png'):
                check_png(recording / filename)
            # Sample static terrain, clear of animated clouds and water.
            crop = {'forest': '420x180+1050+1220', 'open-water': '160x120+0+1260'}[scene]
            images = [subprocess.check_output(['magick', recording / filename, '-crop', crop,
                                              '+repage', '-alpha', 'off', '-depth', '8', 'rgb:-'])
                      for filename in ('before.png', 'after.png')]
            drift = sum(abs(a - b) for a, b in zip(*images, strict=True)) / len(images[0])
            assert drift <= 2.0, (recording, drift)
            archive, = recording.glob('*.zip')
            assert profile_settings(archive) == (runtime, options, name or '(off)'), archive
            analysis = run / 'analysis'
            if analysis.is_dir():
                with baseline.TemporaryDirectory() as temp:
                    generated = Path(temp) / 'analysis'
                    stats = baseline.convert(archive, generated)
                    for filename in ('client-ticking-raw.csv', 'frametimes.csv'):
                        assert (analysis / filename).read_bytes() == (generated / filename).read_bytes(), run
            else:
                stats = baseline.convert(archive, analysis)
            assert 9900 <= stats['profile_span_ms'] <= 10500, run
            raw = analysis / 'client-ticking-raw.csv'
            row = {'batch': batch, 'scene': scene, 'archive': archive.relative_to(ROOT),
                   'raw_csv': raw.relative_to(ROOT), 'raw_csv_sha256': hashlib.sha256(raw.read_bytes()).hexdigest()}
            row.update({field: stats[field] for field in FIELDS})
            rows.append(row)
    return rows


def gpu(root):
    rows = []
    for scene in scenes.SPEC:
        for repeat in ('01', '02'):
            path = root / f'gpu-{scene}-{repeat}.csv'
            device = path.with_name(path.stem + '-device.txt').read_text().strip()
            with path.open(newline='') as file:
                samples = list(csv.DictReader(file))
            assert len(samples) == 32 and 'RTX 4080 SUPER' in device, path
            assert all(sample['draws'] == '64' for sample in samples), path
            assert [sample['order'] for sample in samples] == ['control-first', 'spatial-first'] * 16, path
            control = [int(sample['control_ns']) / 64e6 for sample in samples]
            spatial = [int(sample['spatial_ns']) / 64e6 for sample in samples]
            deltas = [b - a for a, b in zip(control, spatial, strict=True)]
            rows.append({'scene': scene, 'run': repeat, 'pairs': len(samples),
                         'median_control_ms': f'{median(control):.6f}',
                         'median_spatial_ms': f'{median(spatial):.6f}',
                         'median_paired_delta_ms': f'{median(deltas):.6f}',
                         'device': device, 'raw_csv': path.relative_to(ROOT)})
    return rows


def video(root):
    rows = []
    for mode in MODES:
        batch = 'sodium-motion' if mode == 'sodium' else f'{mode}-02'
        directory = root / batch
        logs, = directory.glob('logs-*')
        latest = (logs / 'latest.log').read_text()
        expected = 'Shaders are disabled' if mode == 'sodium' else f'Using shaderpack: {pack(mode).name}'
        assert expected in latest and 'All dimensions are saved' in latest, logs
        ready = re.findall(r'\[CHAT\] TASK03_READY_([a-z-]+)', latest)
        assert ready[:len(scenes.SPEC)] == list(scenes.SPEC), (logs, ready)
        for scene in scenes.SPEC:
            path = directory / scene / 'motion.mp4'
            result = json.loads(subprocess.check_output([
                'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,codec_name,nb_read_frames:format=duration', '-of', 'json', path,
            ]))
            stream, = result['streams']
            assert (stream['width'], stream['height']) == SIZE, path
            duration = float(result['format']['duration'])
            frames = int(stream['nb_read_frames'])
            assert 4 <= duration <= 9 and frames / duration >= 25, (path, frames, duration)
            # Reject the black bands seen in the first X11 trial. These fixtures
            # are daylight exterior scenes with content across every row.
            proxy = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path,
                                             '-vf', 'scale=80:45:flags=area', '-pix_fmt', 'gray',
                                             '-fps_mode', 'passthrough', '-f', 'rawvideo', '-'])
            assert len(proxy) == frames * 80 * 45, path
            assert all(max(proxy[i:i+80]) > 8 for i in range(0, len(proxy), 80)), path
            # Lower-frame luminance changes when terrain passes the camera.
            # This catches captures where the input events never moved the player.
            area = 80 * 45
            first = proxy[area // 2:area]
            end = proxy[-area // 2:]
            motion_delta = sum(abs(a - b) for a, b in zip(first, end, strict=True)) / len(first)
            assert motion_delta > 2.0, (path, motion_delta)
            rows.append({'mode': mode, 'scene': scene, 'frames': frames,
                         'duration_seconds': f'{duration:.3f}', 'frames_per_second': f'{frames / duration:.2f}',
                         'codec': stream['codec_name'], 'terrain_delta_codes': f'{motion_delta:.3f}',
                         'recording': path.relative_to(ROOT)})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=('runs', 'gpu', 'video'))
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    actions = {'runs': runs, 'gpu': gpu, 'video': video}
    write_rows(actions[args.kind](args.root.resolve()))
