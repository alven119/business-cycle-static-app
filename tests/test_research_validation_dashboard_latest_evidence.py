from __future__ import annotations

import subprocess
import sys

from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
)
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    build_local_current_cache_dashboard_bridge_view_model,
    seed_local_current_cache_rehearsal,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


def test_latest_evidence_dashboard_view_renders_phase62_drilldown(tmp_path) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert result["prohibited_claim_count"] == 0
    assert result["prohibited_action_field_count"] == 0
    assert (tmp_path / "data" / "dashboard_bundle.json").is_file()
    assert 'data-dashboard-view="indicator_dashboard_explanation_drilldown"' in html
    assert "Latest Evidence / Indicator Drilldown" in html
    assert "phase score is not the product answer" in html
    assert html.count("data-major-group-drilldown=") == 24
    assert html.count("data-role-drilldown=") == 39
    assert html.count("data-source-detail") == 39
    assert html.count("data-release-timing-detail") == 39
    assert html.count("data-freshness-detail") == 39
    assert html.count("data-transformation-detail") == 39
    assert html.count("data-rule-usability-detail") == 39
    assert html.count("data-provenance-detail") == 39
    assert html.count("data-abstention-detail") == 39
    assert html.count("data-score-transparency-detail") == 39
    assert html.count("data-method-recipe-detail") == 39
    assert html.count("data-method-confidence-detail") == 39
    assert html.count("data-method-pseudo-code-detail") == 39
    assert html.count("data-method-directionality-detail") == 39
    assert html.count("data-indicator-chart-payload") == 39
    assert html.count("data-indicator-trend-link") == 39
    assert html.count("data-role-trend-shortcut") == 39
    assert html.count("data-indicator-trend-target") == 39
    assert html.count('data-chart-period="ytd"') == 39
    assert html.count('data-chart-period="trailing_1y"') == 39
    assert html.count('data-chart-period="trailing_5y"') == 39
    assert html.count("data-chart-data-mode") == 39
    assert html.count("data-chart-unavailable-reason") == 39
    assert "diagnostic method recipe visible" in html
    assert "Diagnostic recipe transparency" in html
    assert "Confidence reducers" in html
    assert "Calculation steps" in html
    assert "unavailable charts are not zero" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_phase69_start_confirmation(
    tmp_path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    confirmation = build_declared_phase_start_confirmation_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        declared_phase_start_confirmation=confirmation,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-declared-phase-start-confirmation" in html
    assert html.count("data-phase-start-window=") == 3
    assert "使用者粗略假設" in html
    assert "registry write allowed: false" in html
    assert "phase age precision: false" in html
    assert "CONFIRM_DECLARED_BOOM_START_DATE_OR_WINDOW" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_phase71_update_gate(tmp_path) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    confirmation = build_declared_phase_start_confirmation_view_model()
    update_gate = build_declared_phase_start_registry_update_gate_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        declared_phase_start_confirmation=confirmation,
        declared_phase_start_registry_update_gate=update_gate,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-declared-phase-start-update-gate" in html
    assert "data-phase-start-update-handoff" in html
    assert html.count("data-phase-start-update-row=") == 3
    assert "canonical write allowed: false" in html
    assert "SUPPLY_EXPLICIT_START_DATE_OR_WINDOW" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_current_macro_numeric_chart_coverage(
    tmp_path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-current-macro-numeric-chart-coverage" in html
    assert "data-chart-coverage-mode" in html
    assert "fixture_current_cache_connectivity" in html
    assert html.count("data-current-macro-chart-row=") == 39
    assert html.count("data-coverage-trend-link") == 39
    assert html.count("data-indicator-trend-link") == 78
    assert html.count("data-indicator-trend-target") == 39
    assert html.count('data-chart-period-svg="ytd"') == 37
    assert html.count('data-chart-period-svg="trailing_1y"') == 37
    assert html.count('data-chart-period-svg="trailing_5y"') == 37
    assert html.count("data-trend-chart-svg") == 111
    assert html.count("data-trend-chart-empty") == 6
    assert "查看走勢" in html
    assert "numeric context is not phase support" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_decision_explanation(
    tmp_path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    explanation = build_dashboard_decision_explanation_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=explanation,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-dashboard-decision-explanation" in html
    assert "data-declared-state-summary" in html
    assert "data-legal-next-transition-summary" in html
    assert "data-support-contradiction-summary" in html
    assert "data-missing-evidence-summary" in html
    assert "data-why-not-formal-summary" in html
    assert html.count("data-decision-explanation-card") == 5
    assert html.count("data-dashboard-trust-caveat") == 5
    assert "Dashboard decision explanation" in html
    assert "declared state: boom" in html
    assert "legal next: recession" in html
    assert "formal gate: closed" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_current_data_refresh_ux(
    tmp_path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    refresh_ux = build_current_data_refresh_ux_view_model(
        current_macro_numeric_chart_coverage=coverage,
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        current_data_refresh_ux=refresh_ux,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["browser_missing_required_element_count"] == 0
    assert "data-current-data-refresh-ux" in html
    assert "data-refresh-mode-summary" in html
    assert "data-last-update-summary" in html
    assert "data-freshness-summary" in html
    assert "data-source-risk-refresh-summary" in html
    assert "data-manual-refresh-handoff" in html
    assert "data-no-live-refresh-execution" in html
    assert html.count("data-refresh-ux-card") == 5
    assert html.count("data-manual-refresh-handoff-step") == 5
    assert html.count("data-refresh-trust-caveat") == 5
    assert "Current data refresh UX" in html
    assert "live refresh 未在本 phase 執行" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_latest_evidence_dashboard_renders_local_current_cache_bridge(
    tmp_path,
) -> None:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_local_current_cache_dashboard_bridge_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    result = build_research_validation_dashboard(output_dir=tmp_path, bundle=bundle)
    html = (tmp_path / "latest-evidence.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert "data-local-current-cache-scope" in html
    assert "tmp_seeded_local_current_cache_rehearsal" in html
    assert "revised/latest explanation context" in html
    assert "not point-in-time evidence" in html
    assert html.count("available_local_current_cache") == 37
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_build_dashboard_script_accepts_latest_evidence_drilldown(tmp_path) -> None:
    output_dir = tmp_path / "dashboard"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
            "--include-latest-evidence-drilldown",
            "--include-phase-start-confirmation",
            "--include-phase-start-update-gate",
            "--include-current-macro-numeric-chart-coverage",
            "--include-dashboard-decision-explanation",
            "--include-current-data-refresh-ux",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "latest-evidence.html").is_file()
    assert "latest_evidence_dashboard_view_ready=true" in result.stdout
    assert "dashboard_decision_explanation_view_ready=true" in result.stdout
    assert "current_data_refresh_ux_view_ready=true" in result.stdout
    assert "current_data_refresh_ux_card_count=5" in result.stdout
    assert "current_data_refresh_ux_handoff_step_count=5" in result.stdout


def test_build_dashboard_script_accepts_explicit_current_cache_dir(tmp_path) -> None:
    output_dir = tmp_path / "dashboard"
    cache_dir = tmp_path / "fred_current_cache"
    seed_local_current_cache_rehearsal(cache_dir)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
            "--current-cache-dir",
            str(cache_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    html = (output_dir / "latest-evidence.html").read_text(encoding="utf-8")

    assert (output_dir / "latest-evidence.html").is_file()
    assert "current_macro_numeric_chart_coverage_view_ready=true" in result.stdout
    assert "phase74_local_current_cache_bridge_ready=true" in result.stdout
    assert "current_macro_numeric_chart_cache_scope=explicit_local_current_cache" in (
        result.stdout
    )
    assert "explicit ignored local current cache" in html
    assert "available_local_current_cache" in html
    assert "latest_evidence_dashboard_view_ready=true" in result.stdout
    assert "browser_verification_ready=true" in result.stdout


def test_portfolio_replay_dashboard_surface_renders_phase81(tmp_path) -> None:
    output_dir = tmp_path / "dashboard"
    surface = build_portfolio_replay_dashboard_surface_view_model()
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=surface,
    )
    result = build_research_validation_dashboard(output_dir=output_dir, bundle=bundle)
    html = (output_dir / "portfolio-replay.html").read_text(encoding="utf-8")

    assert result["browser_verification_ready"] is True
    assert result["prohibited_action_field_count"] == 0
    assert (output_dir / "portfolio-replay.html").is_file()
    assert "Portfolio / Replay Research Surface" in html
    assert "data-dashboard-view=\"portfolio_replay_dashboard_surface\"" in html
    assert html.count("data-backtest-artifact-card") == 10
    assert html.count("data-backtest-lineage-row") == 10
    assert "metric values not computed" in html
    assert "candidate_phase" not in html
    assert "current_phase" not in html


def test_build_dashboard_script_accepts_portfolio_replay_surface(tmp_path) -> None:
    output_dir = tmp_path / "dashboard"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_research_validation_dashboard.py",
            "--output-dir",
            str(output_dir),
            "--include-portfolio-replay-surface",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "portfolio-replay.html").is_file()
    assert "portfolio_replay_dashboard_surface_ready=true" in result.stdout
    assert "portfolio_replay_dashboard_card_count=10" in result.stdout
    assert "research_backtest_artifact_count=10" in result.stdout
    assert "browser_verification_ready=true" in result.stdout
