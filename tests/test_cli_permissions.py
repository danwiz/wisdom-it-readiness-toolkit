"""Real POSIX permission failures; run under an unprivileged identity."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'posix', 'POSIX permission bits; Windows ACLs differ')
@unittest.skipIf(getattr(os, 'geteuid', lambda: -1)() == 0,
                 'Root bypasses permission bits; run as an unprivileged user')
class CliPermissionTests(unittest.TestCase):
    def run_report(self, response, output, format):
        result = subprocess.run([
            sys.executable, str(ROOT/'src/cli.py'), 'report',
            str(ROOT/'assessments/quick-check-v0.1.json'), str(response),
            '--format', format, '--output', str(output)],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn('Cannot read input or write report', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertNotIn('private-marker', result.stderr)

    def test_unreadable_response_preserves_existing_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            response = root/'responses.json'
            original = b'{"STR-01":2}'
            response.write_bytes(original)
            output = root/'report'
            output.write_bytes(b'private-marker existing report')
            response.chmod(0)
            try:
                self.assertFalse(os.access(response, os.R_OK),
                                 'Fixture must actually be unreadable')
                for format in ('markdown', 'html'):
                    with self.subTest(format=format):
                        self.run_report(response, output, format)
                        self.assertEqual(output.read_bytes(), b'private-marker existing report')
            finally:
                response.chmod(0o600)
            self.assertEqual(response.read_bytes(), original)

    def test_unwritable_directory_preserves_files_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            response = root/'responses.json'
            original = b'{"STR-01":2}'
            response.write_bytes(original)
            destination = root/'reports'
            destination.mkdir()
            output = destination/'existing-report'
            output.write_bytes(b'private-marker existing report')
            destination.chmod(0o500)
            try:
                self.assertFalse(os.access(destination, os.W_OK),
                                 'Fixture must actually be unwritable')
                for format in ('markdown', 'html'):
                    for path in (output, destination/'new-report'):
                        with self.subTest(format=format, existing=path == output):
                            self.run_report(response, path, format)
                            self.assertEqual(output.read_bytes(), b'private-marker existing report')
                            self.assertEqual(response.read_bytes(), original)
                            self.assertEqual(sorted(p.name for p in destination.iterdir()),
                                             ['existing-report'])
            finally:
                destination.chmod(0o700)
