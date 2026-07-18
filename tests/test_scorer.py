import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from scorer import score_assessment  # noqa: E402


ASSESSMENT = {
    "scale": {"0": "Not in place", "1": "Partial", "2": "Consistent"},
    "maturity_bands": [
        {"minimum_percent": 0, "maximum_percent": 24, "level": 1, "label": "Unprepared"},
        {"minimum_percent": 25, "maximum_percent": 44, "level": 2, "label": "Basic"},
        {"minimum_percent": 45, "maximum_percent": 64, "level": 3, "label": "Repeatable"},
        {"minimum_percent": 65, "maximum_percent": 84, "level": 4, "label": "Managed"},
        {"minimum_percent": 85, "maximum_percent": 100, "level": 5, "label": "Optimized"},
    ],
    "domains": [
        {
            "id": "strategy",
            "questions": [
                {"id": "STR-01", "weight": 2},
                {"id": "STR-02", "weight": 1},
            ],
        },
        {
            "id": "security",
            "questions": [
                {"id": "SEC-01", "weight": 3},
                {"id": "SEC-02", "weight": 1},
            ],
        },
    ],
}


class ScoreAssessmentTests(unittest.TestCase):
    def test_weighted_complete_assessment(self):
        result = score_assessment(
            ASSESSMENT,
            {"STR-01": 2, "STR-02": 1, "SEC-01": 1, "SEC-02": 0},
        )
        self.assertEqual(result.domain_scores, {"strategy": 83.33, "security": 37.5})
        self.assertEqual(result.overall_percent, 57.14)
        self.assertEqual(result.maturity_level, 3)
        self.assertEqual(result.maturity_label, "Repeatable")
        self.assertEqual(result.unanswered_questions, [])

    def test_reports_missing_responses(self):
        result = score_assessment(ASSESSMENT, {"STR-01": 2})
        self.assertEqual(result.domain_scores, {"strategy": 100.0})
        self.assertEqual(result.unanswered_questions, ["STR-02", "SEC-01", "SEC-02"])

    def test_rejects_out_of_range_response(self):
        with self.assertRaises(ValueError):
            score_assessment(ASSESSMENT, {"STR-01": 3})

    def test_rejects_empty_response_set(self):
        with self.assertRaises(ValueError):
            score_assessment(ASSESSMENT, {})

    def test_rejects_nonpositive_weight(self):
        invalid = dict(ASSESSMENT)
        invalid["domains"] = [{"id": "bad", "questions": [{"id": "BAD-01", "weight": 0}]}]
        with self.assertRaises(ValueError):
            score_assessment(invalid, {"BAD-01": 1})


if __name__ == "__main__":
    unittest.main()
