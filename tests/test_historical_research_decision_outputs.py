from __future__ import annotations

from typing import Any

from business_cycle.validation.historical_research_decision_outputs import (
    load_historical_research_decision_output_artifact_contract,
    summarize_historical_research_decision_outputs,
    validate_historical_research_decision_output_artifact,
)


def test_research_decision_outputs_are_research_only_and_metric_free() -> None:
    summary = summarize_historical_research_decision_outputs()

    assert summary["research_decision_output_artifact_contract_ready"] is True
    assert summary["research_decision_output_runtime_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["research_decision_output_count"] == 5
    assert summary["output_mode_research_only_count"] == 5
    assert summary["predicted_label_output_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_scope"] == "none"
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0


def test_research_decision_output_artifacts_contain_only_allowed_fields() -> None:
    summary = summarize_historical_research_decision_outputs()
    contract = load_historical_research_decision_output_artifact_contract()
    allowed = set(contract["allowed_artifact_fields"])
    forbidden = set(contract["forbidden_artifact_fields"])

    for artifact in summary["artifact_run"]["research_decision_outputs"]:
        assert set(artifact) == allowed
        assert artifact["output_mode"] == "research_historical_validation_only"
        assert artifact["label_used_by_runtime"] is False
        assert artifact["trust_metadata"]["label_used_by_runtime"] is False
        assert artifact["trust_metadata"]["metric_computation_scope"] == "none"
        assert artifact["trust_metadata"]["candidate_phase_emitted"] is False
        assert artifact["trust_metadata"]["current_phase_emitted"] is False
        assert forbidden.isdisjoint(_all_keys(artifact))


def test_forbidden_prediction_or_metric_fields_are_rejected() -> None:
    summary = summarize_historical_research_decision_outputs()
    artifact = dict(summary["artifact_run"]["research_decision_outputs"][0])
    artifact["trust_metadata"] = dict(artifact["trust_metadata"])
    artifact["trust_metadata"]["predicted_label"] = "recession"
    artifact["historical_accuracy"] = 1.0

    validation = validate_historical_research_decision_output_artifact(artifact)

    assert validation["artifact_schema_valid"] is False
    assert validation["predicted_label_output_count"] == 1
    assert validation["prohibited_artifact_field_count"] == 2


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
