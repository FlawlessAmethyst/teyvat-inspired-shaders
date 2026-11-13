#!/usr/bin/env python3
"""Build labeled comparison sheets and index the reviewed native stills."""
import argparse
import csv
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PAIRS = {
    'valley': 'R1', 'rain': 'R4', 'ridges': 'R3', 'dusk': 'R5',
    'grove': 'R2', 'shallows': 'R7', 'night': 'R6', 'cave': None,
}
MATCHED_FILES = ('preset.json', 'options.txt', 'sodium-options.json',
                 'sodium-extra-options.json', 'dynamic_fps.json')


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def review(root):
    with (ROOT / 'evidence/task-17/references.csv').open(newline='') as file:
        references = {row['id']: row for row in csv.DictReader(file)}
    out = root / 'comparisons'
    out.mkdir(exist_ok=True)
    source_hashes = {}
    for name, reference_id in PAIRS.items():
        sodium = root / 'sodium' / name
        pack = root / 'pack' / name
        for filename in MATCHED_FILES:
            if (sodium / filename).read_bytes() != (pack / filename).read_bytes():
                raise RuntimeError(f'{name}: mode settings differ in {filename}')
        panels = []
        row = {'scene': name, 'reference_id': reference_id or '', 'video': '', 'video_sha256': '',
               'decoded_frame_zero_based': '', 'pts_seconds': '', 'reference_png': '', 'reference_sha256': ''}
        if reference_id:
            ref = references[reference_id]
            source = ROOT / ref['source']
            still = ROOT / ref['path']
            if source not in source_hashes:
                source_hashes[source] = sha256(source)
            if source_hashes[source] != ref['source_sha256'] or sha256(still) != ref['sha256']:
                raise RuntimeError(f'Source or decoded frame differs from TASK-04 for {reference_id}')
            timestamp = f'{float(ref["timestamp_seconds"]):.6f}'
            panels += ['-label', f'Genshin | {source.name} at {timestamp} s', str(still)]
            row.update(video=ref['source'], video_sha256=ref['source_sha256'],
                       decoded_frame_zero_based=ref['frame_number_zero_based'],
                       pts_seconds=timestamp, reference_png=ref['path'], reference_sha256=ref['sha256'])
        for mode, label in (('sodium', 'Sodium | shaders off'), ('pack', 'Iris | integrated shaderpack')):
            path = root / mode / name / 'native.png'
            settings = (path.parent / 'iris.properties').read_text().splitlines()
            enabled = mode == 'pack'
            selected = 'TASK-25-comparison' if enabled else ''
            if (f'enableShaders={str(enabled).lower()}' not in settings
                    or f'shaderPack={selected}' not in settings):
                raise RuntimeError(f'{name}: wrong shader settings in {mode} capture')
            panels += ['-label', label, str(path)]
            row[f'{mode}_png'] = path.relative_to(ROOT)
            row[f'{mode}_sha256'] = sha256(path)
        sheet = out / f'{name}.jpg'
        subprocess.run(['magick', 'montage', '-font', 'DejaVu-Sans', '-pointsize', '22',
                        *panels, '-tile', f'{len(panels) // 3}x1', '-geometry', '800x450+5+5',
                        '-background', '#171b22', '-fill', '#f3f3f3', '-quality', '92', str(sheet)],
                       check=True)
        row['comparison_jpg'] = sheet.relative_to(ROOT)
        yield row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='artifact root inside the repository')
    args = parser.parse_args()
    rows = list(review(args.root.resolve()))
    writer = csv.DictWriter(sys.stdout, fieldnames=rows[0], lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    main()
