from __future__ import annotations

from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)


def test_major_group_observation_coverage_does_not_substitute_core_roles() -> None:
    summary = summarize_major_group_observation_coverage()

    assert summary["major_group_observation_coverage_ready"] is True
    assert summary["observation_ready_major_group_count"] > 0
    assert summary["candidate_input_complete_major_group_count"] == 0
    assert summary["group_ready_via_modern_substitution_count"] == 0
    assert summary["group_ready_with_missing_core_role_count"] == 0

