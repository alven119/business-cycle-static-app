from __future__ import annotations

from business_cycle.audits.prospective_observation_inspection import (
    summarize_prospective_observation_inspection_policy,
)


def test_prospective_observation_inspection_policy_blocks_result_inspection() -> None:
    summary = summarize_prospective_observation_inspection_policy()

    assert summary["inspection_governance_ready"] is True
    assert summary["real_result_inspection_count"] == 0
    assert summary["candidate_result_inspection_count"] == 0
    assert summary["result_driven_parameter_change_count"] == 0
    assert summary["sealed_field_exposure_count"] == 0
    assert summary["prospective_result_inspected"] is False
