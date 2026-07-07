#!/usr/bin/env python3
"""Show Phase87 research dashboard migration rehearsal closure."""

from __future__ import annotations

from business_cycle.audits.phase87_research_dashboard_production_readiness_rehearsal_closure import (
    summarize_phase87_research_dashboard_production_readiness_rehearsal_closure,
)


def main() -> int:
    summary = summarize_phase87_research_dashboard_production_readiness_rehearsal_closure()
    keys = [
        "phase",
        "phase_id",
        "phase87_closure_ready",
        "sprint_roadmap_ready",
        "product_capability_100_completion_plan_ready",
        "research_dashboard_production_readiness_rehearsal_ready",
        "dashboard_migration_rehearsal_ready",
        "renderer_caveats_ready",
        "rollback_checklist_ready",
        "production_boundary_drill_ready",
        "latest_evidence_dashboard_page_ready",
        "dashboard_rehearsal_view_ready",
        "rendered_rehearsal_ready",
        "migration_rehearsal_step_count",
        "html_migration_rehearsal_step_count",
        "renderer_caveat_count",
        "html_renderer_caveat_count",
        "rollback_checklist_item_count",
        "html_rollback_checklist_item_count",
        "production_boundary_check_count",
        "html_production_boundary_check_count",
        "production_boundary_violation_count",
        "public_output_count",
        "pages_workflow_change_count",
        "resolver_dependency_count",
        "state_machine_dependency_count",
        "portfolio_policy_output_count",
        "browser_verification_ready",
        "browser_missing_required_element_count",
        "prohibited_claim_count",
        "prohibited_action_field_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_allocation_recommendation_count",
        "trade_signal_output_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_capability_progress_ready",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "portfolio_policy_research_alignment",
        "historical_replay_backtest_alignment",
        "legal_transition_semantics_preserved",
        "development_next_phase",
        "phase87_closure_status",
        "average_product_capability_progress_percent",
        "result",
    ]
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())
