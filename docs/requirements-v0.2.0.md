# v0.2.0 requirements and compatibility baseline

Date: 2026-10-28. Scope baseline for [#6](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/6), under roadmap [#5](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/5).
This document defines intended behavior; unchecked acceptance items are not claims of implementation or release readiness.

## Purpose and users

Provide small-business IT owners and consultants with a local, explainable readiness assessment from user-supplied JSON responses. The narrow workflow is validate, score, prioritize, and export a readable report. Support synthetic demonstrations and incomplete assessments, while making missing evidence visible.

## Existing behavior and compatibility

Source baseline: commit `d1f004a92040a0ca3e86692eacfb16e780f4964c`, specifically `src/scorer.py`, `src/cli.py`, `src/report.py`, the quick-check assessment and synthetic responses.

| Input or interface | v0.2.0 requirement |
|---|---|
| Bundled assessment with `version: 0.1.0` | Continue accepting unchanged; preserve IDs, weights, scale and maturity thresholds. Do not rewrite the historical file in place. |
| Existing response object mapping question IDs to integer scores | Continue accepting unchanged; no envelope or conversion required. |
| Partial responses | Omit unanswered questions from score denominators, retain their IDs, and show coverage prominently. An entirely unanswered domain has no score, not zero. |
| Zero answered questions | Reject; do not emit a plausible readiness score. |
| `witrt score ASSESSMENT RESPONSES` | Preserve command and existing JSON field names/types. Add recommendations and coverage as additive fields. Consumers must tolerate additional fields. |
| `witrt report ... --output PATH` | Keep Markdown as the default. Introduce HTML through explicit `--format html`; do not infer format from the filename. |
| Files without an assessment version, or unsupported versions | Reject with a concise explanation. Supported versions are exactly `0.1.0` and `0.2.0` for this release. This is intentional validation tightening. |
| Unknown response IDs, duplicate IDs/JSON keys, malformed schema | Reject rather than silently ignore or overwrite. Document this tightening in migration notes. |
| Existing score calculations | Preserve numeric results for valid v0.1.0 inputs. New recommendation text is not an existing output compatibility guarantee. |

The assessment `version` is the assessment format/content version, distinct from the installed package version. No new required input fields are introduced for v0.2.0. Assessment expansion is deferred; the existing four-domain quick check remains the supported scenario.

## Requirements and traceability

| ID | Required behavior | Implementation |
|---|---|---|
| VAL-01 | Require object roots; nonempty unique domain IDs and globally unique question IDs; at least one question per domain. Validate before scoring. | #8 |
| VAL-02 | Require a contiguous integer scale with at least two values; reject ambiguous keys, nonfinite or nonpositive weights, Boolean weights and invalid score types. | #8 |
| VAL-03 | Require ordered, nonoverlapping maturity bands covering every two-decimal score from 0 through 100, unique positive integer levels, and nonempty labels. Reject gaps and reversed bounds. | #8 |
| SCORE-01 | Compute weighted normalized percentages from answered questions only; round domain and overall scores to two decimals. Determine maturity from the rounded overall score. | #8 |
| SCORE-02 | Report answered and total question counts and an incomplete flag. Never describe a partial high score as verified readiness. | #7, #9 |
| REC-01 | Produce deterministic recommendations with rule ID, priority, domain ID, rationale and suggested next action in JSON, Markdown and HTML. | #7 |
| REC-02 | Apply the rule policy below. No randomness, timestamps, network calls or model inference may affect recommendation ordering. | #7 |
| CLI-01 | Install wheel and source distribution into clean environments; run installed `witrt` from outside the checkout using supplied file paths. Python 3.11 and 3.12 are the tested release targets. | #8 |
| CLI-02 | Exit 0 on success, 2 on usage/validation errors, 1 on file I/O errors. Expected failures use concise stderr without tracebacks or raw response values. Keep stdout empty on failure. | #8 |
| CLI-03 | Validate all inputs before writing output; failed validation must leave an existing output file unchanged. Never modify assessment or response inputs. | #8 |
| REPORT-01 | Keep JSON and Markdown deterministic for identical input and options; provide self-contained HTML with no external assets, scripts, forms or network requests. | #9 |
| REPORT-02 | Escape user-supplied text in HTML and Markdown contexts. HTML has language, title, one main heading, ordered headings and semantic tables with headers. Verify keyboard use and readable contrast. | #9 |
| PRIV-01 | Scoring/reporting runs locally without telemetry or remote services. Documentation distinguishes installation downloads from processing. Use only synthetic CI fixtures and report examples. | #8, #9 |

## Recommendation policy

Scores describe supplied responses, not security assurance. Priority labels are workflow priorities, not vulnerability severity.

1. For each incomplete domain, emit `complete-evidence` with priority `high`, listing missing question IDs and explaining that its score is provisional (or unavailable if unanswered).
2. For each scored domain below 45%, emit `establish-baseline` with priority `high`: identify an accountable owner and implement the missing practices in that domain, with documented verification evidence.
3. For each scored domain from 45% to below 65%, emit `standardize-practices` with priority `medium`: document repeatable procedures and verify their use.
4. For each scored domain from 65% to below 85%, emit `verify-consistency` with priority `low`: sample evidence and close inconsistent practices.
5. At 85% or above, emit `maintain-evidence` with priority `low`: periodically recheck the supplied evidence; do not claim certification.

Sort by priority (high, medium, low), then domain ID lexicographically, then rule ID lexicographically. Missing evidence does not suppress a score-based recommendation for answered questions. Include the numeric domain score or an explicit unavailable marker and overall maturity label in rationale. Test thresholds at 44.99/45, 64.99/65 and 84.99/85. This policy replaces v0.1.0's generic lowest-two-domain report text; it does not change score weights.

## Release acceptance checklist

- [ ] AC-01: golden compatibility tests preserve all five existing score-result fields for complete and partial v0.1.0 fixtures; zero responses fail.
- [ ] AC-02: malformed JSON, duplicate keys/IDs, unknown IDs, unsupported versions, nonfinite weights, invalid scales/bands and Boolean scores are rejected deterministically.
- [ ] AC-03: recommendation boundary, tie-order and missing-evidence tests pass; repeated runs produce identical JSON and report bytes.
- [ ] AC-04: wheel and sdist installation, external-working-directory CLI execution and documented exit codes pass on Windows, Ubuntu and macOS, with Python 3.11/3.12 coverage.
- [ ] AC-05: missing/unreadable files and unwritable output fail cleanly; invalid input does not change existing output or source files.
- [ ] AC-06: HTML injection fixtures render as text; no external resources are required; semantic/keyboard/contrast review is recorded. No unverified accessibility certification claim.
- [ ] AC-07: synthetic JSON, Markdown and HTML outputs show provenance, coverage, recommendations and limitations consistently.
- [ ] AC-08: release candidate passes tests, build, installed CLI and report checks; checksums and release notes identify the exact commit. Portfolio is updated only after this evidence exists.
- [ ] AC-09: migration notes describe additive JSON fields and validation tightening; README links to installation, error handling and limitations. Coordinate with the separate README pilot (#10 / PR #16).

## Risks, assumptions and exclusions

- Self-reported responses can be inaccurate; no independent evidence verification is performed.
- Missing answers can inflate observed scores; coverage is mandatory and missing evidence gets a high-priority follow-up.
- Stricter validation may reject files previously accepted accidentally; provide actionable migration guidance, never silently repair them.
- Generated reports can contain confidential user-provided text. File permissions, sharing and retention remain the user's responsibility.
- No network scanning, credential collection, cloud storage, autonomous remediation, AI generation, compliance certification, multi-tenant service or live client-data examples.
- Do not expand the assessment domains or change historical academic artifacts as part of this milestone.
- GitHub is authoritative; GitLab supplies secondary commit-specific validation. A green secondary run does not replace the complete release acceptance checks above.

## Change control

### JSON parity refinement — 2026-10-29

AC-07 requires JSON context as well as Markdown/HTML context. `score` adds optional
`--subject` and `--data-note` with the same defaults as `report`. It adds top-level
`metadata` (assessment_id, assessment_version, subject, data_note, provenance_basis)
and `limitations`. Provenance is always labeled caller-supplied and unverified;
no synthetic label is inferred from filenames. Limitations include a coverage-aware
warning. Existing score-result fields and numeric semantics remain unchanged.
No timestamps are introduced. See [JSON contract](json-output.md).
Regression evidence: `tests/test_json_cli.py` and installed CLI checks. This
refinement does not close accessibility or final release acceptance gates.

Any change to scoring semantics, supported formats, recommendation rules or acceptance criteria must update this baseline and corresponding tests in the same pull request. Record actual test and review evidence before checking release items. This baseline does not publish v0.2.0 or close implementation issues #7–#9.
