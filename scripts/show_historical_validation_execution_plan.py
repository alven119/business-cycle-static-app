from __future__ import annotations

from business_cycle.validation.historical_validation_execution_plan import (
    summarize_historical_validation_execution_plan,
)


def main() -> None:
    summary = summarize_historical_validation_execution_plan()
    for key in (
        "phase",
        "plan_id",
        "plan_version",
        "historical_validation_execution_plan_ready",
        "scenario_count",
        "scenario_id_mismatch_count",
        "scenario_with_execution_plan_count",
        "plan_without_required_input_artifacts_count",
        "plan_without_required_label_artifacts_count",
        "plan_without_required_freeze_ids_count",
        "execution_allowed_in_this_phase",
        "execution_allowed_plan_count",
        "model_execution_count",
        "real_historical_validation_executed",
        "historical_validation_result_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
