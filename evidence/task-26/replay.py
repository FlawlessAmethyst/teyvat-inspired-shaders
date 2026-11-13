#!/usr/bin/env python3
"""Replay TASK-26 profiles against disposable builds in GenshinShaderDev."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import time

from variants import ROOT, MODES, SCENES, build, tree_manifest

spec = importlib.util.spec_from_file_location('comparison_replay', ROOT / 'evidence/task-25/replay.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
harness, scenes, mc = comparison.harness, comparison.scenes, comparison.mc
harness.SOURCE_WORLD = ROOT / 'artifacts/task-25-fog-tuning/world'


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-26-{mode}'


def prepare(root):
    if any(path.exists() or path.is_symlink()
           for path in (root, scenes.WORLD, *(pack(mode) for mode in MODES[1:]))):
        raise RuntimeError('A TASK-26 output path, test world or temporary pack already exists')
    if not (harness.SOURCE_WORLD / 'level.dat').is_file():
        raise RuntimeError('Retain the TASK-25 fog-tuning world before profiling')
    build(root)
    (root / 'source-world.sha256').write_text(tree_manifest(harness.SOURCE_WORLD))
    harness.PACK = pack('full')
    # The inherited prepare expects the root to be new.
    stage = root / 'instance-setup'
    harness.prepare(stage, root / 'variants/full/shaders')
    shutil.move(stage / 'before', root / 'before')
    shutil.rmtree(stage)
    for mode in MODES[2:]:
        shaders = root / 'variants' / mode / 'shaders'
        shutil.copytree(shaders, pack(mode) / 'shaders')
    shutil.copy2(ROOT / 'artifacts/task-25-fog-tuning/pack/world-list.png',
                 root / 'world-list-reference.png')
    (root / 'presets.json').write_text(json.dumps(comparison.PRESETS, indent=2) + '\n')


def configure(root, mode):
    selected = 'full' if mode == 'sodium' else mode
    harness.PACK = verified_pack(root, selected)
    harness.configure_mode('sodium' if mode == 'sodium' else 'prototype', root)
    if mode != 'sodium':
        options = mc.GAME / 'options.txt'
        options.write_text(harness.configure.settings(
            options.read_text(), {'key_iris.keybind.reload': 'key.keyboard.f9'}, ':'))


def verified_pack(root, mode):
    installed = pack(mode)
    expected = root / 'variants' / mode / 'pack.sha256'
    if tree_manifest(installed / 'shaders') != expected.read_text():
        raise RuntimeError(f'{installed}: installed shader tree differs from its manifest')
    return installed


def switch(root, mode):
    if mode == 'sodium':
        raise RuntimeError('Use a fresh client for the Sodium baseline')
    scenes.require_scene_world()
    shader_pack = verified_pack(root, mode)
    iris = mc.GAME / 'config/iris.properties'
    settings = harness.configure.settings(iris.read_text(), {'shaderPack': shader_pack.name}, '=')
    replacement = iris.with_suffix('.task26-tmp')
    replacement.write_text(settings)
    replacement.replace(iris)
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.focus()
    mc.press(['F9'])
    for _ in range(20):
        with log.open('rb') as stream:
            stream.seek(offset)
            fresh = stream.read().decode(errors='replace')
        if f'Using shaderpack: {shader_pack.name}\n' in fresh:
            print(f'Reloaded {shader_pack.name}')
            return
        time.sleep(1)
    raise RuntimeError(f'Iris did not acknowledge {shader_pack.name}')


def restore(root):
    archive = root / 'world'
    if scenes.WORLD.exists() and archive.exists():
        raise RuntimeError('World archive already exists')
    harness.PACK = pack('full')
    harness.configure_mode('restore', root)
    if scenes.WORLD.exists():
        shutil.move(scenes.WORLD, archive)
    for mode in MODES[2:]:
        if pack(mode).is_dir():
            shutil.rmtree(pack(mode))
    if (root / 'source-world.sha256').read_text() != tree_manifest(harness.SOURCE_WORLD):
        raise RuntimeError('The TASK-25 source world differs from the preflight manifest')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'configure', 'switch', 'profile', 'restore'))
    parser.add_argument('path', type=Path)
    parser.add_argument('mode', nargs='?', choices=MODES)
    args = parser.parse_args()
    uses_mode = args.action in ('configure', 'switch', 'profile')
    if uses_mode != bool(args.mode):
        parser.error('Only configure, switch and profile take a required mode')
    if args.action == 'profile':
        for name in SCENES[args.mode]:
            scenes.replay(name, args.path / name, resume=False, profile=True)
        return
    if args.action == 'switch':
        switch(args.path, args.mode)
        return
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if args.action == 'prepare':
        prepare(args.path)
    elif args.action == 'configure':
        configure(args.path, args.mode)
    else:
        restore(args.path)


if __name__ == '__main__':
    main()
