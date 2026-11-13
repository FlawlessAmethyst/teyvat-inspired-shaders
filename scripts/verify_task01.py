#!/usr/bin/env python3
"""Read-only TASK-01 source-layout, preservation and Git-ignore checks."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    manifest = json.loads((ROOT / 'evidence/task-01/input-integrity.json').read_text())
    for row in manifest:
        path = ROOT / row['path']
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        assert path.stat().st_size == row['bytes'] and digest == row['sha256'], path
    references = {str(p.relative_to(ROOT)) for p in (ROOT / 'references').rglob('*') if p.is_file()}
    assert references == {r['path'] for r in manifest if r['path'].startswith('references/')}
    print(f'PASS: {len(manifest)} original inputs unchanged, including {len(references)} references')
    for name in ['shaderpack', 'scripts', 'docs', 'evidence']:
        assert (ROOT / name).is_dir(), name
    for name in ['STATUS', 'DECISIONS', 'TEST_LOG', 'CODEX_TASKS', 'SCOPE_OVERRIDES']:
        assert (ROOT / f'docs/{name}.md').is_file(), name
    assert sorted(p.name for p in (ROOT / 'shaderpack').iterdir()) == ['README.md']
    print('PASS: required layout and ledgers exist; shader implementation has not started')
    assert git('rev-parse', '--is-inside-work-tree') == 'true'
    for path in [*sorted(references), 'artifacts/task-00/title.png', 'evidence/task-02/capture.png', 'tools/__pycache__/test.pyc']:
        assert git('check-ignore', '--', path) == path, path
    candidates = git('ls-files', '--others', '--exclude-standard').splitlines()
    for path in candidates:
        assert (ROOT / path).suffix in {'.md', '.py', '.json', '.txt', ''} or path == '.gitignore', path
    for path in ['evidence/README.md', 'evidence/task-01/input-integrity.json', 'evidence/task-01/verification.txt']:
        result = subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '--', path], capture_output=True)
        assert result.returncode == 1, path
    assert not git('ls-files', '--stage'), 'Unexpected staged or tracked files in initial repository'
    print('PASS: Git initialized; references/captures/caches ignored; small TASK-01 evidence eligible')
    print('PASS: initial repository has no staged/committed files; eligible files are source/text only')
    print('NOT TESTED: Minecraft runtime, GLSL compilation, visual quality or performance (outside TASK-01)')


if __name__ == '__main__':
    main()
