# Installation and troubleshooting (v0.2.0 development)

These changes are on the development branch; the published v0.1.0 artifacts are unchanged. The package version is `0.2.0.dev0` until the full release acceptance checklist is met.

## Install

Use Python 3.11 or newer. The release validation matrix exercises 3.11 and 3.12 on Windows, Ubuntu and macOS. Install a built wheel or source distribution with `python -m pip install PATH_TO_PACKAGE`, preferably in a virtual environment. Building from a checkout uses `python -m pip install build` and `python -m build`; installation/build tools may require internet access.

The installed CLI includes the existing quick-check assessment:

```sh
witrt score builtin:quick-check responses.json
witrt report builtin:quick-check responses.json --output report.md
```

You can still supply an assessment path in place of `builtin:quick-check`. File paths are resolved relative to the current directory, not the package directory. No response data is bundled. For a synthetic smoke test, create `responses.json` containing `{"STR-01":2}`. This is a partial assessment: its 100% score applies only to the answered question, not overall verified readiness.

## Error contract

| Exit | Meaning | Action |
|---|---|---|
| 0 | Success | Score JSON is printed, or report path is printed. |
| 2 | Invalid command, schema, response or encoding | Check command help, UTF-8 JSON, supported version, IDs, scores and assessment structure. |
| 1 | Input/output failure | Check input existence/read permissions and output directory/write permissions. |

Expected failures use stderr, without a traceback or raw response values. Validation runs before report writing, and existing outputs remain unchanged on invalid input. Reports cannot overwrite input files. Successful report writes replace the destination through a temporary file in the same directory; concurrent writers and network-filesystem guarantees are outside this release's scope.

## Validation changes from v0.1.0

Assessment versions `0.1.0` and `0.2.0` are supported. Missing versions, duplicate JSON keys, duplicate IDs, unknown response IDs, Boolean/noninteger scores, nonfinite weights, noncontiguous/ambiguous scales, and maturity-band gaps/overlaps are rejected. Maturity bands must cover all two-decimal scores from 0 to 100. Valid historical quick-check scores remain unchanged. Fix invalid data explicitly rather than relying on old permissive behavior.

Scoring/reporting does not transmit assessment data. Protect files and reports yourself; do not put client responses in CI artifacts or public issue reports.

## Verification

`python -m unittest discover -s tests -v` checks scoring and schema behavior. After `python -m build`, run `python scripts/verify_distributions.py`. Each distribution is installed in its own temporary virtual environment and the executable runs outside the checkout, exercising bundled data, scoring, reporting, exit codes and unchanged files after errors.

See [requirements](requirements-v0.2.0.md). Recommendations, richer reports, and final release acceptance are separate milestones; this work does not publish v0.2.0.
