from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.genuine_blocker_resolution_execution import (
    build_genuine_blocker_resolution_execution,
    load_genuine_blocker_resolution_execution_contract,
    validate_genuine_blocker_resolution_execution_artifact,
    validate_genuine_blocker_resolution_execution_contract,
    write_genuine_blocker_resolution_execution,
)


def test_genuine_blocker_resolution_execution_runs_all_safe_packages() -> None:
    run = build_genuine_blocker_resolution_execution()
    artifact = run["genuine_blocker_resolution_execution_artifact"]
    contract = load_genuine_blocker_resolution_execution_contract()

    assert run["genuine_blocker_resolution_execution_ready"] is True
    assert run["work_package_count"] == 5
    assert run["safe_executable_work_package_count"] == 5
    assert run["executed_work_package_count"] == 5
    assert run["still_genuine_blocked_work_package_count"] == 5
    assert run["pre_resolution_blocked_scenario_count"] == 5
    assert run["post_resolution_blocked_scenario_count"] == 5
    assert run["post_resolution_comparable_scenario_count"] == 0
    assert run["false_resolution_count"] == 0
    assert run["new_accuracy_metric_computed_count"] == 0
    assert run["economic_performance_metric_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False
    assert validate_genuine_blocker_resolution_execution_contract(contract)[
        "contract_schema_valid"
    ] is True
    assert validate_genuine_blocker_resolution_execution_artifact(
        artifact,
        contract=contract,
    )["artifact_schema_valid"] is True


def test_resolution_profiles_preserve_blockers_without_runtime_mutation() -> None:
    artifact = build_genuine_blocker_resolution_execution()[
        "genuine_blocker_resolution_execution_artifact"
    ]

    for profile in artifact["scenario_resolution_profiles"]:
        assert profile["pre_resolution_status"] == "blocked"
        assert profile["post_resolution_status"] == "blocked"
        assert profile["comparable_after_resolution"] is False
        assert profile["still_blocked"] is True
        assert profile["label_used_by_runtime"] is False
        assert profile["evidence_rule_modified"] is False
        assert profile["predicted_mapping_rule_modified"] is False
        assert profile["threshold_modified"] is False
        assert profile["false_resolution_detected"] is False
        assert "preserve_blocker_with_documented_reason" in profile[
            "resolution_actions_executed"
        ]


def test_genuine_blocker_resolution_execution_writes_tmp_only(
    tmp_path: Path,
) -> None:
    output = tmp_path / "phase33_resolution_execution.json"
    result = write_genuine_blocker_resolution_execution(
        build_genuine_blocker_resolution_execution(),
        output=output,
    )

    assert result["genuine_blocker_resolution_execution_written"] is True
    assert output.is_file()


def test_genuine_blocker_resolution_execution_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_genuine_blocker_resolution_execution(
            build_genuine_blocker_resolution_execution(),
            output="data/backtests/phase33_resolution_execution.json",
        )


def test_run_genuine_blocker_resolution_execution_script(tmp_path: Path) -> None:
    output = tmp_path / "phase33_resolution_execution.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_genuine_blocker_resolution_execution.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "genuine_blocker_resolution_execution_ready=true" in result.stdout
    assert "executed_work_package_count=5" in result.stdout
    assert output.is_file()
