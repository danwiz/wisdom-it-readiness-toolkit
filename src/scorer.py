"""Deterministic scoring for the Wisdom IT Readiness Toolkit."""

from __future__ import annotations

import json
import math
from decimal import Decimal
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from recommendations import build_guidance


@dataclass(frozen=True)
class ScoreResult:
    overall_percent: float
    maturity_level: int
    maturity_label: str
    domain_scores: dict[str, float]
    unanswered_questions: list[str]
    coverage: dict[str, Any] = field(default_factory=dict)
    recommendations: list[dict[str, Any]] = field(default_factory=list)


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _scale_bounds(assessment: dict[str, Any]) -> tuple[int, int]:
    scale = assessment.get("scale")
    if not isinstance(scale, dict) or len(scale) < 2:
        raise ValueError("Assessment scale must contain at least two integer values")
    values = []
    for key, label in scale.items():
        if not isinstance(key, str) or not key or not isinstance(label, str) or not label.strip():
            raise ValueError("Scale keys and labels must be nonempty strings")
        try:
            number = int(key)
        except ValueError:
            raise ValueError("Scale keys must be canonical integer strings") from None
        if str(number) != key:
            raise ValueError("Scale keys must be canonical integer strings")
        values.append(number)
    values.sort()
    if any(b != a + 1 for a, b in zip(values, values[1:])):
        raise ValueError("Assessment scale must be contiguous")
    return values[0], values[-1]


def validate_assessment(assessment: Any, responses: Any) -> tuple[int, int]:
    if not isinstance(assessment, dict) or not isinstance(responses, dict):
        raise ValueError("Assessment and responses must be JSON objects")
    if assessment.get("version") not in ("0.1.0", "0.2.0"):
        raise ValueError("Assessment version must be 0.1.0 or 0.2.0")
    minimum, maximum = _scale_bounds(assessment)
    domains = assessment.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("Assessment must define at least one domain")
    domain_ids, question_ids, weights = set(), set(), []
    for domain in domains:
        if not isinstance(domain, dict):
            raise ValueError("Each domain must be an object")
        identifier = domain.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in domain_ids:
            raise ValueError("Domain IDs must be unique nonempty strings")
        domain_ids.add(identifier)
        questions = domain.get("questions")
        if not isinstance(questions, list) or not questions:
            raise ValueError("Each domain must contain questions")
        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Each question must be an object")
            identifier = question.get("id")
            if not isinstance(identifier, str) or not identifier.strip() or identifier in question_ids:
                raise ValueError("Question IDs must be globally unique nonempty strings")
            question_ids.add(identifier)
            weight = question.get("weight", 1)
            if not _finite_number(weight) or weight <= 0:
                raise ValueError("Question weights must be finite positive numbers")
            weights.append(weight)
    try:
        total = math.fsum(weights)
    except OverflowError:
        raise ValueError("Combined question weights exceed the supported numeric range") from None
    if not math.isfinite(total):
        raise ValueError("Combined question weights exceed the supported numeric range")
    if any(key not in question_ids for key in responses):
        raise ValueError("Responses contain unknown question IDs; use IDs from the assessment")
    bands = assessment.get("maturity_bands")
    if not isinstance(bands, list) or not bands:
        raise ValueError("Assessment must define maturity bands")
    next_cent, levels = 0, set()
    for band in bands:
        if not isinstance(band, dict):
            raise ValueError("Each maturity band must be an object")
        lo, hi = band.get("minimum_percent"), band.get("maximum_percent")
        if not all(_finite_number(v) and 0 <= v <= 100 for v in (lo, hi)):
            raise ValueError("Maturity bounds must be finite percentages from 0 to 100")
        cents = [Decimal(str(v)) * 100 for v in (lo, hi)]
        if any(v != v.to_integral_value() for v in cents):
            raise ValueError("Maturity bounds must have at most two decimal places")
        low, high = map(int, cents)
        if low != next_cent or high < low:
            raise ValueError("Maturity bands must be ordered without gaps or overlaps")
        next_cent = high + 1
        level, label = band.get("level"), band.get("label")
        if isinstance(level, bool) or not isinstance(level, int) or level <= 0 or level in levels:
            raise ValueError("Maturity levels must be unique positive integers")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Maturity labels must be nonempty strings")
        levels.add(level)
    if next_cent != 10001:
        raise ValueError("Maturity bands must cover 0 through 100")
    return minimum, maximum


def _validate_score(value: Any, question_id: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Response scores must be integers within the assessment scale")
    if not minimum <= value <= maximum:
        raise ValueError("Response scores must be within the assessment scale")
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
    minimum, maximum = validate_assessment(assessment, responses)
    domains = assessment["domains"]

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
    coverage, recommendations = build_guidance(assessment, domain_scores, unanswered, maturity_label)
    return ScoreResult(overall_percent, maturity_level, maturity_label, domain_scores, unanswered, coverage, recommendations)


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = parse_json(handle.read())
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains duplicate keys")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("JSON must not contain nonfinite numbers")


def parse_json(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON at line {exc.lineno}, column {exc.colno}") from None
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data
