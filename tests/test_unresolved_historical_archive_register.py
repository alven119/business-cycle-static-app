from __future__ import annotations

from business_cycle.audits.qa1_temporal_integrity_closure import (
    summarize_unresolved_historical_archive_register,
)


def test_unresolved_archive_register_disables_automatic_retry_and_silent_ignore() -> None:
    summary = summarize_unresolved_historical_archive_register()

    assert summary["unresolved_archive_register_row_count"] == 7
    assert summary["automatic_archive_retry_allowed"] is False
    assert summary["explicit_archive_research_command_required"] is True
    assert summary["unresolved_gap_silently_ignored_count"] == 0
    assert set(summary["unresolved_archive_series_ids"]) == {
        "RSAFS",
        "RRSFS",
        "DGORDER",
        "DGS10",
        "ICSA",
        "MORTGAGE30US",
        "DCOILWTICO",
    }
