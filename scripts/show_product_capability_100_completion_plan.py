#!/usr/bin/env python3
"""Show product capability 100 percent completion plan readiness."""

from __future__ import annotations

from business_cycle.audits.product_capability_100_completion_plan import (
    summarize_product_capability_100_completion_plan,
)


def main() -> None:
    summary = summarize_product_capability_100_completion_plan()
    keys = [
        "product_capability_100_completion_plan_ready",
        "baseline_phase_id",
        "minimum_engineering_phase_count",
        "minimum_total_phase_count_including_calendar_gate",
        "planned_phase_count",
        "planned_phase_ids",
        "active_roadmap_start_phase_id",
        "active_roadmap_end_phase_id",
        "dependency_chain_count",
        "dependency_chain_valid",
        "user_journey_step_count",
        "confusion_prevention_rule_count",
        "atomic_phase_context_switch_required",
        "target_capability_count",
        "all_target_capabilities_reach_100",
        "monotonic_progress_targets",
        "calendar_prospective_validation_gate_required",
        "calendar_gate_cannot_be_bypassed_by_phase_work",
        "prospective_minimum_evaluation_months",
        "prospective_minimum_complete_strict_dates",
        "calendar_validation_phase_id",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "current_allocation_recommendation_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "result",
    ]
    for key in keys:
        print(f"{key}={summary[key]}")


if __name__ == "__main__":
    main()
