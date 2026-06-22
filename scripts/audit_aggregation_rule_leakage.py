from __future__ import annotations

from business_cycle.audits.aggregation_rule_leakage import (
    summarize_aggregation_rule_leakage,
)


def main() -> None:
    summary = summarize_aggregation_rule_leakage()
    for key in (
        "phase",
        "aggregation_rule_leakage_guard_ready",
        "aggregation_rule_scenario_id_reference_count",
        "aggregation_rule_historical_date_reference_count",
        "aggregation_rule_expected_label_reference_count",
        "aggregation_rule_nber_reference_count",
        "aggregation_rule_return_metric_reference_count",
        "aggregation_rule_scenario_branch_count",
        "historical_result_used_for_rule_selection_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
