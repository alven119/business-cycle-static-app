from __future__ import annotations

from business_cycle.transition_monitor.boom_transition_monitor import (
    build_boom_transition_monitor,
    summarize_boom_transition_monitor,
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
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["result"] == "passed"
