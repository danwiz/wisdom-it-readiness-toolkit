# Standalone HTML reports (v0.2.0 development)

```sh
witrt report builtin:quick-check examples/synthetic-responses.json \
  --format html --subject "Synthetic Demonstration" \
  --data-note "Synthetic demonstration only" --output build/readiness.html
```

Open the resulting file locally in a browser. It contains its own styling and
needs no server, JavaScript, external fonts, images or network connection.
Print using the browser's normal print command. Generated reports may contain
confidential subject names and responses: store and share them deliberately.
Package installation can download dependencies; scoring and report generation
perform no network operations.

`--format markdown` is the default. The extension does not choose a renderer;
an `.html` filename without `--format html` still receives Markdown.
JSON remains available through `witrt score`.

HTML includes subject, assessment ID/version, data provenance, overall score,
maturity, response coverage, domain scores, prioritized actions, limitations,
closure evidence and unanswered question IDs. Completely unanswered domains
show **Unavailable**, never zero. Partial assessments carry a visible warning.
Every user-controlled string is HTML-escaped; it cannot create links, scripts
or other active markup. Reports use a restrictive content security policy.

## Accessibility and verification

The document declares English, UTF-8 and viewport metadata, has one main landmark
and one H1, ordered section headings, text priorities (not color-only meaning),
and a table with caption and row/column headers. There are no interactive
controls or custom keyboard handlers. Browser scrolling, search and print remain
native. Body text uses #172536 on white; notices use the same text on #eef3f7.
Styles adapt at narrow widths and for printing.

Automated tests inspect semantics, injection handling, parity, determinism,
incomplete data and input immutability. Installed wheel and sdist checks verify
explicit/default format behavior, repeated bytes, errors and output preservation.
A recorded visual/keyboard/screen-reader review is still a release gate; these
structural checks are not a WCAG certification.

Examples: [complete synthetic report](../examples/readiness-synthetic.html) and
[partial synthetic report](../examples/readiness-partial-synthetic.html).
