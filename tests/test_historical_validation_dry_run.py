from __future__ import annotations

from typing import Any

from business_cycle.validation.historical_validation_dry_run import (
    summarize_historical_validation_dry_run,
)
from business_cycle.validation.historical_validation_result_writer import (
    load_historical_validation_dry_run_contract,
)


def test_historical_validation_dry_run_is_label_blind_and_metric_free() -> None:
    summary = summarize_historical_validation_dry_run()

    assert summary["historical_validation_dry_run_contract_ready"] is True
    assert summary["historical_validation_dry_run_executed"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_dry_run_result_count"] == 5
    assert summary["locked_execution_plan_used"] is True
    assert summary["label_blind_execution_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["model_execution_count"] == 5
    assert summary["real_historical_validation_executed"] is True
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["holdout_registered"] is False
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_result_field_count"] == 0


def test_historical_validation_dry_run_artifacts_contain_no_forbidden_fields() -> None:
    summary = summarize_historical_validation_dry_run()
    contract = load_historical_validation_dry_run_contract()
    forbidden = set(contract["forbidden_result_fields"])

    for artifact in summary["dry_run"]["result_artifacts"]:
        assert artifact["label_provenance_verified"] is True
        assert artifact["label_used_by_runtime"] is False
        assert artifact["decision_runtime_executed"] is True
        assert artifact["metric_computation_enabled"] is False
        assert artifact["backtest_execution_enabled"] is False
        assert artifact["candidate_phase_emitted"] is False
        assert artifact["current_phase_emitted"] is False
        assert "expected_label" not in artifact
        assert "predicted_label" not in artifact
        assert forbidden.isdisjoint(_all_keys(artifact))


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
