#!/usr/bin/env python
"""Run CI closure-check bundles without wiring shadow commands into workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys


FULL_CLOSURE_SCRIPTS = (
    "scripts/audit_product_doctrine_enforcement.py",
    "scripts/audit_test_suite_doctrine_quarantine.py",
    "scripts/show_test_suite_reduction_plan.py",
    "scripts/show_archive_regression_shards.py",
    "scripts/show_product_capability_progress.py",
    "scripts/show_test_suite_index.py",
    "scripts/show_github_actions_test_efficiency.py",
    "scripts/show_phase117_transition_pit_backfill_closure.py",
    "scripts/show_phase110_nas_postgres_live_revised_import_closure.py",
    "scripts/show_phase109_nas_tailscale_private_https_closure.py",
    "scripts/show_qa12_major_group_manual_start_closure.py",
    "scripts/run_qa0_integrity_audit.py",
)

NIGHTLY_CLOSURE_SCRIPTS = (
    "scripts/audit_product_doctrine_enforcement.py",
    "scripts/audit_test_suite_doctrine_quarantine.py",
    "scripts/show_test_suite_reduction_plan.py",
    "scripts/show_archive_regression_shards.py",
    "scripts/show_product_capability_95_roadmap.py",
    "scripts/show_product_capability_completion_sprint.py",
    "scripts/show_test_suite_index.py",
    "scripts/show_github_actions_test_efficiency.py",
    "scripts/show_phase117_transition_pit_backfill_closure.py",
    "scripts/show_phase116_nas_release_aware_refresh_closure.py",
    "scripts/show_phase115_nas_source_retry_restore_closure.py",
    "scripts/show_phase114_nas_official_release_operations_closure.py",
    "scripts/show_phase113_nas_declared_phase_start_governance_closure.py",
    "scripts/show_phase112_nas_scheduled_revised_refresh_closure.py",
    "scripts/show_phase111_nas_live_postgres_dashboard_closure.py",
    "scripts/show_phase110_nas_postgres_live_revised_import_closure.py",
    "scripts/show_phase109_nas_tailscale_private_https_closure.py",
    "scripts/show_phase108_nas_container_manager_live_start_closure.py",
    "scripts/show_phase107_nas_app_container_runtime_bundle_closure.py",
    "scripts/show_phase106_nas_operator_live_deployment_session_closure.py",
    "scripts/show_phase105_nas_operator_deployment_handoff_closure.py",
    "scripts/show_phase104_nas_postgres_revised_import_closure.py",
    "scripts/show_phase103_ds925_connectivity_smoke_closure.py",
    "scripts/show_phase102_guided_ds925_install_smoke_closure.py",
    "scripts/show_phase101_private_local_startup_smoke_closure.py",
    "scripts/show_phase100_container_manager_bundle_closure.py",
    "scripts/show_phase99_nas_postgres_readonly_smoke_closure.py",
    "scripts/show_phase98_nas_service_lifecycle_closure.py",
    "scripts/show_phase97_nas_asgi_adapter_closure.py",
    "scripts/show_phase96_nas_app_shell_closure.py",
    "scripts/show_phase95_nas_service_dashboard_closure.py",
    "scripts/show_phase94_nas_indicator_snapshot_closure.py",
    "scripts/show_phase93_vintage_pit_backfill_availability_closure.py",
    "scripts/show_phase92_revised_macro_data_import_closure.py",
    "scripts/show_phase91_postgres_macro_warehouse_closure.py",
    "scripts/show_phase90_nas_dynamic_service_architecture_closure.py",
    "scripts/show_phase89a_portfolio_policy_wording_alignment_closure.py",
    "scripts/show_phase88_portfolio_policy_replay_research_surface_closure.py",
    "scripts/show_phase87_research_dashboard_production_readiness_rehearsal_closure.py",
    "scripts/show_phase86_transition_risk_evidence_accumulation_closure.py",
    "scripts/show_phase85_current_data_refresh_ux_closure.py",
    "scripts/show_phase84_dashboard_decision_explanation_closure.py",
    "scripts/show_phase83_indicator_trend_drilldown_closure.py",
    "scripts/show_phase82_replay_backtest_lineage_closure.py",
    "scripts/show_phase81_portfolio_replay_dashboard_surface_closure.py",
    "scripts/show_phase80_research_backtest_artifacts_closure.py",
    "scripts/show_phase79_historical_replay_runner_closure.py",
    "scripts/show_phase78_cash_flow_backtest_kernel_closure.py",
    "scripts/show_phase77_portfolio_policy_replay_schedule_closure.py",
    "scripts/show_phase76_portfolio_policy_template_fixtures_closure.py",
    "scripts/show_phase75_all_capability_roadmap_portfolio_research_closure.py",
    "scripts/show_phase74_local_current_cache_dashboard_bridge_closure.py",
    "scripts/show_phase73_dashboard_indicator_method_explanation_closure.py",
    "scripts/show_phase72_current_macro_numeric_chart_coverage_closure.py",
    "scripts/show_phase71_declared_phase_start_registry_update_closure.py",
    "scripts/show_phase70_declared_phase_start_registry_preview_closure.py",
    "scripts/show_phase69_declared_phase_start_confirmation_closure.py",
    "scripts/show_phase68_phase_start_numeric_test_index_closure.py",
    "scripts/show_phase67_transition_timing_replay_preview_closure.py",
    "scripts/show_phase64_indicator_transparency_chart_payload_closure.py",
    "scripts/show_phase63_latest_evidence_dashboard_wiring_closure.py",
    "scripts/show_phase62_indicator_dashboard_explanation_drilldown_closure.py",
    "scripts/show_phase61_major_group_evidence_profile_readiness_closure.py",
    "scripts/show_phase60_evidence_freshness_release_value_continuity_closure.py",
    "scripts/show_phase58_ordered_cycle_transition_lane_templates_closure.py",
    "scripts/show_phase57_boom_to_recession_transition_surface_completion_closure.py",
    "scripts/show_phase56_indicator_detail_source_risk_value_closure.py",
    "scripts/show_phase55_macro_indicator_coverage_readiness_closure.py",
    "scripts/show_phase54_low_cost_macro_source_completion_closure.py",
    "scripts/show_phase53_composite_transition_surface_value_wiring_closure.py",
    "scripts/show_phase52_official_macro_source_adapter_wiring_closure.py",
    "scripts/show_phase51_declared_start_and_gap_alternatives_closure.py",
    "scripts/show_phase50_transition_surface_data_risk_closure.py",
    "scripts/show_phase49_boom_transition_dashboard_closure.py",
    "scripts/show_phase48_boom_transition_evidence_wiring_closure.py",
    "scripts/show_phase47_phase_start_research_assistant_closure.py",
    "scripts/show_phase46_boom_transition_monitor_closure.py",
    "scripts/show_phase45_declared_cycle_state_closure.py",
    "scripts/show_phase42_current_freshness_and_evidence_profile_closure.py",
    "scripts/show_phase41_live_current_refresh_smoke_closure.py",
    "scripts/show_phase40_current_data_refresh_closure.py",
    "scripts/show_phase39_current_research_snapshot_closure.py",
    "scripts/show_phase38_research_validation_dashboard_closure.py",
    "scripts/show_phase37_recession_recovery_pit_remediation_closure.py",
    "scripts/show_phase36r_recession_recovery_evidence_completion_closure.py",
    "scripts/show_phase36_historical_validation_result_realization_closure.py",
    "scripts/show_phase35_historical_comparability_realization_closure.py",
    "scripts/show_phase34_autonomous_blocker_unblock_closure.py",
    "scripts/show_phase33_blocker_resolution_execution_closure.py",
    "scripts/show_phase32_genuine_blocker_resolution_plan_closure.py",
    "scripts/show_phase31_validation_blockage_remediation_closure.py",
    "scripts/show_phase30_validation_blockage_diagnostics_closure.py",
    "scripts/show_phase29_historical_accuracy_metrics_closure.py",
    "scripts/show_phase28_predicted_label_comparison_closure.py",
    "scripts/show_phase27_predicted_label_artifact_closure.py",
    "scripts/show_phase26_predicted_label_mapping_contract_closure.py",
    "scripts/show_phase25_research_decision_output_closure.py",
    "scripts/show_phase24_research_decision_output_contract_closure.py",
    "scripts/show_phase23_comparison_coverage_metrics_closure.py",
    "scripts/show_phase22_label_comparison_artifact_closure.py",
    "scripts/show_phase21_metric_preregistration_closure.py",
    "scripts/show_phase20_historical_validation_dry_run_closure.py",
    "scripts/show_phase19_validation_execution_readiness_closure.py",
    "scripts/show_phase18_historical_input_readiness_closure.py",
    "scripts/show_phase17_historical_manifest_closure.py",
    "scripts/show_phase16_validation_harness_closure.py",
    "scripts/show_phase15_validation_protocol_closure.py",
    "scripts/show_phase14_non_emitting_decision_runtime_closure.py",
    "scripts/show_phase13_formal_decision_contract_closure.py",
    "scripts/show_phase12_book_core_gap_resolution_closure.py",
    "scripts/show_phase11_book_core_phase_evidence_closure.py",
    "scripts/show_phase10_book_core_source_adapter_closure.py",
    "scripts/show_qa12_major_group_manual_start_closure.py",
    "scripts/run_qa0_integrity_audit.py",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=("full", "nightly"), required=True)
    args = parser.parse_args(argv)

    scripts = FULL_CLOSURE_SCRIPTS if args.tier == "full" else NIGHTLY_CLOSURE_SCRIPTS
    for script in scripts:
        print(f"running {script}", flush=True)
        subprocess.run([sys.executable, script], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
