"""Contract tests for an additive importable Python API.

These tests are designed for the actual repository and existing v0.1 fixtures.
Do not interpret synthetic packaging-fixture results as repository test passes.
"""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import wisdom_it_readiness as public  # noqa: E402
from scorer import (  # noqa: E402
    ScoreResult,
    load_json,
    parse_json,
    score_assessment,
    validate_assessment,
)
from report import generate_markdown_report  # noqa: E402
from html_report import generate_html_report  # noqa: E402


class LibraryApiContractTests(unittest.TestCase):
    def test_exact_public_exports_and_compatibility(self):
        expected = {
            "ScoreResult": ScoreResult,
            "score_assessment": score_assessment,
            "validate_assessment": validate_assessment,
            "parse_json": parse_json,
            "load_json": load_json,
            "generate_markdown_report": generate_markdown_report,
            "generate_html_report": generate_html_report,
        }
        self.assertEqual(set(public.__all__), set(expected))
        for name, existing in expected.items():
            with self.subTest(name=name):
                self.assertIs(getattr(public, name), existing)

    def test_readiness_scoring_uses_unchanged_engine(self):
        assessment = load_json(ROOT / "assessments" / "quick-check-v0.1.json")
        responses = load_json(ROOT / "examples" / "synthetic-responses.json")
        direct = score_assessment(assessment, responses)
        reexported = public.score_assessment(assessment, responses)
        self.assertEqual(direct, reexported)
        self.assertIsInstance(reexported, ScoreResult)

    def test_reexported_parser_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            public.parse_json('{"id":1,"id":2}')


if __name__ == "__main__":
    unittest.main()
