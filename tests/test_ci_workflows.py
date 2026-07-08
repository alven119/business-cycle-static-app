from pathlib import Path

import yaml


WORKFLOW_DIR = Path(".github/workflows")
FAST_CI = WORKFLOW_DIR / "fast-ci.yml"
FULL_CI = WORKFLOW_DIR / "full-ci.yml"
NIGHTLY_CI = WORKFLOW_DIR / "nightly-ci.yml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ci_workflow_yaml_is_parseable() -> None:
    for path in [FAST_CI, FULL_CI, NIGHTLY_CI]:
        assert path.is_file()
        assert yaml.safe_load(_read(path))


def test_fast_ci_has_required_quality_gates_without_full_pytest() -> None:
    workflow = _read(FAST_CI)

    required_snippets = [
        "pull_request:",
        "push:",
        "cache: pip",
        "cancel-in-progress: true",
        "ruff check .",
        "git diff --check",
        "python scripts/run_ci_safety_scans.py",
        "python scripts/run_qa0_integrity_audit.py",
        "python scripts/run_fast_ci_contract_tests.py",
    ]
    for snippet in required_snippets:
        assert snippet in workflow

    assert "python -m pytest" not in workflow


def test_full_ci_runs_full_pytest_and_key_closures_on_main_or_manual() -> None:
    workflow = _read(FULL_CI)

    required_snippets = [
        "workflow_dispatch:",
        "branches:",
        "- main",
        "cache: pip",
        "cancel-in-progress: true",
        "Run default product-core pytest without FRED API key",
        "env -u FRED_API_KEY python -m pytest",
        "ruff check .",
        "git diff --check",
        "python scripts/run_ci_closure_checks.py --tier full",
    ]
    for snippet in required_snippets:
        assert snippet in workflow


def test_nightly_ci_runs_full_regression_and_extended_closures() -> None:
    workflow = _read(NIGHTLY_CI)

    required_snippets = [
        "schedule:",
        "cache: pip",
        "cancel-in-progress: true",
        "fail-fast: false",
        "legacy_v1_compatibility",
        "phase_closure_history",
        "historical_validation_replay",
        "portfolio_policy_research",
        "source_provider_cache",
        "book_core_shadow_governance",
        "dashboard_rendering_archive",
        "infrastructure_misc_archive",
        "python scripts/run_archive_regression_shard.py",
        "--shard ${{ matrix.shard }}",
        "python scripts/run_ci_closure_checks.py --tier nightly",
    ]
    for snippet in required_snippets:
        assert snippet in workflow


