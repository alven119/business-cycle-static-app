from __future__ import annotations

from business_cycle.audits.qa8_book_explicit_evaluator_closure import (
    summarize_qa8_book_explicit_evaluator_closure,
)


def main() -> None:
    summary = summarize_qa8_book_explicit_evaluator_closure()
    for key in (
        "phase",
        "blocker_accounting_reconciled",
        "explicit_rule_eligibility_ready",
        "contextual_numeric_guard_ready",
        "evaluator_primitive_library_ready",
        "book_explicit_evaluators_implemented",
        "evaluator_metamorphic_coverage_ready",
        "role_readiness_recalculated",
        "retrospective_evidence_diagnostics_ready",
        "prospective_protocol_registered",
        "prospective_clock_gate_ready",
        "evaluator_freeze_ready",
        "evaluator_leakage_guard_ready",
        "production_isolation_verified",
        "role_count",
        "operationally_complete_explicit_rule_count",
        "implemented_explicit_evaluator_count",
        "operationally_incomplete_explicit_rule_count",
        "evidence_evaluable_role_count",
        "candidate_selection_eligible_role_count",
        "unresolved_rule_count",
        "contextual_numeric_generalization_count",
        "non_book_threshold_added_count",
        "copied_historical_threshold_count",
        "retrospective_candidate_selection_enabled",
        "retrospective_candidate_phase_emitted_count",
        "prospective_protocol_started",
        "prospective_result_inspected",
        "holdout_registered",
        "formal_candidate_phase_computed_on_historical_data",
        "formal_current_phase_decision_enabled",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "qa9_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa8_closure_status",
        "recommended_next_phase_title",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
