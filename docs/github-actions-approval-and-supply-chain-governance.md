# GitHub Actions Approval and Supply-Chain Governance

## Purpose

Define the minimum controls for approving, running, and retaining evidence from GitHub Actions workflows, especially workflows introduced or modified by external contributors, dependency-update bots, coding agents, or third-party Actions.

## Approval authority

The repository owner or a specifically designated maintainer is the approval authority for held workflows. Approval must not be delegated automatically to a bot, coding agent, or unreviewed external contributor.

## Required review before execution

Before approving a held or materially changed workflow, review:

- Event triggers, especially `pull_request_target`, `workflow_run`, release, scheduled, and manual triggers.
- Requested `GITHUB_TOKEN` permissions.
- Use of `id-token: write`, attestations, deployments, packages, or release permissions.
- Exposure of repository, environment, or organization secrets.
- Checkout source and ref, especially code originating from forks.
- Third-party Actions, their publishers, release notes, runtime versions, and immutable commit references.
- Shell commands, downloaded scripts, package installation, artifact paths, and upload destinations.
- Concurrency, timeout, retention, cancellation, and cost behavior.
- Expected artifacts and the evidence needed to validate the run.

## Third-party Action policy

- Prefer GitHub-maintained Actions or well-established publishers.
- Review major-version upgrades independently before merge.
- Use immutable commit SHAs for release and security-sensitive workflows when practical.
- Record the upstream tag or version corresponding to each pinned SHA.
- Do not bypass a held-workflow warning merely to obtain a green check.

## Fork and external-contributor controls

- Do not expose secrets to untrusted fork code.
- Avoid checking out or executing fork-controlled code in privileged `pull_request_target` workflows.
- Require human approval before first-time or untrusted contributors can run workflows with meaningful permissions.
- Separate untrusted validation from release, deployment, signing, and attestation jobs.

## Supply-chain evidence workflow

For `.github/workflows/supply-chain-evidence.yml`:

- Keep manual and release triggers to control Actions usage.
- Retain least-privilege permissions: `contents: read`, `id-token: write`, and `attestations: write` only where needed.
- Verify tests, package build, checksum generation, SBOM generation, provenance attestation, and artifact upload.
- Download and inspect the evidence bundle.
- Independently verify at least one attestation.
- Record the run URL, commit, artifact inventory, verification command, result, and any exceptions in the governing issue.

## Stop conditions

Do not approve or continue a workflow when:

- The trigger or permission model is unclear.
- Fork-controlled code can access secrets or privileged tokens.
- A third-party Action cannot be traced to a trusted source and reviewed version.
- The workflow changes releases, deployments, packages, attestations, or repository contents outside the approved scope.
- Expected evidence cannot be retained or independently verified.
- The workflow produces unexpected cost, network access, or artifact behavior.

## Evidence retention

Retain, as applicable:

- Workflow run URL and run ID.
- Commit SHA and workflow file revision.
- Job and step outcomes.
- Built packages and checksum manifest.
- SPDX or CycloneDX SBOM.
- Provenance attestations and verification output.
- Reviewer identity, review date, decision, exceptions, and follow-up actions.

## Review cadence

Review this standard when GitHub changes workflow-approval behavior, Actions runtimes, artifact handling, attestation capabilities, malicious-package detection, or dependency-update controls.
