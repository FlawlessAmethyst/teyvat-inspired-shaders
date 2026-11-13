#!/usr/bin/env python3
"""Capture a removable vanilla snow swatch via the test world's temporary slot 9."""
import argparse
from pathlib import Path
import shutil
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scenes import mc, require_scene_world


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    output = parser.parse_args().output
    require_scene_world()
    output.mkdir(parents=True, exist_ok=False)
    window = mc.focus()
    screenshots = mc.GAME / 'screenshots'
    log = mc.GAME / 'logs/latest.log'

    def expect(marker, offset):
        if marker not in log.read_text(errors='replace')[offset:]:
            raise RuntimeError(f'Missing test-world acknowledgment: {marker}')

    # The preceding cave capture arms placement. Slot 8 then leaves the cave
    # and rearms slot 9, where the same trigger removes the swatch.
    offset = log.stat().st_size
    mc.press(['9'])
    time.sleep(2)
    try:
        expect('TASK11_SNOW_PLACED_24_6', offset)
        mc.press(['F1'])
        try:
            for _ in range(20):
                if int(mc.run('xdotool', 'getactivewindow')) != int(window, 16):
                    raise RuntimeError('Focus lost')
                time.sleep(1)
            before = set(screenshots.glob('*.png'))
            mc.press(['F2'])
            time.sleep(1)
            capture, = set(screenshots.glob('*.png')) - before
            shutil.copy2(capture, output / 'native.png')
            header = (output / 'native.png').read_bytes()[:24]
            if struct.unpack('>II', header[16:24]) != (2560, 1440):
                raise RuntimeError('Unexpected snow capture dimensions')
        finally:
            mc.press(['F1'])
    finally:
        offset = log.stat().st_size
        mc.press(['8'])
        time.sleep(1)
        mc.press(['9'])
        time.sleep(2)
        expect('TASK11_SNOW_REMOVED_24_6', offset)
        mc.press(['8'])


if __name__ == '__main__':
    main()
