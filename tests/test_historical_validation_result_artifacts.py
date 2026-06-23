from __future__ import annotations

from business_cycle.validation.historical_validation_result_artifacts import (
    summarize_historical_validation_result_artifacts,
)


def test_historical_validation_result_artifact_contract_is_schema_only() -> None:
    summary = summarize_historical_validation_result_artifacts()

    assert summary["result_artifact_contract_ready"] is True
    assert summary["historical_validation_result_count"] == 0
    assert summary["forbidden_output_field_count"] == 0
    assert summary["artifact_written_count"] == 0
    assert summary["metric_field_enabled_count"] == 0
    assert summary["candidate_or_current_phase_field_count"] == 0
