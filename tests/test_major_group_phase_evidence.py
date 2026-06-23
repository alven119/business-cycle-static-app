from __future__ import annotations

from business_cycle.shadow_model.major_group_evidence import (
    build_major_group_phase_evidence_rows,
    summarize_major_group_phase_evidence,
)


def test_major_group_phase_evidence_has_partial_groups_without_candidate_input() -> None:
    summary = summarize_major_group_phase_evidence()

    assert summary["major_group_phase_evidence_ready"] is True
    assert summary["phase_evidence_partial_major_group_count"] > 0
    assert summary["group_promoted_with_missing_core_count"] == 0
    assert summary["group_promoted_via_modern_extension_count"] == 0
    assert summary["candidate_input_complete_major_group_count"] == 0
    assert summary["numeric_weight_aggregation_count"] == 0
    assert summary["role_count_vote_count"] == 0


def test_major_groups_do_not_use_modern_or_supporting_substitution() -> None:
    rows = build_major_group_phase_evidence_rows()

    assert rows
    assert all(row["candidate_input_eligible"] is False for row in rows)
    assert all(row["modern_extension_used_as_core"] is False for row in rows)
    assert all(row["supporting_role_used_as_core"] is False for row in rows)
