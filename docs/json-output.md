# JSON score output (v0.2.0 development)

`witrt score` retains its existing score, coverage and recommendation fields and
adds `metadata` and `limitations`. Existing consumers must tolerate additional
top-level keys. Scoring rules and assessment files are unchanged.

```sh
witrt score builtin:quick-check responses.json \
  --subject "Synthetic Demonstration" \
  --data-note "Synthetic demonstration only"
```

Only supply that data note for genuinely synthetic responses. The defaults are
`Assessment subject` and `User-provided assessment responses`; filenames do not
select provenance. `metadata` contains `assessment_id` (or `unknown` when absent),
`assessment_version`, `subject`, `data_note`, and `provenance_basis`.
The basis is always `caller-supplied; not independently verified`: labels are
context supplied by the caller, not proof of origin or independent validation.
Assessment version is distinct from package version.

`limitations` is an array of readable statements covering self-report limitations,
workflow priority versus vulnerability severity, accountable review, and a
coverage-dependent provisional/unverified warning. Coverage and recommendations
retain their existing structured fields. No timestamp, local path, network call
or inferred synthetic label is added. Identical inputs/options produce identical
JSON. JSON strings preserve supplied text; downstream HTML renderers must escape
it before display. Protect exports because subject/data notes may be confidential.

The same subject/data-note options already exist on Markdown/HTML `report`.
The JSON export now carries corresponding context and limitations without
changing the public Python ScoreResult model. All repository examples are synthetic.
