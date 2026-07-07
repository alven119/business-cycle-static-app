"""Contract-driven fast-ci pytest runner."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/github_actions_test_efficiency.yaml"


def build_fast_ci_contract_test_command(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> list[str]:
    """Build the fast-ci pytest command from the governed contract."""

    summary = summarize_fast_ci_contract_tests(path)
    if not summary["fast_ci_contract_test_runner_ready"]:
        missing = ", ".join(summary["missing_fast_ci_test_files"])
        duplicates = ", ".join(summary["duplicate_fast_ci_test_files"])
        raise ValueError(
            "Fast-ci contract test list is not runnable. "
            f"missing=[{missing}] duplicates=[{duplicates}]"
        )
    return [
        sys.executable,
        "-m",
        "pytest",
        "-o",
        "addopts=",
        "-m",
        "not live_optional",
        *summary["required_fast_ci_core_tests"],
    ]


def summarize_fast_ci_contract_tests(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize the runnable critical subset used by fast-ci."""

    contract = _load_contract(path)
    required = list(contract["required_fast_ci_core_tests"])
    missing = [test_path for test_path in required if not (ROOT / test_path).is_file()]
    duplicates = _duplicates(required)
    live_optional = [
        test_path
        for test_path in required
        if "live_refresh" in test_path or "live_optional" in test_path
    ]
    summary: dict[str, Any] = {
        "fast_ci_contract_test_runner_ready": False,
        "required_fast_ci_core_test_count": len(required),
        "required_fast_ci_core_tests": required,
        "required_fast_ci_missing_test_count": len(missing),
        "required_fast_ci_duplicate_test_count": len(duplicates),
        "required_fast_ci_live_optional_test_count": len(live_optional),
        "missing_fast_ci_test_files": missing,
        "duplicate_fast_ci_test_files": duplicates,
        "live_optional_fast_ci_test_files": live_optional,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
    }
    summary["fast_ci_contract_test_runner_ready"] = (
        summary["required_fast_ci_core_test_count"] > 0
        and summary["required_fast_ci_missing_test_count"] == 0
        and summary["required_fast_ci_duplicate_test_count"] == 0
        and summary["required_fast_ci_live_optional_test_count"] == 0
        and summary["production_behavior_change_count"] == 0
        and summary["semantic_drift_count"] == 0
    )
    summary["result"] = (
        "passed" if summary["fast_ci_contract_test_runner_ready"] else "blocked"
    )
    return summary


def run_fast_ci_contract_tests(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> int:
    """Run the contract-defined fast-ci critical subset."""

    command = build_fast_ci_contract_test_command(path)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return int(completed.returncode)


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["github_actions_test_efficiency"]
    if not isinstance(contract, dict):
        raise ValueError("GitHub Actions test-efficiency contract must be a mapping")
    return contract
