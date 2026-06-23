from __future__ import annotations

from business_cycle.validation.historical_validation_execution_plan import (
    summarize_historical_validation_execution_plan,
)


def test_historical_validation_execution_plan_is_locked() -> None:
    summary = summarize_historical_validation_execution_plan()

    assert summary["historical_validation_execution_plan_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_id_mismatch_count"] == 0
    assert summary["scenario_with_execution_plan_count"] == 5
    assert summary["plan_without_required_input_artifacts_count"] == 0
    assert summary["plan_without_required_label_artifacts_count"] == 0
    assert summary["plan_without_required_freeze_ids_count"] == 0
    assert summary["execution_allowed_in_this_phase"] is False
    assert summary["execution_allowed_plan_count"] == 0
    assert summary["model_execution_count"] == 0
    assert summary["real_historical_validation_executed"] is False
    assert summary["historical_validation_result_count"] == 0
