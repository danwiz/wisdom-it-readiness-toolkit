# Permission-failure verification

AC-05 now has real permission-denial regression cases in
`tests/test_cli_permissions.py`. They run automatically in unittest discovery on
POSIX under a non-root user, including the Ubuntu/macOS distribution jobs.
They explicitly skip on Windows (different ACL semantics) and root (which can
bypass mode bits). A skipped case is not evidence that permission denial passed.

The fixtures verify that access is actually denied before running the CLI:

- Unreadable response file: exit 1, empty stdout, concise stderr, existing
  Markdown/HTML report unchanged and response bytes preserved.
- Unwritable report directory: both new and existing destinations fail with
  exit 1, preserving responses/reports and leaving no temporary files.

Permission changes are confined to temporary fixtures and restored in `finally`.
The tests do not change permissions on repository or user files.
Windows retains missing-file and directory-as-output coverage in the installed
CLI script; Windows ACL-specific denial remains unverified.

## Local evidence — 2026-10-29

This runtime runs as root and denied an attempt to start a test subprocess
under the `nobody` account (Operation not permitted). The two permission tests
therefore skip locally; no local permission-denial pass is claimed.
Production code and the package version are unchanged.
The new remote CI results must be checked at the submitted commit; prior PR #21
CI results do not cover these new tests.
