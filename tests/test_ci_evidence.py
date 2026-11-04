"""Contract tests for machine-readable CI evidence generation."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ci_evidence.py"


class CiEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.log = self.root / "unit-tests.log"
        self.report = self.root / "report.md"
        self.output = self.root / "ci-evidence.json"
        self.log.write_text("test_one ... ok\n\n----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK\n", encoding="utf-8")
        self.report.write_text("# Synthetic report\n", encoding="utf-8")

    def run_generator(self, *, sha="a" * 40):
        env = {**os.environ, "GITHUB_SHA": sha, "SOURCE_HEAD_SHA": "b" * 40,
               "GITHUB_REPOSITORY": "danwiz/wisdom-it-readiness-toolkit"}
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--test-log", str(self.log),
             "--report", str(self.report), "--output", str(self.output)],
            capture_output=True, text=True, env=env, check=False,
        )

    def test_passed_run_produces_traceable_hashes(self):
        result = self.run_generator()
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(evidence["schema_version"], "wisdom.devops.ci-evidence.v1")
        self.assertEqual(evidence["tests"]["executed"], 1)
        self.assertEqual(evidence["tests"]["result"], "passed")
        self.assertFalse(evidence["release_or_deployment_approval"])
        self.assertEqual(evidence["source"]["tested_commit_sha"], "a" * 40)
        self.assertEqual(evidence["source"]["source_head_sha"], "b" * 40)
        self.assertEqual(evidence["reports"][0]["sha256"], hashlib.sha256(self.report.read_bytes()).hexdigest())

    def test_failed_test_summary_is_rejected(self):
        self.log.write_text("Ran 1 test in 0.001s\nFAILED (failures=1)\n", encoding="utf-8")
        result = self.run_generator()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_unverified_source_sha_is_rejected(self):
        result = self.run_generator(sha="unknown")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_missing_report_is_rejected(self):
        self.report.unlink()
        result = self.run_generator()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
