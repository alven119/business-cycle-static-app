#!/usr/bin/env python
"""Run CI safety scans against tracked text files and generated-output paths."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


TRACKED_GENERATED_PATTERN = re.compile(
    r"(__pycache__|\.pyc|\.pytest_cache|\.ruff_cache|\.mypy_cache|"
    r"data/raw|data/backtests|data/prospective|public)"
)
SCAN_PATHS = ("README.md", "docs", "specs", "src", "scripts", "tests", ".github")


def main() -> int:
    failures: list[str] = []
    failures.extend(_scan_tracked_generated_files())
    failures.extend(_git_grep_fixed(_secret_pattern(), "Inline FRED API key assignment"))
    failures.extend(_git_grep_extended(_claim_pattern(), "Unsupported product readiness claim"))
    failures.extend(_scan_generated_output_paths())
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("ci_safety_scans=passed")
    return 0


def _scan_tracked_generated_files() -> list[str]:
    tracked = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    matches = [path for path in tracked if TRACKED_GENERATED_PATTERN.search(path)]
    return _format_matches("Tracked generated/cache/output file detected", matches)


def _git_grep_fixed(pattern: str, label: str) -> list[str]:
    return _git_grep(["git", "grep", "-nI", "-F", pattern, "--", *SCAN_PATHS], label)


def _git_grep_extended(pattern: str, label: str) -> list[str]:
    return _git_grep(["git", "grep", "-nI", "-E", pattern, "--", *SCAN_PATHS], label)


def _git_grep(command: list[str], label: str) -> list[str]:
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode == 0:
        return _format_matches(label, completed.stdout.splitlines())
    if completed.returncode == 1:
        return []
    return [f"{label}: git grep failed: {completed.stderr.strip()}"]


def _scan_generated_output_paths() -> list[str]:
    matches: list[str] = []
    for root_name in ("data/backtests", "data/prospective", "public"):
        root = Path(root_name)
        if root.exists():
            matches.extend(str(path) for path in root.rglob("*") if path.is_file())
    if Path("data/backtests/research").exists():
        matches.append("data/backtests/research")
    return _format_matches("Generated backtest, prospective, or public output detected", matches)


def _format_matches(label: str, matches: list[str]) -> list[str]:
    if not matches:
        return []
    return [f"{label}:", *matches]


def _secret_pattern() -> str:
    return "FRED_API_KEY" + "="


def _claim_pattern() -> str:
    forbidden_claims = (
        "book-faithful model " + "complete",
        "candidate phase " + "ready",
        "prospective monitoring " + "started",
        "economically " + "validated",
        "holdout " + "active",
        "production-" + "ready",
        "real backtest " + "ready",
        "investment-" + "ready",
    )
    return "|".join(re.escape(claim) for claim in forbidden_claims)


if __name__ == "__main__":
    raise SystemExit(main())
