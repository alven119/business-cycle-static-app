from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
    load_historical_accuracy_metric_artifact_contract,
    summarize_historical_accuracy_metrics,
    validate_historical_accuracy_metric_artifact,
    validate_historical_accuracy_metric_artifact_contract,
    write_historical_accuracy_metrics,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
)


def test_historical_accuracy_metrics_compute_research_only_metrics() -> None:
    summary = summarize_historical_accuracy_metrics()

    assert summary["historical_accuracy_metric_artifact_contract_ready"] is True
    assert summary["historical_accuracy_metric_runtime_ready"] is True
    assert summary["preregistered_metric_registry_used"] is True
    assert summary["scenario_count"] == 5
    assert summary["label_comparison_artifact_count"] == 5
    assert summary["comparable_scenario_count"] == 0
    assert summary["non_comparable_scenario_count"] == 0
    assert summary["abstained_scenario_count"] == 0
    assert summary["blocked_scenario_count"] == 5
    assert summary["taxonomy_mismatch_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 5
    assert summary["computed_metric_count"] == 4
    assert summary["skipped_metric_count"] == 1
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is True
    assert summary["metric_computation_scope"] == "historical_accuracy_only"
    assert summary["backtest_execution_enabled"] is False
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["mapping_rule_modified_after_comparison_count"] == 0
    assert summary["threshold_modified_after_metric_count"] == 0
    assert summary["numeric_weight_added_count"] == 0
    assert summary["arbitrary_threshold_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_metric_field_count"] == 0


def test_metric_artifact_contract_and_schema_are_safe() -> None:
    contract = load_historical_accuracy_metric_artifact_contract()
    contract_validation = validate_historical_accuracy_metric_artifact_contract(
        contract
    )
    run = compute_historical_accuracy_metrics()
    artifact = run["accuracy_metric_artifact"]
    artifact_validation = validate_historical_accuracy_metric_artifact(
        artifact,
        contract=contract,
        registry_hash=artifact["source_metric_registry_hash"],
    )

    assert contract_validation["contract_schema_valid"] is True
    assert set(artifact) == set(contract["allowed_artifact_fields"])
    assert artifact_validation["artifact_schema_valid"] is True
    assert artifact_validation["prohibited_metric_field_count"] == 0
    assert artifact["research_only"] is True
    assert artifact["validation_only"] is True
    assert artifact["metric_scope"] == "historical_accuracy_only"
    assert artifact["provenance"]["label_used_by_runtime"] is False
    assert artifact["provenance"]["economic_performance_metric_count"] == 0
    assert artifact["provenance"]["backtest_execution_enabled"] is False


def test_label_match_rate_is_skipped_without_materialized_labels() -> None:
    run = compute_historical_accuracy_metrics()
    results = {
        result["metric_id"]: result
        for result in run["accuracy_metric_artifact"][
            "preregistered_metric_results"
        ]
    }

    assert results["label_join_coverage_rate"]["value"] == 1.0
    assert results["blocked_result_share"]["value"] == 1.0
    assert results["missing_result_share"]["value"] == 0.0
    assert results["label_match_rate"]["result_status"] == (
        "skipped_prerequisite_unavailable"
    )
    assert results["label_match_rate"]["value"] is None
    assert results["label_match_rate"]["skip_reason"] == (
        "phase28_reference_label_values_are_provenance_only"
    )


def test_metric_validation_rejects_forbidden_metric_fields() -> None:
    run = compute_historical_accuracy_metrics()
    artifact = dict(run["accuracy_metric_artifact"])
    artifact["sharpe"] = 1.0

    validation = validate_historical_accuracy_metric_artifact(
        artifact,
        registry_hash=run["accuracy_metric_artifact"][
            "source_metric_registry_hash"
        ],
    )

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_metric_field_count"] == 1


def test_metric_runtime_handles_missing_and_malformed_comparison_artifacts() -> None:
    comparison_run = build_predicted_label_comparison_artifacts()
    comparison_run = {
        **comparison_run,
        "predicted_label_comparison_artifacts": list(
            comparison_run["predicted_label_comparison_artifacts"][:-1]
        ),
    }
    comparison_run["predicted_label_comparison_artifacts"][0] = {
        **comparison_run["predicted_label_comparison_artifacts"][0],
        "accuracy": 1.0,
    }
    run = compute_historical_accuracy_metrics(
        comparison_artifact_run=comparison_run,
    )

    assert run["missing_comparison_artifact_count"] == 1
    assert run["malformed_comparison_artifact_count"] == 1
    assert run["forbidden_comparison_artifact_field_count"] == 1
    missing_metric = next(
        result
        for result in run["metric_results"]
        if result["metric_id"] == "missing_result_share"
    )
    assert missing_metric["numerator"] == 1
    assert missing_metric["value"] == 0.2


def test_historical_accuracy_metric_writer_uses_tmp_only(tmp_path: Path) -> None:
    run = compute_historical_accuracy_metrics()
    output = tmp_path / "phase29_historical_accuracy_metrics.json"

    write_result = write_historical_accuracy_metrics(run, output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write_result["historical_accuracy_metric_artifact_written"] is True
    assert write_result["written_file_count"] == 1
    assert payload["scenario_count"] == 5
    assert payload["label_comparison_artifact_count"] == 5
    assert payload["historical_accuracy_metric_count"] == 5
    assert payload["economic_performance_metric_count"] == 0
    assert payload["metric_computation_scope"] == "historical_accuracy_only"


def test_historical_accuracy_metric_writer_rejects_repo_outputs() -> None:
    run = compute_historical_accuracy_metrics()

    with pytest.raises(ValueError, match="must be under /tmp"):
        write_historical_accuracy_metrics(
            run,
            output="data/backtests/phase29_historical_accuracy_metrics.json",
        )
