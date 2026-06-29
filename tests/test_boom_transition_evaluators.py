from __future__ import annotations

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)
from business_cycle.transition_monitor.boom_evidence_evaluators import (
    evaluate_boom_transition_evidence,
)
from business_cycle.transition_monitor.boom_evidence_wiring import (
    load_boom_transition_indicator_roles,
)
from business_cycle.transition_monitor.boom_transition_rules import lane_rule


def _rule_rows() -> dict[str, dict[str, object]]:
    return {row["role_id"]: row for row in build_book_phase_evidence_rule_rows()}


def _role_rows() -> dict[str, dict[str, object]]:
    readiness = build_current_evidence_readiness()
    return {row["role_id"]: row for row in readiness["role_readiness_rows"]}


def test_missing_claims_role_abstains_in_watch_lane() -> None:
    roles = load_boom_transition_indicator_roles()
    item = evaluate_boom_transition_evidence(
        role_row=_role_rows()["boom_claims_u_shape"],
        rule_row=_rule_rows()["boom_claims_u_shape"],
        role_contract=roles["boom_claims_u_shape"],
        lane_rule=lane_rule("boom_ending_watch"),
    )

    assert item["lane_evidence_state"] == "abstained"
    assert item["explicit_abstention"] is True
    assert item["watch_vs_confirmation_semantics"] == "watch_lane_not_confirmation"
    assert item["watch_evidence_promoted_to_confirmation"] is False
    assert item["smoothing_only_used_as_evidence"] is False
    assert item["raw_direction_alone_used_as_turning_point"] is False
    assert item["missing_treated_as_neutral"] is False
    assert item["missing_treated_as_zero"] is False


def test_recession_confirmation_role_can_emit_confirmation_lane_evidence() -> None:
    roles = load_boom_transition_indicator_roles()
    role_row = dict(_role_rows()["recession_employment_confirmation"])
    role_row.update(
        {
            "current_evidence_status": "supportive",
            "current_phase_evidence_output_available": True,
            "blocker_reason_codes": [],
        }
    )
    item = evaluate_boom_transition_evidence(
        role_row=role_row,
        rule_row=_rule_rows()["recession_employment_confirmation"],
        role_contract=roles["recession_employment_confirmation"],
        lane_rule=lane_rule("recession_confirmation"),
    )

    assert item["lane_evidence_state"] == "supportive"
    assert item["explicit_abstention"] is False
    assert item["watch_vs_confirmation_semantics"] == "confirmation_lane_not_watch"
    assert item["confirmation_derived_from_watch_only"] is False
    assert item["arbitrary_threshold_used"] is False
    assert item["numeric_weight_used"] is False
    assert item["role_count_voting_used"] is False


def test_boom_watch_role_is_not_promoted_to_confirmation() -> None:
    roles = load_boom_transition_indicator_roles()
    role_row = dict(_role_rows()["boom_claims_u_shape"])
    role_row.update(
        {
            "current_evidence_status": "supportive",
            "current_phase_evidence_output_available": True,
            "blocker_reason_codes": [],
        }
    )
    item = evaluate_boom_transition_evidence(
        role_row=role_row,
        rule_row=_rule_rows()["boom_claims_u_shape"],
        role_contract=roles["boom_claims_u_shape"],
        lane_rule=lane_rule("recession_confirmation"),
    )

    assert item["lane_evidence_state"] == "abstained"
    assert item["explicit_abstention"] is True
    assert "boom_watch_role_not_confirmation_input" in item["blocker_reason_codes"]
    assert item["watch_evidence_promoted_to_confirmation"] is False
