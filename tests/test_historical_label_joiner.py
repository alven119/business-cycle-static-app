from __future__ import annotations

from business_cycle.validation.historical_label_joiner import (
    build_historical_label_comparison_artifacts,
)


def test_label_joiner_joins_all_scenarios_without_runtime_label_use() -> None:
    run = build_historical_label_comparison_artifacts()

    assert run["scenario_count"] == 5
    assert run["label_comparison_artifact_count"] == 5
    assert run["label_provenance_verified_count"] == 5
    assert run["label_used_by_runtime_count"] == 0
    assert run["label_comparison_executed"] is True
    assert run["metric_computation_enabled"] is False
    assert run["historical_accuracy_metric_count"] == 0
    assert run["economic_performance_metric_count"] == 0
    assert run["prohibited_artifact_field_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False
    assert {artifact["label_join_status"] for artifact in run[
        "label_comparison_artifacts"
    ]} == {"joined"}
    assert {
        artifact["label_source_id"] for artifact in run[
            "label_comparison_artifacts"
        ]
    } == {
        "nber_us_business_cycle_dates_declared_validation_label",
        "preregistered_period_metadata_no_runtime_label",
    }
