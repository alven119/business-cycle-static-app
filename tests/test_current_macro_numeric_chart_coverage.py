from __future__ import annotations

import subprocess
import sys

from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage,
    build_current_macro_numeric_chart_coverage_view_model,
    summarize_current_macro_numeric_chart_coverage,
)


def test_phase72_current_macro_numeric_chart_coverage_passes() -> None:
    summary = summarize_current_macro_numeric_chart_coverage()

    assert summary["result"] == "passed"
    assert summary["current_macro_numeric_chart_coverage_ready"] is True
    assert summary["role_count"] == 39
    assert summary["role_with_official_series_count"] == 37
    assert summary["role_without_official_series_count"] == 2
    assert summary["role_with_numeric_context_count"] == 37
    assert summary["role_with_available_chart_payload_count"] == 37
    assert summary["role_with_ytd_available_chart_count"] == 37
    assert summary["role_with_trailing_1y_available_chart_count"] == 37
    assert summary["role_with_trailing_5y_available_chart_count"] == 37
    assert summary["chart_unavailable_role_count"] == 2
    assert summary["chart_point_count"] > 0
    assert summary["fixture_cache_written_under_tmp"] is True
    assert summary["repo_output_written_count"] == 0
    assert summary["fixture_mislabeled_as_live_count"] == 0
    assert summary["point_in_time_claim_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase72_rows_preserve_missing_and_research_only_boundaries() -> None:
    artifact = build_current_macro_numeric_chart_coverage()
    rows = {row["role_id"]: row for row in artifact["role_chart_coverage_rows"]}

    assert rows["boom_consumer_confidence"]["chart_available"] is False
    assert rows["growth_adp_employment"]["chart_available"] is False
    assert rows["boom_consumer_confidence"]["chart_coverage_status"] == (
        "unavailable_no_official_series"
    )
    assert rows["growth_adp_employment"]["chart_coverage_status"] == (
        "unavailable_no_official_series"
    )
    assert all(
        row["numeric_context_promoted_to_phase_support"] is False
        for row in artifact["role_chart_coverage_rows"]
    )
    assert all(
        row["current_data_used_to_infer_declared_phase"] is False
        for row in artifact["role_chart_coverage_rows"]
    )
    assert artifact["prohibited_output_field_count"] == 0


def test_phase72_view_model_is_research_only() -> None:
    view_model = build_current_macro_numeric_chart_coverage_view_model()

    assert view_model["view_id"] == "current_macro_numeric_chart_coverage"
    assert view_model["research_only"] is True
    assert view_model["role_with_numeric_context_count"] == 37
    assert view_model["role_with_available_chart_payload_count"] == 37
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0


def test_show_current_macro_numeric_chart_coverage_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_current_macro_numeric_chart_coverage.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "current_macro_numeric_chart_coverage_ready=true" in completed.stdout
    assert "role_with_numeric_context_count=37" in completed.stdout
    assert "role_with_available_chart_payload_count=37" in completed.stdout
    assert "result=passed" in completed.stdout
