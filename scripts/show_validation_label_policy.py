from __future__ import annotations

from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


def main() -> None:
    summary = summarize_validation_label_policy()
    for key in (
        "phase",
        "policy_id",
        "policy_version",
        "validation_label_policy_ready",
        "label_source_count",
        "label_provenance_complete",
        "label_runtime_usage_prohibited",
        "label_tuning_usage_prohibited",
        "scenario_specific_threshold_change_prohibited",
        "nber_dates_label_source_only",
        "book_examples_traceability_only",
        "portfolio_returns_prohibited_as_rule_source",
        "label_source_without_provenance_count",
        "label_runtime_usage_violation_count",
        "label_tuning_usage_violation_count",
        "scenario_threshold_change_violation_count",
        "portfolio_return_rule_source_violation_count",
        "sources_missing_required_prohibition_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
