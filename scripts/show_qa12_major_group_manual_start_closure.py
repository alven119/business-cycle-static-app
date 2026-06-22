from __future__ import annotations

from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)


def main() -> None:
    summary = summarize_qa12_major_group_manual_start_closure()
    for key in (
        "phase",
        "readiness_semantics_reconciled",
        "capture_topology_valid",
        "source_adapter_inventory_ready",
        "no_write_source_preflight_ready",
        "first_period_manifest_ready",
        "period_completeness_engine_ready",
        "manual_preview_bundle_ready",
        "manual_start_gate_ready",
        "manual_operations_runbook_ready",
        "major_group_end_to_end_fixtures_ready",
        "wait_state_governance_ready",
        "prospective_capability_matrix_ready",
        "manual_start_freeze_ready",
        "leakage_guard_ready",
        "production_isolation_verified",
        "automatic_scheduling_disabled",
        "role_count",
        "forward_capture_ready_role_count",
        "live_preflight_ready_role_count",
        "forward_blocked_role_count",
        "major_group_count",
        "observation_contract_ready_group_count",
        "adapter_ready_group_count",
        "live_preflight_ready_group_count",
        "period_manifest_ready_group_count",
        "period_complete_group_count",
        "registry_preview_ready_group_count",
        "phase_evidence_ready_group_count",
        "candidate_input_complete_group_count",
        "observation_period",
        "canonical_as_of",
        "canonical_as_of_reached",
        "current_wait_state",
        "manual_start_contract_ready",
        "manual_start_allowed_now",
        "real_append_allowed_now",
        "real_registry_record_count",
        "real_registry_write_attempt_count",
        "prospective_protocol_started",
        "prospective_result_inspected",
        "holdout_registered",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "formal_candidate_phase_computed",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "qa13_allowed_now",
        "qa13_earliest_as_of",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_action",
        "qa12_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

