from __future__ import annotations

from business_cycle.audits.data_only_shadow_evaluation import (
    run_data_only_shadow_evaluation,
)


def test_data_only_shadow_evaluation_is_diagnostics_only() -> None:
    summary = run_data_only_shadow_evaluation()

    assert summary["data_only_shadow_evaluation_ready"] is True
    assert summary["shadow_case_count"] > 0
    assert summary["strict_complete_real_date_case_count"] == 2
    assert summary["parameter_selection_from_shadow_result_count"] == 0
    assert summary["performance_metric_computed_count"] == 0
    assert summary["shadow_result_written_to_public_count"] == 0
    assert summary["all_rows_use_frozen_model_version"] is True
    assert summary["all_real_data_rows_strict_complete"] is True
    assert summary["data_only_external_context_read_count"] == 0
    assert all(row["used_for_parameter_selection"] is False for row in summary["rows"])
    assert all(row["used_for_validation_claim"] is False for row in summary["rows"])
