from __future__ import annotations

from pathlib import Path

import yaml


AGENTS_PATH = Path("AGENTS.md")
WORKFLOW_PATH = Path("docs/agent_workflow.md")
PROMPT_TEMPLATES_PATH = Path("docs/prompt_templates.md")
GATES_PATH = Path("specs/backtests/phase_acceptance_gates.yaml")


def test_agent_workflow_files_exist() -> None:
    assert AGENTS_PATH.exists()
    assert WORKFLOW_PATH.exists()
    assert PROMPT_TEMPLATES_PATH.exists()
    assert GATES_PATH.exists()


def test_agents_contains_self_repair_contract() -> None:
    text = AGENTS_PATH.read_text(encoding="utf-8")

    assert "Self-repair loop" in text
    assert "Do not report intermediate failed results unless blocked" in text


def test_phase_acceptance_gates_yaml_loads() -> None:
    payload = yaml.safe_load(GATES_PATH.read_text(encoding="utf-8"))

    assert isinstance(payload, dict)
    assert "common_hard_gates" in payload
    assert "common_checks" in payload
    assert "phase_specific_gates" in payload


def test_phase_acceptance_gates_include_required_phase_gates() -> None:
    gates = yaml.safe_load(GATES_PATH.read_text(encoding="utf-8"))
    phase_specific = gates["phase_specific_gates"]

    recovery_gates = phase_specific["recovery_refinement_experiment"]["hard_gates"]
    boom_overlay_gates = phase_specific["boom_ending_watch_overlay"]["hard_gates"]
    recovery_overlay_gates = phase_specific["recovery_watch_overlay"]["hard_gates"]
    recovery_integration_gates = phase_specific["recovery_watch_integration_guardrails"]["hard_gates"]
    evidence_architecture_gates = phase_specific["cycle_transition_evidence_architecture"]["hard_gates"]
    badge_schema_gates = phase_specific["transition_evidence_badge_schema"]["hard_gates"]
    badge_fixture_gates = phase_specific["transition_evidence_badge_fixtures"]["hard_gates"]
    renderer_contract_gates = phase_specific["transition_evidence_badge_renderer_contract"]["hard_gates"]
    display_fixture_gates = phase_specific["transition_evidence_badge_display_fixtures"]["hard_gates"]
    readiness_gates = phase_specific["dashboard_evidence_integration_readiness"]["hard_gates"]
    portfolio_plan_gates = phase_specific["portfolio_policy_research_plan"]["hard_gates"]
    portfolio_template_gates = phase_specific["portfolio_policy_template_schema"]["hard_gates"]
    portfolio_backtest_contract_gates = phase_specific["portfolio_backtest_input_contract"]["hard_gates"]
    portfolio_backtest_fixture_gates = phase_specific["portfolio_backtest_input_fixtures"]["hard_gates"]
    portfolio_dry_run_gates = phase_specific["portfolio_backtest_dry_run_contract"]["hard_gates"]
    portfolio_dry_run_fixture_gates = phase_specific["portfolio_backtest_dry_run_fixtures"]["hard_gates"]
    portfolio_dry_run_runner_gates = phase_specific[
        "portfolio_backtest_structural_dry_run_runner"
    ]["hard_gates"]
    portfolio_safety_closure_gates = phase_specific["portfolio_research_safety_closure"][
        "hard_gates"
    ]
    real_backtest_readiness_gates = phase_specific[
        "real_backtest_prototype_readiness_gate"
    ]["hard_gates"]
    real_backtest_engine_gates = phase_specific["real_backtest_engine_contract"][
        "hard_gates"
    ]
    result_output_gates = phase_specific["backtest_result_output_contract"]["hard_gates"]
    metric_registry_gates = phase_specific["backtest_metric_formula_registry"]["hard_gates"]
    output_location_gates = phase_specific["backtest_output_location_policy"]["hard_gates"]
    result_caveat_gates = phase_specific["backtest_result_caveat_policy"]["hard_gates"]
    safety_validator_gates = phase_specific["backtest_result_safety_validator_contract"][
        "hard_gates"
    ]
    safety_validator_fixture_gates = phase_specific[
        "backtest_result_safety_validator_fixtures"
    ]["hard_gates"]
    result_writer_gates = phase_specific["backtest_result_writer_contract"]["hard_gates"]
    execution_readiness_gates = phase_specific[
        "real_backtest_execution_readiness_closure"
    ]["hard_gates"]
    controlled_prototype_gates = phase_specific["controlled_real_backtest_prototype"][
        "hard_gates"
    ]
    qa0_gates = phase_specific["qa0_integrity_audit"]["hard_gates"]
    qa3_gates = phase_specific["qa3_calibration_integrity_closure"]["hard_gates"]
    qa4_gates = phase_specific["qa4_book_fidelity_scope_closure"]["hard_gates"]
    qa5_gates = phase_specific["qa5_book_core_shadow_model_closure"]["hard_gates"]
    qa6_gates = phase_specific["qa6_shadow_aggregation_closure"]["hard_gates"]
    qa7_gates = phase_specific["qa7_evidence_rule_candidate_freeze_closure"][
        "hard_gates"
    ]
    qa8_gates = phase_specific["qa8_book_explicit_evaluator_closure"]["hard_gates"]
    qa9_gates = phase_specific["qa9_prospective_shadow_registry_closure"][
        "hard_gates"
    ]
    qa10_gates = phase_specific[
        "qa10_shadow_runtime_monitoring_readiness_closure"
    ]["hard_gates"]
    qa11_gates = phase_specific[
        "qa11_book_core_evaluator_data_gap_closure"
    ]["hard_gates"]
    qa12_gates = phase_specific[
        "qa12_major_group_manual_start_closure"
    ]["hard_gates"]
    phase10_gates = phase_specific[
        "phase10_book_core_source_adapter_closure"
    ]["hard_gates"]

    assert "expected_fail_count == 0" in recovery_gates
    assert "fail_count == 0" in boom_overlay_gates
    assert "fail_count == 0" in recovery_overlay_gates
    assert "gfc_has_trough_or_recovery_watch == true" in recovery_overlay_gates
    assert "euro_debt_excessive_recovery_watch == false" in recovery_overlay_gates
    assert "direct_recovery_confirmation_allowed == false" in recovery_integration_gates
    assert "direct_portfolio_action_allowed == false" in recovery_integration_gates
    assert "recommended_next_phase == 7G" in recovery_integration_gates
    assert "formal_phase_change_allowed_now == false" in evidence_architecture_gates
    assert "direct_trade_signal_allowed_now == false" in evidence_architecture_gates
    assert "recommended_next_phase == 7G1" in evidence_architecture_gates
    assert "dashboard_contract_allowed_now == false" in badge_schema_gates
    assert "direct_trade_signal_allowed == false" in badge_schema_gates
    assert "recommended_next_phase == 7G2" in badge_schema_gates
    assert "valid_pass_count == valid_fixture_count" in badge_fixture_gates
    assert "invalid_rejected_count == invalid_fixture_count" in badge_fixture_gates
    assert "result == passed" in badge_fixture_gates
    assert "direct_trade_text_blocked == true" in renderer_contract_gates
    assert "phase_override_field_blocked == true" in renderer_contract_gates
    assert "dashboard_renderer_wiring_allowed_now == false" in renderer_contract_gates
    assert "recommended_next_phase == 7G4" in renderer_contract_gates
    assert "valid_display_pass_count == valid_display_fixture_count" in display_fixture_gates
    assert "invalid_display_rejected_count == invalid_display_fixture_count" in display_fixture_gates
    assert "result == passed" in display_fixture_gates
    assert "dashboard_wiring_allowed_now == false" in readiness_gates
    assert "public_output_allowed_now == false" in readiness_gates
    assert "recommended_next_phase == 8A" in readiness_gates
    assert "live_allocation_allowed_now == false" in portfolio_plan_gates
    assert "trade_signal_generation_allowed_now == false" in portfolio_plan_gates
    assert "recommended_next_phase == 8B" in portfolio_plan_gates
    assert "live_allocation_allowed_now == false" in portfolio_template_gates
    assert "valid_pass_count == valid_template_count" in portfolio_template_gates
    assert "recommended_next_phase == 8C" in portfolio_template_gates
    assert "live_allocation_output_allowed == false" in portfolio_backtest_contract_gates
    assert "mapped_scenario_count == allowed_scenario_count" in portfolio_backtest_contract_gates
    assert "recommended_next_phase == 8D" in portfolio_backtest_contract_gates
    assert "valid_pass_count == valid_input_count" in portfolio_backtest_fixture_gates
    assert "invalid_rejected_count == invalid_input_count" in portfolio_backtest_fixture_gates
    assert "result == passed" in portfolio_backtest_fixture_gates
    assert "compute_returns_allowed == false" in portfolio_dry_run_gates
    assert "allocation_output_allowed == false" in portfolio_dry_run_gates
    assert "recommended_next_phase == 8F" in portfolio_dry_run_gates
    assert "valid_pass_count == valid_output_count" in portfolio_dry_run_fixture_gates
    assert "output_written == false" in portfolio_dry_run_fixture_gates
    assert "trade_signal_generated == false" in portfolio_dry_run_fixture_gates
    assert "result == passed" in portfolio_dry_run_fixture_gates
    assert "performance_metrics_computed == false" in portfolio_dry_run_runner_gates
    assert "output_written == false" in portfolio_dry_run_runner_gates
    assert "data_backtests_output_written == false" in portfolio_dry_run_runner_gates
    assert "trade_signal_generated == false" in portfolio_dry_run_runner_gates
    assert "result == passed" in portfolio_dry_run_runner_gates
    assert "research_only == true" in portfolio_safety_closure_gates
    assert "formal_backtest_executed == false" in portfolio_safety_closure_gates
    assert "performance_metrics_computed == false" in portfolio_safety_closure_gates
    assert "data_backtests_output_written == false" in portfolio_safety_closure_gates
    assert "recommended_next_phase == 8I" in portfolio_safety_closure_gates
    assert "real_backtest_execution_allowed == false" in real_backtest_readiness_gates
    assert "performance_metrics_allowed == false" in real_backtest_readiness_gates
    assert "data_backtests_output_allowed == false" in real_backtest_readiness_gates
    assert "recommended_next_phase == 9A" in real_backtest_readiness_gates
    assert "execute_backtest_allowed == false" in real_backtest_engine_gates
    assert "compute_performance_metrics_allowed == false" in real_backtest_engine_gates
    assert "write_data_backtests_output_allowed == false" in real_backtest_engine_gates
    assert "recommended_next_phase == 9A1" in real_backtest_engine_gates
    assert "produce_backtest_results_allowed == false" in result_output_gates
    assert "compute_metric_values_allowed == false" in result_output_gates
    assert "write_data_backtests_output_allowed == false" in result_output_gates
    assert "metric_values_allowed_now == false" in result_output_gates
    assert "recommended_next_phase == 9A2" in result_output_gates
    assert "compute_metric_values_allowed == false" in metric_registry_gates
    assert "execute_backtest_allowed == false" in metric_registry_gates
    assert "all_metric_compute_allowed_now == false" in metric_registry_gates
    assert "recommended_next_phase == 9A3" in metric_registry_gates
    assert "write_result_files_allowed == false" in output_location_gates
    assert "write_data_backtests_output_allowed == false" in output_location_gates
    assert "create_output_directories_allowed == false" in output_location_gates
    assert "recommended_next_phase == 9A4" in output_location_gates
    assert "produce_backtest_results_allowed == false" in result_caveat_gates
    assert "compute_metric_values_allowed == false" in result_caveat_gates
    assert "caveats_visible_before_metrics == true" in result_caveat_gates
    assert "recommended_next_phase == 9A5" in result_caveat_gates
    assert "run_validator_on_real_results_allowed == false" in safety_validator_gates
    assert "validator_runtime_allowed_now == false" in safety_validator_gates
    assert "real_result_validation_allowed_now == false" in safety_validator_gates
    assert "recommended_next_phase == 9A6" in safety_validator_gates
    assert "valid_pass_count == valid_result_fixture_count" in safety_validator_fixture_gates
    assert (
        "invalid_rejected_count == invalid_result_fixture_count"
        in safety_validator_fixture_gates
    )
    assert "public_output_written == false" in safety_validator_fixture_gates
    assert "result == passed" in safety_validator_fixture_gates
    assert "explicit_user_command_required == true" in result_writer_gates
    assert "implement_writer_runtime_allowed == false" in result_writer_gates
    assert "write_result_files_allowed == false" in result_writer_gates
    assert "output_directory_creation_allowed_now == false" in result_writer_gates
    assert "recommended_next_phase == 9A8" in result_writer_gates
    assert "phase_9a_contract_stack_complete == true" in execution_readiness_gates
    assert "real_backtest_execution_allowed_now == false" in execution_readiness_gates
    assert "result_file_write_allowed_now == false" in execution_readiness_gates
    assert "controlled_9b_prototype_entry_allowed == true" in execution_readiness_gates
    assert "recommended_next_phase == 9B" in execution_readiness_gates
    assert "in_memory_only == true" in controlled_prototype_gates
    assert (
        "controlled_metric_computation_allowed == true" in controlled_prototype_gates
    )
    assert "result_file_written == false" in controlled_prototype_gates
    assert "data_backtests_output_written == false" in controlled_prototype_gates
    assert "public_output_written == false" in controlled_prototype_gates
    assert "output_directory_created == false" in controlled_prototype_gates
    assert "synthetic_fixture_only == true" in controlled_prototype_gates
    assert "economic_validity_established == false" in controlled_prototype_gates
    assert "book_fidelity_validated == false" in controlled_prototype_gates
    assert "point_in_time_validated == false" in controlled_prototype_gates
    assert "recommended_next_phase == QA0" in controlled_prototype_gates
    assert "phase == QA0.1" in qa0_gates
    assert "audit_status == passed" in qa0_gates
    assert "canonical_requirement_count > 22" in qa0_gates
    assert "traceability_row_count == canonical_requirement_count" in qa0_gates
    assert "missing_traceability_requirement_count == 0" in qa0_gates
    assert "unmapped_indicator_count == 0" in qa0_gates
    assert "audited_series_count == discovered_unique_series_count" in qa0_gates
    assert "hard_coded_summary_value_count == 0" in qa0_gates
    assert "qa0_inventory_complete == true" in qa0_gates
    assert "unsupported_claim_count == 0" in qa0_gates
    assert "phase_9b_synthetic_harness_valid == true" in qa0_gates
    assert "phase_9b_economic_validation_claim_allowed == false" in qa0_gates
    assert "real_backtest_progression_allowed == false" in qa0_gates
    assert "phase_9b1_allowed == false" in qa0_gates
    assert "recommended_next_phase == QA1" in qa0_gates
    assert "parameter_inventory_ready == true" in qa3_gates
    assert "parameter_drift_detection_ready == true" in qa3_gates
    assert "formal_model_layer_architecture_ready == true" in qa4_gates
    assert "book_faithful_scope_contract_ready == true" in qa4_gates
    assert "indicator_scope_matrix_ready == true" in qa4_gates
    assert "formal_scope_freeze_ready == true" in qa4_gates
    assert "book_faithful_scope_complete == false" in qa4_gates
    assert "proposed_v2_implemented == false" in qa4_gates
    assert "proposed_v2_holdout_registered == false" in qa4_gates
    assert "production_behavior_change_count == 0" in qa4_gates
    assert "recommended_next_phase == QA5" in qa4_gates
    assert "scope_count_semantics_ready == true" in qa5_gates
    assert "book_core_data_contract_registry_ready == true" in qa5_gates
    assert "shadow_evidence_model_implemented == true" in qa5_gates
    assert "formal_candidate_phase_computed == false" in qa5_gates
    assert "proposed_v2_economically_validated == false" in qa5_gates
    assert "holdout_registered == false" in qa5_gates
    assert "production_behavior_change_count == 0" in qa5_gates
    assert "recommended_next_phase == QA6" in qa5_gates
    assert "freeze_lineage_ready == true" in qa6_gates
    assert "typed_evidence_contract_ready == true" in qa6_gates
    assert "aggregation_schema_preregistered == true" in qa6_gates
    assert "candidate_selection_enabled == false" in qa6_gates
    assert "holdout_registered == false" in qa6_gates
    assert "recommended_next_phase == QA7" in qa6_gates
    assert "evidence_rule_provenance_ready == true" in qa7_gates
    assert "candidate_selection_contract_ready == true" in qa7_gates
    assert "synthetic_candidate_selection_validated == true" in qa7_gates
    assert "real_data_candidate_selection_enabled == false" in qa7_gates
    assert "real_data_candidate_phase_emitted_count == 0" in qa7_gates
    assert "formal_decision_model_ready == false" in qa7_gates
    assert "holdout_registered == false" in qa7_gates
    assert "recommended_next_phase == QA8" in qa7_gates
    assert "book_explicit_evaluators_implemented == true" in qa8_gates
    assert (
        "implemented_explicit_evaluator_count == operationally_complete_explicit_rule_count"
        in qa8_gates
    )
    assert "retrospective_candidate_selection_enabled == false" in qa8_gates
    assert "prospective_protocol_started == false" in qa8_gates
    assert "holdout_registered == false" in qa8_gates
    assert "recommended_next_phase == QA9" in qa8_gates
    assert "evaluator_runtime_audit_ready == true" in qa9_gates
    assert "implemented_evaluator_runtime_wired == true" in qa9_gates
    assert "registry_contract_ready == true" in qa9_gates
    assert "append_only_store_ready == true" in qa9_gates
    assert "forward_clock_gate_ready == true" in qa9_gates
    assert "monitoring_infrastructure_freeze_ready == true" in qa9_gates
    assert "protocol_started == false" in qa9_gates
    assert "real_record_count == 0" in qa9_gates
    assert "candidate_capability_ready == false" in qa9_gates
    assert "holdout_registered == false" in qa9_gates
    assert "recommended_next_phase == QA10" in qa9_gates
    assert "qa8_qa9_lineage_verified == true" in qa10_gates
    assert "runtime_history_window_contract_ready == true" in qa10_gates
    assert "implemented_evaluator_runtime_path_ready == true" in qa10_gates
    assert "runtime_output_on_2019_revised_count == 1" in qa10_gates
    assert "real_registry_record_count == 0" in qa10_gates
    assert "candidate_capability_ready == false" in qa10_gates
    assert "prospective_protocol_started == false" in qa10_gates
    assert "holdout_registered == false" in qa10_gates
    assert "recommended_next_phase == QA11" in qa10_gates
    assert "forward_data_gap_registry_ready == true" in qa11_gates
    assert "observation_evaluator_layer_ready == true" in qa11_gates
    assert "runtime_observable_role_count > 1" in qa11_gates
    assert "candidate_capability_ready == false" in qa11_gates
    assert "real_registry_record_count == 0" in qa11_gates
    assert "recommended_next_phase == QA12" in qa11_gates
    assert "readiness_semantics_reconciled == true" in qa12_gates
    assert "capture_topology_valid == true" in qa12_gates
    assert "no_write_source_preflight_ready == true" in qa12_gates
    assert "first_period_manifest_ready == true" in qa12_gates
    assert "manual_start_gate_ready == true" in qa12_gates
    assert "manual_start_allowed_now == false" in qa12_gates
    assert "real_registry_record_count == 0" in qa12_gates
    assert "candidate_capability_ready == false" in qa12_gates
    assert "qa13_allowed_now == false" in qa12_gates
    assert (
        "recommended_next_action == WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
        in qa12_gates
    )
    assert "source_identity_contract_ready == true" in phase10_gates
    assert "all_safely_implementable_adapters_completed == true" in phase10_gates
    assert "new_adapter_implemented_count > 0" in phase10_gates
    assert "new_forward_capture_ready_role_count > 0" in phase10_gates
    assert "candidate_capability_ready == false" in phase10_gates
    assert "prospective_track_next_action == WAIT_FOR_FIRST_ELIGIBLE_AS_OF" in (
        phase10_gates
    )
    assert "scenario_exposure_registry_ready == true" in qa3_gates
    assert "data_only_baseline_freeze_ready == true" in qa3_gates
    assert "parameter_tuning_executed == false" in qa3_gates
    assert "performance_backtest_executed == false" in qa3_gates
    assert "data_only_model_economically_validated == false" in qa3_gates
    assert "phase_9b1_allowed == false" in qa3_gates
    assert "recommended_next_phase == QA4" in qa3_gates


