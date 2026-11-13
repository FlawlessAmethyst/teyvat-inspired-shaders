#!/usr/bin/env python3
"""Render the TASK-04 inventory from verified metadata and reviewed scene notes."""
import json
from pathlib import Path
from sample_references import ROOT

sources = json.loads((ROOT/'evidence/task-04/sources.json').read_text())
frames = json.loads((ROOT/'evidence/task-04/frames.json').read_text())
notes = json.loads((ROOT/'evidence/task-04/scene_notes.json').read_text())
settings = ['Graphics-quality preset menu', 'Resolution/window mode menu', 'Brightness calibration with town/interior previews', 'Frame-rate menu', 'Vertical-sync menu', 'Render-scale menu', 'Shadow-quality menu', 'Post-processing-quality menu', 'Effects-quality menu', 'Environment-detail menu', 'Anti-aliasing menu', 'Volumetric-fog toggle', 'Reflections toggle', 'Motion-blur menu', 'Bloom toggle', 'Crowd-density menu', 'Co-op teammate effects menu', 'Subsurface-scattering menu', 'Anisotropic-filtering menu']

def link(path, label):
    return f'[{label}](../../{path})'

text = '''# Genshin reference inventory — TASK-04

Status: **DONE**, 2026-11-12. This is an inventory and sampled scene catalog.
Visual target selection, technique attribution and comparison criteria belong to TASK-05 onward.

## Inputs and sampling method

All 30 supplied sources are accounted for: 19 settings JPEGs and 11 gameplay MP4s.
Source bytes and SHA-256 hashes match the TASK-01 input manifest before and after
extraction. Originals were never rewritten. Metadata: [sources.json](../../evidence/task-04/sources.json).

FFprobe enumerates decoded video frame presentation timestamps. FFmpeg selects
frame zero, the first frame at or after each five-second mark, and the final frame.
Timestamps below are actual source presentation times in seconds, not requested
seek times or inferred frame-number/FPS values. Variable frame pacing is preserved
in the index. Full-resolution 1920×1080 PNGs are decoded from compressed video;
PNG storage adds no further lossy compression, but cannot restore source detail.
Contact sheets are reduced JPEG navigation previews, not color-measurement masters.
No grading, cropping, sharpening or HUD/watermark removal was applied to PNGs.

Every video contact sheet and all 19 settings thumbnails were visually reviewed.
Descriptions identify content visible at sampled times; ranges group samples and
are not frame-exact cut boundaries. Sampling does not certify every intervening
frame or short-lived event. No additional samples were needed to represent the
scene categories visible in these sheets. No full-motion/temporal-effect analysis
was performed. Review the original clips if later tasks need animation evidence.

## Settings screenshots

These Russian-language menus document available controls, not implementation
proof, measured costs, or authorization to build a player-facing settings system.
Their relationship to the settings used during gameplay recording is unverified.

[Settings contact sheet](../../artifacts/task-04/settings-contact.jpg).

| Source | Dimensions | Observed screen |
| --- | --- | --- |
'''
for s in sources:
    if s['path'].endswith('.jpg'):
        text += f"| {link(s['path'],Path(s['path']).name)} | {s['width']}×{s['height']} | {settings[int(Path(s['path']).stem)-1]} |\n"
text += '\n## Gameplay inventory and per-video subtasks\n\nAll subtasks below are **DONE**: metadata, extraction, visual sheet review and scene indexing.\n\n| Subtask / source | Duration (s) | Samples | Contact sheet |\n| --- | ---: | ---: | --- |\n'
for s in sources:
    if not s['path'].endswith('.mp4'): continue
    ident=Path(s['path']).stem
    rows=[f for f in frames if f['source']==s['path']]
    text+=f"| {s['task']} / {link(s['path'],ident+'.mp4')} | {s['duration_seconds']:.6f} | {len(rows)} | {link('artifacts/task-04/video-'+ident+'/contact.jpg','view')} |\n"
