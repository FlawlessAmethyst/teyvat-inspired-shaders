#!/usr/bin/env python3
"""Prepare and replay TASK-03 scenes in the single authorized Prism instance."""
import argparse
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import minecraft as mc

ROOT = Path(__file__).resolve().parents[1]
WORLD = mc.GAME / 'saves/TASK-03 Visual Scenes'
SPEC = json.loads((ROOT / 'scripts/scenes/presets.json').read_text())


def nbt_fields(raw):
    """Walk Java NBT, retaining payload offsets so unrelated tags stay byte exact."""
    fields = {}
    def string(pos):
        n = struct.unpack_from('>H', raw, pos)[0]
        return raw[pos+2:pos+2+n].decode(), pos+2+n
    def payload(kind, pos, path):
        start = pos
        sizes = {1:1, 2:2, 3:4, 4:8, 5:4, 6:8}
        if kind in sizes: pos += sizes[kind]
        elif kind == 8: _, pos = string(pos)
        elif kind in (7, 11, 12):
            n = struct.unpack_from('>i', raw, pos)[0]
            pos += 4 + n * {7:1, 11:4, 12:8}[kind]
        elif kind == 9:
            child = raw[pos]; n = struct.unpack_from('>i', raw, pos+1)[0]; pos += 5
            for i in range(n): pos = payload(child, pos, path+(str(i),))
        elif kind == 10:
            while raw[pos]:
                child = raw[pos]; name, pos = string(pos+1)
                pos = payload(child, pos, path+(name,))
            pos += 1
        else: raise ValueError(f'Unsupported NBT tag {kind}')
        fields[path] = (kind, start, pos)
        return pos
    kind = raw[0]; _, pos = string(1)
    assert payload(kind, pos, ()) == len(raw)
    return fields


def prepare():
    if mc.game_pids(): raise RuntimeError('Stop Minecraft before preparation')
    if WORLD.exists(): raise RuntimeError('Scene world exists; refusing overwrite')
    backup = ROOT / 'artifacts/task-03/preparation'
    backup.mkdir(parents=True, exist_ok=False)
    for rel in ('options.txt', 'config/iris.properties', 'config/sodium-options.json', 'config/sodium-extra-options.json'):
        shutil.copy2(mc.GAME / rel, backup / Path(rel).name)
    source = mc.GAME / 'saves/New World'
    shutil.copytree(source, WORLD, ignore=shutil.ignore_patterns('session.lock'))
    raw = gzip.decompress((WORLD / 'level.dat').read_bytes())
    fields = nbt_fields(raw)
    seed_tag = fields[('Data','WorldGenSettings','seed')]
    seed = struct.unpack_from('>q', raw, seed_tag[1])[0]
    edits = []
    for key, value in [('LevelName', struct.pack('>H', len(WORLD.name)) + WORLD.name.encode()), ('allowCommands', b'\x01')]:
        _, start, end = fields[('Data', key)]; edits.append((start, end, value))
    for start, end, value in sorted(edits, reverse=True): raw = raw[:start]+value+raw[end:]
    nbt_fields(raw)
    (WORLD / 'level.dat').write_bytes(gzip.compress(raw))
    shutil.copytree(ROOT / 'scripts/scenes/data', WORLD / 'datapacks/task03/data')
    shutil.copy2(ROOT / 'scripts/scenes/pack.mcmeta', WORLD / 'datapacks/task03/pack.mcmeta')
    options = mc.GAME / 'options.txt'
    settings = {'resourcePacks':'["vanilla","fabric","mod_resources"]', 'bobView':'false', 'pauseOnLostFocus':'false', 'renderDistance':'12', 'simulationDistance':'8', 'fov':'0.0', 'gamma':'0.5', 'enableVsync':'false', 'maxFps':'240', 'fullscreen':'true', 'guiScale':'3'}
    options.write_text('\n'.join(k+':'+settings.get(k,v) for k,v in (line.split(':',1) for line in options.read_text().splitlines()))+'\n')
    iris = mc.GAME / 'config/iris.properties'
    iris.write_text('\n'.join('enableShaders=false' if line.startswith('enableShaders=') else line for line in iris.read_text().splitlines())+'\n')
    extra = mc.GAME / 'config/sodium-extra-options.json'
    value = json.loads(extra.read_text())
    value['extra_settings']['show_fps'] = False
    value['extra_settings']['show_f_p_s_extended'] = False
    extra.write_text(json.dumps(value, indent=2)+'\n')
    (backup / 'world.json').write_text(json.dumps({'source':str(source), 'world':str(WORLD), 'seed':seed, 'source_level_sha256':hashlib.sha256((source/'level.dat').read_bytes()).hexdigest()}, indent=2)+'\n')
    print((backup / 'world.json').read_text())


