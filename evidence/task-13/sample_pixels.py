#!/usr/bin/env python3
"""Report median native sRGB codes for fixed terrain and cave patches."""
import argparse
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'task-12'))
from sample_pixels import sample

REGIONS = {
    'daylight': {'grass': '400x160+1050+1060', 'stone': '80x100+1130+405'},
    'sunset': {'grass': '400x160+1050+1060', 'shaded stone': '130x100+200+435',
               'doorway recess': '40x90+476+594'},
    'forest': {'stone': '80x100+755+328', 'oak trunk': '44x100+490+562',
               'grass beside trunk': '64x28+570+695', 'open grass': '400x160+1050+1060'},
    'cave': {'floor near lantern': '90x40+1840+820', 'ceiling recess': '120x60+1250+360'},
    'night': {'grass': '400x160+1050+1060', 'stone': '80x100+1130+405',
              'brick wall': '220x100+2110+486'},
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', type=Path)
    args = parser.parse_args()
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(('variant', 'scene', 'surface', 'crop', 'r', 'g', 'b'))
    for scene, regions in REGIONS.items():
        for variant in ('sunlight', 'ambient'):
            image = args.artifacts / f'{variant}-01' / scene / 'native.png'
            for surface, geometry in regions.items():
                writer.writerow((variant, scene, surface, geometry, *sample(image, geometry)))
