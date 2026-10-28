# Wisdom IT Readiness Toolkit

**Technology Readiness Quick Check** — a local, deterministic command-line assessment for individuals, founders, working professionals, and small businesses seeking an initial view of technology-readiness strengths, gaps, and remediation priorities.

> **Status:** v0.1.0 released. This is a guided self-assessment and planning aid, **not** a security audit, regulatory certification, risk guarantee, or substitute for professional advice.

## Who it is for and what it does

- Individuals and professionals reviewing their essential digital tools and work practices.
- Founders and small-business operators preparing to improve basic infrastructure, security, and support processes.
- IT consultants facilitating an evidence-led **Technology Readiness Quick Check** as the first step toward a scoped improvement plan.

The v0.1.0 workflow reads an assessment definition and a JSON response file, validates numeric responses, computes weighted scores by domain and overall, assigns an assessment-defined maturity level, and prints JSON or writes a Markdown report. It uses synthetic example data by default and runs locally.

**Not included in v0.1.0:** automatic vulnerability scanning, third-party system discovery, authentication, hosted assessment storage, client-data ingestion, validated professional conclusions, or full remediation implementation. Richer reports and tailored recommendations belong to the proposed [v0.2.0 roadmap](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/5) and are not shipped capabilities.

## Prerequisites

- Python **3.11 or newer** and a working Python/pip installation.
- A local shell or terminal with permission to read assessment files and write your chosen report path.
- No cloud account or API key is needed for the released CLI.

## Install and run the Quick Check

From the repository root, install the package:

```bash
python -m pip install .
```

Score the bundled synthetic example (writes a JSON result to standard output):

```bash
witrt score assessments/quick-check-v0.1.json examples/synthetic-responses.json
```

Generate a Markdown report:

```bash
witrt report assessments/quick-check-v0.1.json examples/synthetic-responses.json \
  --subject "Synthetic Demonstration" \
  --data-note "Synthetic demonstration only" \
  --output build/example-report.md
```

The `--output` path is created locally (including its parent directory if needed). Replace only the two JSON input paths with your **own locally protected files** when you are ready to assess a real environment. The example responses do not describe a real client.

To run directly from source without installation, replace `witrt` with `python src/cli.py` in the two commands above.

## Assessment domains and scoring

The bundled [Quick Check definition](assessments/quick-check-v0.1.json) contains nine questions across four domains:

| Domain | Example considerations |
| --- | --- |
| Strategy and Goals | Documented technology priorities and accountable decision-makers |
| Devices and Infrastructure | Device inventory, Internet/Wi-Fi, continuity of essential services |
| Cybersecurity and Resilience | MFA, backups/restoration, security updates |
| Support and Governance | Support/incident handling, risk and improvement reviews |

Each response is an integer on the assessment's defined **0–2** scale: `0` = not in place, `1` = partially in place, and `2` = consistently in place. Questions carry positive numeric weights. The scorer normalizes each answered response between the minimum and maximum scale values, calculates a weighted percentage for each represented domain and overall, and rounds to two decimal places.

Unanswered questions are reported separately and **excluded** from the percentage denominator. Consequently, a high score with missing responses can overstate readiness; inspect the `unanswered_questions` field and report section before drawing conclusions. At least one valid answered question is required. The score does not measure the actual effectiveness of a security control.

The current assessment maps the overall percentage to these maturity bands:

| Level | Label | Overall score |
| --- | --- | --- |
| 1 | Unprepared | 0–24.99% |
| 2 | Basic | 25–44.99% |
| 3 | Repeatable | 45–64.99% |
| 4 | Managed | 65–84.99% |
| 5 | Optimized | 85–100% |

The JSON result contains `overall_percent`, `maturity_level`, `maturity_label`, `domain_scores`, and `unanswered_questions`. The Markdown report shows the overall result, domains, a small set of **generic** priority actions based on the lowest domain scores, evidence required for closure, and any missing responses. These are planning prompts, not a validated recommendation engine.

## Repository map

| Path | Responsibility |
| --- | --- |
| [`assessments/`](assessments/) | Versioned assessment definition and scoring scale |
| [`examples/`](examples/) | Synthetic response data for safe demonstrations |
| [`src/scorer.py`](src/scorer.py) | Input handling, deterministic weighted scoring, maturity mapping |
| [`src/report.py`](src/report.py) | Markdown report rendering and generic follow-up actions |
| [`src/cli.py`](src/cli.py) | `score` and `report` command-line entry points |
| [`tests/`](tests/) | Unit and characterization tests for scorer, report, and CLI |
| [`.github/workflows/`](.github/workflows/) | CI and supply-chain evidence automation |
| [`docs/`](docs/) | Release notes, verification, and governance records |
| [`SECURITY.md`](SECURITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) | Disclosure, review, and contribution boundaries |

## Testing and reproducibility

```bash
python -m unittest discover -s tests -v
```

The [`Toolkit CI` workflow](.github/workflows/ci.yml) installs the package, runs tests, exercises the installed `witrt` command against synthetic inputs, generates a Markdown report, checks for expected report headings, and uploads that report as a time-limited workflow artifact. Check the latest successful run for the commit you intend to use; historical artifacts can expire.

The public [v0.1.0 release](https://github.com/danwiz/wisdom-it-readiness-toolkit/releases/tag/v0.1.0) and [versioned release notes](docs/releases/v0.1.0.md) describe the released baseline. A newer green CI run on `main` does not retroactively change the original tagged release.

## Privacy, security, and governance

- The CLI reads input locally and writes output locally; the current code has no application-network submission step. Files can still be exposed by your own terminal, backups, version control, file-sharing, or endpoint configuration.
- **Never commit real customer responses, credentials, identifiers, sensitive system inventories, or confidential reports.** The checked-in examples are intentionally synthetic.
- Treat outputs as potentially sensitive operational documents and apply appropriate storage, access controls, and retention rules.
- Verify every answer with appropriate organizational evidence. A self-reported score is not an audit finding, compliance attestation, or proof that a control works.
- Review [`SECURITY.md`](SECURITY.md) before reporting vulnerabilities. Follow [`CONTRIBUTING.md`](CONTRIBUTING.md) for proposed code and documentation changes; avoid publishing private issue details.
- Reproduction of a score requires preserving the assessment version, exact response values, and relevant execution environment.

## Roadmap and participation

The next proposal is [v0.2.0](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/5), with separate work items for [requirements and compatibility](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/6), [recommendations](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/7), [packaging](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/8), and [reporting/release evidence](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/9). These are open plans, **not** release promises or implemented features.

Documentation and code contributions should use a reviewed pull request with tests/evidence proportionate to the change. The [`README` pilot issue](https://github.com/danwiz/wisdom-it-readiness-toolkit/issues/10) is specifically documentation-only and must not be merged without independent review.

## License

Released under the [MIT License](LICENSE).
