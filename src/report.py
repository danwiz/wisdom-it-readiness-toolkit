"""Markdown report generation for the Wisdom IT Readiness Toolkit."""

from __future__ import annotations

from typing import Any

from scorer import ScoreResult


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
        f"# {assessment.get('title', 'Technology Readiness Assessment')} — Report",
        "",
        f"**Subject:** {subject}  ",
        f"**Assessment:** {assessment.get('assessment_id', 'unknown')} v{assessment.get('version', 'unknown')}  ",
        f"**Data:** {data_note}  ",
        f"**Overall score:** {result.overall_percent:.2f}%  ",
        f"**Maturity:** Level {result.maturity_level} — {result.maturity_label}",
        "",
        "## Domain results",
        "",
    ]
    for domain_id, score in result.domain_scores.items():
        lines.append(f"- {titles.get(domain_id, domain_id)}: {score:.2f}%")

    ordered = sorted(result.domain_scores.items(), key=lambda item: item[1])
    lines.extend(["", "## Priority actions", ""])
    for index, (domain_id, score) in enumerate(ordered[:2], start=1):
        lines.append(f"{index}. Create a remediation plan for {titles.get(domain_id, domain_id)} ({score:.2f}%).")
    lines.extend([
        "3. Assign accountable owners to priority technology risks.",
        "4. Define evidence and acceptance criteria before closing actions.",
        "5. Repeat the assessment after remediation.",
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
        lines.extend(f"- {question_id}" for question_id in result.unanswered_questions)
    return "\n".join(lines) + "\n"
