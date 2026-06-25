from __future__ import annotations

from business_cycle.audits.phase35_historical_comparability_realization import (
    summarize_phase35_historical_comparability_realization,
)


def main() -> None:
    summary = summarize_phase35_historical_comparability_realization()
    for key in (
        "phase",
        "phase_id",
        "autonomous_comparability_realization_ready",
        "post_comparability_validation_rerun_ready",
        "historical_comparability_diagnostics_ready",
        "attempted_fix_iteration_count",
        "scenario_count",
        "pre_blocked_scenario_count",
        "post_blocked_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "safe_fixable_comparability_gap_count",
        "unresolved_safe_fixable_comparability_gap_count",
        "all_remaining_non_comparable_reasons_are_genuine",
        "non_comparable_without_attempted_fix_or_genuine_evidence_count",
        "false_comparability_count",
        "scenario_promoted_without_required_evidence_count",
        "scenario_promoted_by_taxonomy_only_count",
        "scenario_promoted_by_modern_proxy_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "phase35_comparability_progress_status",
        "development_next_phase",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