def require_scene_world():
    # Java FileLock and POSIX record locks conflict on Linux. Refuse a closed map.
    with (WORLD / 'session.lock').open('r+b') as lock:
        try:
            fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
    raise RuntimeError('The dedicated TASK-03 world is not open; refusing input')


def replay(name, output, resume, profile=False):
    require_scene_world()
    output.mkdir(parents=True, exist_ok=False)
    wid = mc.focus()
    if resume: mc.press(['Escape'])
    log = mc.GAME / 'logs/latest.log'
    offset = log.stat().st_size
    mc.press(['8'])
    time.sleep(3)
    key = '9' if name == 'build' else str(list(SPEC).index(name)+1)
    mc.press([key])
    time.sleep(3)
    if 'TASK03_READY_'+name not in log.read_text(errors='replace')[offset:]:
        raise RuntimeError('Scene acknowledgment absent; inspect screen/world/datapack, no capture accepted')
    if name == 'build':
        mc.run('maim', '-i', wid, str(output/'build.png'))
        return
    # HUD must be visible before invocation; F1 hides hand, crosshair, chat and HUD.
    mc.press(['F1'])
    try:
        for _ in range(SPEC[name]['warmup_seconds']):
            if int(mc.run('xdotool','getactivewindow')) != int(wid,16): raise RuntimeError('Focus lost')
            time.sleep(1)
        (output/'preset.json').write_text(json.dumps(SPEC[name],indent=2)+'\n')
        if profile:
            mc.record(output/'recording', resume=False)
            return
        before = set((mc.GAME/'screenshots').glob('*.png'))
        mc.press(['F2'])
        time.sleep(1)
        fresh = set((mc.GAME/'screenshots').glob('*.png')) - before
        if len(fresh) != 1: raise RuntimeError('Expected exactly one native screenshot')
        shutil.copy2(fresh.pop(), output/'native.png')
        header = (output/'native.png').read_bytes()[:24]
        if struct.unpack('>II', header[16:24]) != (2560, 1440):
            raise RuntimeError('Baseline capture requires 2560x1440; inspect display settings')
        for rel in ('options.txt','config/iris.properties','config/sodium-options.json',
                    'config/sodium-extra-options.json','config/dynamic_fps.json'):
            shutil.copy2(mc.GAME/rel, output/Path(rel).name)
        print(output)
    finally: mc.press(['F1'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('prepare')
    r=sub.add_parser('capture'); r.add_argument('scene',choices=['build']+list(SPEC)); r.add_argument('output',type=Path); r.add_argument('--resume-paused',action='store_true')
    perf = sub.add_parser('profile', help='record client timings after each scene warm-up')
    perf.add_argument('output', type=Path)
    perf.add_argument('scenes', nargs='+', choices=list(SPEC))
    a=p.parse_args()
    if a.action=='prepare': prepare()
    elif a.action == 'capture': replay(a.scene,a.output,a.resume_paused)
    else:
        if len(set(a.scenes)) != len(a.scenes):
            p.error('Each scene must appear once per profile batch')
        a.output.mkdir(parents=True, exist_ok=False)
        for name in a.scenes:
            replay(name, a.output/name, resume=False, profile=True)
if __name__=='__main__': main()
