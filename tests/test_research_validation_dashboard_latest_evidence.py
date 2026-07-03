from __future__ import annotations

import subprocess
import sys

from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
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
    assert html.count("data-indicator-chart-payload") == 39
    assert html.count('data-chart-period="ytd"') == 39
    assert html.count('data-chart-period="trailing_1y"') == 39
    assert html.count('data-chart-period="trailing_5y"') == 39
    assert html.count("data-chart-data-mode") == 39
    assert html.count("data-chart-unavailable-reason") == 39
    assert "diagnostic method recipe visible" in html
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
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (output_dir / "latest-evidence.html").is_file()
    assert "latest_evidence_dashboard_view_ready=true" in result.stdout
    assert "phase_start_confirmation_view_ready=true" in result.stdout
    assert "phase_start_update_gate_view_ready=true" in result.stdout
    assert "dashboard_view_count=10" in result.stdout
    assert "browser_verification_ready=true" in result.stdout
