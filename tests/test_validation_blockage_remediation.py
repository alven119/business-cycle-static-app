from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from business_cycle.validation.validation_blockage_remediation import (
    build_validation_blockage_remediation,
    load_validation_blockage_remediation_contract,
    summarize_validation_blockage_remediation,
    validate_validation_blockage_remediation_artifact,
    validate_validation_blockage_remediation_contract,
    write_validation_blockage_remediation,
)


FORBIDDEN_REMEDIATION_FIELDS = {
    "economic_return",
    "excess_return",
    "portfolio_return",
    "performance_metric",
    "sharpe",
    "max_drawdown",
    "CAGR",
    "trade_action",
    "portfolio_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "candidate_phase",
    "current_phase",
    "production_phase",
}


def test_validation_blockage_remediation_contract_and_runtime_are_ready() -> None:
    summary = summarize_validation_blockage_remediation()

    assert summary["validation_blockage_remediation_contract_ready"] is True
    assert summary["validation_blockage_remediation_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["pre_remediation_blocked_scenario_count"] == 5
    assert summary["post_remediation_blocked_scenario_count"] == 5
    assert summary["reviewed_blocker_count"] == 5
    assert summary["safe_remediation_candidate_count"] == 0
    assert summary["safe_remediation_executed_count"] == 0
    assert summary["genuine_blocker_count"] == 5
    assert summary["unresolved_blocker_count"] == 5
    assert summary["false_resolution_count"] == 0
    assert summary["remediation_action_executed"] is False
    assert summary["rule_modified_count"] == 0
    assert summary["evidence_rule_modified_count"] == 0
    assert summary["mapping_rule_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == (
        "existing_historical_accuracy_registry_only"
    )
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_remediation_artifact_preserves_genuine_blockers_without_false_resolution() -> None:
    contract = load_validation_blockage_remediation_contract()
    run = build_validation_blockage_remediation()
    artifact = run["validation_blockage_remediation_artifact"]

    assert validate_validation_blockage_remediation_contract(contract)[
        "contract_schema_valid"
    ] is True
    validation = validate_validation_blockage_remediation_artifact(
        artifact,
        contract=contract,
    )
    assert validation["artifact_schema_valid"] is True
    assert validation["prohibited_artifact_field_count"] == 0
    assert FORBIDDEN_REMEDIATION_FIELDS.isdisjoint(_all_keys(artifact))
    assert artifact["research_only"] is True
    assert artifact["validation_only"] is True
    assert artifact["false_resolution_count"] == 0
    assert artifact["post_remediation_blocked_scenario_count"] == 5
    for profile in artifact["scenario_remediation_profiles"]:
        assert profile["blocker_type"] == "genuine_model_gate_or_evidence_limitation"
        assert profile["remediation_allowed"] is False
        assert profile["remediation_executed"] is False
        assert profile["still_blocked"] is True
        assert profile["false_resolution_detected"] is False
        assert profile["evidence_rule_modified"] is False
        assert profile["mapping_rule_modified"] is False
        assert profile["threshold_modified"] is False
        assert profile["label_used_by_runtime"] is False


def test_validation_blockage_remediation_writer_uses_tmp_only(tmp_path: Path) -> None:
    run = build_validation_blockage_remediation()
    output = tmp_path / "phase31_validation_blockage_remediation.json"

    write_result = write_validation_blockage_remediation(run, output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["validation_blockage_remediation_artifact_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["scenario_count"] == 5
    assert payload["pre_remediation_blocked_scenario_count"] == 5
    assert payload["post_remediation_blocked_scenario_count"] == 5
    assert payload["safe_remediation_candidate_count"] == 0
    assert payload["false_resolution_count"] == 0
    assert payload["new_accuracy_metric_computed_count"] == 0
    assert payload["economic_performance_metric_count"] == 0
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False


def test_validation_blockage_remediation_writer_rejects_repo_outputs() -> None:
    run = build_validation_blockage_remediation()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_validation_blockage_remediation(
            run,
            output="data/backtests/phase31_validation_blockage_remediation.json",
        )


def test_run_validation_blockage_remediation_script(tmp_path: Path) -> None:
    output = tmp_path / "remediation.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_validation_blockage_remediation.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "validation_blockage_remediation_contract_ready=true" in result.stdout
    assert "validation_blockage_remediation_runtime_ready=true" in result.stdout
    assert "reviewed_blocker_count=5" in result.stdout
    assert "safe_remediation_candidate_count=0" in result.stdout
    assert "false_resolution_count=0" in result.stdout
    assert "economic_performance_metric_count=0" in result.stdout
    assert output.is_file()


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()
