"""Markdown report generation for the Wisdom IT Readiness Toolkit."""

from __future__ import annotations

from typing import Any
import html
import re

from scorer import ScoreResult


def _text(value: Any) -> str:
    """Render untrusted text literally rather than as Markdown or raw HTML."""
    text = html.escape(str(value), quote=True).replace("\r", " ").replace("\n", " ")
    return re.sub(r"([\\`*_{}\[\]()#+!|>~])", r"\\\1", text)


def generate_markdown_report(
    assessment: dict[str, Any],
    result: ScoreResult,
    *,
    subject: str = "Assessment subject",
    data_note: str = "User-provided assessment responses",
) -> str:
    titles = {
        str(domain["id"]): str(domain.get("title", domain["id"]))
        for domain in assessment.get("domains", [])
    }
    lines = [
        f"# {_text(assessment.get('title', 'Technology Readiness Assessment'))} — Report",
        "",
        f"**Subject:** {_text(subject)}  ",
        f"**Assessment:** {_text(assessment.get('assessment_id', 'unknown'))} v{_text(assessment.get('version', 'unknown'))}  ",
        f"**Data:** {_text(data_note)}  ",
        f"**Overall score:** {result.overall_percent:.2f}%  ",
        f"**Maturity:** Level {result.maturity_level} — {_text(result.maturity_label)}",
        "",
        "## Coverage",
        "",
        (f"Answered {result.coverage['answered']} of {result.coverage['total']} questions."
         if result.coverage else "Coverage unavailable for this result."),
        ("Incomplete assessment: scores describe answered questions only and are provisional."
         if result.coverage.get("incomplete", True) else "All questions answered; responses have not been independently verified."),
        "",
        "## Domain results",
        "",
    ]
    for domain_id, score in result.domain_scores.items():
        lines.append(f"- {_text(titles.get(domain_id, domain_id))}: {score:.2f}%")

    for domain_id, coverage in result.coverage.get('domains', {}).items():
        if domain_id not in result.domain_scores:
            lines.append(f"- {_text(titles.get(domain_id, domain_id))}: unavailable (no answered questions)")
    lines.extend(["", "## Priority actions", ""])
    for index, item in enumerate(result.recommendations, start=1):
        lines.append(f"{index}. **{item['priority'].upper()} — {_text(titles.get(item['domain_id'], item['domain_id']))}** ({_text(item['rule_id'])})")
        lines.append(f"   - Rationale: {_text(item['rationale'])}")
        lines.append(f"   - Next action: {_text(item['next_action'])}")
    if not result.recommendations:
        lines.append("Recommendations unavailable for this result.")
    lines.extend([
        "",
        "## Limitations",
        "",
        "Priorities are workflow priorities, not vulnerability severity. Scores describe supplied responses, not security assurance or certification. Review evidence with an accountable owner before acting.",
        "",
        "## Evidence required for closure",
        "",
        "- Named owner and target date for each remediation action",
        "- Configuration, policy, checklist, or system evidence",
        "- Verification record showing the control operates as intended",
        "- Updated risk and action registers",
    ])
    if result.unanswered_questions:
        lines.extend(["", "## Incomplete responses", ""])
        lines.extend(f"- {_text(question_id)}" for question_id in result.unanswered_questions)
    return "\n".join(lines) + "\n"
