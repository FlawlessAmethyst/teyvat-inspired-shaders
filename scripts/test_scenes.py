"""Safety and scene-source contract checks, without desktop access."""
import fcntl
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import scenes


def hold_lock(path, ready, release):
    with open(path, 'r+b') as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        ready.set()
        release.wait(10)


class ScenesTests(unittest.TestCase):
    def test_reject_closed_world_accept_locked_world(self):
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp)
            (world/'session.lock').write_bytes(b'lock')
            with patch.object(scenes, 'WORLD', world):
                with self.assertRaises(RuntimeError): scenes.require_scene_world()
                ctx = multiprocessing.get_context('fork')
                ready, release = ctx.Event(), ctx.Event()
                worker = ctx.Process(target=hold_lock,args=(world/'session.lock',ready,release))
                worker.start()
                try:
                    self.assertTrue(ready.wait(5))
                    scenes.require_scene_world()
                finally:
                    release.set(); worker.join(5)
                self.assertEqual(worker.exitcode,0)

    def test_function_camera_and_conditions_match_manifest(self):
        for name, spec in scenes.SPEC.items():
            text=(scenes.ROOT/f'scripts/scenes/data/task03/function/{name}.mcfunction').read_text()
            camera=spec['position']+[spec['yaw'],spec['pitch']]
            self.assertIn('tp @s '+' '.join(map(str,camera)),text)
            self.assertIn(f"time set {spec['time']}",text)
            self.assertIn(f"weather {spec['weather']} 1000000",text)
            self.assertIn('TASK03_READY_'+name,text)

    def test_build_edits_stay_bounded_and_within_command_limit(self):
        text=(scenes.ROOT/'scripts/scenes/data/task03/function/build.mcfunction').read_text()
        for line in text.splitlines():
            parts=line.split()
            if parts[0] not in ('fill','fillbiome'): continue
            x,y,z,X,Y,Z=map(int,parts[1:7])
            self.assertTrue(940 <= x <= X <= 1080 and 940 <= z <= Z <= 1080)
            self.assertTrue(176 <= y <= Y <= 211)
            self.assertLessEqual((X-x+1)*(Y-y+1)*(Z-z+1),32768)

if __name__=='__main__': unittest.main()
