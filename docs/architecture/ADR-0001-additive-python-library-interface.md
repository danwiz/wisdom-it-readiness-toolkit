# ADR-0001: Additive, Compatibility-Preserving Python Library API

**Status:** Proposed (requires independent review)  
**Date:** 2026-11-02  
**Repository:** `danwiz/wisdom-it-readiness-toolkit`  
**Exact baseline SHA:** `a21df38d7a564a54ee4c7a2d27f7223f97fdd465`  
**Affected work:** v0.2.0 development only; published v0.1.0 remains unchanged.

## Context

The existing wheel installs `cli`, `scorer`, `report`, `html_report`, and
`recommendations` as top-level Python modules. The `witrt` entry point points
at `cli:main`. Direct module imports already work but provide no namespaced,
documented public library entry point. Converting all functions into classes
or moving modules now would create unnecessary behavioral and import risk.

## Decision

Add a new `wisdom_it_readiness` package containing only an explicit re-export
layer for existing scoring/validation/JSON/report symbols. Keep every existing
module, implementation, package-data resource, and CLI entry point in place.
Add the package to the explicit setuptools `packages` list, alongside
`wisdom_it_readiness_data`. Add contract tests checking exact identity of
re-exported objects and parity on existing synthetic assessment fixtures.

## Consequences and limitations

- Existing `from scorer import score_assessment` remains valid.
- New `from wisdom_it_readiness import score_assessment` becomes supported in
  development builds after approval; this is not yet a v0.2.0 release promise.
- The legacy top-level modules remain importable and may collide with another
  distribution on a user's sys.path. A follow-on migration may resolve this,
  but must retain compatibility shims and prove import/CLI/report parity.
- `ScoreResult` remains the same object; no data migration or API version bump.
- No new dependency or network access is introduced.
- No claim of GDPR, SOC 2, ISO certification or independent risk assurance.

## Dependencies and collision review

PR #22 adds `tests/test_cli_permissions.py` plus documentation; PR #16 edits
`README.md`. Proposed changes are disjoint by filename, but dependency and
integration review remains mandatory. Do not merge automatically.

## Acceptance gates

1. Confirm exact baseline SHA and approved branch scope.
2. Existing full tests pass on Python 3.11 and 3.12 (including non-root POSIX
   permission tests where supported).
3. New API contract tests pass on the real source tree.
4. Build wheel + sdist, inspect artifact contents, install into fresh isolated
   interpreters, run `witrt`, import both flat-module and namespaced APIs.
5. Compare golden JSON, Markdown, and HTML outputs byte-for-byte on synthetic
   fixtures, with documented exceptions only.
6. No new dependency downloads during runtime; no assessment data sent remotely.
7. Independent code, packaging, docs and license reviews on exact candidate SHA.

**Decision gate:** NO-GO until the real checkout is tested and reviewed.
