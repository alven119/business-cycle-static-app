from __future__ import annotations

from business_cycle.shadow_model.observation_evaluators import (
    evaluate_observation_snapshot,
    summarize_book_core_observation_evaluators,
)
from business_cycle.shadow_model.runtime_input_snapshot import build_runtime_input_snapshot


def test_observation_evaluators_are_observation_only() -> None:
    summary = summarize_book_core_observation_evaluators()

    assert summary["observation_evaluator_layer_ready"] is True
    assert (
        summary["implemented_observation_evaluator_count"]
        == summary["runtime_observable_eligible_role_count"]
    )
    assert summary["new_runtime_observable_role_count"] > 0
    assert summary["observation_evaluator_with_numeric_threshold_count"] == 0
    assert summary["observation_evaluator_candidate_eligible_count"] == 0
    assert summary["observation_evaluator_emitted_phase_support_count"] == 0


def test_raw_direction_observation_is_not_phase_support() -> None:
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode="revised",
        evaluator_id="observation::recovery_initial_jobless_claims",
        role_id="recovery_initial_jobless_claims",
        series_id="initial_jobless_claims",
    )
    result = evaluate_observation_snapshot(snapshot)

    assert result["observation_state"].startswith("raw_direction")
    assert result["phase_support_emitted"] is False
    assert result["candidate_selection_eligible"] is False

