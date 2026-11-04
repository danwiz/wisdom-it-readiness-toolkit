#!/usr/bin/env python3
"""Summarize successful unittest execution and hashed CI reports; no external dependencies."""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}\Z")
TEST_SUMMARY = re.compile(r"(?m)^Ran (\d+) tests? in ([\d.]+)s\s*$")
OK_LINE = re.compile(r"(?m)^OK(?:\s*\([^\n]*\))?\s*$")


def digest_file(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty evidence input: {path}")
    hash256 = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hash256.update(chunk)
    return {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": hash256.hexdigest()}


def summarize_unittest(text: str) -> dict:
    summaries = list(TEST_SUMMARY.finditer(text))
    if len(summaries) != 1:
        raise ValueError("Expected exactly one unittest summary in the test log")
    match = summaries[0]
    if int(match.group(1)) < 1 or not OK_LINE.search(text, match.end()):
        raise ValueError("Test log does not certify a passing, nonempty unittest run")
    if re.search(r"(?m)^FAILED\b", text[match.end():]):
        raise ValueError("Test log contains a FAILED summary")
    return {"framework": "unittest", "executed": int(match.group(1)), "result": "passed"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-log", type=Path, required=True)
    parser.add_argument("--report", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        tested_sha = os.environ.get("GITHUB_SHA", "")
        head_sha = os.environ.get("SOURCE_HEAD_SHA", tested_sha)
        if not SHA_PATTERN.fullmatch(tested_sha) or not SHA_PATTERN.fullmatch(head_sha):
            raise ValueError("GITHUB_SHA and SOURCE_HEAD_SHA must identify full Git commit SHAs")
        if args.output.resolve() in {p.resolve() for p in [args.test_log, *args.report]}:
            raise ValueError("Evidence output must not overwrite an input file")
        log_meta = digest_file(args.test_log)
        test_summary = summarize_unittest(args.test_log.read_text(encoding="utf-8"))
        report_paths = sorted(args.report, key=lambda x: x.as_posix())
        if len({p.resolve() for p in report_paths}) != len(report_paths):
            raise ValueError("Report inputs must be unique")
        reports = [digest_file(p) for p in report_paths]
        evidence = {
            "schema_version": "wisdom.devops.ci-evidence.v1",
            "stage": "continuous_integration",
            "release_or_deployment_approval": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": {
                "repository": os.environ.get("GITHUB_REPOSITORY", "local-validation"),
                "tested_commit_sha": tested_sha.lower(),
                "source_head_sha": head_sha.lower(),
                "ref": os.environ.get("GITHUB_REF", ""),
                "event": os.environ.get("GITHUB_EVENT_NAME", ""),
            },
            "execution": {
                "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
                "run_id": os.environ.get("GITHUB_RUN_ID", ""),
                "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            },
            "tests": {**test_summary, "log": log_meta},
            "reports": reports,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"CI evidence generation rejected: {exc}", file=sys.stderr)
        return 2
    print(f"CI evidence written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
