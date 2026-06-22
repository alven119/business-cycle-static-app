from __future__ import annotations

from business_cycle.audits.qa9_prospective_shadow_registry_closure import (
    summarize_qa9_prospective_shadow_registry_closure,
)


def main() -> None:
    summary = summarize_qa9_prospective_shadow_registry_closure()
    for key in (
        "phase",
        "evaluator_runtime_audit_ready",
        "implemented_evaluator_runtime_wired",
        "evaluator_runtime_fixture_suite_ready",
        "registry_contract_ready",
        "append_only_store_ready",
        "input_snapshot_contract_ready",
        "forward_clock_gate_ready",
        "protocol_start_semantics_ready",
        "protocol_versioning_ready",
        "inspection_governance_ready",
        "registry_fixture_validation_ready",
        "monitoring_infrastructure_freeze_ready",
        "production_isolation_verified",
        "contract_evaluable_evaluator_count",
        "runtime_executable_evaluator_count",
        "runtime_output_available_evaluator_count",
        "directional_evidence_evaluable_count",
        "candidate_selection_eligible_evaluator_count",
        "protocol_registered",
        "registry_armed",
        "protocol_started",
        "first_record_written",
        "real_record_count",
        "prospective_result_inspected",
        "candidate_capability_ready",
        "candidate_monitoring_allowed",
        "holdout_registered",
        "retrospective_backfill_allowed",
        "retrospective_candidate_selection_allowed",
        "real_data_candidate_selection_enabled",
        "formal_candidate_phase_computed",
        "formal_decision_model_ready",
        "economic_validation_status",
        "independent_validation_ready",
        "qa10_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "qa9_closure_status",
        "recommended_next_phase_title",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
