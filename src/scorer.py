"""Deterministic scoring for the Wisdom IT Readiness Toolkit."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScoreResult:
    overall_percent: float
    maturity_level: int
    maturity_label: str
    domain_scores: dict[str, float]
    unanswered_questions: list[str]


def _scale_bounds(assessment: dict[str, Any]) -> tuple[int, int]:
    scale = assessment.get("scale")
    if not isinstance(scale, dict) or not scale:
        raise ValueError("Assessment must define a non-empty scale")
    try:
        values = sorted(int(key) for key in scale)
    except (TypeError, ValueError) as exc:
        raise ValueError("Scale keys must be integers or integer strings") from exc
    return values[0], values[-1]


def _validate_score(value: Any, question_id: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Response for {question_id} must be an integer from {minimum} to {maximum}")
    if not minimum <= value <= maximum:
        raise ValueError(f"Response for {question_id} must be between {minimum} and {maximum}")
    return value


def _maturity_for_percent(assessment: dict[str, Any], percent: float) -> tuple[int, str]:
    bands = assessment.get("maturity_bands")
    if not isinstance(bands, list) or not bands:
        raise ValueError("Assessment must define maturity bands")
    for band in bands:
        if band["minimum_percent"] <= percent <= band["maximum_percent"]:
            return int(band["level"]), str(band["label"])
    raise ValueError(f"No maturity band covers score {percent}")


def score_assessment(assessment: dict[str, Any], responses: dict[str, Any]) -> ScoreResult:
    domains = assessment.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("Assessment must define at least one domain")

    minimum, maximum = _scale_bounds(assessment)
    if maximum == minimum:
        raise ValueError("Assessment scale must contain more than one value")

    domain_scores: dict[str, float] = {}
    unanswered: list[str] = []
    overall_earned = 0.0
    overall_possible = 0.0

    for domain in domains:
        domain_id = domain.get("id")
        questions = domain.get("questions", [])
        if not domain_id or not isinstance(questions, list) or not questions:
            raise ValueError("Every domain must have an id and at least one question")

        earned = 0.0
        possible = 0.0
        for question in questions:
            question_id = question.get("id")
            if not question_id:
                raise ValueError(f"Domain {domain_id} contains a question without an id")
            weight = question.get("weight", 1)
            if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
                raise ValueError(f"Question {question_id} must have a positive numeric weight")
            if question_id not in responses:
                unanswered.append(question_id)
                continue

            score = _validate_score(responses[question_id], question_id, minimum, maximum)
            normalized = (score - minimum) / (maximum - minimum)
            earned += normalized * weight
            possible += weight

        if possible:
            percent = round((earned / possible) * 100, 2)
            domain_scores[str(domain_id)] = percent
            overall_earned += earned
            overall_possible += possible

    if not overall_possible:
        raise ValueError("At least one valid response is required")

    overall_percent = round((overall_earned / overall_possible) * 100, 2)
    maturity_level, maturity_label = _maturity_for_percent(assessment, overall_percent)
    return ScoreResult(overall_percent, maturity_level, maturity_label, domain_scores, unanswered)


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data
