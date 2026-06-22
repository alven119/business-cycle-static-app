"""Show QA11 book-core evaluator and data-gap closure."""

from __future__ import annotations

from business_cycle.audits.qa11_book_core_evaluator_data_gap_closure import (
    summarize_qa11_book_core_evaluator_data_gap_closure,
)


def main() -> None:
    summary = summarize_qa11_book_core_evaluator_data_gap_closure()
    for key in (
        "phase",
        "monitoring_readiness_semantics_ready",
        "forward_data_gap_registry_ready",
        "forward_capture_contract_ready",
        "observation_evaluator_layer_ready",
        "book_explicit_evaluator_remediation_ready",
        "generalized_history_window_runtime_ready",
        "role_observation_record_contract_ready",
        "major_group_observation_coverage_ready",
        "retrospective_observation_diagnostics_ready",
        "forward_capture_dry_run_ready",
        "prospective_prestart_invariants_preserved",
        "blocker_remediation_registry_ready",
        "observation_freeze_ready",
        "leakage_guard_ready",
        "production_isolation_verified",
        "role_count",
        "forward_capture_ready_role_count",
        "forward_blocked_role_count",
        "runtime_observable_role_count",
        "new_runtime_observable_role_count",
        "phase_evidence_evaluable_role_count",
        "candidate_selection_eligible_role_count",
        "observation_ready_major_group_count",
        "phase_evidence_evaluable_major_group_count",
        "candidate_input_complete_major_group_count",
        "evidence_recording_runtime_ready",
        "single_role_observation_monitoring_ready",
        "multi_role_observation_monitoring_ready",
        "major_group_observation_monitoring_ready",
        "phase_evidence_monitoring_ready",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "real_registry_record_count",
        "real_registry_write_attempt_count",
        "prospective_protocol_started",
        "prospective_result_inspected",
        "holdout_registered",
        "formal_candidate_phase_computed",
        "formal_decision_model_ready",
        "data_only_model_economically_validated",
        "independent_validation_ready",
        "production_book_fidelity_ready",
        "book_alignment_claim_allowed",
        "qa12_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa11_closure_status",
        "recommended_next_phase_title",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
