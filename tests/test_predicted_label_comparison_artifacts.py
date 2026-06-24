from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
    load_predicted_label_comparison_artifact_contract,
    summarize_predicted_label_comparison_artifacts,
    validate_predicted_label_comparison_artifact,
    validate_predicted_label_comparison_artifact_contract,
    write_predicted_label_comparison_artifacts,
)


def test_predicted_label_comparison_artifacts_generate_without_metrics() -> None:
    summary = summarize_predicted_label_comparison_artifacts()

    assert summary["predicted_label_comparison_artifact_contract_ready"] is True
    assert summary["predicted_label_comparison_generator_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["predicted_label_artifact_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["label_comparison_executed"] is True
    assert summary["predicted_label_provenance_verified_count"] == 5
    assert summary["historical_label_provenance_verified_count"] == 5
    assert summary["mapping_contract_hash_verified"] is True
    assert summary["label_used_by_runtime_count"] == 0
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


def test_predicted_label_comparison_contract_and_artifacts_are_safe() -> None:
    contract = load_predicted_label_comparison_artifact_contract()
    contract_validation = validate_predicted_label_comparison_artifact_contract(
        contract
    )
    run = build_predicted_label_comparison_artifacts()

    assert contract_validation["contract_schema_valid"] is True
    assert "comparable" in contract["comparison_status_taxonomy"]
    assert "taxonomy_mismatch" in contract["comparison_status_taxonomy"]
    assert contract["reference_label_policy"]["label_values_materialized"] is False
    assert contract["reference_label_policy"]["labels_may_enter_runtime"] is False
    assert contract["comparison_policy"]["label_comparison_executed"] is True
    assert contract["comparison_policy"]["accuracy_metric_allowed"] is False
    assert contract["comparison_policy"]["confusion_matrix_allowed"] is False
    assert contract["comparison_policy"]["mapping_rule_mutation_allowed"] is False

    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    for artifact in run["predicted_label_comparison_artifacts"]:
        validation = validate_predicted_label_comparison_artifact(
            artifact,
            contract=contract,
            mapping_contract_hash=run["mapping_contract_hash"],
        )
        assert set(artifact) == allowed_fields
        assert validation["artifact_schema_valid"] is True
        assert validation["prohibited_artifact_field_count"] == 0
        assert artifact["comparison_status"] in contract["comparison_status_taxonomy"]
        assert artifact["predicted_label_provenance"]["label_used_by_runtime"] is False
        assert (
            artifact["predicted_label_provenance"]["metric_computation_enabled"]
            is False
        )
        assert artifact["historical_label_provenance"]["label_values_materialized"] is False
        assert artifact["historical_label_provenance"]["label_used_by_runtime"] is False
        assert (
            artifact["historical_label_provenance"][
                "historical_accuracy_metric_count"
            ]
            == 0
        )
        assert (
            artifact["historical_label_provenance"][
                "economic_performance_metric_count"
            ]
            == 0
        )
        assert forbidden_fields.isdisjoint(artifact)


def test_predicted_label_comparison_preserves_blocked_nonjudgment_status() -> None:
    run = build_predicted_label_comparison_artifacts()

    assert {
        artifact["comparison_status"]
        for artifact in run["predicted_label_comparison_artifacts"]
    } == {"blocked"}
    assert all(
        artifact["comparable"] is False
        for artifact in run["predicted_label_comparison_artifacts"]
    )
    assert all(
        artifact["comparison_status_reason"] == "blocked_reason_codes_preserved"
        for artifact in run["predicted_label_comparison_artifacts"]
    )


def test_predicted_label_comparison_validation_rejects_forbidden_fields() -> None:
    run = build_predicted_label_comparison_artifacts()
    artifact = dict(run["predicted_label_comparison_artifacts"][0])
    artifact["accuracy"] = 1.0

    validation = validate_predicted_label_comparison_artifact(
        artifact,
        mapping_contract_hash=run["mapping_contract_hash"],
    )

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_artifact_field_count"] == 1


def test_predicted_label_comparison_writer_uses_tmp_only(tmp_path: Path) -> None:
    run = build_predicted_label_comparison_artifacts()
    output = tmp_path / "phase28_predicted_label_comparison_artifacts.json"

    write_result = write_predicted_label_comparison_artifacts(run, output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["predicted_label_comparison_artifact_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["predicted_label_artifact_count"] == 5
    assert payload["label_comparison_artifact_count"] == 5
    assert payload["label_comparison_executed"] is True
    assert payload["historical_accuracy_metric_count"] == 0
    assert payload["economic_performance_metric_count"] == 0
    assert payload["metric_computation_enabled"] is False


def test_predicted_label_comparison_writer_rejects_repo_outputs() -> None:
    run = build_predicted_label_comparison_artifacts()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_predicted_label_comparison_artifacts(
            run,
            output="data/backtests/phase28_predicted_label_comparison_artifacts.json",
        )
