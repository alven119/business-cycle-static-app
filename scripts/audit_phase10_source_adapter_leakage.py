from __future__ import annotations

from business_cycle.audits.phase10_source_adapter_leakage import (
    summarize_phase10_source_adapter_leakage,
)


def main() -> None:
    summary = summarize_phase10_source_adapter_leakage()
    for key in (
        "phase",
        "leakage_guard_ready",
        "scenario_id_reference_count",
        "historical_date_adapter_branch_count",
        "expected_phase_label_reference_count",
        "nber_date_reference_count",
        "historical_pass_fail_count_reference_count",
        "portfolio_return_reference_count",
        "historical_value_used_as_threshold_count",
        "contextual_250k_runtime_count",
        "scenario_result_source_selection_count",
        "post_preflight_rule_change_count",
        "post_preflight_threshold_change_count",
        "post_preflight_window_change_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
