# Wisdom IT Readiness Toolkit

A governed open-source toolkit for assessing and improving practical technology readiness for individuals, founders, working professionals, and small businesses.

## Current release

**v0.1.0 release candidate**

The initial release provides a Technology Readiness Quick Check, deterministic weighted scoring, maturity classification, JSON output, Markdown report generation, synthetic example data, tests, and continuous integration.

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