def test_ci_closure_helper_contains_expected_closure_bundles() -> None:
    helper = Path("scripts/run_ci_closure_checks.py").read_text(encoding="utf-8")

    required_snippets = [
        "show_test_suite_reduction_plan.py",
        "show_archive_regression_shards.py",
        "show_product_capability_progress.py",
        "show_product_capability_95_roadmap.py",
        "show_product_capability_completion_sprint.py",
        "show_github_actions_test_efficiency.py",
        "show_phase105_nas_operator_deployment_handoff_closure.py",
        "show_phase104_nas_postgres_revised_import_closure.py",
        "show_phase103_ds925_connectivity_smoke_closure.py",
        "show_phase102_guided_ds925_install_smoke_closure.py",
        "show_phase101_private_local_startup_smoke_closure.py",
        "show_phase100_container_manager_bundle_closure.py",
        "show_phase99_nas_postgres_readonly_smoke_closure.py",
        "show_phase98_nas_service_lifecycle_closure.py",
        "show_phase97_nas_asgi_adapter_closure.py",
        "show_phase96_nas_app_shell_closure.py",
        "show_phase95_nas_service_dashboard_closure.py",
        "show_phase94_nas_indicator_snapshot_closure.py",
        "show_phase93_vintage_pit_backfill_availability_closure.py",
        "show_phase92_revised_macro_data_import_closure.py",
        "show_phase91_postgres_macro_warehouse_closure.py",
        "show_phase90_nas_dynamic_service_architecture_closure.py",
        "show_phase89a_portfolio_policy_wording_alignment_closure.py",
        "show_phase88_portfolio_policy_replay_research_surface_closure.py",
        "show_phase87_research_dashboard_production_readiness_rehearsal_closure.py",
        "show_phase86_transition_risk_evidence_accumulation_closure.py",
        "show_phase85_current_data_refresh_ux_closure.py",
        "show_phase84_dashboard_decision_explanation_closure.py",
        "show_phase83_indicator_trend_drilldown_closure.py",
        "show_phase82_replay_backtest_lineage_closure.py",
        "show_phase81_portfolio_replay_dashboard_surface_closure.py",
        "show_phase80_research_backtest_artifacts_closure.py",
        "show_phase79_historical_replay_runner_closure.py",
        "show_phase78_cash_flow_backtest_kernel_closure.py",
        "show_phase77_portfolio_policy_replay_schedule_closure.py",
        "show_phase76_portfolio_policy_template_fixtures_closure.py",
        "show_phase75_all_capability_roadmap_portfolio_research_closure.py",
        "show_phase74_local_current_cache_dashboard_bridge_closure.py",
        "show_phase73_dashboard_indicator_method_explanation_closure.py",
        "show_phase71_declared_phase_start_registry_update_closure.py",
        "show_phase70_declared_phase_start_registry_preview_closure.py",
        "show_phase69_declared_phase_start_confirmation_closure.py",
        "show_phase67_transition_timing_replay_preview_closure.py",
        "show_qa12_major_group_manual_start_closure.py",
        "run_qa0_integrity_audit.py",
        "sys.executable",
    ]
    for snippet in required_snippets:
        assert snippet in helper

    nightly_only_snippets = [
        "show_phase64_indicator_transparency_chart_payload_closure.py",
        "show_phase63_latest_evidence_dashboard_wiring_closure.py",
        "show_phase62_indicator_dashboard_explanation_drilldown_closure.py",
        "show_phase61_major_group_evidence_profile_readiness_closure.py",
        "show_phase60_evidence_freshness_release_value_continuity_closure.py",
        "show_phase58_ordered_cycle_transition_lane_templates_closure.py",
        "show_phase57_boom_to_recession_transition_surface_completion_closure.py",
        "show_phase56_indicator_detail_source_risk_value_closure.py",
        "show_phase55_macro_indicator_coverage_readiness_closure.py",
        "show_phase54_low_cost_macro_source_completion_closure.py",
        "show_phase53_composite_transition_surface_value_wiring_closure.py",
        "show_phase52_official_macro_source_adapter_wiring_closure.py",
        "show_phase51_declared_start_and_gap_alternatives_closure.py",
        "show_phase50_transition_surface_data_risk_closure.py",
        "show_phase49_boom_transition_dashboard_closure.py",
        "show_phase48_boom_transition_evidence_wiring_closure.py",
        "show_phase47_phase_start_research_assistant_closure.py",
        "show_phase46_boom_transition_monitor_closure.py",
        "show_phase45_declared_cycle_state_closure.py",
        "show_phase42_current_freshness_and_evidence_profile_closure.py",
        "show_phase40_current_data_refresh_closure.py",
        "show_phase39_current_research_snapshot_closure.py",
        "show_phase38_research_validation_dashboard_closure.py",
        "show_phase37_recession_recovery_pit_remediation_closure.py",
        "show_phase36r_recession_recovery_evidence_completion_closure.py",
        "show_phase36_historical_validation_result_realization_closure.py",
        "show_phase35_historical_comparability_realization_closure.py",
        "show_phase34_autonomous_blocker_unblock_closure.py",
        "show_phase33_blocker_resolution_execution_closure.py",
        "show_phase32_genuine_blocker_resolution_plan_closure.py",
        "show_phase31_validation_blockage_remediation_closure.py",
        "show_phase30_validation_blockage_diagnostics_closure.py",
        "show_phase29_historical_accuracy_metrics_closure.py",
        "show_phase28_predicted_label_comparison_closure.py",
        "show_phase27_predicted_label_artifact_closure.py",
        "show_phase26_predicted_label_mapping_contract_closure.py",
        "show_phase25_research_decision_output_closure.py",
        "show_phase24_research_decision_output_contract_closure.py",
        "show_phase23_comparison_coverage_metrics_closure.py",
        "show_phase22_label_comparison_artifact_closure.py",
        "show_phase21_metric_preregistration_closure.py",
        "show_phase20_historical_validation_dry_run_closure.py",
        "show_phase14_non_emitting_decision_runtime_closure.py",
        "show_phase10_book_core_source_adapter_closure.py",
    ]
    for snippet in nightly_only_snippets:
        assert snippet in helper


def test_ci_safety_scan_helper_uses_tracked_text_claim_scan() -> None:
    helper = Path("scripts/run_ci_safety_scans.py").read_text(encoding="utf-8")

    assert "git\", \"ls-files" in helper
    assert "git\", \"grep\", \"-nI\", \"-E" in helper
    assert "grep -R" not in helper
    assert '"book-faithful model " + "complete"' in helper
    assert '"production-" + "ready"' in helper


def test_ci_workflows_do_not_publish_or_mutate_git_history() -> None:
    workflow = "\n".join(_read(path) for path in [FAST_CI, FULL_CI, NIGHTLY_CI])

    forbidden_snippets = [
        "actions/deploy-pages",
        "git add ",
        "git commit",
        "git push",
        "git reset",
        "git clean",
        "candidate_phase:",
        "current_phase:",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in workflow
