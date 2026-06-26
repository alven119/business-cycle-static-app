#!/usr/bin/env python
"""Show Phase 38 research validation dashboard audit."""

from __future__ import annotations

from business_cycle.audits.phase38_research_validation_dashboard import (
    summarize_phase38_research_validation_dashboard,
)


def main() -> None:
    summary = summarize_phase38_research_validation_dashboard()
    for key in (
        "phase",
        "phase_id",
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
        "candidate_phase_emitted",
        "current_phase_emitted",
        "label_used_by_runtime_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "phase38_dashboard_status",
        "development_next_phase",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
