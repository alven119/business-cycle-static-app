from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.validation.offline_predicted_label_artifacts import (
    build_offline_predicted_label_artifacts,
    load_offline_predicted_label_artifact_contract,
    summarize_offline_predicted_label_artifacts,
    validate_offline_predicted_label_artifact,
    validate_offline_predicted_label_artifact_contract,
    write_offline_predicted_label_artifacts,
)


def test_offline_predicted_label_artifacts_are_generated_without_metrics() -> None:
    summary = summarize_offline_predicted_label_artifacts()

    assert summary["offline_predicted_label_artifact_contract_ready"] is True
    assert summary["offline_predicted_label_artifact_generator_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["research_decision_output_count"] == 5
    assert summary["predicted_label_artifact_count"] == 5
    assert summary["predicted_label_output_count"] == 5
    assert summary["predicted_label_provenance_complete_count"] == 5
    assert summary["mapping_contract_hash_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["label_comparison_executed"] is False
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_artifact_field_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0


def test_offline_predicted_label_contract_and_artifacts_are_label_blind() -> None:
    contract = load_offline_predicted_label_artifact_contract()
    contract_validation = validate_offline_predicted_label_artifact_contract(contract)
    run = build_offline_predicted_label_artifacts()

    assert contract_validation["contract_schema_valid"] is True
    assert "expected_label" in contract["prohibited_inputs"]
    assert "nber_label" in contract["prohibited_inputs"]
    assert "historical_accuracy" in contract["prohibited_inputs"]
    assert contract["mapping_execution_policy"]["historical_labels_may_be_read"] is False
    assert contract["mapping_execution_policy"]["nber_dates_may_be_read"] is False
    assert contract["mapping_execution_policy"]["label_comparison_may_execute"] is False
    assert contract["mapping_execution_policy"]["metrics_may_execute"] is False

    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    for artifact in run["offline_predicted_label_artifacts"]:
        validation = validate_offline_predicted_label_artifact(
            artifact,
            contract=contract,
            mapping_contract_hash=run["mapping_contract_hash"],
        )
        assert set(artifact) == allowed_fields
        assert validation["artifact_schema_valid"] is True
        assert validation["prohibited_artifact_field_count"] == 0
        assert artifact["predicted_label"] in contract["predicted_label_taxonomy"]
        assert artifact["research_only"] is True
        assert artifact["validation_only"] is True
        assert artifact["provenance"]["historical_labels_read"] is False
        assert artifact["provenance"]["nber_dates_read"] is False
        assert artifact["provenance"]["label_comparison_executed"] is False
        assert artifact["provenance"]["label_used_by_runtime"] is False
        assert artifact["provenance"]["metric_computation_enabled"] is False
        assert artifact["provenance"]["candidate_phase_emitted"] is False
        assert artifact["provenance"]["current_phase_emitted"] is False
        assert forbidden_fields.isdisjoint(artifact)


def test_offline_predicted_label_validation_rejects_forbidden_fields() -> None:
    run = build_offline_predicted_label_artifacts()
    artifact = dict(run["offline_predicted_label_artifacts"][0])
    artifact["actual_label"] = "recession"

    validation = validate_offline_predicted_label_artifact(
        artifact,
        mapping_contract_hash=run["mapping_contract_hash"],
    )

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_artifact_field_count"] == 1


def test_offline_predicted_label_artifact_writer_uses_tmp_only(
    tmp_path: Path,
) -> None:
    run = build_offline_predicted_label_artifacts()
    output = tmp_path / "phase27_predicted_label_artifacts.json"

    write_result = write_offline_predicted_label_artifacts(run, output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["offline_predicted_label_artifact_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["predicted_label_artifact_count"] == 5
    assert payload["predicted_label_output_count"] == 5
    assert payload["label_comparison_executed"] is False
    assert payload["historical_accuracy_metric_count"] == 0
    assert payload["economic_performance_metric_count"] == 0


def test_offline_predicted_label_artifact_writer_rejects_repo_outputs() -> None:
    run = build_offline_predicted_label_artifacts()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_offline_predicted_label_artifacts(
            run,
            output="data/backtests/phase27_predicted_label_artifacts.json",
        )
