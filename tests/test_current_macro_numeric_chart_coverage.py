from __future__ import annotations

import subprocess
import sys

from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage,
    build_current_macro_numeric_chart_coverage_view_model,
    summarize_current_macro_numeric_chart_coverage,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    build_local_current_cache_dashboard_bridge,
    build_local_current_cache_dashboard_bridge_view_model,
    seed_local_current_cache_rehearsal,
    summarize_local_current_cache_dashboard_bridge,
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
    available_row = next(row for row in rows.values() if row["chart_available"])

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
    assert [period["period_id"] for period in available_row["chart_periods"]] == [
        "ytd",
        "trailing_1y",
        "trailing_5y",
    ]
    assert all(
        period["chart_status"] == "available"
        for period in available_row["chart_periods"]
    )
    assert all(
        period["point_count"] > 0
        for period in available_row["chart_periods"]
    )
    assert [period["period_id"] for period in rows["growth_adp_employment"]["chart_periods"]] == [
        "ytd",
        "trailing_1y",
        "trailing_5y",
    ]
    assert all(
        period["chart_status"] == "unavailable"
        for period in rows["growth_adp_employment"]["chart_periods"]
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


def test_phase74_local_current_cache_bridge_passes_with_tmp_rehearsal() -> None:
    summary = summarize_local_current_cache_dashboard_bridge()

    assert summary["result"] == "passed"
    assert summary["local_current_cache_dashboard_bridge_ready"] is True
    assert summary["local_current_cache_input_supported"] is True
    assert summary["tmp_seeded_local_current_cache_rehearsal_ready"] is True
    assert summary["role_count"] == 39
    assert summary["role_with_local_cache_numeric_context_count"] == 37
    assert summary["role_with_available_local_cache_chart_count"] == 37
    assert summary["role_with_ytd_available_local_cache_chart_count"] == 37
    assert summary["role_with_trailing_1y_available_local_cache_chart_count"] == 37
    assert summary["role_with_trailing_5y_available_local_cache_chart_count"] == 37
    assert summary["local_cache_unavailable_role_count"] == 2
    assert summary["local_cache_series_file_found_count"] > 0
    assert summary["local_cache_chart_point_count"] > 0
    assert summary["repo_output_written_count"] == 0
    assert summary["local_cache_written_by_bridge_count"] == 0
    assert summary["fixture_mislabeled_as_live_count"] == 0
    assert summary["local_cache_value_mislabeled_as_point_in_time_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase74_bridge_accepts_explicit_tmp_cache(tmp_path) -> None:
    cache_dir = tmp_path / "fred_current_cache"
    seed = seed_local_current_cache_rehearsal(cache_dir)
    artifact = build_local_current_cache_dashboard_bridge(
        cache_dir=cache_dir,
        seed_tmp_cache_when_missing=False,
    )
    view_model = build_local_current_cache_dashboard_bridge_view_model(
        artifact=artifact,
    )

    assert seed["seeded_series_count"] == artifact["unique_official_series_count"]
    assert artifact["cache_dir_kind"] == "tmp"
    assert artifact["cache_scope"] == "explicit_local_current_cache"
    assert artifact["role_with_available_local_cache_chart_count"] == 37
    assert artifact["chart_coverage_status_counts"][
        "available_local_current_cache"
    ] == 37
    assert artifact["chart_coverage_status_counts"][
        "unavailable_no_official_series"
    ] == 2
    assert view_model["view_id"] == "current_macro_numeric_chart_coverage"
    assert view_model["phase74_local_current_cache_bridge_ready"] is True
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_phase74_bridge_rejects_forbidden_repo_cache_path() -> None:
    try:
        build_local_current_cache_dashboard_bridge(
            cache_dir="data/backtests/not_allowed",
            seed_tmp_cache_when_missing=False,
        )
    except ValueError as exc:
        assert "local current cache must be under" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("forbidden cache path should fail closed")


def test_show_local_current_cache_dashboard_bridge_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_local_current_cache_dashboard_bridge.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "local_current_cache_dashboard_bridge_ready=true" in completed.stdout
    assert "role_with_available_local_cache_chart_count=37" in completed.stdout
    assert "tmp_seeded_local_current_cache_rehearsal_ready=true" in completed.stdout
    assert "result=passed" in completed.stdout
