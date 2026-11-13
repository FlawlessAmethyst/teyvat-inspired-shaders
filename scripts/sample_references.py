#!/usr/bin/env python3
"""Inventory immutable references and extract timestamped TASK-04 samples.
Run from any directory. Existing frames are reused only after hash validation.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/task-04'
EVIDENCE = ROOT / 'evidence/task-04'


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    originals = json.loads((ROOT / 'evidence/task-01/input-integrity.json').read_text())
    expected = {x['path']: x for x in originals if x['path'].startswith('references/')}
    paths = sorted(p for p in (ROOT / 'references').rglob('*') if p.is_file())
    assert {str(p.relative_to(ROOT)) for p in paths} == set(expected), 'Source set changed'
    sources, frames = [], []
    commands = []
    for p in paths:
        rel = str(p.relative_to(ROOT))
        sha = digest(p)
        assert sha == expected[rel]['sha256'], f'Original changed: {rel}'
        probe = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', rel]))
        stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        item = dict(path=rel, sha256=sha, bytes=p.stat().st_size, width=stream['width'], height=stream['height'], codec=stream['codec_name'])
        sources.append(item)
        if p.suffix != '.mp4':
            continue
        item.update(duration_seconds=float(probe['format']['duration']), average_frame_rate=stream['avg_frame_rate'], task=f'TASK-04-VID-{int(p.stem):03d}')
        folder = OUT / f'video-{p.stem}'
        folder.mkdir(exist_ok=True)
        cache = folder / 'frames.json'
        if cache.exists():
            entries = json.loads(cache.read_text())
            assert entries and all(e['source_sha256'] == sha and digest(ROOT / e['path']) == e['sha256'] for e in entries)
        else:
            times = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', rel]))['frames']
            stamps = [float(f['best_effort_timestamp_time']) for f in times]
            chosen = {0, len(stamps)-1}
            target = 5.0
            for i, t in enumerate(stamps):
                if t >= target:
                    chosen.add(i)
                    target += 5.0
            chosen = sorted(chosen)
            select = '+'.join(f'eq(n,{i})' for i in chosen)
            args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', '-i', rel, '-vf', f'select={select.replace(",", chr(92)+",")}', '-fps_mode', 'vfr', '-compression_level', '3', str(folder / 'frame-%03d.png')]
            commands.append(args)
            subprocess.run(args, cwd=ROOT, check=True)
            entries = []
            for j, i in enumerate(chosen, 1):
                dest = folder / f'frame-{j:03d}.png'
                entries.append(dict(source=rel, source_sha256=sha, frame_number_zero_based=i, timestamp_seconds=stamps[i], path=str(dest.relative_to(ROOT)), sha256=digest(dest)))
            cache.write_text(json.dumps(entries, indent=2)+'\n')
        frames.extend(entries)
        tiles = []
        for j, e in enumerate(entries, 1):
            tile = folder / f'tile-{j:03d}.jpg'
            subprocess.run(['magick', str(ROOT/e['path']), '-resize', '480x270', '-background', '#151515', '-fill', 'white', '-font', 'DejaVu-Sans', '-gravity', 'south', '-splice', '0x26', '-pointsize', '17', '-annotate', '+0+4', f"{p.stem} / {e['timestamp_seconds']:.3f}s / #{e['frame_number_zero_based']}", str(tile)], check=True)
            tiles.append(str(tile))
        subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '+3+3', '-background', '#303030', str(folder/'contact.jpg')], check=True)
        print(f"{item['task']}: {len(entries)} frames", flush=True)
    screenshots = [str(ROOT/s['path']) for s in sources if s['path'].endswith('.jpg')]
    subprocess.run(['magick', 'montage', *screenshots, '-set', 'label', '%f', '-font', 'DejaVu-Sans', '-pointsize', '18', '-label', '%f', '-geometry', '480x270+4+4', '-tile', '3x', '-background', '#303030', '-fill', 'white', str(OUT/'settings-contact.jpg')], check=True)
    for s in sources:
        assert digest(ROOT/s['path']) == s['sha256'], 'Post-run integrity failure'
    (EVIDENCE/'sources.json').write_text(json.dumps(sources, indent=2)+'\n')
    (EVIDENCE/'frames.json').write_text(json.dumps(frames, indent=2)+'\n')
    if commands:
        (EVIDENCE/'extraction_commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    (EVIDENCE/'versions.txt').write_text(run(['ffmpeg','-version'])+run(['magick','-version']))
    print(f'PASS: {len(sources)} immutable sources; {len(frames)} indexed frames')


if __name__ == '__main__':
    main()
