import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from report import generate_markdown_report  # noqa: E402
from scorer import score_assessment  # noqa: E402


ASSESSMENT = {
    "title": "Test",
    "assessment_id": "TEST-1",
    "version": "0.1.0",
    "scale": {"0": "No", "1": "Partial", "2": "Yes"},
    "domains": [
        {"id": "a", "title": "Domain A", "questions": [{"id": "A1", "weight": 2}]},
        {"id": "b", "title": "Domain B", "questions": [{"id": "B1", "weight": 1}]},
    ],
    "maturity_bands": [
        {"minimum_percent": 0, "maximum_percent": 24.99, "level": 1, "label": "Unprepared"},
        {"minimum_percent": 25, "maximum_percent": 44.99, "level": 2, "label": "Basic"},
        {"minimum_percent": 45, "maximum_percent": 64.99, "level": 3, "label": "Repeatable"},
        {"minimum_percent": 65, "maximum_percent": 84.99, "level": 4, "label": "Managed"},
        {"minimum_percent": 85, "maximum_percent": 100, "level": 5, "label": "Optimized"},
    ],
}


class ToolkitTests(unittest.TestCase):
    def test_weighted_scoring(self):
        result = score_assessment(ASSESSMENT, {"A1": 2, "B1": 0})
        self.assertEqual(result.overall_percent, 66.67)
        self.assertEqual(result.maturity_label, "Managed")

    def test_missing_response_is_reported(self):
        result = score_assessment(ASSESSMENT, {"A1": 2})
        self.assertEqual(result.unanswered_questions, ["B1"])

    def test_report_uses_overall_percent(self):
        result = score_assessment(ASSESSMENT, {"A1": 2, "B1": 1})
        report = generate_markdown_report(ASSESSMENT, result, subject="Demo")
        self.assertIn("Overall score:", report)
        self.assertIn("Domain A", report)

    def test_rejects_invalid_response(self):
        with self.assertRaises(ValueError):
            score_assessment(ASSESSMENT, {"A1": 3})


if __name__ == "__main__":
    unittest.main()
