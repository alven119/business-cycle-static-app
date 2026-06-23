from __future__ import annotations

from business_cycle.audits.phase10_book_core_source_adapter_closure import (
    summarize_phase10_book_core_source_adapter_closure,
)


def main() -> None:
    summary = summarize_phase10_book_core_source_adapter_closure()
    for key in (
        "phase",
        "blocked_role_inventory_reconciled",
        "source_identity_contract_ready",
        "source_equivalence_reviews_ready",
        "adapter_interface_ready",
        "release_semantics_registry_ready",
        "all_safely_implementable_adapters_completed",
        "no_write_preflight_ready",
        "genuine_blocker_register_ready",
        "forward_capture_integration_ready",
        "observation_runtime_integration_ready",
        "major_group_readiness_recalculated",
        "source_adapter_freeze_ready",
        "leakage_guard_ready",
        "production_isolation_verified",
        "prospective_track_untouched",
        "blocked_role_count_before",
        "blocked_role_count_after",
        "source_identity_unknown_count_before",
        "source_identity_unknown_count_after",
        "access_blocked_count_after",
        "release_semantics_blocked_count_after",
        "genuine_blocker_count_after",
        "new_adapter_implemented_count",
        "new_forward_capture_ready_role_count",
        "new_runtime_observable_role_count",
        "observation_contract_ready_group_count",
        "phase_evidence_ready_group_count",
        "candidate_input_complete_group_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "candidate_selection_enabled",
        "formal_candidate_phase_computed",
        "production_behavior_change_count",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "holdout_registered",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "prospective_protocol_started",
        "real_registry_record_count",
        "real_registry_write_attempt_count",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "development_next_phase",
        "prospective_track_next_action",
        "phase10_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
