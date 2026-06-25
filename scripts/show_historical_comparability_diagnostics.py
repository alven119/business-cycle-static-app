from __future__ import annotations

from business_cycle.validation.historical_comparability_diagnostics import (
    summarize_historical_comparability_diagnostics,
)


def main() -> None:
    summary = summarize_historical_comparability_diagnostics()
    for key in (
        "phase",
        "historical_comparability_diagnostics_ready",
        "scenario_count",
        "pre_blocked_scenario_count",
        "post_blocked_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "remaining_non_comparable_scenario_count",
        "false_comparability_count",
        "scenario_promoted_without_required_evidence_count",
        "scenario_promoted_by_taxonomy_only_count",
        "scenario_promoted_by_modern_proxy_count",
        "label_used_by_runtime_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
