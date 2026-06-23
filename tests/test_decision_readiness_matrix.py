from __future__ import annotations

from business_cycle.shadow_model.decision_readiness_matrix import (
    build_decision_readiness_matrix,
    summarize_decision_readiness_matrix,
)


def test_decision_readiness_matrix_is_ready_and_non_emitting() -> None:
    summary = summarize_decision_readiness_matrix()

    assert summary["decision_readiness_matrix_ready"] is True
    assert summary["decision_readiness_matrix_row_count"] > 0
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_decision_output_field_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["phase_rank_output_count"] == 0
    assert summary["phase_score_output_count"] == 0


def test_decision_readiness_matrix_preserves_candidate_output_disabled() -> None:
    rows = build_decision_readiness_matrix()

    assert rows
    assert all(row["candidate_input_eligible"] is False for row in rows)
    assert all(row["candidate_selection_enabled"] is False for row in rows)
    assert all(row["candidate_phase_emitted"] is False for row in rows)
    assert all(row["current_phase_emitted"] is False for row in rows)
    assert all("candidate_phase" not in row for row in rows)
    assert all("current_phase" not in row for row in rows)
    assert all("phase_score" not in row for row in rows)
