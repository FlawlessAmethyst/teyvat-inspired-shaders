#!/usr/bin/env python3
"""TASK-02 entry point; reuses the instance-scoped Minecraft toolkit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import minecraft

if __name__ == '__main__':
    minecraft.ARTIFACTS = minecraft.ROOT / 'artifacts/task-02'
    try:
        minecraft.main()
    except (RuntimeError, OSError, minecraft.subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
