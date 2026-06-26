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
    failures.extend(_scan_unsupported_product_claims())
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


def _scan_unsupported_product_claims() -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-nI", "-E", _claim_pattern(), "--", *SCAN_PATHS],
        capture_output=True,
        text=True,
    )
    label = "Unsupported product readiness claim"
    if completed.returncode == 1:
        return []
    if completed.returncode != 0:
        return [f"{label}: git grep failed: {completed.stderr.strip()}"]
    matches = [
        line
        for line in completed.stdout.splitlines()
        if not _approved_prohibited_claim_definition(line)
    ]
    return _format_matches(label, matches)


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


def _approved_prohibited_claim_definition(grep_line: str) -> bool:
    """Allow only explicit denylist/validator definitions, never user-facing text."""

    try:
        path_text, line_text, _ = grep_line.split(":", 2)
        line_number = int(line_text)
    except ValueError:
        return False

    path = Path(path_text)
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    index = line_number - 1
    if not 0 <= index < len(lines):
        return False
    if path == Path("specs/common/research_validation_dashboard_contract.yaml"):
        return _inside_yaml_list(lines, index, parent_key="prohibited_claims")
    if path == Path("src/business_cycle/render/research_validation_dashboard.py"):
        return _inside_python_tuple_assignment(lines, index, assignment_name="PROHIBITED_CLAIMS")
    if path == Path("scripts/run_ci_safety_scans.py"):
        return (
            "_claim_pattern" in "\n".join(lines[max(0, index - 12) : index + 3])
            or "forbidden_claims" in "\n".join(lines[max(0, index - 12) : index + 3])
        )
    return False


def _inside_yaml_list(lines: list[str], index: int, *, parent_key: str) -> bool:
    line = lines[index]
    if not line.startswith("    - "):
        return False
    for previous in range(index - 1, -1, -1):
        text = lines[previous]
        if not text.strip():
            continue
        if not text.startswith("  "):
            return False
        if text.strip() == f"{parent_key}:":
            return True
        if text.startswith("  ") and not text.startswith("    "):
            return False
    return False


def _inside_python_tuple_assignment(
    lines: list[str],
    index: int,
    *,
    assignment_name: str,
) -> bool:
    start = None
    for previous in range(index, -1, -1):
        text = lines[previous]
        if text.startswith(f"{assignment_name} = ("):
            start = previous
            break
        if text and not text.startswith((" ", "\t", "#")):
            break
    if start is None:
        return False
    for current in range(start + 1, len(lines)):
        if current >= index and lines[current].strip() == ")":
            return index < current
    return False


def _secret_pattern() -> str:
    return "FRED" + "_API_KEY" + "="


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
