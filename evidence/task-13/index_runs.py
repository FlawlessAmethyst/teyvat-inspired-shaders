#!/usr/bin/env python3
"""Validate and index the matched TASK-13 client-loop captures."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'task-11'))
from summarize import summarize

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', required=True, type=Path)
    summarize(parser.parse_args().artifacts_dir, 'TASK-13',
              ('sunlight-01', 'ambient-01', 'ambient-02', 'sunlight-02'),
              ('forest', 'cave', 'night'))
