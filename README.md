# Wisdom IT Readiness Toolkit

A governed open-source toolkit for assessing and improving practical technology readiness for individuals, founders, working professionals, and small businesses.

## Current release

**v0.1.0 released**

The first public release provides a Technology Readiness Quick Check, deterministic weighted scoring, maturity classification, JSON output, Markdown report generation, synthetic example data, tests, and continuous integration.

## Quick start

```bash
python src/cli.py score assessments/quick-check-v0.1.json examples/synthetic-responses.json
```

Generate a Markdown report:

```bash
python src/cli.py report assessments/quick-check-v0.1.json examples/synthetic-responses.json \
  --subject "Synthetic Demonstration" \
  --data-note "Synthetic demonstration only" \
  --output build/example-report.md
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Readiness domains

- Strategy and goals
- Devices and infrastructure
- Cybersecurity and resilience
- Support and governance

## Maturity model

1. Unprepared
2. Basic
3. Repeatable
4. Managed
5. Optimized

## Governance and privacy

The toolkit operates locally and does not transmit assessment data. Users are responsible for protecting response files and generated reports. Scores support structured decision-making but do not replace professional judgment, security testing, or regulatory assessment.

## License

MIT License. See `LICENSE`.

## Development installation and errors

The unreleased v0.2.0 work adds strict validation, bundled assessment access, and documented CLI exit codes. See [installation and troubleshooting](docs/installation-and-errors.md) and the [requirements baseline](docs/requirements-v0.2.0.md). Published v0.1.0 artifacts are unchanged.

The development CLI also adds [deterministic recommendations and coverage](docs/recommendations.md) to JSON and Markdown; see the synthetic examples and documented limitations.

Standalone HTML is available in development with explicit `--format html`; see [HTML reports and accessibility checks](docs/html-reports.md), [prepared v0.2.0 release notes](RELEASE_NOTES_v0.2.0.md), and the [development case study](docs/toolkit-case-study.md). Published release references remain v0.1.0.
