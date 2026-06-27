from __future__ import annotations

from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
    summarize_current_evidence_readiness,
)


def test_current_evidence_readiness_is_non_emitting() -> None:
    readiness = build_current_evidence_readiness(
        refresh_manifest={
            "snapshot_as_of": "2026-06-26",
            "data_mode": "revised_metadata_fixture",
            "live_fetch_succeeded": False,
            "cache_used": False,
            "fixture_used": True,
            "requested_series_count": 0,
            "fetched_series_count": 0,
            "stale_series_count_before": 0,
            "manifest_hash": "fixture",
            "series_refresh_rows": [],
        },
    )

    assert readiness["current_evidence_readiness_ready"] is True
    assert readiness["phase_profile_count"] == 4
    assert readiness["current_phase_emitted"] is False
    assert readiness["candidate_phase_emitted"] is False
    assert readiness["selected_phase_output_count"] == 0
    assert readiness["phase_rank_output_count"] == 0
    assert readiness["numeric_phase_score_output_count"] == 0
    assert readiness["role_count_voting_added_count"] == 0
    assert readiness["formal_phase_eligible_count"] == 0
    assert readiness["candidate_phase_eligible_count"] == 0
    assert readiness["why_not_formal_phase_present"] is True
    assert readiness["blocker_summary_present"] is True
    assert readiness["result"] == "passed"


def test_show_current_evidence_readiness_summary() -> None:
    summary = summarize_current_evidence_readiness(
        refresh_manifest={
            "snapshot_as_of": "2026-06-26",
            "data_mode": "revised_metadata_fixture",
            "live_fetch_succeeded": False,
            "cache_used": False,
            "fixture_used": True,
            "requested_series_count": 0,
            "fetched_series_count": 0,
            "stale_series_count_before": 0,
            "manifest_hash": "fixture",
            "series_refresh_rows": [],
        },
    )

    assert summary["phase_profile_count"] == 4
    assert summary["result"] == "passed"
