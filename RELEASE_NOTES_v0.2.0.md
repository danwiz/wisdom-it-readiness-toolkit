# Wisdom IT Readiness Toolkit v0.2.0

Status: prepared release notes for the development candidate; not published.
The package remains 0.2.0.dev0 until release acceptance is complete.

## Changes

- Strict assessment and JSON validation, including versions, scales, finite
  weights, maturity-band coverage, unique IDs and duplicate JSON keys.
- Deterministic recommendations with priorities, rules, rationale and next action.
- Answered/total coverage and clear provisional/unavailable results.
- Local standalone HTML reports via `--format html`, alongside JSON and Markdown.
- Bundled `builtin:quick-check` assessment for installed CLI use.
- Atomic report writes, input overwrite protection and concise exit-code errors.
- Independent wheel/sdist installation and CLI verification on Windows, Ubuntu
  and macOS, with Python 3.11 and 3.12.

## Migration from v0.1.0

JSON score exports also add `metadata` and `limitations`. Optional `score`
arguments `--subject` and `--data-note` mirror report context. The default data
note is user-provided responses; provenance is explicitly unverified. No label
is inferred from the filename. See [JSON output](docs/json-output.md).

Valid versioned v0.1.0 assessments and integer response mappings remain supported;
existing numeric score fields retain their meanings. JSON adds `coverage` and
`recommendations`; consumers should accept additional fields. Partial scores
still use answered questions only. Recommendation text replaces the earlier
lowest-domain suggestions and is not a byte-for-byte v0.1.0 output guarantee.

Previously tolerated invalid files now fail: missing/unsupported versions,
unknown question IDs, duplicate keys/IDs, invalid scales or maturity bands,
Boolean scores and nonfinite/nonpositive weights. Correct the input rather than
silently dropping data. Empty responses are rejected. Exit codes are 0 success,
2 usage/validation, 1 file I/O. Rejected input leaves an existing report unchanged.

The report default remains Markdown, regardless of filename. Select HTML
explicitly with `--format html`. The four-domain historical quick-check file is
unchanged; domain expansion is deferred.

## Privacy and limitations

Processing is local without telemetry. Installation may download packages.
Protect report files as carefully as assessment inputs. Self-reported scores are
not independent control verification, vulnerability severity, certification or
compliance assurance. Synthetic demonstrations contain no client data.

## Publication gates

Before publishing, record the exact release commit and passing six-job matrix,
complete visual/keyboard/screen-reader review, set the final package version,
rebuild and reverify both distributions, and retain checksums. Attach only those
verified artifacts. Update public portfolio release claims after publication.
The separate README governance pilot retains its independent review requirement.
