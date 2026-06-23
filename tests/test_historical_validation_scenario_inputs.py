from __future__ import annotations

from business_cycle.audits.historical_validation_scenario_inputs import (
    summarize_historical_validation_scenario_inputs,
)


def test_historical_validation_scenario_inputs_are_complete_contracts() -> None:
    summary = summarize_historical_validation_scenario_inputs()

    assert summary["scenario_input_requirements_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["scenario_id_mismatch_count"] == 0
    assert summary["scenario_with_complete_input_contract_count"] == 5
    assert summary["scenario_missing_input_contract_count"] == 0
    assert summary["scenario_with_label_provenance_gap_count"] == 0
    assert summary["total_required_input_count"] == 30
    assert summary["total_available_input_count"] == 30
    assert summary["total_missing_input_count"] == 0
    assert summary["total_unavailable_input_count"] == 0
    assert summary["total_required_vintage_count"] == 5
    assert summary["total_available_vintage_count"] == 5
    assert summary["total_missing_vintage_count"] == 0
    assert summary["label_provenance_complete"] is True
    assert summary["forbidden_output_field_count"] == 0
    assert summary["model_execution_count"] == 0