def test_agent_workflow_documents_qa4_scope_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA4 Scope-Governance Gates" in workflow
    assert "Phase QA4 book fidelity scope" in readme
    assert "production defaults" in readme
    assert "preserved" in readme


def test_agent_workflow_documents_qa5_shadow_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA5 Shadow Evidence Gates" in workflow
    assert "Phase QA5 book-core data contracts" in readme
    assert "shadow evidence model" in readme
    assert "production v1 remains unchanged" in readme


def test_agent_workflow_documents_qa6_aggregation_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA6 Shadow Aggregation Gates" in workflow
    assert "Phase QA6 shadow aggregation preregistration" in readme
    assert "candidate_selection_enabled=false" in readme
    assert "QA7" in readme


def test_agent_workflow_documents_qa8_evaluator_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA8 Book-Explicit Evaluator Gates" in workflow
    assert "Phase QA8 book-explicit evaluators and forward protocol" in readme
    assert "prospective shadow diagnostic protocol is registered but not started" in readme
    assert "QA9" in readme


def test_agent_workflow_documents_qa9_registry_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA9 Prospective Registry Gates" in workflow
    assert "Phase QA9 prospective shadow registry" in readme
    assert "armed_not_started" in readme
    assert "real_record_count=0" in readme
    assert "QA10" in readme


