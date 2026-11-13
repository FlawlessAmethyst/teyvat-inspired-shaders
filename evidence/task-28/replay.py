#!/usr/bin/env python3
"""Replay runtime smoke checks in a disposable GenshinShaderDev world."""
import argparse
import csv
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_replay(task):
    spec = importlib.util.spec_from_file_location(f'task_{task}', ROOT / f'evidence/task-{task}/replay.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


water = load_replay(19)
harness = water.harness
scenes = harness.scenes
mc = scenes.mc
ORIGINAL = harness.SOURCE_WORLD
harness.SOURCE_WORLD = ROOT / 'artifacts/task-22/world'
scenes.WORLD = mc.GAME / 'saves/TASK-28 Runtime Regression'
harness.PACK = mc.GAME / 'shaderpacks/TASK-28-regression'
LOG = mc.GAME / 'logs/latest.log'
SHOTS = mc.GAME / 'screenshots'
DIMENSIONS = json.loads((ROOT / 'evidence/task-22/presets.json').read_text())
VALLEY = json.loads((ROOT / 'evidence/task-25/presets.json').read_text())['valley']
GROUPS = (
    tuple(scenes.SPEC),
    ('lamps', 'unlit', 'nether', 'end', 'return', 'shore-motion', 'valley'),
    ('water-fixture', 'underwater', 'underside', 'waterline', 'cave-entry', 'rain-on', 'rain-off'),
)
PRESETS = scenes.SPEC | DIMENSIONS | {
    'return': scenes.SPEC['daylight'],
    'shore-motion': dict(scenes.SPEC['open-water'], yaw=150, pitch=12),
    'valley': VALLEY,
    'cave-entry': dict(scenes.SPEC['cave'], yaw=0, position=[969.5, 184, 1020.5]),
}
for name, preset in water.preset_specs():
    if name in ('underwater', 'underside'):
        PRESETS[name] = preset
PRESETS['waterline'] = dict(PRESETS['underwater'], position=[1027.5, 179, 1037.5])
SOURCES = (ORIGINAL, harness.SOURCE_WORLD)


def manifest(path):
    return subprocess.check_output(
        ['sha256sum', '--', *sorted(str(p.relative_to(path)) for p in path.rglob('*') if p.is_file())],
        cwd=path, text=True,
    )


def install_functions():
    functions = scenes.WORLD / 'datapacks/task03/data/task03/function'
    shutil.copy2(ROOT / 'evidence/task-19/fixture.mcfunction', functions / 'task28-basin.mcfunction')
    (functions / 'task28-water-fixture.mcfunction').write_text(
        'execute in minecraft:overworld run tp @s 1025.5 184 1037.5 -90 5\n'
        'forceload add 1007 1028 1047 1046\n'
        'schedule function task03:task28-build-basin 3s replace\n'
    )
    (functions / 'task28-build-basin.mcfunction').write_text(
        'execute as @a at @s run function task03:task28-basin\n'
        'forceload remove 1007 1028 1047 1046\n'
    )
    (functions / 'slot7.mcfunction').write_text(
        'scoreboard players set @s task03 7\n'
        'tellraw @s [{"text":"TASK28_POSITION "},{"nbt":"Pos","entity":"@s"},'
        '{"text":" ROTATION "},{"nbt":"Rotation","entity":"@s"}]\n'
    )
    (functions / 'slot8.mcfunction').write_text(
        'scoreboard players set @s task03 8\n'
        'scoreboard players add #group task03 1\n'
        'execute if score #group task03 matches 3.. run scoreboard players set #group task03 0\n'
        'tellraw @s [{"text":"TASK28_GROUP_"},{"score":{"name":"#group","objective":"task03"}}]\n'
    )
    with (functions / 'load.mcfunction').open('a') as load:
        load.write('scoreboard players set #group task03 0\n')
    with (functions / 'tick.mcfunction').open('a') as tick:
        tick.write(
            'execute as @a[tag=task28_water] at @s anchored eyes positioned ^ ^ ^ '
            'if block ~ ~ ~ minecraft:water unless score #water task03 matches 1 '
            'run function task03:task28-water-in\n'
            'execute as @a[tag=task28_water] at @s anchored eyes positioned ^ ^ ^ '
            'unless block ~ ~ ~ minecraft:water unless score #water task03 matches 0 '
            'run function task03:task28-water-out\n'
        )
    for state, score in (('in', 1), ('out', 0)):
        (functions / f'task28-water-{state}.mcfunction').write_text(
            f'scoreboard players set #water task03 {score}\n'
            f'tellraw @s {{"text":"TASK28_EYES_{state.upper()}"}}\n'
        )

    for slot in range(7):
        dispatch = [f'scoreboard players set @s task03 {slot}']
        for group, names in enumerate(GROUPS):
            name = names[slot]
            dispatch.append(f'execute if score #group task03 matches {group} run function task03:task28-{name}')
            if name == 'water-fixture':
                continue
            acknowledgment = f'tellraw @s {{"text":"TASK28_READY_{name}"}}'
            if name.startswith('rain-'):
                state = 'rain' if name == 'rain-on' else 'clear'
                lines = [f'weather {state} 1000000',
                         'execute store result score #time task03 run time query daytime',
                         f'tellraw @s [{{"text":"TASK28_READY_{name}_"}},'
                         '{"score":{"name":"#time","objective":"task03"}}]']
            else:
                preset = PRESETS[name]
                dim = preset.get('dimension', 'minecraft:overworld')
                position = ' '.join(map(str, preset['position']))
                lines = ['tag @s remove task28_water', 'gamemode creative @s', 'effect clear @s', 'clear @s',
                         f"execute in {dim} run tp @s {position} {preset['yaw']} {preset['pitch']}"]
                if dim == 'minecraft:overworld':
                    lines += ['gamerule doDaylightCycle false', 'gamerule doWeatherCycle false',
                              f"time set {preset['time']}", f"weather {preset['weather']} 1000000"]
                if name == 'cave-entry':
                    lines += ['fill 968 183 1018 971 183 1022 minecraft:stone']
                if name == 'waterline':
                    lines += ['scoreboard players set #water task03 -1', 'tag @s add task28_water']
                lines += [f'execute at @s if dimension {dim} run {acknowledgment}']
            (functions / f'task28-{name}.mcfunction').write_text('\n'.join(lines) + '\n')
        (functions / f'slot{slot}.mcfunction').write_text('\n'.join(dispatch) + '\n')


def prepare(root):
    for path in (root, scenes.WORLD, harness.PACK):
        if path.exists() or path.is_symlink():
            raise RuntimeError(f'Refusing to overwrite {path}')
    subprocess.run(['sha256sum', '--quiet', '-c', 'evidence/task-25/fog-pack.sha256'], cwd=ROOT, check=True)
    shaders = ROOT / 'shaderpack/shaders'
    subprocess.run(['diff', '-rq', shaders, ROOT / 'artifacts/task-25-fog-tuning/shaders'], check=True)
    sources = [manifest(source) for source in SOURCES]
    harness.prepare(root)
    install_functions()
    for name, value in zip(('original-world', 'source-world'), sources, strict=True):
        (root / f'{name}.sha256').write_text(value)
    (root / 'presets.json').write_text(json.dumps(PRESETS, indent=2) + '\n')
    harness.configure_mode('prototype', root)
    subprocess.run(['diff', '-rq', root / 'shaders', harness.PACK / 'shaders'], check=True)
    for rel in harness.configure.FILES:
        dest = root / 'settings'
        dest.mkdir(exist_ok=True)
        shutil.copy2(mc.GAME / rel, dest / Path(rel).name)


def restore(root):
    archive = root / 'world'
    if scenes.WORLD.exists() and archive.exists():
        raise RuntimeError('World archive already exists')
    harness.configure_mode('restore', root)
    if scenes.WORLD.is_dir():
        shutil.move(scenes.WORLD, archive)
    for name, source in zip(('original-world', 'source-world'), SOURCES, strict=True):
        if manifest(source) != (root / f'{name}.sha256').read_text():
            raise RuntimeError(f'Changed source world: {source}')
    scenes.WORLD = archive
    if (archive / 'session.lock').exists():
        try:
            scenes.require_scene_world()
        except RuntimeError as error:
            if not str(error).startswith('The dedicated TASK-03 world is not open'):
                raise
        else:
            raise RuntimeError('Archived world still holds a session lock')
    if harness.PACK.exists():
        raise RuntimeError('Temporary shaderpack was not removed')
    print('Verified unchanged source worlds and archived the disposable world')


def new_log(offset):
    return LOG.read_bytes()[offset:].decode(errors='replace')


def expect(offset, marker, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if marker in new_log(offset):
            return
        time.sleep(0.25)
    raise RuntimeError(f'Missing fresh log marker: {marker}')


def focus_check(wid):
    if int(mc.run('xdotool', 'getactivewindow')) != int(wid, 16):
        raise RuntimeError('GenshinShaderDev lost focus')


def select(group, name, reset=True):
    offset = LOG.stat().st_size
    if reset:
        mc.press(['8'])
    mc.press([str(GROUPS[group].index(name) + 1)])
    marker = 'TASK03_READY_build' if name == 'water-fixture' else f'TASK28_READY_{name}'
    if name.startswith('rain-'):
        marker += '_6000'
    expect(offset, marker, 24)
    return offset


def advance(group):
    offset = LOG.stat().st_size
    mc.press(['8', '9'])
    expect(offset, f'TASK28_GROUP_{group}')


@contextmanager
def hidden_hud(wid):
    focus_check(wid)
    mc.press(['F1'])
    try:
        yield
    finally:
        focus_check(wid)
        mc.press(['F1'])


def save_shot(source, dest):
    with source.open('rb') as file:
        header = file.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (2560, 1440):
        raise RuntimeError(f'Expected native 2560x1440 image: {source}')
    shutil.move(source, dest)


def still(dest, wid):
    before = set(SHOTS.glob('*.png'))
    with hidden_hud(wid):
        mc.press(['F2'])
        expect_shots = time.monotonic() + 6
        while time.monotonic() < expect_shots:
            fresh = set(SHOTS.glob('*.png')) - before
            if len(fresh) == 1:
                source = fresh.pop()
                time.sleep(0.5)
                save_shot(source, dest)
                return
            time.sleep(0.25)
    raise RuntimeError(f'No single native screenshot for {dest}')


def capture(root, wid, group, name):
    offset = select(group, name)
    time.sleep(8)
    still(root / f'{name}.png', wid)
    print(f'Captured {name}', flush=True)
    return offset


def weather(root, wid):
    output = root / 'weather'
    output.mkdir()
    before = set(SHOTS.glob('*.png'))
    with hidden_hud(wid), (output / 'timeline.csv').open('w') as timing:
        writer = csv.writer(timing)
        writer.writerow(('frame', 'seconds', 'event'))
        start = time.monotonic()
        for frame in range(42):
            time.sleep(max(0, start + frame * 0.5 - time.monotonic()))
            focus_check(wid)
            event = {4: 'rain-on', 22: 'rain-off'}.get(frame, '')
            if event:
                select(2, event, reset=False)
            elapsed = time.monotonic() - start
            mc.press(['F2'])
            writer.writerow((frame, f'{elapsed:.3f}', event))
        time.sleep(1)
    fresh = sorted(set(SHOTS.glob('*.png')) - before)
    if len(fresh) != 42:
        raise RuntimeError(f'Expected 42 weather frames, got {len(fresh)}')
    for number, source in enumerate(fresh):
        save_shot(source, output / f'{number:03}.png')
    print('Captured rain onset and clearing', flush=True)


def record(root, wid, name, action):
    service = ('gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus',
               '--object-path', '/org/freedesktop/DBus', '--method',
               'org.freedesktop.DBus.NameHasOwner', 'org.kde.Spectacle')
    if mc.run(*service) != '(false,)':
        raise RuntimeError('Spectacle is already active')
    video = (root / f'{name}.mp4').resolve()
    args = ['spectacle', '-b', '-n', '-R', 'window', '-o', str(video)]
    with hidden_hud(wid), (root / f'{name}-spectacle.log').open('wb') as output:
        with subprocess.Popen(args, stderr=output, stdout=output) as recorder:
            try:
                time.sleep(1.5)
                mc.run('xdotool', 'mousemove', '1280', '720', 'click', '1')
                time.sleep(1.5)
                focus_check(wid)
                if recorder.poll() is not None:
                    raise RuntimeError(f'Spectacle ended early for {name}')
                action()
                time.sleep(1.25)
                focus_check(wid)
                subprocess.run(args, stdout=output, stderr=output, check=True, timeout=8)
                if recorder.wait(timeout=15) or not video.is_file():
                    raise RuntimeError(f'Spectacle did not save {video}')
            finally:
                if recorder.poll() is None:
                    recorder.terminate()
    print(f'Recorded {name}', flush=True)


def motion(root, wid, group, preset, name, action):
    offset = select(group, preset)
    time.sleep(2)

    def move():
        focus_check(wid)
        subprocess.run([root.parent / 'motion-input', action], timeout=9, check=True)

    record(root, wid, name, move)
    position_offset = LOG.stat().st_size
    mc.press(['8'])
    expect(position_offset, 'TASK28_POSITION')
    if preset == 'waterline':
        states = [line.rsplit('_', 1)[-1] for line in new_log(offset).splitlines() if '[CHAT] TASK28_EYES_' in line]
        if states != ['IN', 'OUT', 'IN']:
            raise RuntimeError(f'Unexpected waterline crossing sequence: {states}')


def run(root):
    scenes.require_scene_world()
    wid = mc.focus()
    stills = root / 'stills'
    clips = root / 'clips'
    stills.mkdir()
    clips.mkdir()
    for name in GROUPS[0]:
        capture(stills, wid, 0, name)
    motion(clips, wid, 0, 'daylight', 'stone-strafe', 'd')
    motion(clips, wid, 0, 'forest', 'forest-walk', 'w')
    motion(clips, wid, 0, 'forest', 'forest-turn', 'turn')
    advance(1)
    for name in ('lamps', 'unlit', 'nether', 'end', 'return'):
        capture(stills, wid, 1, name)
    motion(clips, wid, 1, 'shore-motion', 'shore-strafe', 'd')
    select(1, 'valley')
    time.sleep(8)
    advance(2)
    weather(root, wid)
    select(2, 'water-fixture')
    for name in ('underwater', 'underside'):
        capture(stills, wid, 2, name)
    motion(clips, wid, 2, 'waterline', 'waterline', 'swim')
    motion(clips, wid, 2, 'cave-entry', 'cave-entry', 'w')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'restore'))
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    action = {'prepare': prepare, 'run': run, 'restore': restore}[args.action]
    if args.action != 'run' and mc.game_pids():
        raise RuntimeError('Stop GenshinShaderDev before changing instance files')
    action(args.path.resolve())


if __name__ == '__main__':
    main()
