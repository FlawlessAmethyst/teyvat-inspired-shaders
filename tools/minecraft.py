#!/usr/bin/env python3
"""Instance-scoped desktop automation. No root, downloads, or global configuration."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import shutil
import zipfile
import hashlib

INSTANCE = Path.home() / '.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances/GenshinShaderDev'
GAME = INSTANCE / 'minecraft'
ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'artifacts/task-00'

def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()

def game_pids():
    result = set()
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            is_java = bool(args) and Path(os.fsdecode(args[0])).name == 'java'
            if is_java and (proc / 'cwd').resolve() == GAME.resolve():
                result.add(int(proc.name))
        except (OSError, IndexError):
            pass
    return result

def window():
    pids = game_pids()
    window_pids = set(pids)
    # X11 advertises Flatpak's namespace PID; map only verified game processes.
    for pid in pids:
        try:
            status = Path(f'/proc/{pid}/status').read_text()
            ns = re.search(r'^NSpid:\s+(.+)$', status, re.MULTILINE)
            if ns:
                window_pids.add(int(ns.group(1).split()[-1]))
        except OSError:
            pass
    # Refuse namespace-ID collisions with other Java processes.
    for proc in Path('/proc').glob('[0-9]*'):
        if int(proc.name) in pids:
            continue
        try:
            argv = (proc / 'cmdline').read_bytes().split(b'\0')
            if not argv or Path(os.fsdecode(argv[0])).name != 'java':
                continue
            ns = re.search(r'^NSpid:\s+(.+)$', (proc / 'status').read_text(), re.MULTILINE)
            if ns and int(ns.group(1).split()[-1]) in window_pids:
                raise RuntimeError('Ambiguous Flatpak PID mapping; close other Java applications first')
        except OSError:
            pass
    matches = []
    for line in run('wmctrl', '-lp').splitlines():
        parts = line.split(None, 4)
        if len(parts) == 5 and int(parts[2]) in window_pids and 'Minecraft' in parts[4]:
            matches.append(parts[0])
    if len(matches) != 1:
        raise RuntimeError(f'Expected one Minecraft window belonging to GenshinShaderDev; found {matches}')
    return matches[0]

def focus():
    wid = window()
    if int(run('xdotool', 'getactivewindow')) != int(wid, 16):
        run('xdotool', 'windowactivate', '--sync', wid)
    if int(run('xdotool', 'getactivewindow')) != int(wid, 16):
        raise RuntimeError('Minecraft did not receive focus')
    run('xdotool', 'windowfocus', '--sync', wid)
    time.sleep(0.25)
    return wid

def paths():
    if not (INSTANCE / 'mmc-pack.json').is_file() or not GAME.is_dir():
        raise RuntimeError(f'Instance missing: {INSTANCE}')
    result = {'instance': str(INSTANCE), 'minecraft': str(GAME)}
    for name in ('shaderpacks', 'logs', 'screenshots'):
        p = GAME / name
        p.mkdir(exist_ok=True)
        with tempfile.TemporaryFile(dir=p) as f:
            f.write(b'TASK-00 access probe')
            f.seek(0)
            assert f.read() == b'TASK-00 access probe'
        result[name] = str(p)
    print(json.dumps(result, indent=2))

def press(keys):
    # GLFW polls modifier/debug-key state separately from key callbacks.
    # Keep each chord held across several frames, release in reverse order.
    wid = window()
    for chord in keys:
        held = []
        try:
            for key in chord.split('+'):
                run('xdotool', 'keydown', '--window', wid, key)
                held.append(key)
                time.sleep(0.1)
        finally:
            for key in reversed(held):
                run('xdotool', 'keyup', '--window', wid, key)
                time.sleep(0.1)

def record(output, resume):
    output.mkdir(parents=True, exist_ok=False)
    before = set((GAME / 'debug/profiling').glob('*.zip'))
    wid = focus()
    if resume:
        press(['Escape'])
        time.sleep(1)
    run('maim', '-i', wid, str(output / 'before.png'))
    for rel in ('options.txt', 'config/iris.properties', 'config/sodium-options.json',
                'config/sodium-extra-options.json', 'config/dynamic_fps.json'):
        src = GAME / rel
        if src.exists():
            shutil.copy2(src, output / src.name)
    (output / 'mmc-pack.json').write_bytes((INSTANCE / 'mmc-pack.json').read_bytes())
    (output / 'mods.json').write_text(json.dumps({
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((GAME / 'mods').glob('*.jar'))}, indent=2) + '\n')
    press(['F3+L'])
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if int(run('xdotool', 'getactivewindow')) != int(wid, 16):
            raise RuntimeError('Focus lost during recording; discard this run')
        fresh = set((GAME / 'debug/profiling').glob('*.zip')) - before
        if len(fresh) > 1:
            raise RuntimeError('Multiple new metric archives; cannot attribute recording')
        if fresh:
            src = fresh.pop()
            try:
                with zipfile.ZipFile(src) as z:
                    if z.testzip() is not None:
                        raise RuntimeError('Invalid metric archive')
                shutil.copy2(src, output / src.name)
                run('maim', '-i', wid, str(output / 'after.png'))
                print(output.resolve())
                return
            except zipfile.BadZipFile:
                pass
        time.sleep(0.5)
    raise RuntimeError('No completed native performance ZIP within 30 seconds')

def stop(timeout):
    if not game_pids():
        print('Target instance is already stopped')
        return
    wid = focus()
    # WM_DELETE_WINDOW asks GLFW/Minecraft to shut down normally; never kill Java.
    run('wmctrl', '-ic', wid)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not game_pids():
            print('Target instance exited normally after window close request')
            return
        time.sleep(0.5)
    raise RuntimeError('Graceful stop timed out; game left running, no forced kill')

def launch(timeout):
    run('wmctrl', '-lp')  # Fail before launching when desktop access is unavailable.
    if not game_pids():
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        with (ARTIFACTS / 'launcher.log').open('a') as log:
            subprocess.Popen(['flatpak', 'run', 'org.prismlauncher.PrismLauncher', '--launch', INSTANCE.name], stdout=log, stderr=log, start_new_session=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            print(window())
            return
        except RuntimeError:
            time.sleep(1)
    raise RuntimeError('Timed out waiting for Minecraft window; inspect launcher.log and latest.log')

def collect():
    dest = ARTIFACTS / ('logs-' + time.strftime('%Y%m%d-%H%M%S'))
    dest.mkdir(parents=True, exist_ok=False)
    for src in (GAME / 'logs').glob('*.log'):
        data = src.read_text(errors='replace')
        data = re.sub(r'(?i)(--accessToken[, =]+)[^,\s\]]+', r'\1[REDACTED]', data)
        (dest / src.name).write_text(data)
    (dest / 'mmc-pack.json').write_bytes((INSTANCE / 'mmc-pack.json').read_bytes())
    print(dest)

def main():
    global ARTIFACTS
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifacts-dir', type=Path, default=ARTIFACTS)
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('paths', 'window', 'focus', 'logs', 'input-info'):
        sub.add_parser(name)
    sub.add_parser('launch').add_argument('--timeout', type=float, default=120)
    sub.add_parser('stop').add_argument('--timeout', type=float, default=60)
    sub.add_parser('key').add_argument('keys', nargs='+', help='xdotool key names, e.g. Escape or F2')
    c = sub.add_parser('click')
    c.add_argument('x', type=int)
    c.add_argument('y', type=int)
    sub.add_parser('screenshot').add_argument('output', type=Path)
    r = sub.add_parser('record')
    r.add_argument('output', type=Path)
    r.add_argument('--resume-paused', action='store_true')
    a = p.parse_args()
    ARTIFACTS = a.artifacts_dir
    if a.command == 'paths': paths()
    elif a.command == 'launch': launch(a.timeout)
    elif a.command == 'record': record(a.output, a.resume_paused)
    elif a.command == 'stop': stop(a.timeout)
    elif a.command == 'window': print(window())
    elif a.command == 'focus': print(focus())
    elif a.command == 'key':
        focus()
        press(a.keys)
        time.sleep(2)
    elif a.command == 'click':
        wid = focus()
        geometry = dict(line.split('=', 1) for line in run('xdotool', 'getwindowgeometry', '--shell', wid).splitlines())
        if not (0 <= a.x < int(geometry['WIDTH']) and 0 <= a.y < int(geometry['HEIGHT'])):
            raise RuntimeError('Click is outside the Minecraft window')
        run('xdotool', 'mousemove', '--window', wid, str(a.x), str(a.y))
        time.sleep(0.2)
        run('xdotool', 'click', '1')
        time.sleep(2)
    elif a.command == 'screenshot':
        wid = focus()
        a.output.parent.mkdir(parents=True, exist_ok=True)
        run('maim', '-i', wid, str(a.output))
        print(a.output.resolve())
    elif a.command == 'logs': collect()
    elif a.command == 'input-info':
        print(run('setxkbmap', '-query'))

if __name__ == '__main__':
    try: main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        if isinstance(e, subprocess.CalledProcessError): print(e.stderr, file=sys.stderr)
        sys.exit(1)
