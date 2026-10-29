# Case study: local technology readiness assessment

Status: v0.2.0 development case study; v0.1.0 remains the published release.

## Problem

Small-business IT owners need an explainable way to turn self-reported readiness
answers into a practical evidence follow-up list. A high score from incomplete
answers can mislead if missing evidence is hidden.

## Architecture

A Python CLI loads and validates versioned JSON, computes weighted scores, builds
coverage and deterministic recommendations, and renders JSON, Markdown or
standalone HTML. The scoring result is shared across renderers. File writes use
an atomic replacement after validation and prohibit overwriting input files.
The package bundles a fixed four-domain quick check. Processing needs no cloud
service, credentials, AI model or external assets.

## Verification

The suite tests numerical compatibility, malformed data, recommendation
thresholds, ordering, missing responses, escaping and deterministic output.
The distribution matrix installs wheel and sdist independently outside the source
checkout on Windows/macOS/Ubuntu with Python 3.11/3.12, then exercises CLI success,
error and preservation paths. HTML fixtures are explicitly synthetic.
Release evidence must identify the exact commit and workflow run; current
branch validation is not proof that a new release is published.

## Limitations and follow-up

This is a small self-reporting aid, not an automated security assessment or
compliance certification. It does not verify evidence or remediate systems.
The domain set remains narrow. Visual/assistive-technology review and final
release packaging remain publication gates. There is no claim of measured
customer adoption, production deployment or ecosystem impact.