def test_agent_workflow_documents_qa10_runtime_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA10 Runtime Readiness Gates" in workflow
    assert "Phase QA10 shadow runtime and pre-start monitoring" in readme
    assert "runtime path" in readme
    assert "candidate capability" in readme
    assert "QA11" in readme


def test_agent_workflow_documents_qa11_forward_gap_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA11 Forward Observation Gates" in workflow
    assert "Phase QA11 book-core evaluator and forward data gaps" in readme
    assert "observation-only" in readme
    assert "QA12" in readme


def test_agent_workflow_documents_qa12_manual_start_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "QA12 Major-Group Manual Start Gates" in workflow
    assert "Phase QA12 major-group manual start readiness" in readme
    assert "WAIT_FOR_FIRST_ELIGIBLE_AS_OF" in readme
    assert "manual-start" in readme


def test_agent_workflow_documents_phase10_source_adapter_gates() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Phase 10 Source Adapter Remediation Gates" in workflow
    assert "Phase 10 book-core official source adapter remediation" in readme
    assert "development remediation track" in readme
    assert "WAIT_FOR_FIRST_ELIGIBLE_AS_OF" in readme


def test_prompt_templates_include_autonomous_policy() -> None:
    text = PROMPT_TEMPLATES_PATH.read_text(encoding="utf-8")

    assert "Autonomous completion policy" in text
    assert "If hard gates fail, inspect root cause, fix, and rerun" in text
