"""Verify pinned TASK-07 research provenance and local handoff links."""
import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
data=json.loads((root/'evidence/task-07/sources.json').read_text())
n=0
for repo in data['repositories']:
 p=root/repo['local_path']
 assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()==repo['revision']
 assert not subprocess.check_output(['git','-C',str(p),'status','--porcelain'],text=True).strip()
 for f in repo['files']:
  assert hashlib.sha256((p/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
  assert f['url']==f"{repo['url']}/blob/{repo['revision']}/{f['path']}"
  n+=1
print(f'PASS: {len(data["repositories"])} pinned clean upstream clones, {n} file hashes and permalinks')
doc=root/'docs/research/implementation_patterns.md'
s=doc.read_text()
for i in range(1,8):
 assert f'| S{i} ' in s
assert 'Approach A' in s and 'Approach B' in s
count=0
for file in [doc,root/'docs/STATUS.md',root/'docs/DECISIONS.md',root/'docs/TEST_LOG.md']:
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if '://' in target or target.startswith('#'): continue
  assert (file.parent/target.split('#')[0]).exists(),(file,target)
  count+=1
print(f'PASS: S1–S7 alternative coverage, {count} local document/ledger links')
assert not list((root/'shaderpack').rglob('*.glsl'))
print('PASS: no GLSL implementation introduced; acceptance is documentary, not runtime')
