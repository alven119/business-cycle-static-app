from __future__ import annotations

import subprocess
import sys

from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation,
    build_transition_risk_evidence_accumulation_view_model,
    summarize_transition_risk_evidence_accumulation,
)


def test_transition_risk_evidence_accumulation_passes() -> None:
    summary = summarize_transition_risk_evidence_accumulation()

    assert summary["result"] == "passed"
    assert summary["transition_risk_evidence_accumulation_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["transition_accumulation_lane_card_count"] == 13
    assert summary["evidence_accumulation_event_count"] == 39
    assert summary["continuation_lane_card_count"] == 4
    assert summary["watch_lane_card_count"] == 5
    assert summary["confirmation_lane_card_count"] == 4
    assert summary["watch_confirmation_boundary_count"] == 13
    assert summary["lane_with_missing_evidence_count"] == 13
    assert summary["missing_evidence_event_count"] == 39
    assert summary["contradictory_evidence_lane_count"] == 0
    assert summary["contradictory_evidence_event_count"] == 0
    assert summary["next_required_observation_count"] == 13
    assert summary["phase_presence_transition_separation_valid"] is True
    assert summary["watch_confirmation_separation_valid"] is True
    assert summary["missing_value_treated_as_neutral_count"] == 0
    assert summary["metadata_only_promoted_to_phase_support_count"] == 0
    assert summary["contradictory_evidence_promoted_to_confirmation_count"] == 0
    assert summary["watch_promoted_to_confirmation_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["prohibited_output_field_count"] == 0


def test_transition_risk_evidence_accumulation_preserves_boundaries() -> None:
    artifact = build_transition_risk_evidence_accumulation()

    assert artifact["output_mode"] == (
        "research_only_transition_risk_evidence_accumulation"
    )
    assert artifact["research_only"] is True
    assert artifact["trust_metadata"]["watch_confirmation_separated"] is True
    assert artifact["trust_metadata"]["phase_presence_transition_separated"] is True
    assert artifact["trust_metadata"]["missing_values_are_neutral"] is False
    assert artifact["trust_metadata"]["metadata_only_is_phase_support"] is False
    assert "phase_rank_or_score" in artifact["prohibited_uses"]
    assert all(
        card["phase_presence_transition_boundary_valid"]
        for card in artifact["accumulation_lane_cards"]
    )
    assert all(
        row["next_required_observation_zh"]
        for row in artifact["next_required_observations"]
    )


def test_transition_risk_evidence_accumulation_view_model_is_bundle_ready() -> None:
    view_model = build_transition_risk_evidence_accumulation_view_model()

    assert view_model["view_id"] == "transition_risk_evidence_accumulation"
    assert view_model["transition_risk_evidence_accumulation_ready"] is True
    assert len(view_model["accumulation_lane_cards"]) == 13
    assert len(view_model["next_required_observations"]) == 13
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_show_transition_risk_evidence_accumulation_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_transition_risk_evidence_accumulation.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "transition_risk_evidence_accumulation_ready=true" in completed.stdout
    assert "transition_accumulation_lane_card_count=13" in completed.stdout
    assert "evidence_accumulation_event_count=39" in completed.stdout
    assert "next_required_observation_count=13" in completed.stdout
    assert "result=passed" in completed.stdout
