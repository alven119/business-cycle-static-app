from __future__ import annotations

from business_cycle.transition_monitor.boom_evidence_wiring import (
    PRIORITY_ROLE_IDS,
    build_boom_transition_evidence_wiring,
    load_boom_transition_indicator_roles,
    priority_role_ids_for_lane,
)


def test_phase48_wiring_has_all_priority_roles_and_lanes() -> None:
    wiring = build_boom_transition_evidence_wiring()

    assert wiring["result"] == "passed"
    assert wiring["boom_transition_evidence_wiring_ready"] is True
    assert wiring["boom_transition_evaluator_runtime_ready"] is True
    assert wiring["required_priority_role_count"] == 5
    assert wiring["wired_priority_role_count"] == 5
    assert wiring["evaluable_priority_role_count"] > 0
    assert wiring["lane_output_count"] >= 4
    assert {row["role_id"] for row in wiring["priority_role_rows"]} == set(
        PRIORITY_ROLE_IDS
    )


def test_phase48_wiring_maps_required_roles_to_transition_lanes() -> None:
    roles = load_boom_transition_indicator_roles()

    assert roles["boom_claims_u_shape"]["lane_mappings"] == [
        "boom_ending_watch",
        "recession_watch",
    ]
    assert "boom_retail_sales_vs_broad_pce" in priority_role_ids_for_lane(
        "boom_continuation"
    )
    assert "boom_private_investment" in priority_role_ids_for_lane(
        "boom_ending_watch"
    )
    assert set(priority_role_ids_for_lane("recession_confirmation")) == {
        "recession_employment_confirmation",
        "recession_consumption_confirmation",
    }


def test_phase48_wiring_preserves_safety_boundaries() -> None:
    wiring = build_boom_transition_evidence_wiring()

    assert wiring["watch_confirmation_separation_valid"] is True
    assert wiring["recession_confirmation_not_derived_from_watch_only"] is True
    assert wiring["phase_age_used_as_transition_gate"] is False
    assert wiring["current_data_used_to_infer_declared_phase_count"] == 0
    assert wiring["standalone_classifier_added_count"] == 0
    assert wiring["phase_rank_or_score_added_count"] == 0
    assert wiring["selected_phase_output_count"] == 0
    assert wiring["candidate_phase_emitted"] is False
    assert wiring["current_phase_emitted"] is False
    assert wiring["declared_registry_modified"] is False
    assert wiring["arbitrary_threshold_added_count"] == 0
    assert wiring["numeric_weight_added_count"] == 0
    assert wiring["role_count_voting_added_count"] == 0
