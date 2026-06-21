from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_dgs10_segmented_query_and_substitution_are_blocked_pending_archive() -> None:
    rows = load_formal_temporal_gap_remediation()["rows"]
    row = next(item for item in rows if item["series_id"] == "DGS10")

    assert row["segmented_query_status"]["segment_query_count"] == 4
    assert row["segmented_query_status"]["segment_query_failure_count"] == 0
    assert row["segmented_query_status"]["earliest_exact_alfred_realtime_start"] == "2005-07-06"
    assert row["full_range_query_status"] == "failed"
    assert row["alfred_history_gap"] is True
    assert row["proposed_substitute_series"] == "GS10"
    assert row["final_strict_ready"] is False
