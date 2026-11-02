"""Public Python API for Wisdom IT Readiness Toolkit.

This compatibility layer re-exports the existing deterministic engine and
renderers. It does not copy or replace the implementation modules. The legacy
flat-module imports and ``witrt`` console script remain supported.

The API exposes supplied-response assessments, not independent evidence of
security assurance or compliance certification.
"""

from scorer import ScoreResult, load_json, parse_json, score_assessment, validate_assessment
from report import generate_markdown_report
from html_report import generate_html_report

__all__ = (
    "ScoreResult",
    "score_assessment",
    "validate_assessment",
    "parse_json",
    "load_json",
    "generate_markdown_report",
    "generate_html_report",
)
