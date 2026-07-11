from __future__ import annotations

from business_cycle.transition_monitor.boom_transition_monitor import (
    build_boom_transition_monitor,
    summarize_boom_transition_monitor,
)
from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
    summarize_phase123_live_ordered_cycle_evidence_closure,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
)


def test_boom_transition_monitor_uses_declared_state_without_inference() -> None:
    monitor = build_boom_transition_monitor()

    assert monitor["declared_state_input_used"] is True
    assert monitor["declared_current_phase"] == "boom"
    assert monitor["legal_next_phase"] == "recession"
    assert monitor["current_data_used_to_infer_declared_phase_count"] == 0
    assert monitor["candidate_phase_emitted"] is False
    assert monitor["current_phase_emitted"] is False


def test_all_required_lanes_are_ready_and_separated() -> None:
    monitor = build_boom_transition_monitor()

    assert monitor["boom_continuation_evidence"]["lane_ready"] is True
    assert monitor["boom_ending_watch_evidence"]["lane_ready"] is True
    assert monitor["recession_watch_evidence"]["lane_ready"] is True
    assert monitor["recession_confirmation_evidence"]["lane_ready"] is True
    assert monitor["boom_ending_watch_evidence"]["watch_lane"] is True
    assert monitor["recession_watch_evidence"]["watch_lane"] is True
    assert monitor["recession_confirmation_evidence"]["confirmation_lane"] is True
    assert monitor["watch_confirmation_separation_valid"] is True
    assert monitor["recession_confirmation_not_derived_from_watch_only"] is True


def test_phase48_priority_evidence_is_wired_into_lanes() -> None:
    monitor = build_boom_transition_monitor()

    assert monitor["boom_transition_evidence_wiring_ready"] is True
    assert monitor["boom_transition_evaluator_runtime_ready"] is True
    assert monitor["required_priority_role_count"] == 5
    assert monitor["wired_priority_role_count"] == 5
    assert monitor["evaluable_priority_role_count"] > 0
    assert monitor["lane_output_count"] >= 4
    assert monitor[
        "boom_continuation_lane_has_evidence_or_explicit_abstention"
    ] is True
    assert monitor[
        "boom_ending_watch_lane_has_evidence_or_explicit_abstention"
    ] is True
    assert monitor[
        "recession_watch_lane_has_evidence_or_explicit_abstention"
    ] is True
    assert monitor[
        "recession_confirmation_lane_has_evidence_or_explicit_abstention"
    ] is True


def test_phase_age_unknown_status_is_not_a_transition_gate() -> None:
    monitor = build_boom_transition_monitor()

    assert monitor["declared_phase_start_date"] is None
    assert monitor["phase_age_context_available"] is False
    assert monitor["phase_age_status"] == "unknown_or_user_required"
    assert monitor["phase_age_used_as_transition_gate"] is False
    assert monitor["phase_age_false_precision_count"] == 0


def test_monitor_summary_hard_gates_pass() -> None:
    summary = summarize_boom_transition_monitor()

    assert summary["boom_transition_monitor_contract_ready"] is True
    assert summary["boom_transition_monitor_runtime_ready"] is True
    assert summary["boom_transition_evidence_wiring_ready"] is True
    assert summary["boom_transition_evaluator_runtime_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["required_priority_role_count"] == 5
    assert summary["wired_priority_role_count"] == 5
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["result"] == "passed"


def test_phase123_live_runtime_connects_transformed_evidence_without_phase_output() -> None:
    summary = summarize_phase123_live_ordered_cycle_evidence_closure()
    runtime = summary["runtime"]

    assert summary["result"] == "passed"
    assert summary["live_evidence_evaluator_connected"] is True
    assert summary["evaluated_role_count"] == 5
    assert summary["phase_evidence_output_role_count"] == 5
    assert summary["lane_output_count"] == 4
    assert runtime["lanes"]["boom_ending_watch"]["lane_status"] == (
        "supportive_evidence_present"
    )
    assert runtime["lanes"]["recession_confirmation"]["why_not_confirmation"]
    assert runtime["watch_confirmation_separation_verified"] is True
    assert runtime["raw_value_promoted_to_evidence_count"] == 0
    assert runtime["smoothing_alone_promoted_to_evidence_count"] == 0
    assert runtime["role_count_voting_added_count"] == 0
    assert runtime["candidate_phase_emitted"] is False
    assert runtime["current_phase_emitted"] is False


def test_phase123_missing_component_abstains_instead_of_becoming_neutral() -> None:
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    retail = next(
        row
        for row in snapshot["role_snapshots"]
        if row["role_id"] == "boom_retail_sales_vs_broad_pce"
    )
    retail["evidence_input_series"] = [
        row for row in retail["evidence_input_series"] if row["series_id"] != "PCEC96"
    ]

    runtime = build_live_ordered_cycle_evidence(snapshot)

    assert runtime["role_evidence"]["boom_retail_sales_vs_broad_pce"][
        "evidence_status"
    ] == "abstained"
    assert runtime["lanes"]["boom_ending_watch"]["lane_status"] == (
        "incomplete_evidence"
    )
    assert runtime["missing_value_treated_as_neutral_count"] == 0
    assert runtime["missing_value_treated_as_zero_count"] == 0


def test_phase123_component_disagreement_remains_mixed_without_voting() -> None:
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    retail = next(
        row
        for row in snapshot["role_snapshots"]
        if row["role_id"] == "boom_retail_sales_vs_broad_pce"
    )
    pce = next(
        row for row in retail["evidence_input_series"] if row["series_id"] == "PCEC96"
    )
    pce["observations"][-1]["value"] = 120

    runtime = build_live_ordered_cycle_evidence(snapshot)

    assert runtime["role_evidence"]["boom_retail_sales_vs_broad_pce"][
        "evidence_status"
    ] == "mixed"
    assert runtime["lanes"]["boom_ending_watch"]["lane_status"] == "mixed_evidence"
    assert runtime["role_count_voting_added_count"] == 0
    assert runtime["watch_promoted_to_confirmation_count"] == 0
