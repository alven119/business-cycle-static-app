from __future__ import annotations

from business_cycle.audits.qa5_book_core_shadow_model_closure import (
    summarize_qa5_book_core_shadow_model_closure,
)


def main() -> None:
    summary = summarize_qa5_book_core_shadow_model_closure()
    keys = (
        "phase",
        "scope_count_semantics_ready",
        "formal_v1_primary_partition_valid",
        "major_group_contract_ready",
        "book_core_data_contract_registry_ready",
        "official_series_verification_ready",
        "transformation_contract_registry_ready",
        "shadow_evidence_model_implemented",
        "synthetic_structural_validation_ready",
        "real_data_shadow_diagnostics_ready",
        "promotion_gate_updated",
        "shadow_candidate_freeze_ready",
        "book_fidelity_rollups_ready",
        "production_isolation_verified",
        "canonical_indicator_role_count",
        "data_contract_row_count",
        "ready_strict_complete_count",
        "ready_strict_partial_count",
        "ready_revised_diagnostic_count",
        "blocked_role_count",
        "ready_for_shadow_evidence_model_count",
        "shadow_major_group_ready_count",
        "unresolved_major_group_count",
        "formal_candidate_phase_computed",
        "formal_decision_model_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "proposed_v2_economically_validated",
        "new_weight_defined_count",
        "new_threshold_defined_count",
        "parameter_tuning_executed",
        "performance_backtest_executed",
        "holdout_registered",
        "production_behavior_change_count",
        "qa6_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa5_closure_status",
        "recommended_next_phase_title",
        "result",
    )
    for key in keys:
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
