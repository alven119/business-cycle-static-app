from __future__ import annotations

from business_cycle.cycle_state.phase_start_research_assistant import (
    build_phase_start_research_assistant,
    summarize_phase_start_research_assistant,
)


def test_phase_start_research_assistant_preserves_declared_registry_boundary() -> None:
    artifact = build_phase_start_research_assistant()

    assert artifact["declared_current_phase"] == "boom"
    assert artifact["legal_next_phase"] == "recession"
    assert artifact["declared_phase_start_date_current_value"] is None
    assert artifact["declared_phase_start_date_unchanged"] is True
    assert artifact["registry_write_allowed"] is False
    assert artifact["declared_registry_modified"] is False
    assert artifact["user_confirmation_required"] is True


def test_phase_start_research_assistant_emits_required_hypotheses() -> None:
    artifact = build_phase_start_research_assistant()
    hypotheses = {
        hypothesis["hypothesis_id"]: hypothesis
        for hypothesis in artifact["hypotheses"]
    }

    assert artifact["hypothesis_count"] >= 2
    assert artifact["user_prior_hypothesis_present"] is True
    assert artifact["evidence_based_hypothesis_present"] is True
    assert hypotheses["user_prior_hypothesis"]["hypothesis_status"] == (
        "user_input_unverified"
    )
    assert hypotheses["evidence_based_research_hypothesis"]["hypothesis_status"] in {
        "insufficient_evidence",
        "needs_user_review",
    }
    assert hypotheses["evidence_based_research_hypothesis"][
        "registry_write_allowed"
    ] is False


def test_evidence_based_hypothesis_does_not_force_date_when_inputs_missing() -> None:
    artifact = build_phase_start_research_assistant()
    evidence_hypothesis = [
        hypothesis
        for hypothesis in artifact["hypotheses"]
        if hypothesis["hypothesis_id"] == "evidence_based_research_hypothesis"
    ][0]

    if evidence_hypothesis["hypothesis_status"] == "insufficient_evidence":
        assert evidence_hypothesis["candidate_start_date_or_window"] is None
        assert evidence_hypothesis["missing_evidence"]


def test_phase48_wiring_plan_contains_required_lanes_and_priorities() -> None:
    artifact = build_phase_start_research_assistant()
    plan = artifact["phase48_boom_monitor_evidence_wiring_plan"]

    assert plan["phase48_boom_monitor_evidence_wiring_plan_ready"] is True
    assert plan["boom_continuation_candidate_inputs"]
    assert plan["boom_ending_watch_candidate_inputs"]
    assert plan["recession_watch_candidate_inputs"]
    assert plan["recession_confirmation_candidate_inputs"]
    priority_ids = {
        item["role_id"]
        for item in plan["highest_product_value_evidence_to_wire_first"]
    }
    assert "boom_claims_u_shape" in priority_ids
    assert "recession_employment_confirmation" in priority_ids


def test_phase_start_summary_hard_gates_pass() -> None:
    summary = summarize_phase_start_research_assistant()

    assert summary["phase_start_research_assistant_contract_ready"] is True
    assert summary["phase_start_research_assistant_runtime_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["declared_phase_start_date_unchanged"] is True
    assert summary["false_precision_start_date_count"] == 0
    assert summary["phase_age_used_as_transition_gate"] is False
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["result"] == "passed"
