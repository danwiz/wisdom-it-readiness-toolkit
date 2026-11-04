# DevOps Phase 02 — CI Evidence Baseline

Status: PROPOSED / pending PR CI verification. This pilot is additive; no production deployment or release publication is authorized.

## Scope
The existing Toolkit CI workflow installs the package, runs Python unittest tests, performs synthetic CLI smoke checks, and generates Markdown and HTML reports. Phase 02 preserves these checks and adds a portable JSON evidence record. It does not supersede distribution, release-candidate, or supply-chain workflows.

## Controlled requirements and acceptance

| ID | Requirement | Verification |
| --- | --- | --- |
| DVO2-CI-001 | Capture a passing, nonempty unittest run and hash its log | Contract tests and CI artifact |
| DVO2-CI-002 | Record the GitHub-tested commit and originating PR head SHA separately | Manifest source fields |
| DVO2-CI-003 | Record SHA-256 and byte length for each synthetic report | Contract tests and artifact inspection |
| DVO2-CI-004 | Reject missing evidence, failing tests, and invalid source SHAs | Negative contract tests |
| DVO2-CI-005 | Retain JSON manifest and test log per successful CI run | Actions artifact retention of 30 days |
| DVO2-REL-001 | Never equate CI success with production or release approval | Manifest approval field remains false |

## Execution and review procedure

1. A pull request triggers Toolkit CI with read-only repository access.
2. The unittest command uses Bash pipefail, so a failing test still fails the job when output is captured with tee.
3. The synthetic installed CLI and Markdown/HTML report generation must complete before evidence creation.
4. The generator verifies a passing unittest summary, source revision fields, and nonempty report files; it computes SHA-256 hashes.
5. Actions uploads the JSON and test log as a run-specific artifact. The example reports remain available under their existing artifact.
6. Reviewer compares the PR, Actions run URL, tested source revision, evidence hashes, and release acceptance controls.
7. CI success is only an integration gate. The release candidate and supply-chain verification workflows remain independently required.

For pull_request events, GITHUB_SHA generally identifies the tested merge commit, while SOURCE_HEAD_SHA identifies the original PR head revision. Neither field is a cryptographic attestation. This record is not a signed provenance statement.

## Local contract verification

    python -m unittest discover -s tests -p 'test_ci_evidence.py' -v

To create sample evidence locally, provide a captured successful unittest log, existing nonempty report files, and real 40-character commit SHAs in GITHUB_SHA and SOURCE_HEAD_SHA. Local evidence is not proof of a successful hosted CI run.

## Engineering Knowledge Graph linkage (proposed)

| Entity | Identifier convention | Relationship |
| --- | --- | --- |
| Repository | WT:REPO:WITRT | HAS_WORKFLOW |
| Workflow | WT:CIWF:WITRT:TOOLKIT-CI | EXECUTES |
| CI run | WT:CIRUN:GH:{run_id}:{attempt} | VERIFIES |
| Revision | WT:COMMIT:WITRT:{sha} | IMPLEMENTS |
| Artifact | WT:ARTIFACT:SHA256:{digest} | DERIVED_FROM |
| Requirement | WT:REQ:DVO2-CI-001 | VERIFIED_BY |

Insert into a central Software Engineering Knowledge Graph only after database authority and target identifiers are established. This PR does not mutate a central knowledge-graph database.

## Constraints and follow-ups

- No automatic releases, production credentials, environments, Kubernetes, containers, cloud provisioning, or direct changes to main.
- Main currently lacks enforced branch protection. Required CI checks and PR review controls need an authorized administrator's configuration.
- The v0.2.0 release acceptance checklist, packaging matrix, SBOM, attestations, and separate open PRs remain independently gated.
- Download and inspect real GitHub-hosted output before changing status from proposed to verified.
