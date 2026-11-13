#!/usr/bin/env python3
"""Compare a native diagnostic capture to the expected single sRGB encode."""
import argparse
from pathlib import Path
import subprocess

WIDTH = 2560
HEIGHT = 1440
ROWS = ((240, 'SDR gray', (1.0, 1.0, 1.0)),
        (720, 'HDR gray', (4.0, 4.0, 4.0)),
        (1200, 'HDR green', (0.44, 4.0, 0.88)))


def encode(value):
    value = max(0.0, min(value, 1.0))
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def model(x, channels):
    color = [1.48 * x * channel for channel in channels]
    luminance = sum(channel * weight for channel, weight in zip(color, (0.2126, 0.7152, 0.0722)))
    darkest = min(color)
    boost = min(0.24, 0.70 * darkest / max(luminance - darkest, 1e-6))
    color = [channel + (channel - luminance) * boost for channel in color]
    peak = max(color)
    excess = max(peak - 0.52, 0)
    mapped_peak = 0.52 + 0.48 * (excess / (0.48 + excess))
    return [round(255 * encode(channel * mapped_peak / max(peak, 0.52))) for channel in color]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native_png', type=Path)
    args = parser.parse_args()
    size = subprocess.check_output(['magick', 'identify', '-format', '%wx%h', args.native_png],
                                   text=True)
    if size != f'{WIDTH}x{HEIGHT}':
        raise ValueError(f'Unexpected diagnostic screenshot size: {size}')
    pixels = subprocess.check_output(['magick', args.native_png, '-depth', '8', 'rgb:-'])
    for row, label, channels in ROWS:
        start = 3 * row * WIDTH
        actual = [tuple(pixels[start + 3 * x:start + 3 * x + 3]) for x in range(WIDTH)]
        expected = [model(x / (WIDTH - 1), channels) for x in range(WIDTH)]
        error = max(abs(a - b) for pixel, target in zip(actual, expected)
                    for a, b in zip(pixel, target))
        if error > 1 or actual[0] != (0, 0, 0) or max(actual[-1]) == 255:
            raise ValueError(f'{label}: output departs from the grade or clips')
        if any(a > b for left, right in zip(actual, actual[1:]) for a, b in zip(left, right)):
            raise ValueError(f'{label}: nonmonotonic output')
        print(f'{label}: {len(set(actual))} distinct RGB codes; max model error {error}; '
              f'black {actual[0]}, midpoint {actual[WIDTH // 2]}, endpoint {actual[-1]}')


if __name__ == '__main__':
    main()
