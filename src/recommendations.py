"""Deterministic workflow priorities for validated readiness results.

Priority is not vulnerability severity. Inputs must first pass scorer validation.
"""
from typing import Any

PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}


def build_guidance(assessment: dict[str, Any], scores: dict[str, float],
                   unanswered: list[str], maturity: str) -> tuple[dict, list[dict]]:
    missing = set(unanswered)
    domains = {}
    recommendations = []
    total = answered = 0
    for domain in sorted(assessment['domains'], key=lambda item: item['id']):
        domain_id = domain['id']
        ids = [q['id'] for q in domain['questions']]
        absent = sorted(q for q in ids if q in missing)
        count = len(ids) - len(absent)
        domains[domain_id] = {'answered': count, 'total': len(ids), 'incomplete': bool(absent)}
        total += len(ids)
        answered += count
        score = scores.get(domain_id)
        score_note = 'unavailable' if score is None else f'{score:.2f}%'
        context = f'Domain score: {score_note}; overall maturity from supplied responses: {maturity}.'
        def add(rule, priority, rationale, action):
            recommendations.append({'rule_id': rule, 'priority': priority, 'domain_id': domain_id,
                                    'rationale': rationale + ' ' + context, 'next_action': action})
        if absent:
            add('complete-evidence', 'high', 'Missing question IDs: ' + ', '.join(absent) +
                '. The domain score is ' + ('unavailable.' if score is None else 'provisional.'),
                'Collect and review evidence for the missing questions before treating this domain as assessed.')
        if score is None:
            continue
        if score < 45:
            add('establish-baseline', 'high', 'Supplied responses score below 45%.',
                'Identify an accountable owner and implement missing practices in this domain with documented verification evidence.')
        elif score < 65:
            add('standardize-practices', 'medium', 'Supplied responses score from 45% to below 65%.',
                'Document repeatable procedures for this domain and verify their use.')
        elif score < 85:
            add('verify-consistency', 'low', 'Supplied responses score from 65% to below 85%.',
                'Sample evidence for this domain and close inconsistent practices.')
        else:
            add('maintain-evidence', 'low', 'Supplied responses score at least 85%; this is not certification.',
                'Periodically recheck the supplied evidence for this domain.')
    recommendations.sort(key=lambda item: (PRIORITY_ORDER[item['priority']], item['domain_id'], item['rule_id']))
    return {'answered': answered, 'total': total, 'incomplete': answered != total, 'domains': domains}, recommendations
