from __future__ import annotations

from business_cycle.audits.book_explicit_evaluator_leakage import (
    summarize_book_explicit_evaluator_leakage,
)


def main() -> None:
    summary = summarize_book_explicit_evaluator_leakage()
    for key in (
        "phase",
        "evaluator_leakage_guard_ready",
        "scenario_id_reference_count",
        "historical_date_reference_count",
        "expected_label_reference_count",
        "nber_reference_count",
        "return_metric_reference_count",
        "copied_historical_threshold_count",
        "contextual_250k_executable_count",
        "post_diagnostic_rule_change_without_new_version_count",
        "historical_result_used_for_rule_selection_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
