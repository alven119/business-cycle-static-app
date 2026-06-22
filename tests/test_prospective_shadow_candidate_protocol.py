from __future__ import annotations

from business_cycle.audits.prospective_shadow_protocol import (
    summarize_prospective_shadow_candidate_protocol,
)


def test_prospective_shadow_protocol_is_registered_not_started() -> None:
    summary = summarize_prospective_shadow_candidate_protocol()

    assert summary["prospective_protocol_registered"] is True
    assert summary["prospective_protocol_started"] is False
    assert summary["first_eligible_observation_period"] == "2026-07"
    assert summary["retrospective_backfill_allowed"] is False
    assert summary["retrospective_candidate_selection_allowed"] is False
    assert summary["holdout_registered"] is False
    assert summary["prospective_result_inspected"] is False
