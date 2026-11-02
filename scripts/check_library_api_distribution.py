#!/usr/bin/env python3
"""Read-only installed-distribution smoke test (standard library only)."""
from __future__ import annotations

import argparse
import importlib.metadata as metadata
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distribution", default="wisdom-it-readiness-toolkit")
    args = parser.parse_args()
    import wisdom_it_readiness as api
    import scorer
    import cli

    if api.score_assessment is not scorer.score_assessment:
        raise SystemExit("scoring identity mismatch")
    if not callable(api.generate_markdown_report) or not callable(api.generate_html_report):
        raise SystemExit("report renderers unavailable")
    if not callable(cli.main):
        raise SystemExit("witrt CLI entry point unavailable")
    dist = metadata.distribution(args.distribution)
    entry_points = {(ep.name, ep.value) for ep in dist.entry_points if ep.group == "console_scripts"}
    if ("witrt", "cli:main") not in entry_points:
        raise SystemExit("console-script metadata changed")
    print(f"PASS: {dist.metadata['Name']}=={dist.version}; flat and namespaced imports resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
