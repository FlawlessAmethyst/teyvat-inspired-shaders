#!/usr/bin/env python3
"""Validate Minecraft 1.21.1 native client loop timings and export milliseconds.

These are instrumented CPU render-loop durations, not GPU/presentation timings.
Never read server/metrics/ticking.csv as frame times.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics
import zipfile


def read_metrics(archive):
    with zipfile.ZipFile(archive) as z:
        raw = z.read('client/metrics/ticking.csv')
        profile = z.read('client/profiling.txt').decode()
    reader = csv.DictReader(io.StringIO(raw.decode()))
    if reader.fieldnames != ['@tick', 'ticktime']:
        raise ValueError('Unsupported client metric schema')
    rows = [(int(r['@tick']), float(r['ticktime'])) for r in reader]
    if not rows or any(not math.isfinite(t) or t <= 0 for _, t in rows):
        raise ValueError('Missing, nonfinite or nonpositive timings')
    if [i for i, _ in rows] != list(range(rows[0][0], rows[0][0] + len(rows))):
        raise ValueError('Duplicate or non-contiguous samples')
    span = re.search(r'^Time span: (\d+) ms$', profile, re.M)
    ticks = re.search(r'^Tick span: (\d+) ticks$', profile, re.M)
    if not span or not ticks or int(ticks[1]) != len(rows) or int(span[1]) <= 0:
        raise ValueError('Profiler span and sample count disagree')
    if not re.search(r'updateDisplay\(' + str(len(rows)) + r'/', profile):
        raise ValueError('Cannot establish one display update per client sample')
    return raw, rows, int(span[1])


def convert(archive, output):
    raw, rows, span_ms = read_metrics(archive)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'client-ticking-raw.csv').write_bytes(raw)
    ms = [t / 1_000_000 for _, t in rows]
    ordered = sorted(ms)
    def percentile(p):
        return ordered[math.ceil(p * len(ordered)) - 1]
    with (output / 'frametimes.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['client_frame', 'client_loop_ns', 'client_loop_ms'])
        writer.writerows((i, ns, ns / 1_000_000) for i, ns in rows)
    summary = {
        'source': str(archive.resolve()),
        'source_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'metric': 'instrumented client render-loop CPU duration; not presentation latency',
        'samples': len(rows), 'profile_span_ms': span_ms,
        'profile_frames_per_second': len(rows) * 1000 / span_ms,
        'mean_client_loop_ms': statistics.mean(ms),
        'p50_client_loop_ms': percentile(0.50),
        'p95_client_loop_ms': percentile(0.95),
        'p99_client_loop_ms': percentile(0.99),
        'max_client_loop_ms': max(ms),
        'percentile_method': 'nearest rank; all samples retained',
        'limitations': 'Approximately 10 seconds with unquantified profiler overhead. See the run record for scene, frame cap and other capture conditions.'
    }
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    print(json.dumps(convert(a.archive, a.output), indent=2))
