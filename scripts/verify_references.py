#!/usr/bin/env python3
"""Validate TASK-04 coverage, source preservation and generated PNG metadata."""
import json
from pathlib import Path
import struct
from sample_references import ROOT, digest

sources = json.loads((ROOT/'evidence/task-04/sources.json').read_text())
frames = json.loads((ROOT/'evidence/task-04/frames.json').read_text())
originals = json.loads((ROOT/'evidence/task-01/input-integrity.json').read_text())
checked = 0
for item in originals:
    if item['path'] in {'tools/minecraft.py', 'docs/minecraft-environment.md'}:
        # Authorized later edits: TASK-02 toolkit; post-TASK-06 historical Git
        # wording correction. Original media remains checked below without exceptions.
        continue
    assert digest(ROOT/item['path']) == item['sha256'], item['path']
    checked += 1
assert {s['path'] for s in sources} == {str(p.relative_to(ROOT)) for p in (ROOT/'references').rglob('*') if p.is_file()}
for s in sources:
    assert digest(ROOT/s['path']) == s['sha256']
    if not s['path'].endswith('.mp4'):
        continue
    rows = [f for f in frames if f['source'] == s['path']]
    ts = [f['timestamp_seconds'] for f in rows]
    assert ts == sorted(set(ts)) and ts[0] == 0
    assert max(b-a for a,b in zip(ts,ts[1:])) < 5.1
    assert 0 <= s['duration_seconds']-ts[-1] < .1
    for f in rows:
        p = ROOT/f['path']
        assert p.is_relative_to(ROOT/'artifacts/task-04')
        assert f['source_sha256'] == s['sha256'] and digest(p) == f['sha256']
        with p.open('rb') as image:
            header = image.read(24)
        assert header[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II',header[16:24]) == (s['width'],s['height'])
print(f'PASS: {checked} original inputs unchanged; {len(sources)} sources accounted for; {len(frames)} full-resolution PNG hashes/dimensions verified; all videos sampled start/interior/end with gaps <5.1s.')

notes = json.loads((ROOT/'evidence/task-04/scene_notes.json').read_text())
assert set(notes) == {Path(s['path']).stem for s in sources if s['path'].endswith('.mp4')}
for f in frames:
    assert any(start <= f['timestamp_seconds'] <= end + .1 for start,end,_ in notes[Path(f['source']).stem]), f
import re
links = 0
for name in ('reference_index.md','frame_index.md'):
    p = ROOT/'docs/research'/name
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        assert (p.parent/target).resolve().exists(), target
        links += 1
print(f'PASS: all 11 scene-note groups cover every sampled frame; {links} Markdown local links resolve.')
