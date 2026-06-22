from __future__ import annotations

from business_cycle.audits.qa7_evidence_rule_candidate_freeze_closure import (
    summarize_qa7_evidence_rule_candidate_freeze_closure,
)


def main() -> None:
    summary = summarize_qa7_evidence_rule_candidate_freeze_closure()
    for key in (
        "phase",
        "evaluability_root_cause_audit_ready",
        "book_statement_operationalization_ready",
        "evidence_rule_provenance_ready",
        "role_evaluation_contract_registry_ready",
        "evaluator_metamorphic_tests_ready",
        "candidate_selection_contract_ready",
        "synthetic_candidate_selection_validated",
        "real_data_candidate_diagnostics_ready",
        "evidence_rule_leakage_guard_ready",
        "candidate_selection_freeze_ready",
        "production_isolation_verified",
        "canonical_role_count",
        "evaluation_contract_count",
        "preregistered_evaluable_role_count",
        "raw_transform_only_role_count",
        "blocked_rule_count",
        "blocked_threshold_count",
        "blocked_data_count",
        "blocked_equivalence_count",
        "explicit_book_rule_count",
        "contextual_example_count",
        "contextual_example_generalized_count",
        "qualitative_statement_given_arbitrary_threshold_count",
        "contaminated_rule_allowed_for_independent_validation_count",
        "synthetic_candidate_selection_enabled",
        "synthetic_candidate_fixture_count",
        "synthetic_candidate_fixture_pass_count",
        "real_data_candidate_selection_enabled",
        "real_data_candidate_phase_emitted_count",
        "formal_candidate_phase_computed_on_real_data",
        "formal_current_phase_decision_enabled",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "holdout_registered",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "qa8_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa7_closure_status",
        "recommended_next_phase_title",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
