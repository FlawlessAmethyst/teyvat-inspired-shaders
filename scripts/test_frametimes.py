"""Guard against reporting server ticks, corrupt data or wrong timing units."""
import tempfile
import unittest
from pathlib import Path
import zipfile

from frametimes import convert, read_metrics


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, csv='@tick,ticktime\n1,1000000\n2,3000000\n',
                member='client/metrics/ticking.csv', ticks=2):
        p = self.root / 'profile.zip'
        with zipfile.ZipFile(p, 'w') as z:
            z.writestr(member, csv)
            z.writestr('client/profiling.txt',
                       f'Time span: 4 ms\nTick span: {ticks} ticks\n[00] updateDisplay(2/1)')
        return p

    def test_nanoseconds_and_summary(self):
        summary = convert(self.archive(), self.root / 'converted')
        self.assertEqual(summary['mean_client_loop_ms'], 2)
        self.assertEqual(summary['p95_client_loop_ms'], 3)
        self.assertEqual(summary['profile_frames_per_second'], 500)

    def test_server_metrics_never_substituted(self):
        with self.assertRaises(KeyError):
            read_metrics(self.archive(member='server/metrics/ticking.csv'))

    def test_bad_values_and_sequence_rejected(self):
        for body in ('', '1,nan\n2,1\n', '1,-1\n2,1\n',
                     '1,0\n2,1\n', '1,1\n1,2\n', '1,1\n3,2\n'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                read_metrics(self.archive('@tick,ticktime\n' + body))

    def test_mismatched_profile_rejected(self):
        with self.assertRaises(ValueError):
            read_metrics(self.archive(ticks=20))

    def test_unknown_schema_rejected(self):
        with self.assertRaises(ValueError):
            read_metrics(self.archive('@tick,frame_ms\n1,1\n2,3\n'))

    def test_existing_output_not_overwritten(self):
        p = self.archive()
        convert(p, self.root / 'converted')
        with self.assertRaises(FileExistsError):
            convert(p, self.root / 'converted')


if __name__ == '__main__':
    unittest.main()
