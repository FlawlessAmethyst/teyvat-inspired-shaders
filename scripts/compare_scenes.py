#!/usr/bin/env python3
"""ImageMagick-based replay diagnostics; pixel difference is not artistic similarity."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def mae(a,b):
    r=subprocess.run(['magick','compare','-metric','MAE',str(a),str(b),'null:'],capture_output=True,text=True)
    if r.returncode not in (0,1): raise RuntimeError(r.stderr)
    return float(re.search(r'\(([^)]+)\)',r.stderr)[1])


def compare(root):
    results={}
    with tempfile.TemporaryDirectory() as tmp:
        for name in ('daylight','forest','cave'):
            a=root/f'{name}-01/native.png';b=root/f'{name}-02/native.png'
            # Lower half excludes sky/clouds in outdoor scenes. Full cave retained.
            crop='2560x720+0+720' if name!='cave' else '2560x1440+0+0'
            pair=[]
            for i,path in enumerate((a,b)):
                dest=Path(tmp)/f'{i}.png'
                subprocess.run(['magick',str(path),'-crop',crop,'+repage',str(dest)],check=True)
                pair.append(dest)
            error=mae(*pair)
            results[name]={'first':str(a),'repeat':str(b),'full_frame_normalized_mae':mae(a,b),
                           'static_region':crop,'static_region_normalized_mae':error,
                           'static_region_below_0_01':error<0.01,
                           'sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)]}
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);a=p.parse_args()
    results=compare(a.root);print(json.dumps(results,indent=2))
    if not all(r['static_region_below_0_01'] for r in results.values()): raise SystemExit(1)
