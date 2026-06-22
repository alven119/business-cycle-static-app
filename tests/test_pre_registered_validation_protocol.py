from __future__ import annotations

from business_cycle.audits.pre_registered_validation import (
    summarize_pre_registered_validation_protocol,
)


def test_pre_registered_validation_protocol_hard_gates() -> None:
    summary = summarize_pre_registered_validation_protocol()

    assert summary["development_scenario_count"] == 5
    assert summary["historical_external_validation_scenario_count"] == 0
    assert summary["prospective_holdout_registered"] is True
    assert summary["prospective_holdout_result_inspected"] is False
    assert summary["final_untouched_holdout_ready"] is False
    assert summary["parameter_change_resets_holdout"] is True
    assert summary["result_peeking_allowed"] is False
    assert summary["holdout_protocol_complete"] is True
    assert summary["first_eligible_observation_period"] == "2026-07"


def test_qa4_candidate_model_holdout_is_not_registered() -> None:
    from business_cycle.audits.model_freeze_semantics import (
        summarize_model_freeze_and_holdout_semantics,
    )

    summary = summarize_model_freeze_and_holdout_semantics()

    assert summary["research_baseline_holdout_protocol_registered"] is True
    assert summary["book_faithful_candidate_holdout_registered"] is False
    assert summary["final_model_holdout_active"] is False
