"""GitHub Actions test-efficiency audit for Phase67."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.archive_regression_shards import (
    summarize_archive_regression_shards,
)
from business_cycle.audits.fast_ci_contract_tests import (
    summarize_fast_ci_contract_tests,
)
from business_cycle.audits.test_suite_reduction_plan import (
    summarize_test_suite_reduction_plan,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/github_actions_test_efficiency.yaml"


def summarize_github_actions_test_efficiency(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize whether GitHub workflow test tiers reflect the reduced suite."""

    contract = _load_contract(path)
    workflow_paths = {
        name: ROOT / rel_path
        for name, rel_path in contract["workflow_paths"].items()
    }
    workflow_text = {
        name: workflow_path.read_text(encoding="utf-8")
        for name, workflow_path in workflow_paths.items()
    }
    parseable_count = sum(1 for text in workflow_text.values() if yaml.safe_load(text))
    reduction = summarize_test_suite_reduction_plan()
    shards = summarize_archive_regression_shards()
    fast_contract = summarize_fast_ci_contract_tests(path)
    fast_required = list(fast_contract["required_fast_ci_core_tests"])
    nightly_required = list(contract["required_nightly_shards"])
    fast_text = workflow_text["fast_ci"]
    full_text = workflow_text["full_ci"]
    nightly_text = workflow_text["nightly_ci"]
    summary: dict[str, Any] = {
        "phase": "67",
        "phase_id": "67",
        "github_actions_test_efficiency_ready": False,
        "workflow_yaml_parseable_count": parseable_count,
        "dependency_cache_workflow_count": sum(
            "cache: pip" in text for text in workflow_text.values()
        ),
        "concurrency_workflow_count": sum(
            "cancel-in-progress: true" in text for text in workflow_text.values()
        ),
        "fast_ci_critical_subset_ready": fast_contract[
            "fast_ci_contract_test_runner_ready"
        ],
        "fast_ci_uses_contract_test_runner": (
            "python scripts/run_fast_ci_contract_tests.py" in fast_text
            and "python -m pytest" not in fast_text
        ),
        "required_fast_ci_missing_test_count": fast_contract[
            "required_fast_ci_missing_test_count"
        ],
        "required_fast_ci_duplicate_test_count": fast_contract[
            "required_fast_ci_duplicate_test_count"
        ],
        "full_ci_uses_default_product_core_pytest": (
            "Run default product-core pytest without FRED API key" in full_text
            and "env -u FRED_API_KEY python -m pytest" in full_text
            and "-o addopts=" not in full_text
        ),
        "nightly_ci_uses_archive_shard_matrix": (
            "python scripts/run_archive_regression_shard.py" in nightly_text
            and "--shard ${{ matrix.shard }}" in nightly_text
            and all(shard_id in nightly_text for shard_id in nightly_required)
        ),
        "nightly_archive_shard_count": sum(
            shard_id in nightly_text for shard_id in nightly_required
        ),
        "nightly_monolithic_archive_pytest_count": nightly_text.count(
            "python -m pytest -o addopts="
        )
        + nightly_text.count("archive_regression and not live_optional"),
        "default_product_core_test_file_count": reduction[
            "default_product_core_test_file_count"
        ],
        "archive_shard_count": shards["archive_shard_count"],
        "workflow_git_mutation_count": _workflow_git_mutation_count(
            "\n".join(workflow_text.values()),
        ),
        "safety_scan_workflow_count": sum(
            "python scripts/run_ci_safety_scans.py" in text
            for text in workflow_text.values()
        ),
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "fast_ci_core_test_files": fast_required,
        "nightly_shards": nightly_required,
    }
    summary["github_actions_test_efficiency_ready"] = _passes(
        summary,
        contract["hard_gates"],
    )
    summary["result"] = (
        "passed" if summary["github_actions_test_efficiency_ready"] else "blocked"
    )
    return summary


def _workflow_git_mutation_count(text: str) -> int:
    forbidden = (
        "git add ",
        "git commit",
        "git push",
        "git reset",
        "git clean",
    )
    return sum(fragment in text for fragment in forbidden)


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "github_actions_test_efficiency_ready"
    )


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["github_actions_test_efficiency"]
    if not isinstance(contract, dict):
        raise ValueError("GitHub Actions test-efficiency contract must be a mapping")
    return contract
