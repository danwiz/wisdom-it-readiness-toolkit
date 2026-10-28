# Recommendations and coverage (v0.2.0 development)

Recommendations are deterministic workflow priorities derived from validated responses. They are not vulnerability severity, certification, or independent verification. No model, external service, timestamp or randomness is used. Existing numerical scoring is unchanged.

## Rules

| Condition per domain | Rule ID | Priority | Suggested action |
|---|---|---|---|
| Any unanswered question | complete-evidence | high | Collect and review missing evidence; scores are provisional or unavailable. |
| Score below 45% | establish-baseline | high | Assign an owner and implement missing practices with verification evidence. |
| Score 45% to below 65% | standardize-practices | medium | Document repeatable procedures and verify use. |
| Score 65% to below 85% | verify-consistency | low | Sample evidence and close inconsistent practices. |
| Score at least 85% | maintain-evidence | low | Periodically recheck supplied evidence; no certification implied. |

Each recommendation contains `rule_id`, `priority`, `domain_id`, `rationale`, and `next_action`. Rationale includes the domain score (or unavailable), overall maturity label, and missing question IDs when applicable. A partially answered domain can receive both an evidence recommendation and a score-based recommendation. A wholly unanswered domain receives only the evidence rule.

Ordering is priority (high, medium, low), domain ID lexicographically, then rule ID lexicographically. Missing IDs within rationale are sorted. Identical inputs/options yield identical JSON and Markdown bytes; input response-key insertion order does not affect recommendations.

## Additive JSON fields

`coverage` contains `answered`, `total`, `incomplete`, and a `domains` map with the same three coverage values per domain. Counts are question counts, not weighted coverage. `recommendations` is an ordered array of rule objects. The five existing score-result fields retain their meanings and values. Consumers should accept additive fields.

A response containing only `STR-01: 2` produces a 100% score over that one answered question and coverage of 1/9. This does not indicate complete readiness. The report prominently marks it incomplete. Empty and invalid responses fail before recommendations are generated.

Markdown renders supplied titles, subject, notes and identifiers as literal text. Its priority-actions section replaces the previous generic lowest-two-domain text. HTML reporting remains a separate milestone under #9.

## Synthetic examples and verification

See [synthetic score JSON](../examples/recommendations-synthetic.json) and [synthetic Markdown report](../examples/recommendations-synthetic.md). These use the existing demonstration responses, with no client data.

Tests cover 44.99/45, 64.99/65 and 84.99/85 boundaries, tie ordering, missing domains, incomplete domains with both rules, invalid data, stable repeated output, compatibility and Markdown escaping. Installed wheel/sdist checks also verify recommendations and coverage outside the checkout. Requirements: SCORE-02, REC-01, REC-02 in the [baseline](requirements-v0.2.0.md).
