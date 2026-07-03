from __future__ import annotations

from business_cycle.audits.test_suite_doctrine_quarantine import (
    MARKER_NAMES,
    TEST_FILE_MARKER_MAP,
    markers_for_test_path,
    summarize_test_suite_doctrine_quarantine,
)


def test_pytest_marker_taxonomy_registered() -> None:
    summary = summarize_test_suite_doctrine_quarantine()

    assert summary["pytest_marker_taxonomy_ready"] is True
    for marker in MARKER_NAMES:
        assert summary[f"{marker}_marker_registered"] is True


def test_high_risk_marker_map_has_all_categories() -> None:
    summary = summarize_test_suite_doctrine_quarantine()

    assert summary["legacy_v1_test_count"] > 0
    assert summary["doctrine_aligned_test_count"] > 0
    assert summary["transition_monitor_test_count"] > 0
    assert summary["portfolio_policy_research_test_count"] > 0
    assert summary["historical_replay_backtest_test_count"] > 0
    assert summary["governance_scaffold_test_count"] > 0
    assert summary["safety_test_count"] > 0
    assert summary["live_optional_test_count"] > 0
    assert summary["archive_regression_test_count"] > 0
    assert summary["closure_archive_test_count"] > 0
    assert summary["legacy_v1_default_test_count"] == 0


def test_marker_lookup_for_known_high_risk_files() -> None:
    assert "legacy_v1" in markers_for_test_path("tests/test_phase_scoring.py")
    assert "archive_regression" in markers_for_test_path(
        "tests/test_phase_scoring.py"
    )
    assert "archive_regression" in markers_for_test_path(
        "tests/test_phase20_historical_validation_dry_run_closure.py"
    )
    assert "archive_regression" not in markers_for_test_path(
        "tests/test_boom_transition_monitor.py"
    )
    assert "transition_monitor" in markers_for_test_path("tests/test_state_machine.py")
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_ordered_cycle_state_machine.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_boom_transition_monitor.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase_start_research_assistant.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_boom_transition_evidence_wiring.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_boom_transition_dashboard_surface.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase50_transition_surface_data_risk_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_declared_boom_start_governance.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_macro_indicator_gap_alternative_sources.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase51_declared_start_and_gap_alternatives_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_declared_phase_start_confirmation.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase69_declared_phase_start_confirmation_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_declared_phase_start_registry_preview.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase70_declared_phase_start_registry_preview_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_declared_phase_start_registry_update_gate.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase71_declared_phase_start_registry_update_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_official_macro_source_adapter_wiring.py"
    )
    assert "doctrine_aligned" in markers_for_test_path(
        "tests/test_product_capability_progress.py"
    )
    assert "doctrine_aligned" in markers_for_test_path(
        "tests/test_product_capability_95_roadmap.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase52_official_macro_source_adapter_wiring_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_composite_transition_surface_value_wiring.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase53_composite_transition_surface_value_wiring_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_low_cost_macro_source_completion.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase54_low_cost_macro_source_completion_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_macro_indicator_coverage_readiness_matrix.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase55_macro_indicator_coverage_readiness_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_indicator_detail_source_risk_value_rendering.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase56_indicator_detail_source_risk_value_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_boom_to_recession_transition_surface_completion.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase57_boom_to_recession_transition_surface_completion_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_ordered_cycle_transition_lane_templates.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase58_ordered_cycle_transition_lane_templates_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_evidence_freshness_release_value_continuity.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase60_evidence_freshness_release_value_continuity_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_major_group_evidence_profile_readiness.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase61_major_group_evidence_profile_readiness_closure.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_indicator_dashboard_explanation_drilldown.py"
    )
    assert "transition_monitor" in markers_for_test_path(
        "tests/test_phase62_indicator_dashboard_explanation_drilldown_closure.py"
    )
    assert "portfolio_policy_research" in markers_for_test_path(
        "tests/test_portfolio_policy_template_schema.py"
    )
    assert "historical_replay_backtest" in markers_for_test_path(
        "tests/test_historical_accuracy_metrics.py"
    )
    assert "live_optional" in markers_for_test_path("tests/test_current_live_refresh_probe.py")


def test_legacy_v1_entries_have_compatibility_labels() -> None:
    legacy_entries = [
        entry for entry in TEST_FILE_MARKER_MAP.values() if "legacy_v1" in entry.markers
    ]

    assert legacy_entries
    assert all(entry.legacy_compatibility_label for entry in legacy_entries)


def test_live_optional_marker_registered_but_not_required_by_default() -> None:
    summary = summarize_test_suite_doctrine_quarantine()

    assert summary["live_optional_marker_registered"] is True
    assert summary["live_optional_tests_not_in_default_ci"] is True


def test_archive_regression_marker_registered_but_not_required_by_default() -> None:
    summary = summarize_test_suite_doctrine_quarantine()

    assert summary["archive_regression_marker_registered"] is True
    assert summary["archive_regression_tests_not_in_default_ci"] is True
    assert summary["v1_default_removed"] is True
