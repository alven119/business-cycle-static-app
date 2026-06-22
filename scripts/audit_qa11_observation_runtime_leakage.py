"""Audit QA11 observation-runtime leakage."""

from __future__ import annotations

from business_cycle.audits.qa11_observation_runtime_leakage import (
    summarize_qa11_observation_runtime_leakage,
)


def main() -> None:
    summary = summarize_qa11_observation_runtime_leakage()
    for key in (
        "phase",
        "leakage_guard_ready",
        "scenario_id_reference_count",
        "historical_date_reference_count",
        "expected_label_reference_count",
        "nber_reference_count",
        "acceptance_window_reference_count",
        "false_positive_date_reference_count",
        "portfolio_return_reference_count",
        "copied_historical_threshold_count",
        "contextual_250k_executable_use_count",
        "scenario_specific_branch_count",
        "post_diagnostic_rule_mutation_without_version_change_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
