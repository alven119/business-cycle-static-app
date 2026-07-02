#!/usr/bin/env python
from __future__ import annotations

from business_cycle.audits.phase63_latest_evidence_dashboard_wiring_closure import (
    summarize_phase63_latest_evidence_dashboard_wiring_closure,
)


def main() -> None:
    summary = summarize_phase63_latest_evidence_dashboard_wiring_closure()
    keys = (
        "phase",
        "phase63_latest_evidence_dashboard_wiring_ready",
        "latest_evidence_dashboard_page_ready",
        "dashboard_indicator_drilldown_view_ready",
        "dashboard_bundle_latest_evidence_ready",
        "rendered_latest_evidence_page_count",
        "major_group_drilldown_rendered_count",
        "role_drilldown_rendered_count",
        "role_source_detail_rendered_count",
        "role_release_timing_detail_rendered_count",
        "role_freshness_detail_rendered_count",
        "role_transformation_detail_rendered_count",
        "role_rule_usability_detail_rendered_count",
        "role_provenance_detail_rendered_count",
        "role_abstention_detail_rendered_count",
        "latest_evidence_research_only_label_missing_count",
        "prohibited_claim_count",
        "prohibited_action_field_count",
        "browser_missing_required_element_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "current_data_used_to_infer_declared_phase_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
        "product_capability_progress_ready",
        "product_capability_progress_impacted_count",
        "phase63_closure_status",
    )
    for key in keys:
        value = summary[key]
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
