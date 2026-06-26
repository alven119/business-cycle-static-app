#!/usr/bin/env python
"""Show Phase 38 research validation dashboard closure."""

from __future__ import annotations

from business_cycle.audits.phase38_research_validation_dashboard_closure import (
    summarize_phase38_research_validation_dashboard_closure,
)


def main() -> None:
    summary = summarize_phase38_research_validation_dashboard_closure()
    for key in (
        "phase",
        "phase_id",
        "north_star_alignment_status",
        "semantic_drift_count",
        "research_dashboard_contract_ready",
        "research_dashboard_bundle_ready",
        "research_dashboard_runtime_ready",
        "local_preview_server_ready",
        "browser_verification_ready",
        "dashboard_view_count",
        "scenario_count",
        "rendered_scenario_count",
        "comparable_scenario_count",
        "non_comparable_scenario_count",
        "remaining_pit_role_gap_count",
        "rule_unresolved_gap_count",
        "artifact_consistency_error_count",
        "missing_trust_metadata_count",
        "missing_research_only_label_count",
        "prohibited_claim_count",
        "prohibited_action_field_count",
        "browser_console_error_count",
        "browser_failed_resource_count",
        "browser_missing_required_element_count",
        "browser_horizontal_overflow_count",
        "browser_critical_overlap_count",
        "scenario_detail_route_failure_count",
        "generated_repo_output_count",
        "secret_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "label_used_by_runtime_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "alpha35_freeze_hash_valid",
        "alpha34_parent_preserved",
        "qa12_freeze_unchanged",
        "economic_validation_status",
        "phase38_dashboard_status",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "formal_decision_model_ready",
        "candidate_capability_ready",
        "development_next_phase",
        "prospective_track_next_action",
        "phase38_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
