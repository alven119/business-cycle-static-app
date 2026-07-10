from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
    summarize_research_validation_dashboard_runtime,
    verify_research_validation_dashboard_directory,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    seed_local_current_cache_rehearsal,
)


def test_research_validation_dashboard_builds_to_tmp_path(tmp_path: Path) -> None:
    result = build_research_validation_dashboard(output_dir=tmp_path)

    assert result["research_dashboard_runtime_ready"] is True
    assert result["local_preview_server_ready"] is True
    assert result["browser_verification_ready"] is True
    assert result["rendered_scenario_count"] == 5
    assert result["missing_research_only_label_count"] == 0
    assert result["prohibited_claim_count"] == 0
    assert result["prohibited_action_field_count"] == 0
    assert result["browser_missing_required_element_count"] == 0
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "scenarios.html").is_file()
    assert (tmp_path / "scenario-euro_debt_slowdown_2011_2012.html").is_file()
    assert (tmp_path / "scenario-dotcom_cycle_2000_2003.html").is_file()
    assert (tmp_path / "assets" / "dashboard.css").is_file()
    assert (tmp_path / "assets" / "dashboard.js").is_file()


def test_research_validation_dashboard_static_summary_passes() -> None:
    summary = summarize_research_validation_dashboard_runtime()

    assert summary["research_dashboard_runtime_ready"] is True
    assert summary["dashboard_view_count"] == 7
    assert summary["scenario_count"] == 5
    assert summary["rendered_scenario_count"] == 5
    assert summary["browser_console_error_count"] == 0
    assert summary["browser_failed_resource_count"] == 0
    assert summary["browser_horizontal_overflow_count"] == 0
    assert summary["desktop_screenshot_nonblank"] is True
    assert summary["mobile_screenshot_nonblank"] is True


def test_research_validation_dashboard_rejects_repo_output_paths() -> None:
    with pytest.raises(ValueError, match="under /tmp"):
        build_research_validation_dashboard(output_dir="public/phase38")


def test_research_validation_dashboard_directory_verification_fails_closed(
    tmp_path: Path,
) -> None:
    result = build_research_validation_dashboard(output_dir=tmp_path)
    Path(result["index_path"]).unlink()

    verification = verify_research_validation_dashboard_directory(tmp_path)

    assert verification["browser_verification_ready"] is False
    assert verification["browser_missing_required_element_count"] > 0


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
            "--include-transition-risk-evidence-accumulation",
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
    assert "transition_risk_evidence_accumulation_view_ready=true" in result.stdout
    assert "transition_accumulation_lane_card_count=13" in result.stdout
    assert "next_required_observation_count=13" in result.stdout


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

    assert "current_macro_numeric_chart_coverage_view_ready=true" in result.stdout
    assert "phase74_local_current_cache_bridge_ready=true" in result.stdout
    assert "current_macro_numeric_chart_cache_scope=explicit_local_current_cache" in (
        result.stdout
    )
    assert "explicit ignored local current cache" in html
    assert "local current cache 可用" in html
    assert "browser_verification_ready=true" in result.stdout


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
