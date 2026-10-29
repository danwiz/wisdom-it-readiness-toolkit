"""Command-line interface for the Wisdom IT Readiness Toolkit."""

from __future__ import annotations

import argparse
import json
import sys
import os
import tempfile
from importlib.resources import files
from pathlib import Path

from report import generate_markdown_report
from html_report import generate_html_report
from scorer import load_json, parse_json, score_assessment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="witrt", description="Score technology readiness assessments")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score_parser = subparsers.add_parser("score", help="Score an assessment and print JSON")
    score_parser.add_argument("assessment")
    score_parser.add_argument("responses")
    score_parser.add_argument("--subject", default="Assessment subject")
    score_parser.add_argument("--data-note", default="User-provided assessment responses")

    report_parser = subparsers.add_parser("report", help="Generate a Markdown or standalone HTML readiness report")
    report_parser.add_argument("assessment")
    report_parser.add_argument("responses")
    report_parser.add_argument("--subject", default="Assessment subject")
    report_parser.add_argument("--data-note", default="User-provided assessment responses")
    report_parser.add_argument("--output", required=True)
    report_parser.add_argument("--format", choices=("markdown", "html"), default="markdown")
    return parser


def _load_assessment(reference: str) -> dict:
    if reference == "builtin:quick-check":
        return parse_json(files("wisdom_it_readiness_data").joinpath("quick-check-v0.1.json").read_text(encoding="utf-8"))
    return load_json(reference)


def _write_report(output: Path, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    args = build_parser().parse_args()
    try:
        assessment = _load_assessment(args.assessment)
        responses = load_json(args.responses)
        result = score_assessment(assessment, responses)
        if args.command == "score":
            payload = dict(result.__dict__)
            payload["metadata"] = {
                "assessment_id": assessment.get("assessment_id", "unknown"),
                "assessment_version": assessment["version"],
                "subject": args.subject,
                "data_note": args.data_note,
                "provenance_basis": "caller-supplied; not independently verified",
            }
            payload["limitations"] = [
                "Scores describe supplied responses, not security assurance or certification.",
                "Priorities are workflow priorities, not vulnerability severity.",
                "Review evidence with an accountable owner before acting.",
                ("Incomplete assessment: scores describe answered questions only and are provisional."
                 if result.coverage["incomplete"] else
                 "All questions answered; responses have not been independently verified."),
            ]
            print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
            return 0
        output = Path(args.output)
        # Never overwrite an input file, including paths that resolve through symlinks.
        sources = [Path(args.responses).resolve()]
        if args.assessment != "builtin:quick-check":
            sources.append(Path(args.assessment).resolve())
        if output.resolve() in sources or any(output.exists() and output.samefile(p) for p in sources):
            raise ValueError("Report output must be different from input files")
        renderer = generate_html_report if args.format == "html" else generate_markdown_report
        text = renderer(assessment, result, subject=args.subject, data_note=args.data_note)
        _write_report(output, text)
        print(output)
        return 0
    except (ValueError, UnicodeError, RecursionError) as exc:
        message = "Input nesting is too deep" if isinstance(exc, RecursionError) else str(exc)
        if isinstance(exc, UnicodeError):
            message = "Input files must contain UTF-8 text"
        print(f"witrt: {message}", file=sys.stderr)
        return 2
    except OSError:
        print("witrt: Cannot read input or write report; check file existence, permissions and output directory", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
