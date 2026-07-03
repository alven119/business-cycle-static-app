#!/usr/bin/env python3
"""Show product capability 95 percent roadmap readiness."""

from __future__ import annotations

from business_cycle.audits.product_capability_95_roadmap import (
    summarize_product_capability_95_roadmap,
)


def main() -> None:
    summary = summarize_product_capability_95_roadmap()
    keys = [
        "roadmap_ready",
        "baseline_phase_id",
        "baseline_phase_label",
        "max_phase_count",
        "planned_phase_count",
        "target_phase_id",
        "target_capability_count",
        "target_capability_ids",
        "post_target_enabler_count",
        "post_target_enabler_phase_ids",
        "phase65_test_suite_reduction_enabler_present",
        "phase66_archive_shard_enabler_present",
        "phase67_transition_timing_enabler_present",
        "phase68_test_index_and_numeric_overlay_enabler_present",
        "phase69_start_confirmation_enabler_present",
        "all_target_capabilities_reach_95",
        "monotonic_progress_targets",
        "planned_phase_ids",
        "final_targets",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "semantic_drift_count",
        "prohibited_claim_count",
        "result",
    ]
    for key in keys:
        print(f"{key}={summary[key]}")


if __name__ == "__main__":
    main()
