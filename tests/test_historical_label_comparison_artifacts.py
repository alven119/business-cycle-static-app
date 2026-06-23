from __future__ import annotations

from typing import Any

from business_cycle.validation.historical_label_comparison_artifacts import (
    load_historical_label_comparison_artifact_contract,
    validate_historical_label_comparison_artifact,
)
from business_cycle.validation.historical_label_joiner import (
    summarize_historical_label_comparison_artifact_generation,
)


def test_label_comparison_artifact_generation_is_metric_free() -> None:
    summary = summarize_historical_label_comparison_artifact_generation()

    assert summary["label_comparison_artifact_contract_ready"] is True
    assert summary["label_comparison_artifact_generator_ready"] is True
    assert summary["label_joiner_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_provenance_verified_count"] == 5
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["label_comparison_executed"] is True
    assert summary["metric_computation_enabled"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_label_comparison_artifacts_contain_only_allowed_fields() -> None:
    summary = summarize_historical_label_comparison_artifact_generation()
    contract = load_historical_label_comparison_artifact_contract()
    allowed = set(contract["allowed_artifact_fields"])
    forbidden = set(contract["forbidden_artifact_fields"])

    for artifact in summary["artifact_run"]["label_comparison_artifacts"]:
        assert set(artifact) == allowed
        assert artifact["label_available_for_offline_comparison"] is True
        assert artifact["label_used_by_runtime"] is False
        assert artifact["metric_computation_enabled"] is False
        assert artifact["runtime_result_summary"]["candidate_phase_emitted"] is False
        assert artifact["runtime_result_summary"]["current_phase_emitted"] is False
        assert forbidden.isdisjoint(_all_keys(artifact))


def test_forbidden_nested_metric_fields_are_rejected() -> None:
    summary = summarize_historical_label_comparison_artifact_generation()
    artifact = dict(summary["artifact_run"]["label_comparison_artifacts"][0])
    artifact["runtime_result_summary"] = dict(artifact["runtime_result_summary"])
    artifact["runtime_result_summary"]["historical_accuracy"] = 1.0

    validation = validate_historical_label_comparison_artifact(artifact)

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_artifact_field_count"] == 1


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
