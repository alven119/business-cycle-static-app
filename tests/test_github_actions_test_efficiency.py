from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.github_actions_test_efficiency import (
    summarize_github_actions_test_efficiency,
)
from business_cycle.audits.fast_ci_contract_tests import (
    build_fast_ci_contract_test_command,
    summarize_fast_ci_contract_tests,
)


def test_github_actions_test_efficiency_passes() -> None:
    summary = summarize_github_actions_test_efficiency()

    assert summary["result"] == "passed"
    assert summary["github_actions_test_efficiency_ready"] is True
    assert summary["workflow_yaml_parseable_count"] == 3
    assert summary["dependency_cache_workflow_count"] == 3
    assert summary["concurrency_workflow_count"] == 3
    assert summary["fast_ci_critical_subset_ready"] is True
    assert summary["fast_ci_uses_contract_test_runner"] is True
    assert summary["required_fast_ci_missing_test_count"] == 0
    assert summary["required_fast_ci_duplicate_test_count"] == 0
    assert summary["full_ci_uses_default_product_core_pytest"] is True
    assert summary["nightly_ci_uses_archive_shard_matrix"] is True
    assert summary["nightly_archive_shard_count"] == 8
    assert summary["nightly_monolithic_archive_pytest_count"] == 0
    assert summary["default_product_core_test_file_count"] == 30
    assert summary["archive_shard_count"] == 8
    assert summary["workflow_git_mutation_count"] == 0
    assert summary["safety_scan_workflow_count"] == 3


def test_fast_ci_contract_test_runner_is_runnable_and_scope_limited() -> None:
    summary = summarize_fast_ci_contract_tests()
    command = build_fast_ci_contract_test_command()

    assert summary["result"] == "passed"
    assert summary["fast_ci_contract_test_runner_ready"] is True
    assert summary["required_fast_ci_core_test_count"] > 0
    assert summary["required_fast_ci_missing_test_count"] == 0
    assert summary["required_fast_ci_duplicate_test_count"] == 0
    assert summary["required_fast_ci_live_optional_test_count"] == 0
    assert command[0] == sys.executable
    assert "-o" in command
    assert "addopts=" in command
    assert "not live_optional" in command
    assert "tests/test_transition_risk_evidence_accumulation.py" in command


def test_show_github_actions_test_efficiency_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_github_actions_test_efficiency.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "github_actions_test_efficiency_ready=true" in completed.stdout
    assert "nightly_archive_shard_count=8" in completed.stdout
    assert "nightly_monolithic_archive_pytest_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