text += '\n## Observed scene groups\n\nEach row links one representative PNG; the [complete frame index](frame_index.md)\nlinks every sampled frame with its exact source timestamp and decoded frame number.\n\n| Source | Sample group (seconds, approximate) | Observed content | Representative (actual time) |\n| --- | --- | --- | --- |\n'
for ident, groups in sorted(notes.items()):
    rows=[f for f in frames if Path(f['source']).stem == ident]
    for start,end,description in groups:
        representative = {('05',45):50, ('10',0):10, ('10',30):40, ('11',40):45}.get((ident,start), (start+end)/2)
        row=min(rows,key=lambda r:abs(r['timestamp_seconds']-representative))
        text+=f"| {link(row['source'],ident+'.mp4')} | {start}–{end} | {description} | {link(row['path'],format(row['timestamp_seconds'],'.3f')+' s')} |\n"
text+='''
## Coverage and limits

Observed sample coverage includes green daylight valleys and cliffs (01–03),
coasts/islands and distant water (02, 04), rain/overcast (02), mist-filled mountains
(03), pink/purple vegetation and blue-lit landscapes (04–05), lush grassland (06), desert/oasis shallows (07), warm lakeshore light (08),
a sunset-to-dusk canyon sequence (09), luminous purple-blue ruins (10), and a
moonlit snowy village with warm lamps (11). This is a navigation catalog, not a ranking of visual signatures.

- Settings screenshot 03 includes a small dark-interior preview; that is not a
  full-resolution gameplay cave/interior sequence.
- No controlled fixed-camera full day/sunset/night comparison, isolated graphics-option
  A/B pair, known exposure calibration, or performance recording is supplied.
- Time of day, geographic names and rendering algorithms are not inferred solely
  from color. Blue lighting can be environmental; darkness alone does not prove night.
- Characters, authored geometry/textures, HUD text, watermark and particles appear
  in the footage. These remain in the references and do not expand shaderpack scope.
- Five-second still sampling cannot characterize temporal stability, wind cadence,
  cloud motion, rain density or water animation. Compression and unknown recording
  settings limit fine-detail/color judgments. Brief events between samples may be missed.
- Original media and generated images remain local/ignored. Include both
  `references/` and `artifacts/task-04/` in the developer handoff alongside the small
  checked-in-eligible JSON/Markdown indexes. No redistribution rights are inferred.

## Reproduce, validate and resume

From the repository root, run:

```sh
python3 scripts/sample_references.py
python3 scripts/verify_references.py
python3 scripts/index_references.py
```

Requires installed FFmpeg/FFprobe, ImageMagick and DejaVu Sans; versions are recorded
in [versions.txt](../../evidence/task-04/versions.txt). Completed video caches are
reused after source/frame hash checks. If extraction was interrupted before a
video's `frames.json` was written, move that incomplete generated `video-NN/`
directory aside before retrying; originals are never overwrite targets.
Scene notes are human-reviewed input in
[scene_notes.json](../../evidence/task-04/scene_notes.json); adding/changing source
media requires a deliberate new inventory, not bypassing the integrity assertions.
Exact extraction argument arrays: [extraction_commands.json](../../evidence/task-04/extraction_commands.json).
Validation: [verification.txt](../../evidence/task-04/verification.txt).

TASK-04 is complete. At its completion, the next task was TASK-05.
See [STATUS.md](../STATUS.md) for current progress and the next task to request.
'''
(ROOT/'docs/research/reference_index.md').write_text(text)
text='# Generated frame index — TASK-04\n\nGenerated by `python3 scripts/index_references.py`. Source PTS timestamps in seconds;\nframe numbers are zero-based decoded-frame indices. Hashes: [frames.json](../../evidence/task-04/frames.json).\nSee [reference inventory](reference_index.md) for scene notes and sampling limits.\n\n| Source | Timestamp (s) | Frame number | Full-resolution PNG |\n| --- | ---: | ---: | --- |\n'
for f in frames:
    text+=f"| {link(f['source'],Path(f['source']).name)} | {f['timestamp_seconds']:.6f} | {f['frame_number_zero_based']} | {link(f['path'],Path(f['path']).parent.name+'/'+Path(f['path']).name)} |\n"
(ROOT/'docs/research/frame_index.md').write_text(text)
print(f'Generated inventory and index for {len(sources)} sources / {len(frames)} frames.')
