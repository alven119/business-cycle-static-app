from __future__ import annotations

from business_cycle.audits.qa6_shadow_aggregation_closure import (
    summarize_qa6_shadow_aggregation_closure,
)


def main() -> None:
    summary = summarize_qa6_shadow_aggregation_closure()
    for key in (
        "phase",
        "freeze_lineage_ready",
        "prior_freeze_artifact_preserved",
        "readiness_semantics_ready",
        "typed_evidence_contract_ready",
        "layer_routing_contract_ready",
        "aggregation_schema_preregistered",
        "structural_candidate_eligibility_ready",
        "synthetic_structural_eligibility_validated",
        "real_data_aggregation_diagnostics_ready",
        "aggregation_rule_leakage_guard_ready",
        "shadow_aggregation_freeze_ready",
        "production_isolation_verified",
        "structurally_mapped_role_count",
        "evidence_evaluable_role_count",
        "structurally_routable_major_group_count",
        "evidence_evaluable_major_group_count",
        "aggregation_eligible_major_group_count",
        "numeric_weight_count",
        "newly_defined_threshold_count",
        "historical_label_used_for_rule_selection_count",
        "candidate_selection_enabled",
        "formal_candidate_phase_computed",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "holdout_registered",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "qa7_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa6_closure_status",
        "recommended_next_phase_title",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
