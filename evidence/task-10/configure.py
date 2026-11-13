#!/usr/bin/env python3
"""Back up, configure and restore only GenshinShaderDev for TASK-10."""
import argparse
import filecmp
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import minecraft as mc

FILES = ('options.txt', 'config/iris.properties', 'config/sodium-options.json',
         'config/sodium-extra-options.json', 'config/dynamic_fps.json')
PACK = mc.GAME / 'shaderpacks/TASK-10-neutral'


def settings(text, values, separator):
    for key, value in values.items():
        text, count = re.subn(rf'^{re.escape(key + separator)}.*$', key + separator + value,
                              text, flags=re.MULTILINE)
        if count != 1:
            raise RuntimeError(f'Expected one {key} setting, got {count}')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts-dir', type=Path, default=ROOT / 'artifacts/task-10')
    parser.add_argument('--shaders-dir', type=Path, default=ROOT / 'shaderpack/shaders',
                        help='Shader source directory to install during prepare')
    parser.add_argument('action', choices=('prepare', 'sodium', 'neutral', 'restore'))
    args = parser.parse_args()
    action = args.action
    before = args.artifacts_dir / 'before'
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev first')
    if action == 'prepare':
        if PACK.exists():
            raise RuntimeError(f'Temporary shaderpack path already exists: {PACK}')
        before.mkdir(parents=True, exist_ok=False)
        for relative in FILES:
            shutil.copy2(mc.GAME / relative, before / Path(relative).name)
        shutil.copytree(args.shaders_dir, PACK / 'shaders')
        return

    if action == 'restore':
        if not all((before / Path(relative).name).is_file() for relative in FILES):
            raise RuntimeError('Backup is incomplete')
        for relative in FILES:
            shutil.copy2(before / Path(relative).name, mc.GAME / relative)
        if not all(filecmp.cmp(before / Path(rel).name, mc.GAME / rel, shallow=False)
                   for rel in FILES):
            raise RuntimeError('Restoration failed verification')
        if PACK.is_dir():
            shutil.rmtree(PACK)
        print('Restored five byte-identical settings files and removed temporary pack')
        return

    if not PACK.is_dir():
        raise RuntimeError('Run prepare first')
    options = settings((before / 'options.txt').read_text(),
                       {'maxFps': '260', 'enableVsync': 'false'}, ':')
    enabled = action == 'neutral'
    iris = settings((before / 'iris.properties').read_text(),
                    {'enableShaders': str(enabled).lower(),
                     'shaderPack': PACK.name if enabled else ''}, '=')
    for relative in FILES[2:]:
        shutil.copy2(before / Path(relative).name, mc.GAME / relative)
    (mc.GAME / 'options.txt').write_text(options)
    (mc.GAME / 'config/iris.properties').write_text(iris)
    print(f'Configured {action}')


if __name__ == '__main__':
    main()
