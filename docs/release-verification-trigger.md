# Release Verification Trigger

This file records the explicit push used to trigger a fresh GitHub Actions run for the `v0.1.0` release candidate.

- Workflow: `Toolkit CI`
- Required evidence: passing unit tests, successful installed CLI smoke tests, non-empty Markdown report, and uploaded `example-readiness-report` artifact.
- Release remains gated until GitHub-hosted evidence is visible.
