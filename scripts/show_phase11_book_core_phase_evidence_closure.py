from __future__ import annotations

from business_cycle.audits.phase11_book_core_phase_evidence_closure import (
    summarize_phase11_book_core_phase_evidence_closure,
)


def main() -> None:
    summary = summarize_phase11_book_core_phase_evidence_closure()
    for key in (
        "phase",
        "north_star_document_present",
        "north_star_contract_valid",
        "phase_capability_mapping_complete",
        "web_surface_mapping_complete",
        "semantic_drift_count",
        "role_type_registry_ready",
        "denominator_semantics_valid",
        "economic_role_count",
        "methodology_requirement_count",
        "evidence_rule_registry_ready",
        "safely_operationalizable_role_count",
        "implemented_phase_evidence_evaluator_count",
        "new_phase_evidence_evaluable_role_count",
        "genuine_rule_blocked_role_count",
        "phase_evidence_partial_major_group_count",
        "phase_evidence_complete_major_group_count",
        "candidate_input_complete_major_group_count",
        "retrospective_diagnostics_ready",
        "phase_evidence_view_model_ready",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "holdout_registered",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "development_next_phase",
        "prospective_track_next_action",
        "phase11_closure_status",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
