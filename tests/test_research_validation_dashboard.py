from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
    summarize_research_validation_dashboard_runtime,
    verify_research_validation_dashboard_directory,
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
