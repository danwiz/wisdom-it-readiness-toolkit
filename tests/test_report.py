import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from report import generate_markdown_report  # noqa: E402
from scorer import score_assessment  # noqa: E402


ASSESSMENT = {
    "assessment_id": "WITRT-TEST-001",
    "title": "Test Readiness Assessment",
    "version": "0.1.0",
    "scale": {"0": "No", "1": "Partial", "2": "Yes"},
    "maturity_bands": [
        {"minimum_percent": 0, "maximum_percent": 24, "level": 1, "label": "Unprepared"},
        {"minimum_percent": 25, "maximum_percent": 44, "level": 2, "label": "Basic"},
        {"minimum_percent": 45, "maximum_percent": 64, "level": 3, "label": "Repeatable"},
        {"minimum_percent": 65, "maximum_percent": 84, "level": 4, "label": "Managed"},
        {"minimum_percent": 85, "maximum_percent": 100, "level": 5, "label": "Optimized"},
    ],
    "domains": [
        {"id": "strategy", "title": "Strategy", "questions": [{"id": "STR-01", "weight": 1}]},
        {"id": "security", "title": "Security", "questions": [{"id": "SEC-01", "weight": 1}]},
    ],
}


class ReportTests(unittest.TestCase):
    def test_generates_accessible_markdown_report(self):
        result = score_assessment(ASSESSMENT, {"STR-01": 2, "SEC-01": 1})
        report = generate_markdown_report(
            ASSESSMENT,
            result,
            subject="Synthetic Example",
            data_note="Synthetic data only",
        )
        self.assertIn("# Test Readiness Assessment — Report", report)
        self.assertIn("**Overall score:** 75.00%", report)
        self.assertIn("- Strategy: 100.00%", report)
        self.assertIn("- Security: 50.00%", report)
        self.assertIn("## Priority actions", report)
        self.assertTrue(report.endswith("\n"))

    def test_lists_incomplete_responses(self):
        result = score_assessment(ASSESSMENT, {"STR-01": 2})
        report = generate_markdown_report(ASSESSMENT, result)
        self.assertIn("## Incomplete responses", report)
        self.assertIn("- SEC-01", report)


if __name__ == "__main__":
    unittest.main()
