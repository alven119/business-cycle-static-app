from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
    load_historical_validation_blockage_diagnostics_contract,
    summarize_historical_validation_blockage_diagnostics,
    validate_historical_validation_blockage_diagnostics_artifact,
    validate_historical_validation_blockage_diagnostics_contract,
    write_historical_validation_blockage_diagnostics,
)


FORBIDDEN_DIAGNOSTIC_FIELDS = {
    "accuracy",
    "precision",
    "recall",
    "f1",
    "hit_rate",
    "confusion_matrix",
    "economic_return",
    "excess_return",
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


def test_blockage_diagnostics_contract_and_runtime_are_ready() -> None:
    summary = summarize_historical_validation_blockage_diagnostics()

    assert summary["historical_validation_blockage_diagnostics_contract_ready"] is True
    assert summary["historical_validation_blockage_diagnostics_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_trace_count"] == 5
    assert summary["blockage_diagnostic_scenario_count"] == 5
    assert summary["blocked_scenario_count"] == 5
    assert summary["blockage_reason_summary_ready"] is True
    assert summary["remediation_plan_registry_ready"] is True
    assert summary["remediation_action_executed"] is False
    assert summary["rule_modified_count"] == 0
    assert summary["mapping_rule_modified_count"] == 0
    assert summary["threshold_modified_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["new_accuracy_metric_computed_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "diagnostic_summary_only"
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0


def test_blockage_diagnostics_schema_is_descriptive_only() -> None:
    contract = load_historical_validation_blockage_diagnostics_contract()
    run = build_historical_validation_blockage_diagnostics()
    artifact = run["blockage_diagnostics_artifact"]

    assert validate_historical_validation_blockage_diagnostics_contract(contract)[
        "contract_schema_valid"
    ] is True
    validation = validate_historical_validation_blockage_diagnostics_artifact(
        artifact,
        contract=contract,
    )
    assert validation["artifact_schema_valid"] is True
    assert validation["prohibited_artifact_field_count"] == 0
    assert FORBIDDEN_DIAGNOSTIC_FIELDS.isdisjoint(_all_keys(artifact))
    assert artifact["research_only"] is True
    assert artifact["validation_only"] is True
    assert artifact["scenario_count"] == 5
    assert artifact["blocked_scenario_count"] == 5
    assert artifact["blockage_reason_summary"]
    assert artifact["metric_skip_reason_summary"] == {
        "phase28_reference_label_values_are_provenance_only": 1
    }
    for item in artifact["remediation_plan_registry"]:
        assert item["status"] == "descriptive_only_not_executed"
        assert item["requires_new_preregistered_contract"] is True
        assert item["tuning_leakage_risk"] == "must_not_use_historical_results"


def test_blockage_diagnostics_writer_uses_tmp_only(tmp_path: Path) -> None:
    run = build_historical_validation_blockage_diagnostics()
    output = tmp_path / "phase30_blockage_diagnostics.json"

    write_result = write_historical_validation_blockage_diagnostics(
        run,
        output=output,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["blockage_diagnostics_artifact_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["scenario_count"] == 5
    assert payload["blockage_diagnostic_scenario_count"] == 5
    assert payload["blocked_scenario_count"] == 5
    assert payload["new_accuracy_metric_computed_count"] == 0
    assert payload["economic_performance_metric_count"] == 0
    assert payload["remediation_action_executed"] is False


def test_blockage_diagnostics_writer_rejects_repo_outputs() -> None:
    run = build_historical_validation_blockage_diagnostics()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_historical_validation_blockage_diagnostics(
            run,
            output="data/backtests/phase30_blockage_diagnostics.json",
        )


def test_generate_blockage_diagnostics_script(tmp_path: Path) -> None:
    output = tmp_path / "blockage.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_historical_validation_blockage_diagnostics.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "historical_validation_blockage_diagnostics_contract_ready=true"
        in result.stdout
    )
    assert (
        "historical_validation_blockage_diagnostics_runtime_ready=true"
        in result.stdout
    )
    assert "blockage_diagnostic_scenario_count=5" in result.stdout
    assert "remediation_action_executed=false" in result.stdout
    assert "new_accuracy_metric_computed_count=0" in result.stdout
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
