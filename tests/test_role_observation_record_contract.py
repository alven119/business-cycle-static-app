from __future__ import annotations

from business_cycle.shadow_model.evidence_observation_record import (
    build_role_observation_record,
    validate_role_observation_record,
)
from business_cycle.shadow_model.observation_evaluators import (
    evaluate_observation_snapshot,
)
from business_cycle.shadow_model.runtime_input_snapshot import build_runtime_input_snapshot


def test_role_observation_record_is_not_candidate_or_phase_evidence() -> None:
    snapshot = build_runtime_input_snapshot(
        as_of="2026-08-31",
        data_mode="revised",
        evaluator_id="observation::recovery_initial_jobless_claims",
        role_id="recovery_initial_jobless_claims",
        series_id="initial_jobless_claims",
    )
    record = build_role_observation_record(
        observation_result=evaluate_observation_snapshot(snapshot)
    )
    validation = validate_role_observation_record(record)

    assert validation["observation_record_count"] == 1
    assert validation["observation_record_marked_candidate_eligible_count"] == 0
    assert validation["raw_observation_record_mislabeled_phase_evidence_count"] == 0
    assert validation["prohibited_decision_field_count"] == 0

