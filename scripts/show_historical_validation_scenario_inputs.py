from __future__ import annotations

from business_cycle.audits.historical_validation_scenario_inputs import (
    summarize_historical_validation_scenario_inputs,
)


def main() -> None:
    summary = summarize_historical_validation_scenario_inputs()
    for key in (
        "phase",
        "requirements_id",
        "requirements_version",
        "scenario_input_requirements_ready",
        "scenario_count",
        "scenario_id_mismatch_count",
        "scenario_with_complete_input_contract_count",
        "scenario_missing_input_contract_count",
        "scenario_with_label_provenance_gap_count",
        "total_required_input_count",
        "total_available_input_count",
        "total_missing_input_count",
        "total_unavailable_input_count",
        "total_required_vintage_count",
        "total_available_vintage_count",
        "total_missing_vintage_count",
        "label_provenance_complete",
        "forbidden_output_field_count",
        "model_execution_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
