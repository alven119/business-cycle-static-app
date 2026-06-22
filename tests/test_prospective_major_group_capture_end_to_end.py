from __future__ import annotations

from business_cycle.audits.prospective_major_group_capture_fixtures import (
    summarize_prospective_major_group_capture_fixtures,
)


def test_major_group_capture_end_to_end_fixtures_pass_without_real_append() -> None:
    summary = summarize_prospective_major_group_capture_fixtures()

    assert summary["major_group_end_to_end_fixtures_ready"] is True
    assert summary["fixture_count"] == 18
    assert summary["fixture_pass_count"] == summary["fixture_count"]
    assert summary["invalid_fixture_accepted_count"] == 0
    assert summary["incomplete_group_marked_complete_count"] == 0
    assert summary["candidate_enabled_fixture_count"] == 0
    assert summary["real_registry_write_fixture_count"] == 0

