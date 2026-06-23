from __future__ import annotations

from business_cycle.shadow_model.phase_evidence_evaluators import (
    evaluate_phase_evidence,
)


def test_phase_evidence_evaluator_is_deterministic() -> None:
    first = evaluate_phase_evidence(
        role_id="growth_nonfarm_payrolls",
        as_of="2019-12-31",
        data_mode="revised",
    )
    second = evaluate_phase_evidence(
        role_id="growth_nonfarm_payrolls",
        as_of="2019-12-31",
        data_mode="revised",
    )

    assert first == second


def test_metamorphic_opposite_direction_changes_support() -> None:
    supportive = evaluate_phase_evidence(
        role_id="growth_nonfarm_payrolls",
        as_of="2019-12-31",
        data_mode="revised",
        observations=[
            {"date": "2019-11-30", "value": 1.0, "data_mode": "revised"},
            {"date": "2019-12-31", "value": 2.0, "data_mode": "revised"},
        ],
    )
    contradictory = evaluate_phase_evidence(
        role_id="growth_nonfarm_payrolls",
        as_of="2019-12-31",
        data_mode="revised",
        observations=[
            {"date": "2019-11-30", "value": 2.0, "data_mode": "revised"},
            {"date": "2019-12-31", "value": 1.0, "data_mode": "revised"},
        ],
    )

    assert supportive["supportive"] is True
    assert contradictory["contradictory"] is True
    assert supportive["candidate_phase_emitted"] is False
    assert contradictory["candidate_phase_emitted"] is False
