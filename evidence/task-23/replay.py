#!/usr/bin/env python3
"""Compare TASK-22, a disposable spatial AA build, and Sodium in GenshinShaderDev."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('prototype_replay', ROOT / 'evidence/task-17/replay.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
scenes = harness.scenes
mc = scenes.mc
scenes.WORLD = harness.SOURCE_WORLD.with_name('TASK-23 Motion Scenes')
scenes.SPEC = {name: scenes.SPEC[name] for name in ('daylight', 'forest', 'open-water')}
scenes.SPEC['open-water'].update(yaw=150, pitch=12)
MOTION_KEYS = {'daylight': 'd', 'forest': 'w', 'open-water': 'd'}
MODES = ('control', 'spatial', 'sodium')


def pack(mode):
    return mc.GAME / 'shaderpacks' / f'TASK-23-{mode}'


def prepare(root):
    if any(path.exists() or path.is_symlink()
           for path in (root, scenes.WORLD, pack('control'), pack('spatial'))):
        raise RuntimeError('A TASK-23 artifact root, world or pack already exists')
    subprocess.run(['sha256sum', '--quiet', '-c', 'evidence/task-22/pack.sha256'], cwd=ROOT, check=True)
    subprocess.run(['diff', '-rq', 'artifacts/task-22/shaders', 'shaderpack/shaders'], cwd=ROOT, check=True)
    subprocess.run(['sha256sum', '--quiet', '-c', 'artifacts/task-22/source-world.sha256'], cwd=ROOT, check=True)
    harness.PACK = pack('control')
    harness.prepare(root)
    shutil.copytree(root / 'shaders', root / 'spatial-shaders')
    fragment = root / 'spatial-shaders/final.fsh'
    original = fragment.read_text()
    trial = original.replace('void main() {', '#include "/lib/spatial-aa.glsl"\n\nvoid main() {')
    trial = trial.replace('    gl_FragColor', '    sceneColor = filterSceneEdge(sceneUV, sceneColor);\n    gl_FragColor')
    if trial == original:
        raise RuntimeError('Could not stage spatial filter in the final pass')
    fragment.write_text(trial)
    shutil.copy2(HERE / 'spatial-aa.glsl', fragment.parent / 'lib/spatial-aa.glsl')
    shutil.copytree(root / 'spatial-shaders', pack('spatial') / 'shaders')
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    for slot, (name, preset) in enumerate(scenes.SPEC.items()):
        (functions / f'slot{slot}.mcfunction').write_text(
            f'scoreboard players set @s task03 {slot}\nfunction task03:{name}\n')
        source = functions / f'{name}.mcfunction'
        position = ' '.join(map(str, preset['position']))
        lines = source.read_text().splitlines()
        lines = [f"execute in minecraft:overworld run tp @s {position} {preset['yaw']} {preset['pitch']}"
                 if line.startswith('execute in minecraft:overworld run tp ') else line for line in lines]
        source.write_text('\n'.join(lines) + '\n')
    shutil.copy2(ROOT / 'artifacts/task-22/source-world.sha256', root / 'source-world.sha256')
    (root / 'presets.json').write_text(json.dumps(scenes.SPEC, indent=2) + '\n')


def configure(action, root):
    if mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    if action == 'prepare':
        prepare(root)
        return
    harness.PACK = pack('spatial' if action == 'spatial' else 'control')
    if action == 'restore':
        archive = root / 'world'
        if scenes.WORLD.exists() and archive.exists():
            raise RuntimeError('World archive already exists')
        harness.configure_mode('restore', root)
        if pack('spatial').is_dir():
            shutil.rmtree(pack('spatial'))
        if scenes.WORLD.is_dir():
            shutil.move(scenes.WORLD, archive)
    else:
        harness.configure_mode('sodium' if action == 'sodium' else 'prototype', root)


def motion(name, output):
    scenes.require_scene_world()
    output.mkdir(parents=True, exist_ok=True)
    wid = mc.focus()
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8', str(list(scenes.SPEC).index(name) + 1)])
    time.sleep(2)
    if f'TASK03_READY_{name}' not in log.read_text(errors='replace')[offset:]:
        raise RuntimeError('Missing preset acknowledgment')
    mc.press(['F1'])
    try:
        # Wait for a settled render after the teleport and HUD transition.
        time.sleep(2)
        if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
            raise RuntimeError('Minecraft lost focus before motion')
        video = (output / 'motion.mp4').resolve()
        if video.exists():
            raise RuntimeError(f'Recording already exists: {video}')
        # Use Spectacle's KWin window capture. A second activation stops and
        # flushes the same recording. The XWayland pixel readback tore.
        service = ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus',
                   '--object-path', '/org/freedesktop/DBus', '--method',
                   'org.freedesktop.DBus.NameHasOwner', 'org.kde.Spectacle']
        if mc.run(*service) != '(false,)':
            raise RuntimeError('Spectacle is already active; leave the existing session alone')
        args = ['spectacle', '-b', '-n', '-R', 'window', '-o', str(video)]
        with (output / 'spectacle.log').open('wb') as capture_log:
            with subprocess.Popen(args, stderr=capture_log, stdout=capture_log) as recorder:
                try:
                    time.sleep(1.5)
                    # KWin's window picker selects the active fullscreen game.
                    mc.run('xdotool', 'mousemove', '1280', '720', 'click', '1')
                    time.sleep(1.5)
                    if recorder.poll() is not None:
                        raise RuntimeError(f'Spectacle stopped early. See {capture_log.name}')
                    if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
                        raise RuntimeError('Minecraft lost focus during window selection')
                    subprocess.run([output.parents[1].resolve() / 'hold_key', MOTION_KEYS[name]],
                                   check=True, timeout=6)
                    time.sleep(1.25)
                    subprocess.run(args, stdout=capture_log, stderr=capture_log, check=True, timeout=6)
                    if recorder.wait(timeout=12) != 0 or not video.is_file():
                        raise RuntimeError(f'Spectacle did not save the video. See {capture_log.name}')
                finally:
                    if recorder.poll() is None:
                        recorder.terminate()
        if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
            raise RuntimeError('Minecraft lost focus during motion capture')
    finally:
        mc.press(['F1'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', *MODES, 'restore', 'capture', 'motion', 'profile'))
    parser.add_argument('path', type=Path)
    parser.add_argument('scene', nargs='?', choices=tuple(scenes.SPEC))
    args = parser.parse_args()
    if args.scene and args.action != 'motion':
        parser.error('The scene argument is only supported by motion')
    if args.action == 'capture':
        for name in scenes.SPEC:
            output = args.path / name
            scenes.replay(name, output, resume=False)
    elif args.action == 'motion':
        for name in ((args.scene,) if args.scene else scenes.SPEC):
            motion(name, args.path / name)
    elif args.action == 'profile':
        for name in ('forest', 'open-water'):
            scenes.replay(name, args.path / name, resume=False, profile=True)
    else:
        configure(args.action, args.path)


if __name__ == '__main__':
    main()
